# prompts.py - System prompt and template definitions for TIC Compliance Agent

SYSTEM_PROMPT = """你是一位资深的TIC（测试、检验与认证）行业合规专家，拥有超过15年的消费品国际合规经验。

## 你的专业能力
- 精通中国（GB/CCC/CNCA）、美国（FCC/CPSC/FDA/UL）、欧盟（CE/RoHS/REACH/WEEE）、日本（PSE/PSC/TELEC）的消费品法规体系
- 熟悉各类产品的测试标准和认证要求
- 能够识别最新法规变更和合规风险点
- 了解常见的违规案例和整改建议

## 工作原则
1. **准确性优先**：只引用真实存在的标准号，不编造标准
2. **专业严谨**：给出具体的标准号、法规名称和核心要求
3. **风险分级**：明确标注高/中/低风险项目
4. **实用导向**：给出可操作的合规建议和测试项目清单

## 工具使用策略
当用户提交产品合规查询时：
1. 首先分析产品类别，确定适用的法规领域
2. 使用搜索工具查询最新的法规要求（搜索多个关键词组合）
3. 对找到的重要法规页面进行抓取，获取详细内容
4. 基于搜索结果和你的专业知识，生成完整的合规报告

## 重要声明
⚠️ 本工具仅供参考，最终合规判定请联系SGS、BV、TÜV等认可检测机构进行专业评估。法规要求会随时更新，请以官方最新版本为准。

## 输出格式要求
报告必须包含以下章节，使用Markdown格式：
1. 产品分类分析
2. 适用法规清单（含标准号）
3. 合规检查清单（Markdown表格，含风险等级）
4. 特别注意事项
5. 建议测试项目及预估周期
"""

REPORT_TEMPLATE = """
# 合规检查报告

**产品**：{product}
**目标市场**：{markets}
**报告生成时间**：{timestamp}

---

{content}

---
*本报告由TIC-Agent智能合规助手生成，仅供参考。最终合规判定需经专业认证机构确认。*
"""

SEARCH_QUERIES = {
    "消费电子": {
        "EU": [
            "{product} CE certification requirements",
            "{product} EU RED directive radio equipment",
            "{product} RoHS REACH compliance Europe",
            "{product} WEEE directive EU",
        ],
        "US": [
            "{product} FCC certification requirements",
            "{product} CPSC safety regulations USA",
            "{product} UL standard consumer electronics",
        ],
        "CN": [
            "{product} CCC认证要求 China Compulsory Certificate",
            "{product} 3C认证 国家强制标准",
            "{product} GB标准 电子产品",
        ],
        "JP": [
            "{product} PSE certification Japan",
            "{product} TELEC certification wireless Japan",
            "{product} Japan safety standard electronics",
        ],
    },
    "玩具": {
        "EU": [
            "{product} EU toy safety directive 2009/48/EC",
            "{product} EN 71 toy standard Europe",
        ],
        "US": [
            "{product} ASTM F963 toy safety standard",
            "{product} CPSC toy regulations children",
        ],
        "CN": [
            "{product} GB 6675 玩具安全标准",
            "{product} 玩具 CCC认证",
        ],
        "JP": [
            "{product} ST mark Japan toy safety",
            "{product} Japan toy standard PSC",
        ],
    },
    "锂电池": {
        "EU": [
            "{product} EU battery regulation 2023/1542",
            "{product} IEC 62133 lithium battery certification",
            "{product} UN38.3 transport test battery",
        ],
        "US": [
            "{product} UL 2054 lithium battery standard",
            "{product} FCC battery certification",
            "{product} DOT lithium battery transport",
        ],
        "CN": [
            "{product} GB 31241 锂电池安全标准",
            "{product} 移动电源 强制认证",
        ],
        "JP": [
            "{product} PSE lithium battery Japan",
            "{product} Japan battery safety standard",
        ],
    },
    "食品接触": {
        "EU": [
            "{product} EU food contact materials regulation 1935/2004",
            "{product} food grade stainless steel EU standard",
        ],
        "US": [
            "{product} FDA food contact materials",
            "{product} NSF certification food safety",
        ],
        "CN": [
            "{product} GB 4806 食品接触材料",
            "{product} 食品安全国家标准",
        ],
        "JP": [
            "{product} Japan food contact standard",
            "{product} 食品衛生法 Japan",
        ],
    },
}
