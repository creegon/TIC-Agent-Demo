# TIC-Agent | 智能合规检查助手

> TIC（Testing, Inspection & Certification）行业合规法规监控 Agent Demo  
> 输入产品描述和目标市场，自动搜索适用法规标准，生成结构化合规报告

---

## 功能概述

| 功能 | 说明 |
|------|------|
| 产品智能分类 | 自动识别消费电子/玩具/食品接触/锂电池等品类 |
| 多市场法规搜索 | 覆盖中国、美国、欧盟、日本主流市场 |
| 法规标准详情抓取 | 从官方页面提取真实标准号和核心要求 |
| 结构化合规报告 | Markdown 表格格式，含风险等级（高/中/低） |
| 流式输出 | 实时显示 Agent 搜索推理过程 |

---

## 环境要求

- Python 3.10+
- 本地 Vertex AI 代理运行在 `http://127.0.0.1:8046/v1`（OpenAI 兼容接口）
- `BRAVE_API_KEY` 环境变量已配置

---

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

确保系统中已设置：

```bash
# Windows PowerShell
$env:BRAVE_API_KEY = "your_brave_api_key"

# 或在 .env 文件中（项目根目录）
BRAVE_API_KEY=your_brave_api_key
```

获取 Brave Search API Key：https://api.search.brave.com/

### 3. 启动本地模型代理

确保 Vertex AI 本地代理在 `http://127.0.0.1:8046` 运行，使用模型 `gemini-3-flash`。

### 4. 启动应用

```bash
python app.py
```

浏览器将自动打开 `http://localhost:7860`

---

## 项目结构

```
D:\TIC-Agent-Demo\
├── app.py          # Gradio 主应用，双栏布局，自定义 CSS
├── agent.py        # Agent 核心逻辑（OpenAI function calling，while 循环）
├── tools.py        # 搜索工具 + 网页抓取（含结果去噪过滤）
├── prompts.py      # System prompt + 搜索模板
├── requirements.txt
├── README.md
└── examples/       # 示例输出（可选）
```

---

## 技术架构

### Agent 框架
不依赖 LangChain，直接使用 OpenAI function calling 原生实现：

```python
while iteration < MAX_ITERATIONS:
    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOL_DEFINITIONS
    )
    if response.choices[0].message.tool_calls:
        # 执行工具，结果加入 messages
    else:
        # 生成最终报告，退出循环
```

### 搜索去噪策略
- 过滤电商/SEO垃圾域名（Amazon、eBay 等）
- 优先权威域名（ec.europa.eu、fcc.gov、cnca.org.cn 等）
- 关键词评分 + 标准号模式匹配
- 商业广告内容检测

### 法规覆盖范围

| 市场 | 主要法规/标准 |
|------|-------------|
| 欧盟 | CE标志、RED指令、RoHS、REACH、WEEE、玩具安全指令 2009/48/EC、电池法规 2023/1542/EU |
| 美国 | FCC认证、CPSC法规、ASTM F963、UL标准、FDA法规 |
| 中国 | CCC（3C认证）、GB强制标准、CNCA法规 |
| 日本 | PSE认证（电安法）、PSC标志、TELEC（无线设备） |

---

## 测试用例

```bash
# 在 Python 中直接测试（不启动 Gradio）
python -c "
from agent import run_agent_sync
result = run_agent_sync('蓝牙耳机', ['欧盟'], '支持蓝牙5.3，内置锂电池')
print(result[:2000])
"
```

### 预期测试用例
1. **蓝牙耳机 + 欧盟**：应包含 RED 指令、RoHS、IEC 62368-1 等
2. **儿童毛绒玩具 + 美国**：应包含 ASTM F963、CPSIA、CPSC 要求
3. **锂电池移动电源 + 中国+欧盟**：应包含 GB 31241、UN38.3、EU 电池法规
4. **不锈钢保温杯 + 日本**：应包含食品卫生法、食品接触材料标准

---

## 常见问题

**Q: 模型连接失败**  
A: 检查本地代理是否运行：`curl http://127.0.0.1:8046/v1/models`

**Q: 搜索返回空结果**  
A: 检查 `BRAVE_API_KEY` 是否有效：PowerShell 中运行 `$env:BRAVE_API_KEY`

**Q: 报告生成慢**  
A: Agent 需要进行多轮搜索（通常 5-8 次工具调用），正常耗时 1-3 分钟

**Q: 标准号准确性**  
A: Agent 被明确指示只引用真实标准号，但建议通过官方渠道验证

---

## 免责声明

本工具仅供演示和参考使用。**最终合规判定必须由 SGS、BV、TÜV Rheinland 等经认可的第三方检测机构进行专业评估。** 法规要求持续更新，请以官方最新版本为准。

---

*Powered by Gemini Flash · Brave Search · Demo Purpose Only*
