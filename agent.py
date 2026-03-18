# agent.py - Core agent logic using OpenAI function calling (no LangChain)

import json
import time
from datetime import datetime
from typing import Generator, Optional
from openai import OpenAI
from tools import TOOL_DEFINITIONS, execute_tool
from prompts import SYSTEM_PROMPT, REPORT_TEMPLATE
from knowledge_base import cross_validate, build_cross_validation_html

# Google AI Studio (Gemini API, OpenAI-compatible endpoint)
import os
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ.get("GOOGLE_AI_API_KEY", ""),
)

MODEL = "gemini-2.0-flash"
MAX_ITERATIONS = 15  # Safety limit for tool call loop (iter-4: increased for deeper search)
MAX_TOKENS = 8192

# ─────────────────────────────────────────────────────────────────────────────
# VIZ protocol helpers
# Visualization events are emitted as lines prefixed with __VIZ__:
# followed by a JSON payload. These are intercepted by app.py and
# stripped from the report output.
# ─────────────────────────────────────────────────────────────────────────────

def _viz(event_type: str, **kwargs) -> str:
    """Encode a visualization event as a special-prefixed line."""
    payload = {"type": event_type, **kwargs}
    return f"\n__VIZ__:{json.dumps(payload, ensure_ascii=False)}\n"


def _classify_domain(domain: str) -> str:
    """Classify a domain into a credibility tier."""
    OFFICIAL_DOMAINS = {
        # EU institutions
        "ec.europa.eu", "eur-lex.europa.eu", "europa.eu",
        # US govt
        "fcc.gov", "cpsc.gov", "fda.gov", "nist.gov", "ftc.gov", "epa.gov",
        # China govt
        "cnca.org.cn", "sac.gov.cn", "samr.gov.cn", "miit.gov.cn", "aqsiq.gov.cn",
        # Japan govt
        "meti.go.jp", "mhlw.go.jp", "nite.go.jp",
        # Generic .gov / .gov.xx
    }
    STANDARD_DOMAINS = {
        "iso.org", "iec.ch", "itu.int",
        "bsigroup.com", "din.de", "afnor.org", "astm.org", "ansi.org",
        "gb688.cn", "std.samr.gov.cn",
    }
    TIC_DOMAINS = {
        "sgs.com", "tuvsud.com", "bureauveritas.com", "intertek.com",
        "dekra.com", "ul.com", "tuvrheinland.com", "bv.com",
    }

    if not domain:
        return "ref"

    # Check exact domain match
    if domain in OFFICIAL_DOMAINS:
        return "official"
    if domain in STANDARD_DOMAINS:
        return "standard"
    if domain in TIC_DOMAINS:
        return "tic"

    # Heuristic: .gov TLD or .gov.* ccTLD
    parts = domain.split(".")
    if "gov" in parts or "gouv" in parts:
        return "official"

    # .org heuristic — often standards/NGO
    if domain.endswith(".org") or domain.endswith(".eu"):
        return "official"

    return "ref"


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
2. 针对**每个目标市场至少搜索3次**，使用不同关键词组合（法规名称、测试标准、认证机构+费用）
3. 优先抓取官方来源（.gov/.europa.eu/.org 等域名）的法规页面，获取详细测试要求
4. 生成**严格三段式**的Markdown格式合规报告

**报告必须严格包含以下三段，缺一不可**：

### 第一段：Executive Summary（≤200字）
2段话总结：①涉及几个市场、几项核心法规；②最高风险点和首要行动。给管理层看，不用技术细节。

### 第二段：详细分析（按市场分节）
每个市场独立Section，每条法规用表格展开，必须包含：
- 标准号 + 完整名称
- 版本年份/最新修订
- 适用范围
- 强制/自愿
- 主要认证机构（TUV/SGS/BV/UL等）
- 预估费用区间（标注"行业参考"）
- 预估认证周期
- 关键测试项目列表
- 常见不合格项（Top 3）

### 第三段：行动建议清单
编号列表，按优先级，每条可操作，标注高/中/低优先级。

