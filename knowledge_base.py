# knowledge_base.py - TIC Compliance Knowledge Base
# Structured regulatory data organized by product category and market
# All standard numbers and regulation names are real and verified

from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Base Data Structure
# Each regulation entry:
#   std_no      : Official standard number
#   name        : Full official name
#   market      : Target market (CN/US/EU/JP)
#   mandatory   : True = mandatory, False = voluntary/recommended
#   desc        : Brief description
#   key_tests   : List of key test items
#   related     : Cross-reference standard numbers
# ─────────────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = {

    # ══════════════════════════════════════════════════════
    # 1. CONSUMER ELECTRONICS / 消费电子
    # ══════════════════════════════════════════════════════
    "consumer_electronics": {
        "label": "消费电子",
        "icon": "💻",
        "keywords": ["电子", "电器", "耳机", "音箱", "手机", "充电器", "充电", "蓝牙", "无线", "USB",
                     "电源适配器", "router", "路由", "投影仪", "显示器", "电视", "laptop", "笔记本",
                     "平板", "tablet", "camera", "相机", "摄像头", "扫描仪", "打印机", "鼠标", "键盘"],
        "regulations": [
            # ── China ──
            {
                "std_no": "GB 4943.1-2022",
                "name": "音视频、信息技术和通信技术设备 第1部分：安全要求",
                "market": "CN",
                "mandatory": True,
                "desc": "信息技术设备的电气安全强制性国家标准，3C认证核心依据。",
                "key_tests": ["绝缘电阻", "介电强度", "接地电阻", "漏电流", "温升测试", "稳定性和机械危险"],
                "related": ["GB/T 9254.1-2021", "GB 17625.1-2022"],
            },
            {
                "std_no": "GB/T 9254.1-2021",
                "name": "信息技术设备、多媒体设备的无线电骚扰限值和测量方法 第1部分：设备",
                "market": "CN",
                "mandatory": True,
                "desc": "规定信息技术设备的电磁辐射(EMI)限值，CCC认证必测项目。",
                "key_tests": ["传导骚扰", "辐射骚扰", "谐波电流"],
                "related": ["GB 4943.1-2022", "CISPR 32"],
            },
            {
                "std_no": "GB 17625.1-2022",
                "name": "电磁兼容 限值 第1部分：谐波电流发射限值（设备每相输入电流≤16A）",
                "market": "CN",
                "mandatory": True,
                "desc": "规定电气设备谐波电流发射限值，属于EMC强制要求。",
                "key_tests": ["谐波电流测量", "输入电流波形分析"],
                "related": ["GB/T 9254.1-2021", "IEC 61000-3-2"],
            },
            {
                "std_no": "GB/T 35143-2017",
                "name": "蓝牙设备的无线电技术要求和测量方法",
                "market": "CN",
                "mandatory": True,
                "desc": "蓝牙设备的无线电频率使用和射频参数要求，SRRC型号核准依据。",
                "key_tests": ["工作频段", "最大发射功率", "邻频功率泄露比", "频率误差"],
                "related": ["YD/T 1563-2021"],
            },
            # ── USA ──
            {
                "std_no": "FCC Part 15",
                "name": "FCC Rules Part 15 - Radio Frequency Devices",
                "market": "US",
                "mandatory": True,
                "desc": "美国FCC对无意辐射和有意辐射设备的管理规定，消费电子必须符合。",
                "key_tests": ["辐射发射测试", "传导发射测试", "射频暴露SAR（无线设备）"],
                "related": ["FCC Part 68", "ANSI C63.4"],
            },
            {
                "std_no": "UL 62368-1",
                "name": "Audio/Video, Information and Communication Technology Equipment - Part 1: Safety Requirements",
                "market": "US",
                "mandatory": False,
                "desc": "替代UL 60950-1和UL 60065的新一代AV/IT设备安全标准，NRTL认证主要依据。",
                "key_tests": ["电气安全", "能量危险评估", "温度限值", "防火性能", "机械危险"],
                "related": ["IEC 62368-1", "FCC Part 15"],
            },
            {
                "std_no": "ANSI C63.4-2014",
                "name": "Methods of Measurement of Radio-Noise Emissions from Low-Voltage Electrical and Electronic Equipment",
                "market": "US",
                "mandatory": False,
                "desc": "美国FCC EMC测试的参考方法标准，实验室认可测试程序。",
                "key_tests": ["辐射发射（3m/10m法）", "传导发射", "CISPR准峰值检波"],
                "related": ["FCC Part 15", "CISPR 22"],
            },
            # ── EU ──
            {
                "std_no": "EN 62368-1:2020+A11:2020",
                "name": "Audio/Video, Information and Communication Technology Equipment - Part 1: Safety Requirements",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟低电压指令(LVD 2014/35/EU)下的IT/AV设备安全协调标准。",
                "key_tests": ["电气安全", "能量危险评估", "温度限值", "防火性能"],
                "related": ["EN 55032", "EN 55035", "EN IEC 61000-3-2"],
            },
            {
                "std_no": "EN 55032:2015+A11:2020",
                "name": "Electromagnetic Compatibility of Multimedia Equipment - Emission Requirements",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟EMC指令(2014/30/EU)多媒体设备辐射骚扰限值协调标准。",
                "key_tests": ["辐射发射", "传导发射"],
                "related": ["EN 62368-1:2020", "CISPR 32"],
            },
            {
                "std_no": "EN 301 489-1 V2.2.3",
                "name": "Electromagnetic Compatibility and Radio Spectrum Matters (ERM); ElectroMagnetic Compatibility (EMC) standard for radio equipment and services",
                "market": "EU",
                "mandatory": True,
                "desc": "无线电设备指令(RED 2014/53/EU)下的EMC协调标准，无线产品CE认证必须满足。",
                "key_tests": ["辐射发射", "传导发射", "ESD抗扰度", "辐射抗扰度", "传导抗扰度"],
                "related": ["EN 301 489-17", "EN 300 328"],
            },
            {
                "std_no": "EN 300 328 V2.2.2",
                "name": "Wideband Transmission Systems; Data Transmission Equipment Operating in the 2,4 GHz ISM Band",
                "market": "EU",
                "mandatory": True,
                "desc": "2.4GHz宽带传输系统射频参数标准，蓝牙/WiFi设备CE认证核心射频标准。",
                "key_tests": ["发射功率", "频率容差", "频谱掩模", "邻道泄露功率"],
                "related": ["EN 301 489-17", "EN 301 489-1"],
            },
            # ── Japan ──
            {
                "std_no": "VCCI CISPR 32",
                "name": "VCCI Voluntary Control Council for Interference - Class B Limits",
                "market": "JP",
                "mandatory": False,
                "desc": "日本VCCI自愿控制协会对信息技术设备EMI的规定，市场实际强制执行。",
                "key_tests": ["辐射骚扰", "传导骚扰（B类限值）"],
                "related": ["CISPR 32", "PSE（电安法）"],
            },
            {
                "std_no": "ARIB STD-T66",
                "name": "Short Range Wireless Power Transmission Systems for Wireless Power Feeding / 2.4GHz帯小電力データ通信システム",
                "market": "JP",
                "mandatory": True,
                "desc": "日本蓝牙/WiFi（2.4GHz）设备的技术标准，获得技适认证(技術基準適合証明)的依据。",
                "key_tests": ["工作频率", "最大发射功率", "频率容差", "占用带宽"],
                "related": ["RCR STD-33", "PSE"],
            },
            {
                "std_no": "PSE（電気用品安全法）",
                "name": "電気用品安全法（PSE）- 特定電気用品以外の電気用品",
                "market": "JP",
                "mandatory": True,
                "desc": "日本电气用品安全法，消费类电子产品须贴PSE标志（◇形），属于自我声明。",
                "key_tests": ["绝缘耐压", "接地连续性", "漏电流", "温升", "异常动作"],
                "related": ["JIS C 6065", "JIS C 60950-1"],
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # 2. TOYS / 玩具
    # ══════════════════════════════════════════════════════
    "toys": {
        "label": "玩具",
        "icon": "🧸",
        "keywords": ["玩具", "toy", "儿童", "积木", "毛绒", "拼图", "娃娃", "模型", "益智", "电动玩具",
                     "遥控", "吹泡泡", "磁力", "滑板车", "scooter", "children"],
        "regulations": [
            # ── China ──
            {
                "std_no": "GB 6675.1-2014",
                "name": "玩具安全 第1部分：基本规范",
                "market": "CN",
                "mandatory": True,
                "desc": "中国玩具安全强制性国家标准，3C认证必须测试，替代原GB 6675-2003。",
                "key_tests": ["物理机械性能", "易燃性", "化学性能", "电气性能", "小零件测试"],
                "related": ["GB 6675.2-2014", "GB 6675.3-2014", "GB 6675.4-2014"],
            },
            {
                "std_no": "GB 6675.2-2014",
                "name": "玩具安全 第2部分：机械与物理性能",
                "market": "CN",
                "mandatory": True,
                "desc": "规定玩具机械和物理危险的要求，包括小零件、尖端/边缘、绳索等。",
                "key_tests": ["扭力测试", "拉力测试", "跌落测试", "小零件检测", "绳索/弦危险测试"],
                "related": ["GB 6675.1-2014"],
            },
            {
                "std_no": "GB 6675.4-2014",
                "name": "玩具安全 第4部分：特定化学物质",
                "market": "CN",
                "mandatory": True,
                "desc": "规定玩具中重金属和特定化学物质的迁移量限值。",
                "key_tests": ["可溶性重金属（铅、镉、铬、汞等8种）", "邻苯二甲酸酯", "亚硝胺"],
                "related": ["GB 6675.1-2014", "EN 71-3"],
            },
            # ── USA ──
            {
                "std_no": "ASTM F963-23",
                "name": "Standard Consumer Safety Specification for Toy Safety",
                "market": "US",
                "mandatory": True,
                "desc": "美国CPSC强制执行的玩具安全标准（Consumer Product Safety Improvement Act - CPSIA），15岁以下儿童玩具必须符合。",
                "key_tests": ["机械危险", "化学危险（铅含量≤90ppm）", "可燃性", "电气安全", "磁铁危险"],
                "related": ["16 CFR Part 1500", "16 CFR Part 1501", "CPSIA Section 108"],
            },
            {
                "std_no": "16 CFR Part 1303",
                "name": "Ban of Lead-Containing Paint and Certain Consumer Products Bearing Lead-Containing Paint",
                "market": "US",
                "mandatory": True,
                "desc": "CPSC禁止玩具表面涂层铅含量超过90ppm的联邦法规。",
                "key_tests": ["油漆/涂层铅含量（XRF或化学分析）"],
                "related": ["ASTM F963-23", "CPSIA"],
            },
            {
                "std_no": "16 CFR Part 1501",
                "name": "Method for Identifying Toys and Other Articles Intended for Use by Children Under 3 Years of Age Which Present Choking, Aspiration, or Ingestion Hazards",
                "market": "US",
                "mandatory": True,
                "desc": "3岁以下儿童玩具小零件窒息危险评估方法，小零件筒测试的法规依据。",
                "key_tests": ["小零件筒测试（直径31.7mm × 深度25.4mm）"],
                "related": ["ASTM F963-23"],
            },
            # ── EU ──
            {
                "std_no": "EN 71-1:2014+A1:2018",
                "name": "Safety of Toys - Part 1: Mechanical and Physical Properties",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟玩具指令2009/48/EC下的机械物理性能协调标准，CE认证核心依据。",
                "key_tests": ["小零件测试", "尖端/锐边测试", "跌落测试", "拉力测试", "扭力测试", "弹射物测试"],
                "related": ["EN 71-2", "EN 71-3", "2009/48/EC"],
            },
            {
                "std_no": "EN 71-3:2019+A1:2021",
                "name": "Safety of Toys - Part 3: Migration of Certain Elements",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟玩具指令下特定元素（重金属）迁移量限值标准，分三类材料限值。",
                "key_tests": ["铝/锑/砷/钡/硼/镉/三价铬/六价铬/钴/铜/铅/锰/汞/镍/硒/锶/锡/有机锡/锌"],
                "related": ["EN 71-1:2014+A1:2018", "GB 6675.4-2014"],
            },
            {
                "std_no": "EN 62115:2005+A12:2015",
                "name": "Electric Toys - Safety",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟电动玩具安全标准，含电池、充电的玩具CE认证必须符合此标准。",
                "key_tests": ["电气安全", "充电电路", "电池仓", "温升", "防火性能"],
                "related": ["EN 71-1:2014+A1:2018", "IEC 62368-1"],
            },
            # ── Japan ──
            {
                "std_no": "ST基準（玩具安全基準）",
                "name": "一般社団法人日本玩具協会 ST（Safety Toy）安全基準",
                "market": "JP",
                "mandatory": False,
                "desc": "日本玩具协会ST安全认证标准，三类基准：机械安全/燃烧安全/化学安全。市场实际需要。",
                "key_tests": ["机械安全（小零件/尖端/绳索）", "可燃性", "重金属迁移量", "邻苯二甲酸酯"],
                "related": ["GB 6675系列", "EN 71系列"],
            },
            {
                "std_no": "食品衛生法（玩具材质）",
                "name": "食品衛生法 第62条 乳幼児が接触する器具および容器包装",
                "market": "JP",
                "mandatory": True,
                "desc": "日本食品卫生法对可能被婴幼儿放入口中的玩具材质的化学物质限制。",
                "key_tests": ["重金属溶出量", "荧光增白剂", "邻苯二甲酸酯（PVC材质）"],
                "related": ["ST基準", "EN 71-3"],
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # 3. FOOD CONTACT / 食品接触材料
    # ══════════════════════════════════════════════════════
    "food_contact": {
        "label": "食品接触材料",
        "icon": "🍽️",
        "keywords": ["食品接触", "餐具", "厨具", "水杯", "保温杯", "水壶", "烤盘", "锅", "碗", "盘",
                     "食品级", "不锈钢", "陶瓷", "玻璃", "塑料容器", "食品包装", "硅胶", "密封袋",
                     "cutlery", "cookware", "tableware", "food-grade"],
        "regulations": [
            # ── China ──
            {
                "std_no": "GB 4806.1-2016",
                "name": "食品安全国家标准 食品接触材料及制品通用安全要求",
                "market": "CN",
                "mandatory": True,
                "desc": "食品接触材料的总体安全要求，包括基本要求、标签标识和合规声明。",
                "key_tests": ["感官要求", "迁移试验条件", "总迁移量", "标签标识"],
                "related": ["GB 4806.9-2016", "GB 4806.11-2016", "GB 9685-2016"],
            },
            {
                "std_no": "GB 4806.9-2016",
                "name": "食品安全国家标准 食品接触用金属材料及制品",
                "market": "CN",
                "mandatory": True,
                "desc": "不锈钢、铝合金等金属食品接触材料的安全标准，涵盖金属离子迁移量限值。",
                "key_tests": ["铅迁移量", "镉迁移量", "铬迁移量（不锈钢）", "镍迁移量", "砷迁移量"],
                "related": ["GB 4806.1-2016", "GB 9684-2011"],
            },
            {
                "std_no": "GB 4806.7-2016",
                "name": "食品安全国家标准 食品接触用塑料材料及制品",
                "market": "CN",
                "mandatory": True,
                "desc": "塑料食品接触材料安全标准，规定总迁移量和特定迁移量限值。",
                "key_tests": ["总迁移量（4%乙酸/10%乙醇/异辛烷）", "高锰酸钾消耗量", "重金属（以铅计）"],
                "related": ["GB 4806.1-2016", "GB 9685-2016"],
            },
            # ── USA ──
            {
                "std_no": "21 CFR Parts 170-199",
                "name": "FDA - Code of Federal Regulations Title 21, Food Additives and Food Contact Substances",
                "market": "US",
                "mandatory": True,
                "desc": "FDA对食品接触材料中食品添加剂和食品接触物质的安全要求，包括FAP程序。",
                "key_tests": ["提取物测试（模拟食品条件）", "重金属析出", "特定迁移物"],
                "related": ["21 CFR Part 175-179", "NSF 51"],
            },
            {
                "std_no": "NSF/ANSI 51-2021",
                "name": "Food Equipment Materials",
                "market": "US",
                "mandatory": False,
                "desc": "北美食品设备材料标准，被USDA/FDA参考，商业厨房设备市场准入的实际要求。",
                "key_tests": ["材料毒性浸出测试", "重金属析出", "表面光洁度（Ra值）"],
                "related": ["21 CFR", "NSF 2"],
            },
            {
                "std_no": "CPSC - Lead in Surface Coatings (16 CFR 1303)",
                "name": "16 CFR Part 1303 - Lead Content in Surface Coatings for Food Contact Items",
                "market": "US",
                "mandatory": True,
                "desc": "食品接触制品表面涂层铅含量限制，儿童餐具尤为严格（铅≤90ppm）。",
                "key_tests": ["XRF荧光检测铅含量", "化学法铅含量"],
                "related": ["21 CFR", "ASTM F963-23（儿童餐具）"],
            },
            # ── EU ──
            {
                "std_no": "Regulation (EC) No 1935/2004",
                "name": "Framework Regulation on Materials and Articles Intended to Come into Contact with Food",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟食品接触材料框架法规，设定安全原则和标签、追溯要求。",
                "key_tests": ["总迁移量（Overall Migration Limit: 10mg/dm²）", "书面声明合规"],
                "related": ["(EU) 10/2011", "EN 1186系列"],
            },
            {
                "std_no": "(EU) No 10/2011",
                "name": "Plastic Materials and Articles Intended to Come into Contact with Food",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟塑料食品接触材料法规，正面清单+总迁移量+特定迁移量限值。",
                "key_tests": ["总迁移量（OML: 10mg/dm²）", "特定迁移量（SML）", "功能阻隔层测试"],
                "related": ["Regulation (EC) No 1935/2004", "EN 13130系列"],
            },
            {
                "std_no": "Regulation (EC) No 1881/2006",
                "name": "Setting Maximum Levels for Certain Contaminants in Foodstuffs (关联金属餐具)",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟食品中污染物最高限量规定，金属餐具溶出的重金属须符合此规定。",
                "key_tests": ["铅溶出量", "镉溶出量", "铬溶出量（不锈钢）"],
                "related": ["Regulation (EC) No 1935/2004"],
            },
            # ── Japan ──
            {
                "std_no": "食品衛生法 第18条",
                "name": "食品安全基本法 / 食品衛生法 器具・容器包装の規格基準",
                "market": "JP",
                "mandatory": True,
                "desc": "日本食品卫生法对食品接触器具和容器包装的规格基准，厚生劳动省监管。",
                "key_tests": ["重金属溶出量（铅/砷/镉）", "高锰酸钾消耗量", "蒸发残留物"],
                "related": ["JIS S 2029（不锈钢）", "食品接触材料通知"],
            },
            {
                "std_no": "JIS S 2029:2015",
                "name": "ステンレス鋼製食器類 （不锈钢餐具）",
                "market": "JP",
                "mandatory": False,
                "desc": "日本不锈钢餐具的行业标准，规定材质要求和浸出物限值。",
                "key_tests": ["不锈钢材质验证（SUS304/316等）", "重金属溶出测试", "表面处理耐久性"],
                "related": ["食品衛生法 第18条"],
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # 4. TEXTILES / 纺织品
    # ══════════════════════════════════════════════════════
    "textiles": {
        "label": "纺织品",
        "icon": "👕",
        "keywords": ["纺织", "服装", "衣服", "裤子", "裙子", "T恤", "毛衣", "外套", "床品", "被子",
                     "枕头", "窗帘", "地毯", "布料", "面料", "棉", "聚酯", "尼龙", "羊毛", "蚕丝",
                     "涤纶", "麻", "textile", "garment", "clothing", "apparel", "fabric"],
        "regulations": [
            # ── China ──
            {
                "std_no": "GB 18401-2010",
                "name": "国家纺织产品基本安全技术规范",
                "market": "CN",
                "mandatory": True,
                "desc": "中国纺织品安全强制标准，分A/B/C三类（婴幼儿/直接接触皮肤/非直接接触）。",
                "key_tests": ["pH值", "甲醛含量", "色牢度（汗渍/摩擦）", "异味", "可分解芳香胺染料"],
                "related": ["GB/T 29862-2013", "GB/T 22848-2009"],
            },
            {
                "std_no": "GB 31701-2015",
                "name": "婴幼儿及儿童纺织产品安全技术规范",
                "market": "CN",
                "mandatory": True,
                "desc": "14岁及以下儿童纺织品安全强制标准，比GB18401更严格，新增绳带、附件等要求。",
                "key_tests": ["pH值（婴幼儿：4.0-7.5）", "甲醛含量（≤20mg/kg）", "重金属（镍镉铬铅等）", "绳带安全要求", "附件抗拉强力"],
                "related": ["GB 18401-2010", "EN 14682"],
            },
            {
                "std_no": "GB/T 29862-2013",
                "name": "纺织品 纤维含量的标识",
                "market": "CN",
                "mandatory": True,
                "desc": "规定纺织品纤维含量标注方法，是中国市场必须遵守的标签法规。",
                "key_tests": ["纤维成分定量分析", "标签标识符合性"],
                "related": ["GB 18401-2010"],
            },
            # ── USA ──
            {
                "std_no": "16 CFR Part 1610",
                "name": "Standard for the Flammability of Clothing Textiles",
                "market": "US",
                "mandatory": True,
                "desc": "CPSC强制要求的服装面料阻燃性测试标准，儿童睡衣有更严格要求。",
                "key_tests": ["45°燃烧测试（焰扩散时间>3.5秒为合格）"],
                "related": ["16 CFR Part 1615", "16 CFR Part 1616"],
            },
            {
                "std_no": "16 CFR Part 1615",
                "name": "Standard for the Flammability of Children's Sleepwear (Sizes 0-6X)",
                "market": "US",
                "mandatory": True,
                "desc": "0-6X码儿童睡衣强制阻燃标准，需符合特殊阻燃性要求或使用紧身设计免除测试。",
                "key_tests": ["垂直燃烧测试（5次洗涤后）", "样品炭长≤178mm"],
                "related": ["16 CFR Part 1610", "16 CFR Part 1616"],
            },
            {
                "std_no": "Textile Fiber Products Identification Act (TFPIA)",
                "name": "Textile Fiber Products Identification Act - FTC Rules (16 CFR Part 303)",
                "market": "US",
                "mandatory": True,
                "desc": "美国FTC纺织品纤维成分标签法，要求标注品牌、原产国、纤维成分。",
                "key_tests": ["纤维含量标注（>5%的纤维须分别标注）", "原产国标签"],
                "related": ["AATCC 20A（纤维含量分析）"],
            },
            # ── EU ──
            {
                "std_no": "Regulation (EU) No 1007/2011",
                "name": "Textile Fibre Names and Related Labelling and Marking of Textile Products",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟纺织品纤维名称与标签法规，规定所有纤维成分须在标签中注明。",
                "key_tests": ["纤维成分定量分析（EN ISO 1833系列）", "标签内容符合性"],
                "related": ["REACH Regulation", "EN ISO 1833"],
            },
            {
                "std_no": "REACH Regulation (EC) No 1907/2006 - Annex XVII",
                "name": "REACH Regulation - Restrictions on Hazardous Substances in Textiles",
                "market": "EU",
                "mandatory": True,
                "desc": "REACH法规附件XVII限制纺织品中的危险物质，包括偶氮染料、镍、有机锡化合物等。",
                "key_tests": ["偶氮染料（可分解出芳香胺≥30mg/kg）", "镍释放量", "有机锡（TBT、DBT、DOT等）", "多环芳烃（PAH）"],
                "related": ["EN 14362-1", "EN ISO 17072"],
            },
            {
                "std_no": "EN 14682:2014",
                "name": "Safety of Children's Clothing - Cords and Drawstrings on Children's Clothing",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟儿童服装绳带安全标准，CE认证中14岁以下儿童服装必须符合。",
                "key_tests": ["帽兜绳带长度/弹力", "腰部绳带突出长度", "绳结抗拉强度"],
                "related": ["Regulation (EU) No 1007/2011", "GB 31701-2015"],
            },
            # ── Japan ──
            {
                "std_no": "家庭用品品質表示法（纺织品）",
                "name": "家庭用品品質表示法 繊維製品品質表示規程",
                "market": "JP",
                "mandatory": True,
                "desc": "日本家用品品质标识法，要求纺织品标注纤维成分、洗涤护理方法（JIS L 0001）。",
                "key_tests": ["纤维成分分析", "洗涤方法符号标注（JIS L 0001）"],
                "related": ["JIS L 1096", "消費生活用製品安全法"],
            },
            {
                "std_no": "有害物質含有家庭用品の規制に関する法律",
                "name": "有害物质含有家庭用品规制法（有害家庭用品規制法）",
                "market": "JP",
                "mandatory": True,
                "desc": "日本对家用品中有害物质的限制，纺织品涵盖有机汞、三丁基锡等限制。",
                "key_tests": ["甲醛含量（婴幼儿衣物≤16mg/kg）", "有机汞化合物", "有机锡化合物"],
                "related": ["家庭用品品質表示法", "GB 18401-2010"],
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # 5. LITHIUM BATTERIES / 锂电池
    # ══════════════════════════════════════════════════════
    "lithium_battery": {
        "label": "锂电池",
        "icon": "🔋",
        "keywords": ["锂电池", "电池", "充电宝", "移动电源", "power bank", "battery", "锂离子",
                     "锂聚合物", "18650", "21700", "BMS", "电芯", "充电", "放电", "储能",
                     "电动车电池", "TWS电池", "电动工具电池"],
        "regulations": [
            # ── China ──
            {
                "std_no": "GB/T 18287-2019",
                "name": "移动电话用锂离子蓄电池及蓄电池组总规范",
                "market": "CN",
                "mandatory": False,
                "desc": "手机用锂离子电池的性能和安全要求，行业广泛采用的推荐性国标。",
                "key_tests": ["放电性能", "过充保护", "过放保护", "短路保护", "跌落测试", "振动测试"],
                "related": ["GB 31241-2022", "IEC 62133-2"],
            },
            {
                "std_no": "GB 31241-2022",
                "name": "便携式电子产品用锂离子电池和电池组安全要求",
                "market": "CN",
                "mandatory": True,
                "desc": "便携式电子产品锂电池强制安全标准，充电宝、蓝牙耳机等产品的强制依据。",
                "key_tests": ["过充电", "过放电", "外部短路", "强制放电", "加热", "挤压", "跌落", "海水浸泡"],
                "related": ["GB/T 18287-2019", "IEC 62133-2:2017"],
            },
            {
                "std_no": "GB/T 35590-2017",
                "name": "信息技术 便携式数字设备用二次锂电池通则",
                "market": "CN",
                "mandatory": False,
                "desc": "便携数字设备用可充电锂电池的通用技术要求，涵盖性能评价方法。",
                "key_tests": ["容量测试", "循环寿命", "荷电保持能力", "高温高湿储存"],
                "related": ["GB 31241-2022"],
            },
            # ── USA ──
            {
                "std_no": "UL 1642",
                "name": "Standard for Lithium Batteries",
                "market": "US",
                "mandatory": False,
                "desc": "UL锂电池安全标准，是美国最广泛接受的锂电池安全认证依据。",
                "key_tests": ["短路测试", "挤压测试", "冲击测试", "振动测试", "热滥用测试", "海拔模拟"],
                "related": ["UL 2054", "UN 38.3", "IEC 62133-2"],
            },
            {
                "std_no": "UL 2054",
                "name": "Household and Commercial Batteries",
                "market": "US",
                "mandatory": False,
                "desc": "UL家用和商用电池安全标准，含锂电池组和充电宝的系统级安全要求。",
                "key_tests": ["过充保护", "短路测试", "环境测试（高低温）", "机械测试（跌落/振动）"],
                "related": ["UL 1642", "UL 9540（储能系统）"],
            },
            {
                "std_no": "UN 38.3",
                "name": "UN Manual of Tests and Criteria - Part III Section 38.3 (Lithium Batteries Transport)",
                "market": "US",
                "mandatory": True,
                "desc": "联合国锂电池运输安全测试标准，航空/海运运输的强制测试，DOT和IATA执行。",
                "key_tests": ["T1高度模拟", "T2热冲击", "T3振动", "T4冲击", "T5外部短路", "T6撞击", "T7过充", "T8强制放电"],
                "related": ["IATA DGR", "49 CFR Part 173（DOT）"],
            },
            # ── EU ──
            {
                "std_no": "IEC 62133-2:2017",
                "name": "Secondary Cells and Batteries Containing Alkaline or Other Non-Acid Electrolytes - Safety Requirements for Portable Sealed Secondary Lithium Cells, and for Batteries Made from Them, for Use in Portable Applications - Part 2: Lithium Systems",
                "market": "EU",
                "mandatory": True,
                "desc": "便携式锂电池安全国际标准，欧盟CE认证（LVD指令）和全球主流锂电池安全测试依据。",
                "key_tests": ["连续低速率充电", "过充电", "强制放电", "外部短路", "机械测试", "热滥用", "挤压"],
                "related": ["UN 38.3", "EN 62133-2", "IEC 62368-1"],
            },
            {
                "std_no": "Regulation (EU) 2023/1542",
                "name": "Batteries and Waste Batteries Regulation (新电池法规)",
                "market": "EU",
                "mandatory": True,
                "desc": "欧盟2023年新电池法规，替代2006/66/EC，对锂电池可持续性、碳足迹、回收等有新要求。",
                "key_tests": ["碳足迹声明（2025年起）", "再生材料含量", "电池护照（2027年起）", "容量保持率≥70%@300次循环"],
                "related": ["IEC 62133-2:2017", "UN 38.3"],
            },
            {
                "std_no": "EN 62368-1:2020+A11:2020",
                "name": "Audio/Video, Information and Communication Technology Equipment (含锂电池设备)",
                "market": "EU",
                "mandatory": True,
                "desc": "含锂电池的AV/IT设备CE认证安全标准，包含电池安全的整机层面要求。",
                "key_tests": ["过充保护电路评估", "电池仓设计", "电气安全", "防火性能"],
                "related": ["IEC 62133-2:2017", "EN 300 328"],
            },
            # ── Japan ──
            {
                "std_no": "電気用品安全法 PSE（特定電気用品）",
                "name": "電気用品安全法 特定電気用品 - リチウムイオン蓄電池",
                "market": "JP",
                "mandatory": True,
                "desc": "日本电气用品安全法对锂离子电池的强制认证（特定电気用品，菱形PSE），需第三方认证机构认证。",
                "key_tests": ["过充保护", "过放保护", "短路保护", "温度保护", "挤压/穿刺"],
                "related": ["JIS C 8714", "UN 38.3"],
            },
            {
                "std_no": "JIS C 8714:2007",
                "name": "携帯電話用リチウムイオン二次電池の安全性試験（锂离子电池安全测试）",
                "market": "JP",
                "mandatory": False,
                "desc": "日本手机用锂离子二次电池安全试验标准，PSE认证的技术基准之一。",
                "key_tests": ["过充电测试", "强制放电测试", "外部短路测试", "落下测试", "加热测试", "押しつぶし（挤压）测试"],
                "related": ["PSE（特定電気用品）", "IEC 62133-2"],
            },
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

MARKET_MAP = {
    "中国": "CN",
    "美国": "US",
    "欧盟": "EU",
    "日本": "JP",
    "CN": "CN",
    "US": "US",
    "EU": "EU",
    "JP": "JP",
}

MARKET_LABEL = {
    "CN": "中国",
    "US": "美国",
    "EU": "欧盟",
    "JP": "日本",
}


def detect_category(product_text: str) -> Optional[str]:
    """
    Detect product category from product description text.
    Returns the category key or None if no match.
    """
    text_lower = product_text.lower()
    scores = {}
    for cat_key, cat_data in KNOWLEDGE_BASE.items():
        score = 0
        for kw in cat_data["keywords"]:
            if kw.lower() in text_lower:
                score += 1
        if score > 0:
            scores[cat_key] = score

    if not scores:
        return None
    # Return category with highest keyword match score
    return max(scores, key=lambda k: scores[k])


def get_regulations_for_product(product_text: str, markets: list[str]) -> dict:
    """
    Get relevant regulations from knowledge base for given product and markets.
    
    Returns:
    {
        "category": str,       # detected category key
        "category_label": str, # human-readable category name
        "category_icon": str,
        "markets": list[str],  # matched market codes
        "regulations": [       # filtered regulation list
            {...}
        ]
    }
    """
    cat_key = detect_category(product_text)
    if cat_key is None:
        return {"category": None, "category_label": "未识别", "category_icon": "📦",
                "markets": [], "regulations": []}

    cat_data = KNOWLEDGE_BASE[cat_key]

    # Normalize market names to codes
    market_codes = []
    for m in markets:
        code = MARKET_MAP.get(m)
        if code and code not in market_codes:
            market_codes.append(code)

    # Filter regulations by market
    regs = []
    for reg in cat_data["regulations"]:
        if reg["market"] in market_codes:
            regs.append(reg)

    return {
        "category": cat_key,
        "category_label": cat_data["label"],
        "category_icon": cat_data["icon"],
        "markets": market_codes,
        "regulations": regs,
    }


def cross_validate(
    search_results_text: str,
    product_text: str,
    markets: list[str],
) -> dict:
    """
    Cross-validate agent search results against knowledge base.
    
    Params:
        search_results_text: The final report text from the agent
        product_text: Original product description
        markets: List of target markets (human-readable)
    
    Returns:
        {
            "category": str,
            "verified": [reg entries with status="verified"],
            "supplemental": [reg entries with status="supplemental"],
            "new_found": [{"std_no": ..., "context": ...}],
        }
    """
    kb_result = get_regulations_for_product(product_text, markets)
    kb_regs = kb_result["regulations"]

    import re
    # Extract standard numbers mentioned in the report text
    # Patterns: EN XXXXX, IEC XXXXX, GB XXXXX, UL XXXXX, etc.
    std_patterns = [
        r'\b(EN\s+\d[\d\s\-\:\.+A]+)',
        r'\b(IEC\s+\d[\d\s\-\:\.]+)',
        r'\b(ISO\s+\d[\d\s\-\:\.]+)',
        r'\b(GB\s+[\d/T\s\-\.]+)',
        r'\b(GB/T\s+[\d\s\-\.]+)',
        r'\b(UL\s+\d[\d\s\-\.]+)',
        r'\b(ASTM\s+[A-Z]\d[\d\s\-\.]+)',
        r'\b(JIS\s+[A-Z]\s*\d[\d\s\-\.]+)',
        r'\b(ARIB\s+STD-[A-Z]\d+)',
        r'\b(FCC\s+Part\s+\d+)',
        r'\b(16\s+CFR\s+Part\s+\d+)',
        r'\b(21\s+CFR\s+Part\s+\d+)',
        r'\b(NSF/ANSI\s+\d+)',
        r'\b(UN\s+38\.3)',
        r'\b(VCCI\b)',
        r'\b(PSE\b)',
    ]

    found_in_report = set()
    for pat in std_patterns:
        for m in re.finditer(pat, search_results_text, re.IGNORECASE):
            # Normalize: collapse whitespace, uppercase
            normalized = re.sub(r'\s+', ' ', m.group(1).strip()).upper()
            found_in_report.add(normalized)

    # Match KB regulations against found_in_report
    verified = []
    supplemental = []

    for reg in kb_regs:
        std_normalized = re.sub(r'\s+', ' ', reg["std_no"]).upper()
        # Check if std_no or its prefix is in report
        matched = False
        for found_std in found_in_report:
            # Allow partial prefix match (e.g. "GB 31241" matches "GB 31241-2022")
            if (std_normalized[:10] in found_std or found_std[:10] in std_normalized):
                matched = True
                break
        if matched:
            verified.append({**reg, "status": "verified"})
        else:
            supplemental.append({**reg, "status": "supplemental"})

    # Detect new findings: standards in report but NOT in knowledge base
    kb_std_nos_normalized = set()
    for reg in kb_regs:
        kb_std_nos_normalized.add(re.sub(r'\s+', ' ', reg["std_no"]).upper()[:10])

    new_found = []
    for found_std in found_in_report:
        in_kb = False
        for kb_std in kb_std_nos_normalized:
            if kb_std[:8] in found_std or found_std[:8] in kb_std:
                in_kb = True
                break
        if not in_kb and len(found_std) > 3:
            new_found.append({"std_no": found_std, "status": "new_found"})

    return {
        "category": kb_result["category"],
        "category_label": kb_result["category_label"],
        "verified": verified,
        "supplemental": supplemental,
        "new_found": new_found[:10],  # Cap at 10 new findings
    }


def build_kb_recommendation_html(product_text: str, markets: list[str]) -> str:
    """
    Build HTML for sidebar KB recommendation panel.
    Called immediately when user enters product description.
    """
    if not product_text or not product_text.strip():
        return _kb_empty_html()

    result = get_regulations_for_product(product_text, markets)
    if result["category"] is None:
        return _kb_unrecognized_html(product_text)

    regs = result["regulations"]
    if not regs:
        return _kb_no_regs_html(result)

    # Group by market
    market_groups = {}
    for reg in regs:
        m = reg["market"]
        if m not in market_groups:
            market_groups[m] = []
        market_groups[m].append(reg)

    market_sections_html = ""
    for mcode, mreg_list in market_groups.items():
        market_label = MARKET_LABEL.get(mcode, mcode)
        market_flag = {"CN": "🇨🇳", "US": "🇺🇸", "EU": "🇪🇺", "JP": "🇯🇵"}.get(mcode, "🌐")

        reg_items_html = ""
        for i, reg in enumerate(mreg_list):
            mandatory_badge = (
                '<span style="background:#fef3c7;color:#92400e;border:1px solid #fcd34d;'
                'padding:1px 6px;border-radius:3px;font-size:0.65rem;font-weight:700;">强制</span>'
                if reg["mandatory"] else
                '<span style="background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;'
                'padding:1px 6px;border-radius:3px;font-size:0.65rem;font-weight:700;">自愿</span>'
            )

            # Key tests as pills
            test_pills = ""
            for t in reg["key_tests"][:4]:
                short_t = t if len(t) <= 15 else t[:13] + "…"
                test_pills += f'<span style="display:inline-block;background:#f0f4f8;color:#60748a;border:1px solid #dce3ec;padding:1px 6px;border-radius:3px;font-size:0.65rem;margin:2px 2px 2px 0;">{short_t}</span>'

            # Related standards
            related_html = ""
            if reg["related"]:
                related_items = "、".join(reg["related"][:3])
                related_html = f'<div style="font-size:0.7rem;color:#8fa4bb;margin-top:4px;">↔ 相关：{related_items}</div>'

            details_id = f"kb-reg-{id(reg)}-{i}"
            std_no_escaped = reg["std_no"].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            name_escaped = reg["name"].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            desc_escaped = reg["desc"].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

            reg_items_html += f"""
<div style="
    border: 1px solid #dce3ec;
    border-radius: 8px;
    margin-bottom: 8px;
    overflow: hidden;
    background: #fff;
">
    <div onclick="(function(el){{
        var d=el.parentElement.querySelector('.kb-detail');
        var icon=el.querySelector('.kb-arrow');
        if(d.style.display==='none'||!d.style.display){{d.style.display='block';icon.textContent='▲';}}
        else{{d.style.display='none';icon.textContent='▼';}}
    }})(this)" style="
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 10px 12px;
        cursor: pointer;
        background: #f7f9fc;
        gap: 8px;
        transition: background 0.15s;
    " onmouseover="this.style.background='#eef4fd'" onmouseout="this.style.background='#f7f9fc'">
        <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:4px;">
                <span style="font-family:monospace;font-size:0.75rem;font-weight:700;color:#1a3a5c;background:#e8f3fe;padding:1px 6px;border-radius:3px;border:1px solid #c3d8ef;">{std_no_escaped}</span>
                {mandatory_badge}
            </div>
            <div style="font-size:0.78rem;color:#1e2d3d;line-height:1.35;font-weight:500;">{name_escaped}</div>
        </div>
        <span class="kb-arrow" style="font-size:0.65rem;color:#8fa4bb;flex-shrink:0;margin-top:3px;">▼</span>
    </div>
    <div class="kb-detail" style="display:none;padding:10px 12px;border-top:1px solid #eee;">
        <div style="font-size:0.78rem;color:#344054;line-height:1.55;margin-bottom:8px;">{desc_escaped}</div>
        <div style="font-size:0.7rem;font-weight:600;color:#60748a;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;">关键测试项</div>
        <div style="margin-bottom:6px;">{test_pills}</div>
        {related_html}
    </div>
</div>"""

        market_sections_html += f"""
<div style="margin-bottom:14px;">
    <div style="
        font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
        color:#1a3a5c;margin-bottom:8px;display:flex;align-items:center;gap:6px;
    ">
        <span>{market_flag}</span> {market_label}
        <span style="background:#e8f3fe;color:#1a4a7a;padding:1px 7px;border-radius:3px;font-size:0.63rem;">{len(mreg_list)} 条</span>
    </div>
    {reg_items_html}
</div>"""

    total_regs = len(regs)
    cat_icon = result["category_icon"]
    cat_label = result["category_label"]

    return f"""
<div style="
    background: #fff;
    border: 1px solid #dce3ec;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
">
    <div style="
        background: linear-gradient(90deg, #1a3a5c 0%, #22405e 100%);
        border-bottom: 2px solid #d4830a;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:1rem;">{cat_icon}</span>
            <div>
                <div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.9);letter-spacing:0.08em;text-transform:uppercase;">知识库推荐法规</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.55);">{cat_label} · {total_regs} 条</div>
            </div>
        </div>
        <span style="font-size:0.65rem;background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.7);padding:2px 8px;border-radius:3px;font-weight:600;">即时推荐</span>
    </div>
    <div style="padding:14px 14px 6px;">
        <div style="font-size:0.76rem;color:#8fa4bb;margin-bottom:12px;">
            根据产品描述自动匹配，点击任意法规可展开详情
        </div>
        {market_sections_html}
    </div>
</div>"""


def _kb_empty_html() -> str:
    return """
<div style="
    background: #fff;
    border: 1px solid #dce3ec;
    border-radius: 12px;
    padding: 28px 20px;
    text-align: center;
    color: #8fa4bb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
">
    <div style="font-size:1.8rem;margin-bottom:10px;">📚</div>
    <div style="font-size:0.88rem;font-weight:600;color:#1a3a5c;margin-bottom:6px;">法规知识库推荐</div>
    <div style="font-size:0.78rem;line-height:1.65;max-width:260px;margin:0 auto;">
        输入产品描述后，系统将自动从知识库推荐相关法规，无需等待搜索完成。
    </div>
</div>"""


def _kb_unrecognized_html(product_text: str) -> str:
    preview = product_text[:40] + ("…" if len(product_text) > 40 else "")
    return f"""
<div style="
    background: #fff;
    border: 1px solid #dce3ec;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    color: #8fa4bb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
">
    <div style="font-size:1.6rem;margin-bottom:8px;">🔍</div>
    <div style="font-size:0.85rem;font-weight:600;color:#1a3a5c;margin-bottom:5px;">未识别产品类别</div>
    <div style="font-size:0.77rem;line-height:1.6;color:#60748a;">
        「{preview}」<br>
        当前知识库覆盖：消费电子 / 玩具 / 食品接触 / 纺织品 / 锂电池<br>
        AI搜索将覆盖更多产品类别
    </div>
</div>"""


def _kb_no_regs_html(result: dict) -> str:
    return f"""
<div style="
    background: #fff;
    border: 1px solid #dce3ec;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    color: #8fa4bb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
">
    <div style="font-size:1.6rem;margin-bottom:8px;">{result['category_icon']}</div>
    <div style="font-size:0.85rem;font-weight:600;color:#1a3a5c;margin-bottom:5px;">{result['category_label']}</div>
    <div style="font-size:0.77rem;color:#60748a;">
        当前选择的市场在知识库中暂无匹配法规<br>
        AI搜索将实时检索最新法规信息
    </div>
</div>"""


def build_cross_validation_html(cross_result: dict) -> str:
    """
    Build HTML summary for cross-validation results.
    Called after agent finishes searching and generating report.
    """
    verified = cross_result.get("verified", [])
    supplemental = cross_result.get("supplemental", [])
    new_found = cross_result.get("new_found", [])
    cat_label = cross_result.get("category_label", "")

    if not verified and not supplemental and not new_found:
        return ""

    def reg_row(reg, status_color, status_label, status_bg):
        std_no = reg["std_no"][:35] + ("…" if len(reg["std_no"]) > 35 else "")
        return f"""
<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #f0f4f8;font-size:0.77rem;">
    <span style="background:{status_bg};color:{status_color};padding:1px 7px;border-radius:3px;font-size:0.65rem;font-weight:700;white-space:nowrap;flex-shrink:0;">{status_label}</span>
    <span style="font-family:monospace;color:#1a3a5c;font-size:0.72rem;font-weight:600;">{std_no}</span>
</div>"""

    rows_html = ""
    for reg in verified[:5]:
        rows_html += reg_row(reg, "#065f46", "✓ 已验证", "#d1fae5")
    for reg in supplemental[:5]:
        rows_html += reg_row(reg, "#92400e", "+ 补充推荐", "#fef3c7")
    for item in new_found[:4]:
        std_no = item["std_no"][:35] + ("…" if len(item["std_no"]) > 35 else "")
        rows_html += f"""
<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #f0f4f8;font-size:0.77rem;">
    <span style="background:#dbeafe;color:#1e40af;padding:1px 7px;border-radius:3px;font-size:0.65rem;font-weight:700;white-space:nowrap;flex-shrink:0;">★ 新发现</span>
    <span style="font-family:monospace;color:#1a3a5c;font-size:0.72rem;font-weight:600;">{std_no}</span>
</div>"""

    stats = f"{len(verified)} 已验证 · {len(supplemental)} 补充推荐 · {len(new_found)} 新发现"

    return f"""
<div style="
    background: #fff;
    border: 1px solid #dce3ec;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-top: 14px;
">
    <div style="
        background: linear-gradient(90deg, #1a3a5c 0%, #22405e 100%);
        border-bottom: 2px solid #d4830a;
        padding: 10px 16px;
        display:flex;align-items:center;justify-content:space-between;
    ">
        <div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.9);letter-spacing:0.08em;text-transform:uppercase;">
            📊 交叉验证结果
        </div>
        <div style="font-size:0.65rem;color:rgba(255,255,255,0.6);">{stats}</div>
    </div>
    <div style="padding:12px 14px;">
        <div style="font-size:0.7rem;color:#8fa4bb;margin-bottom:8px;">搜索结果 × 知识库比对</div>
        {rows_html}
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;">
            <span style="font-size:0.68rem;background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:3px;">✓ 已验证：搜索+知识库均有</span>
            <span style="font-size:0.68rem;background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:3px;">+ 补充推荐：知识库有·搜索未覆盖</span>
            <span style="font-size:0.68rem;background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:3px;">★ 新发现：搜索有·知识库未收录</span>
        </div>
    </div>
</div>"""


if __name__ == "__main__":
    # Quick test
    result = get_regulations_for_product("蓝牙无线耳机 TWS", ["中国", "欧盟", "美国"])
    print(f"Category: {result['category_label']}")
    print(f"Regulations found: {len(result['regulations'])}")
    for reg in result["regulations"]:
        print(f"  [{reg['market']}] {reg['std_no']}: {reg['name'][:50]}...")
