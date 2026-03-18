# agent.py - Core agent logic using OpenAI function calling (no LangChain)

import json
import time
from datetime import datetime
from typing import Generator, Optional
from openai import OpenAI
from tools import TOOL_DEFINITIONS, execute_tool
from prompts import SYSTEM_PROMPT, REPORT_TEMPLATE

# Local Vertex AI proxy (OpenAI-compatible)
client = OpenAI(
    base_url="http://127.0.0.1:8046/v1",
    api_key="dummy",
)

MODEL = "gemini-3-flash"
MAX_ITERATIONS = 10  # Safety limit for tool call loop
MAX_TOKENS = 8192


def build_user_message(product: str, markets: list[str], extra_info: str = "") -> str:
    """Build the initial user message."""
    market_str = "、".join(markets) if markets else "未指定"
    
    msg = f"""请为以下产品生成完整的合规检查报告：

**产品描述**：{product}
**目标市场**：{market_str}
"""
    
    if extra_info and extra_info.strip():
        msg += f"**补充信息**：{extra_info.strip()}\n"
    
    msg += """
请按以下步骤处理：
1. 分析产品类别（消费电子/玩具/食品接触/纺织/化学品等）
2. 针对每个目标市场，搜索适用的法规和标准（每个市场搜索2-3次，使用不同关键词）
3. 对最重要的1-2个法规页面进行内容抓取，获取详细要求
4. 生成完整的Markdown格式合规报告

**报告必须包含**：
- 产品分类分析
- 各市场适用法规清单（含真实标准号）
- 合规检查清单（Markdown表格格式，含风险等级 高/中/低）
- 特别注意事项和常见违规点
- 建议测试项目及预估周期

注意：只引用真实存在的标准号，不要编造。"""
    
    return msg


def run_agent_stream(
    product: str,
    markets: list[str],
    extra_info: str = "",
) -> Generator[str, None, None]:
    """
    Run the compliance agent with streaming output.
    
    Yields strings progressively:
    - Status updates (tool calls being made)
    - Final report content
    """
    
    if not product.strip():
        yield "❌ 错误：请输入产品描述"
        return
    
    if not markets:
        yield "❌ 错误：请选择至少一个目标市场"
        return
    
    # Initialize conversation
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(product, markets, extra_info)},
    ]
    
    yield f"🔍 **正在分析产品**：{product}\n"
    yield f"🌍 **目标市场**：{'、'.join(markets)}\n\n"
    yield "---\n\n"
    
    iteration = 0
    tool_call_count = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        
        try:
            # Call model (non-streaming for tool-use phase)
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                max_tokens=MAX_TOKENS,
                temperature=0.2,
            )
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                yield f"\n⚠️ **模型连接超时**，请确认本地代理（http://127.0.0.1:8046）正在运行。\n"
            else:
                yield f"\n❌ **模型调用失败**：{error_msg}\n"
            return
        
        choice = response.choices[0]
        message = choice.message
        
        # Add assistant message to history
        messages.append(message.model_dump(exclude_none=True))
        
        # Check if there are tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_call_count += 1
                
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}
                
                # Show status to user
                if tool_name == "search_regulations":
                    query = tool_args.get("query", "")
                    yield f"🔎 **搜索**：`{query[:80]}{'...' if len(query) > 80 else ''}`\n"
                elif tool_name == "fetch_page_content":
                    url = tool_args.get("url", "")
                    # Extract domain for display
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                    except Exception:
                        domain = url[:50]
                    yield f"📄 **抓取页面**：`{domain}`\n"
                
                # Execute the tool
                try:
                    tool_result = execute_tool(tool_name, tool_args)
                    
                    # Check if search returned useful results
                    result_data = json.loads(tool_result)
                    if "error" in result_data and result_data.get("results", []) == []:
                        yield f"  ⚠️ 工具执行警告：{result_data['error']}\n"
                    elif tool_name == "search_regulations":
                        count = len(result_data.get("results", []))
                        yield f"  ✅ 获得 {count} 条相关结果\n"
                    elif tool_name == "fetch_page_content":
                        if result_data.get("content"):
                            chars = result_data.get("char_count", 0)
                            yield f"  ✅ 成功抓取 {chars} 字符\n"
                        else:
                            yield f"  ⚠️ 页面抓取失败：{result_data.get('error', '未知错误')}\n"
                
                except Exception as e:
                    tool_result = json.dumps({"error": f"Tool execution error: {str(e)}"})
                    yield f"  ❌ 工具执行失败：{str(e)}\n"
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })
            
            # Continue loop to process tool results
            continue
        
        # No tool calls - model is generating final response
        if choice.finish_reason in ("stop", "end_turn", "length"):
            final_content = message.content or ""
            
            if final_content:
                yield "\n\n---\n\n"
                
                # Add metadata header
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                yield f"# 合规检查报告\n\n"
                yield f"**产品**：{product}  \n"
                yield f"**目标市场**：{'、'.join(markets)}  \n"
                yield f"**报告时间**：{timestamp}  \n"
                if tool_call_count > 0:
                    yield f"**搜索轮次**：{tool_call_count} 次工具调用\n\n"
                yield "---\n\n"
                yield final_content
                yield "\n\n---\n\n"
                yield "*⚠️ 免责声明：本报告由AI生成，仅供参考。最终合规判定请联系SGS、BV、TÜV等认可检测机构进行专业评估。法规要求会随时更新，请以官方最新版本为准。*"
            else:
                yield "\n⚠️ 模型未返回内容，请重试。"
            
            return
        
        # Unexpected finish reason
        yield f"\n⚠️ 意外的停止原因：{choice.finish_reason}\n"
        return
    
    # Exceeded max iterations
    yield f"\n⚠️ 已达到最大工具调用次数（{MAX_ITERATIONS}次），生成部分报告...\n"
    
    # Force final generation
    messages.append({
        "role": "user",
        "content": "请根据已搜索到的信息，立即生成完整的合规报告。"
    })
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.2,
        )
        final_content = response.choices[0].message.content or ""
        if final_content:
            yield "\n\n" + final_content
    except Exception as e:
        yield f"\n❌ 最终报告生成失败：{str(e)}"


def run_agent_sync(
    product: str,
    markets: list[str],
    extra_info: str = "",
) -> str:
    """
    Synchronous version - returns complete report as string.
    Used for testing.
    """
    parts = []
    for chunk in run_agent_stream(product, markets, extra_info):
        parts.append(chunk)
    return "".join(parts)