注意：只引用真实存在的标准号，不要编造。费用和周期标注"行业参考，以机构报价为准"。"""
    
    return msg


def run_agent_stream(
    product: str,
    markets: list[str],
    extra_info: str = "",
) -> Generator[str, None, None]:
    """
    Run the compliance agent with streaming output.
    
    Yields strings progressively:
    - __VIZ__:{...} lines carrying visualization events (intercepted by app.py)
    - Status update text (tool call progress shown in report area)
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

    # Emit viz: session start
    yield _viz("session_start", product=product, markets=markets)
    
    iteration = 0
    tool_call_count = 0
    search_round = 0  # Track search rounds for color coding

    # Aggregated funnel counters across all searches
    total_raw = 0
    total_filtered = 0
    total_cited = 0  # tracked post-report via heuristic

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
                yield f"\n⚠️ **模型连接超时**，请稍后重试。\n"
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
                    search_round += 1
                    yield f"🔎 **搜索**：`{query[:80]}{'...' if len(query) > 80 else ''}`\n"
                    # Emit viz event: search keyword
                    yield _viz("search_start", query=query, round=search_round)

                elif tool_name == "fetch_page_content":
                    url = tool_args.get("url", "")
                    # Extract domain for display
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        if domain.startswith("www."):
                            domain = domain[4:]
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
                        results_list = result_data.get("results", [])
                        raw_count = result_data.get("total_found", len(results_list))
                        filtered_count = result_data.get("after_filter", len(results_list))
                        count = len(results_list)

                        total_raw += raw_count
                        total_filtered += filtered_count

                        yield f"  ✅ 获得 {count} 条相关结果\n"

                        # Build source info for viz
                        sources = []
                        for r in results_list:
                            domain = r.get("domain", "")
                            tier = _classify_domain(domain)
                            sources.append({
                                "domain": domain,
                                "title": r.get("title", "")[:60],
                                "tier": tier,
                            })

                        # Emit viz event: search results with source credibility
                        yield _viz(
                            "search_results",
                            query=tool_args.get("query", ""),
                            round=search_round,
                            raw_count=raw_count,
                            filtered_count=filtered_count,
                            result_count=count,
                            sources=sources,
                        )

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
                # Heuristic: count inline citations (URLs or standard numbers)
                import re
                cited_urls = len(re.findall(r'https?://\S+', final_content))
                cited_standards = len(re.findall(
                    r'\b(?:EN|IEC|ISO|GB|UL|ASTM|JIS|ANSI|BS|DIN)\s*\d+[\d\-/\.]*',
                    final_content
                ))
                total_cited = cited_urls + min(cited_standards, 15)

                # Emit final funnel summary
                yield _viz(
                    "funnel_summary",
                    total_raw=total_raw,
                    total_filtered=total_filtered,
                    total_cited=total_cited,
                    search_rounds=search_round,
                )

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

                # ── Cross-validation: compare search results with knowledge base ──
                try:
                    cross_result = cross_validate(final_content, product, markets)
                    cross_html = build_cross_validation_html(cross_result)
                    if cross_html:
                        yield _viz("cross_validation", html=cross_html,
                                   verified=len(cross_result.get("verified", [])),
                                   supplemental=len(cross_result.get("supplemental", [])),
                                   new_found=len(cross_result.get("new_found", [])))
                except Exception:
                    pass  # Cross-validation is non-critical

                # ── Emit messages snapshot for follow-up use ──
                # Add the final assistant message (already in messages list)
                yield _viz("messages_snapshot", messages=messages)
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
            # Emit funnel even at max-iteration fallback
            yield _viz(
                "funnel_summary",
                total_raw=total_raw,
                total_filtered=total_filtered,
                total_cited=0,
                search_rounds=search_round,
            )
            yield "\n\n" + final_content
            # Emit messages snapshot for follow-up
            messages.append({"role": "assistant", "content": final_content})
            yield _viz("messages_snapshot", messages=messages)
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
        # Strip viz events for sync mode
        if not chunk.strip().startswith("__VIZ__:"):
            parts.append(chunk)
    return "".join(parts)


def follow_up_stream(
    messages: list[dict],
    question: str,
) -> Generator[str, None, None]:
    """
    Follow-up question stream: given existing conversation messages,
    add the user's follow-up question and get a streaming response.
    
    Does NOT re-run tools/searches — uses only existing context.
    Yields text chunks for streaming display.
    """
    if not question or not question.strip():
        yield "❌ 请输入追问内容"
        return
    
    if not messages:
        yield "❌ 没有对话上下文，请先生成合规报告"
        return
    
    # Add the follow-up question to the conversation
    follow_up_messages = list(messages) + [
        {
            "role": "user",
            "content": (
                f"基于上面的合规报告和搜索结果，请回答以下追问：\n\n{question.strip()}\n\n"
                "请直接回答，引用报告中的相关内容。如果报告中没有相关信息，请说明并给出建议。"
                "回答使用Markdown格式，清晰简洁。"
            ),
        }
    ]
    
    try:
        # Use streaming for follow-up responses
        stream = client.chat.completions.create(
            model=MODEL,
            messages=follow_up_messages,
            max_tokens=MAX_TOKENS,
            temperature=0.3,
            stream=True,
        )
        
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
                
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            yield f"\n⚠️ **连接超时**，请稍后重试。\n"
        else:
            yield f"\n❌ **追问失败**：{error_msg}\n"


def extract_messages_from_stream(product: str, markets: list[str], extra_info: str = "") -> list[dict]:
    """
    Run the full agent and return the final messages list for follow-up use.
    This is a helper to capture messages; main streaming is done in run_agent_stream.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(product, markets, extra_info)},
    ]
    return messages
