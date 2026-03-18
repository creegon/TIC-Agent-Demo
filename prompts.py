# prompts.py - System prompt and template definitions for TIC Compliance Agent
# iter-4: 提升信息密度 — 三段式结构 + 法规详细字段 + 搜索策略优化

SYSTEM_PROMPT = """你是一位资深的TIC（测试、检验与认证）行业合规专家，拥有超过15年的消费品国际合规经验。

## 专业能力
- 精通中国（GB/CCC/CNCA）、美国（FCC/CPSC/FDA/UL）、欧盟（CE/RoHS/REACH/WEEE）、日本（PSE/PSC/TELEC）的消费品法规体系
- 熟悉各类产品测试标准、认证流程、费用范围和认证周期
- 能识别最新法规变更、常见不合格项及整改建议

## 工具使用策略（必须严格遵守）
当用户提交产品合规查询时，**按以下顺序执行**：

**第一阶段：充分搜索（每个市场至少3次搜索）**
1. 搜索该产品在目标市场的强制性法规：`{产品} {市场} mandatory regulation certification 2023 2024`
2. 搜索具体测试标准：`{产品} {市场} testing standard IEC EN GB UL requirement`
3. 搜索认证机构和流程：`{产品} {市场} certification body process TUV SGS BV UL cost timeline`
4. **优先访问官方来源**（.gov .europa.eu .gov.cn .org 域名）——对搜索到的官方页面执行fetch_page_content获取详细要求

**第二阶段：抓取关键页面**
- 对每个市场最重要的1-2个官方法规页面执行fetch_page_content
- 重点抓取：具体测试项目、限量值、适用范围声明

**第三阶段：生成报告**
- 基于搜索+抓取的真实信息，填充下方报告模板

## ⚠️ 数据真实性要求
- 只引用真实存在的标准号，**不编造**
- 费用/周期数据标注"行业参考，以机构报价为准"
- 如搜索结果不足，明确标注"待核实"

## 报告格式（严格按三段式输出）

### 第一段：Executive Summary（≤200字，中文）
用2段话总结：①本产品需要满足几个市场、几项核心法规；②最高风险点和首要行动。
面向管理层，不用技术细节，只说结论和行动。

### 第二段：详细分析（按市场分节）
每个目标市场独立一个Section，格式如下：

```
## 🇺🇸 [市场名称] 合规要求

### [法规/认证名称]
| 字段 | 内容 |
|------|------|
| 标准号 | 例：47 CFR Part 15 / EN 55032:2015 |
| 完整名称 | 例：FCC Part 15 — 无意辐射设备认证 |
| 版本/最新修订 | 例：2021年修订版 |
| 适用范围 | 例：所有无线频率设备，含蓝牙、Wi-Fi |
| 强制/自愿 | 强制（上市必须） |
| 主要认证机构 | TUV Rheinland / SGS / UL / Intertek |
| 预估费用 | USD 1,500–4,000（行业参考，以机构报价为准） |
| 预估周期 | 6–10周 |
| 关键测试项目 | • 辐射发射测试<br>• 传导干扰测试<br>• ESD静电放电 |
| 常见不合格项（Top 3） | 1. 辐射发射超标<br>2. 标签标识不符合要求<br>3. 说明书缺少FCC声明 |
```

（每个市场可包含多条法规，逐一展开）

### 第三段：行动建议清单
编号列表，按优先级排列，每条可操作：
1. **[优先级：高]** 立即联系TUV/SGS申请FCC/CE测试——预计X周内完成
2. ...

---

## 最终输出必须完整包含以上三段，缺少任何一段均为不合格输出。
"""

REPORT_TEMPLATE = """
# TIC 合规检查报告

**产品**：{product}
**目标市场**：{markets}
**报告生成时间**：{timestamp}

---

{content}

---
*本报告由TIC-Agent智能合规助手生成，仅供参考。费用及周期均为行业参考值，最终合规判定请联系SGS、BV、TÜV等认可检测机构进行专业评估。法规要求会随时更新，请以官方最新版本为准。*
"""

SEARCH_QUERIES = {
    "消费电子": {
        "EU": [
            "{product} CE marking certification requirements 2024",
            "{product} EU RED directive 2014/53/EU radio equipment compliance",
            "{product} RoHS REACH WEEE compliance Europe testing",
            "{product} EN 55032 EMC emission standard Europe",
            "{product} CE certification cost timeline TUV SGS",
        ],
        "US": [
            "{product} FCC certification requirements Part 15 2024",
            "{product} CPSC safety regulations consumer product USA",
            "{product} UL standard consumer electronics certification",
            "{product} FCC ID authorization process cost timeline",
            "{product} CPSC testing lab accredited USA",
        ],
        "CN": [
            "{product} CCC认证要求 中国强制认证 2024",
            "{product} 3C认证 国家强制标准 GB标准",
            "{product} 中国电子产品 CCC认证费用 周期",
            "{product} CNCA 认证目录 消费电子",
            "{product} GB/T标准 电磁兼容 EMC",
        ],
        "JP": [
            "{product} PSE certification Japan mandatory 2024",
            "{product} TELEC certification wireless Japan MIC",
            "{product} Japan Electrical Appliance Safety Law PSE",
            "{product} PSE mark cost timeline Japan electronics",
            "{product} Japan VCCI EMC standard electronics",
        ],
    },
    "玩具": {
        "EU": [
            "{product} EU toy safety directive 2009/48/EC requirements",
            "{product} EN 71 toy standard testing Europe",
            "{product} CE toy certification cost timeline Europe",
            "{product} toy chemical requirements REACH phthalates Europe",
        ],
        "US": [
            "{product} ASTM F963 toy safety standard testing",
            "{product} CPSC toy regulations children safety USA",
            "{product} CPSIA children product certificate CPC",
            "{product} toy lead content CPSC limit testing",
        ],
        "CN": [
            "{product} GB 6675 玩具安全标准 要求",
            "{product} 玩具 CCC认证 强制认证",
            "{product} 玩具 GB标准 测试机构 费用",
        ],
        "JP": [
            "{product} ST mark Japan toy safety standard",
            "{product} Japan toy standard PSC safety mark",
            "{product} Japan toy certification cost timeline",
        ],
    },
    "锂电池": {
        "EU": [
            "{product} EU battery regulation 2023/1542 requirements",
            "{product} IEC 62133 lithium battery certification Europe",
            "{product} UN38.3 transport test battery requirements",
            "{product} EU battery directive CE certification cost",
            "{product} lithium battery REACH RoHS compliance Europe",
        ],
        "US": [
            "{product} UL 2054 lithium battery standard certification",
            "{product} FCC battery certification requirements",
            "{product} DOT lithium battery transport UN38.3",
            "{product} lithium battery CPSC safety standard USA",
        ],
        "CN": [
            "{product} GB 31241 锂电池安全标准",
            "{product} 移动电源 强制认证 CCC",
            "{product} 锂电池 GB/T 认证费用 周期",
        ],
        "JP": [
            "{product} PSE lithium battery Japan mandatory",
            "{product} Japan battery safety standard PSE mark",
            "{product} Japan lithium battery certification cost timeline",
        ],
    },
    "食品接触": {
        "EU": [
            "{product} EU food contact materials regulation 1935/2004",
            "{product} food grade material EU standard testing",
            "{product} food contact material migration testing Europe",
            "{product} BfR recommendation food safe material Europe",
        ],
        "US": [
            "{product} FDA food contact materials compliance 21 CFR",
            "{product} NSF certification food safety standard",
            "{product} FDA food grade testing requirements USA",
        ],
        "CN": [
            "{product} GB 4806 食品接触材料国家标准",
            "{product} 食品安全国家标准 食品接触",
            "{product} 食品接触材料 检测机构 费用",
        ],
        "JP": [
            "{product} Japan food contact standard Food Sanitation Act",
            "{product} 食品衛生法 食品接触材料 Japan",
            "{product} Japan food contact testing certification cost",
        ],
    },
    "纺织品": {
        "EU": [
            "{product} EU textile regulation REACH OEKO-TEX",
            "{product} EN ISO textile standard flammability safety",
            "{product} OEKO-TEX Standard 100 certification textile",
            "{product} EU textile labeling regulation 1007/2011",
        ],
        "US": [
            "{product} CPSC textile flammability standard USA",
            "{product} ASTM textile testing standard",
            "{product} FTC textile fiber products identification act",
        ],
        "CN": [
            "{product} GB 18401 纺织品安全标准",
            "{product} 纺织品 强制性标准 GB 甲醛",
            "{product} 纺织品 检测 认证机构 费用",
        ],
        "JP": [
            "{product} Japan textile safety standard regulation",
            "{product} 家庭用品品質表示法 textile Japan",
        ],
    },
}
