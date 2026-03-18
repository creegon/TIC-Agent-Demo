# charts.py - Compliance visualization charts for TIC Agent
# Generates interactive Plotly charts based on agent report analysis

import re
import json
import plotly.graph_objects as go
import plotly.colors as pc
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Color palette (matches existing UI: Deep Navy + Amber Gold)
# ─────────────────────────────────────────────────────────────────────────────
COLOR_PRIMARY      = "#1a3a5c"   # Deep navy
COLOR_PRIMARY_MID  = "#1e4976"
COLOR_PRIMARY_LIGHT= "#2563a8"
COLOR_ACCENT       = "#d4830a"   # Amber gold
COLOR_ACCENT_LIGHT = "#e8a838"
COLOR_ACCENT_PALE  = "#fef3dc"
COLOR_BG           = "#f0f4f8"
COLOR_SURFACE      = "#ffffff"
COLOR_BORDER       = "#dce3ec"
COLOR_TEXT         = "#1e2d3d"
COLOR_TEXT_MUTED   = "#60748a"
COLOR_DANGER       = "#c0392b"
COLOR_SUCCESS      = "#0f7a60"
COLOR_WARNING      = "#e67e22"


# ─────────────────────────────────────────────────────────────────────────────
# Radar chart dimensions
# ─────────────────────────────────────────────────────────────────────────────
RADAR_DIMS = [
    "Electrical Safety\n(电气安全)",
    "EMC\n(电磁兼容)",
    "Chemical Substances\n(化学物质)",
    "Labeling\n(标签要求)",
    "Environmental\n(环保法规)",
    "Certification\n(认证要求)",
]

# Short labels for display
RADAR_DIMS_SHORT = [
    "电气安全",
    "EMC",
    "化学物质",
    "标签要求",
    "环保法规",
    "认证要求",
]

# ─────────────────────────────────────────────────────────────────────────────
# Risk matrix axes
# ─────────────────────────────────────────────────────────────────────────────
MATRIX_CATEGORIES = ["电气安全", "EMC", "化学物质", "标签要求", "环保法规", "认证要求"]
MATRIX_PRODUCTS   = ["消费电子", "玩具", "食品接触", "纺织品", "锂电池"]


# ─────────────────────────────────────────────────────────────────────────────
# Score extraction heuristics
# ─────────────────────────────────────────────────────────────────────────────

def _count_regex_hits(text: str, patterns: list[str]) -> int:
    """Count unique regex pattern matches (case-insensitive)."""
    total = 0
    for p in patterns:
        hits = re.findall(p, text, re.IGNORECASE)
        total += len(set(hits))
    return total


def _extract_risk_level(text: str, keyword: str) -> float:
    """
    Extract risk level for a given keyword from surrounding context.
    Returns 0.0-1.0 multiplier.
    """
    # Search for the keyword and look at nearby words
    positions = [m.start() for m in re.finditer(keyword, text, re.IGNORECASE)]
    if not positions:
        return 0.5  # neutral if not found

    high_words = r"(高风险|高|严格|复杂|强制|mandatory|high|strict|critical|complex|required)"
    low_words  = r"(低风险|低|简单|宽松|optional|low|simple|minor|exempt)"
    mid_words  = r"(中风险|中|一般|moderate|medium)"

    high_count = low_count = mid_count = 0
    for pos in positions:
        window = text[max(0, pos - 150): pos + 150]
        high_count += len(re.findall(high_words, window, re.IGNORECASE))
        low_count  += len(re.findall(low_words,  window, re.IGNORECASE))
        mid_count  += len(re.findall(mid_words,  window, re.IGNORECASE))

    if high_count >= low_count and high_count >= mid_count:
        return 0.9
    elif low_count > high_count and low_count > mid_count:
        return 0.4
    return 0.65


def extract_scores_from_report(report_text: str) -> dict:
    """
    Analyze report text and infer compliance complexity scores (0-100)
    for each of the 6 radar dimensions.

    Strategy:
    1. Count mentions of relevant regulation/standard keywords per dimension
    2. Apply risk-level multiplier based on surrounding context
    3. Normalize to 0-100 range with reasonable floor/ceiling
    4. Build hover tooltips from detected standards

    Returns: {
        'scores': [float×6],
        'tooltips': [str×6],
        'standards_detected': [list-of-str×6],
    }
    """
    # --- Patterns per dimension -----------------------------------------
    dim_patterns = {
        "电气安全": {
            "keywords": [
                r"IEC\s*60950", r"IEC\s*62368", r"EN\s*60950", r"EN\s*62368",
                r"UL\s*60950", r"UL\s*62368", r"GB\s*4943",
                r"电气安全", r"electrical safety", r"过压保护", r"过流保护",
                r"漏电", r"绝缘", r"接地", r"LVD", r"low voltage directive",
                r"电击", r"electric shock", r"短路", r"short circuit",
                r"PSE", r"PSC",
            ],
            "base": 35,
        },
        "EMC": {
            "keywords": [
                r"EMC", r"FCC\s*Part\s*15", r"FCC\s*ID", r"RED\s*directive",
                r"EN\s*55032", r"EN\s*61000", r"CISPR", r"TELEC",
                r"电磁兼容", r"辐射", r"干扰", r"emission", r"immunity",
                r"蓝牙.*认证", r"Wi-Fi.*认证", r"无线.*认证",
                r"GB\s*9254", r"GB\s*17625",
                r"MIC\s*Japan", r"电波法",
            ],
            "base": 30,
        },
        "化学物质": {
            "keywords": [
                r"RoHS", r"REACH", r"SVHCs?", r"邻苯二甲酸", r"phthalate",
                r"重金属", r"heavy metal", r"铅", r"铬", r"镉", r"汞",
                r"PFAS", r"有害物质", r"hazardous substance",
                r"GB\s*30981", r"GB\s*6675", r"ASTM\s*F963",
                r"化学品", r"chemical", r"卤素", r"halogen",
            ],
            "base": 25,
        },
        "标签要求": {
            "keywords": [
                r"标签", r"label", r"标识", r"marking", r"CE\s*标志",
                r"FCC\s*标识", r"警告.*标签", r"warning.*label",
                r"使用说明", r"instruction", r"manual",
                r"原产地", r"country of origin", r"型号", r"model number",
                r"额定", r"rating", r"能效", r"energy label",
                r"WEEE.*标志", r"回收.*标志",
            ],
            "base": 20,
        },
        "环保法规": {
            "keywords": [
                r"WEEE", r"废弃电器", r"回收", r"recycl",
                r"RoHS", r"REACH", r"EU Battery", r"电池法规",
                r"碳足迹", r"carbon", r"EPR", r"生产者责任",
                r"包装.*指令", r"packaging directive",
                r"能效", r"energy efficiency", r"ErP", r"Ecodesign",
                r"GB\s*26572", r"环保.*要求",
            ],
            "base": 20,
        },
        "认证要求": {
            "keywords": [
                r"CCC", r"3C认证", r"CE认证", r"CE\s*mark",
                r"FCC\s*certif", r"UL\s*certif", r"PSE", r"TELEC",
                r"认证", r"certif", r"第三方.*测试", r"third.party.*test",
                r"notified body", r"公告机构", r"TCB",
                r"DoC", r"declaration of conformity", r"符合性声明",
                r"CNCA", r"CNAS", r"CB scheme", r"IECEE",
            ],
            "base": 30,
        },
    }

    scores = []
    tooltips = []
    standards_per_dim = []

    for dim_key, cfg in dim_patterns.items():
        patterns  = cfg["keywords"]
        base      = cfg["base"]

        # Count keyword hits
        hits = _count_regex_hits(report_text, patterns)

        # Collect specific matched standards for tooltip
        detected = set()
        for p in patterns:
            for m in re.finditer(p, report_text, re.IGNORECASE):
                s = m.group(0).strip()
                if len(s) >= 3:
                    detected.add(s)
        detected = sorted(detected)

        # Risk multiplier from context
        risk_mult = _extract_risk_level(report_text, dim_key)

        # Score formula: base + min(hits * 8, 50) * risk_mult
        raw_score = base + min(hits * 7, 50) * risk_mult
        # Clamp 15..95
        score = max(15.0, min(95.0, raw_score))

        # Build tooltip
        if detected:
            tip_stds = "、".join(detected[:5])
            if len(detected) > 5:
                tip_stds += f"等{len(detected)}项"
            tip = f"<b>{dim_key}</b><br>相关标准：{tip_stds}<br>复杂度评分：{score:.0f}/100"
        else:
            tip = f"<b>{dim_key}</b><br>（报告中未检测到具体标准）<br>基础评分：{score:.0f}/100"

        scores.append(round(score, 1))
        tooltips.append(tip)
        standards_per_dim.append(detected)

    return {
        "scores": scores,
        "tooltips": tooltips,
        "standards_detected": standards_per_dim,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Radar Chart
# ─────────────────────────────────────────────────────────────────────────────

def generate_radar_chart(report_text: str) -> str:
    """
    Generate an interactive Plotly radar chart based on report text analysis.

    Args:
        report_text: Full text of the compliance report

    Returns:
        HTML string (Plotly figure, no full_html wrapper)
    """
    data = extract_scores_from_report(report_text)
    scores   = data["scores"]
    tooltips = data["tooltips"]

    # Radar needs the first value repeated to close the polygon
    categories = RADAR_DIMS_SHORT + [RADAR_DIMS_SHORT[0]]
    values     = scores + [scores[0]]
    texts      = tooltips + [tooltips[0]]

    fig = go.Figure()

    # Filled area
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor=f"rgba(212, 131, 10, 0.18)",
        line=dict(color=COLOR_ACCENT, width=2.5),
        marker=dict(color=COLOR_ACCENT, size=8, symbol="circle",
                    line=dict(color="#fff", width=1.5)),
        text=texts,
        hovertemplate="%{text}<extra></extra>",
        name="合规风险评分",
    ))

    # Reference ring at 50
    ref50 = [50] * (len(RADAR_DIMS_SHORT) + 1)
    fig.add_trace(go.Scatterpolar(
        r=ref50,
        theta=categories,
        fill=None,
        line=dict(color="rgba(26,58,92,0.25)", width=1, dash="dot"),
        hoverinfo="skip",
        showlegend=False,
        name="",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=COLOR_SURFACE,
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20", "40", "60", "80", "100"],
                gridcolor="rgba(220,227,236,0.8)",
                linecolor="rgba(220,227,236,0.8)",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=COLOR_PRIMARY, family="'Segoe UI', sans-serif"),
                linecolor=COLOR_BORDER,
                gridcolor=COLOR_BORDER,
            ),
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=11, color=COLOR_TEXT_MUTED),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=COLOR_BORDER,
            borderwidth=1,
            x=0.85, y=1.1,
        ),
        paper_bgcolor=COLOR_SURFACE,
        plot_bgcolor=COLOR_SURFACE,
        margin=dict(l=60, r=60, t=60, b=60),
        height=420,
        title=dict(
            text="合规复杂度雷达图",
            font=dict(size=14, color=COLOR_PRIMARY, family="'Segoe UI', sans-serif"),
            x=0.5, xanchor="center",
            y=0.97,
        ),
        hoverlabel=dict(
            bgcolor=COLOR_PRIMARY,
            font=dict(color="#fff", size=12),
            bordercolor=COLOR_ACCENT,
        ),
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=False, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "displaylogo": False,
        "responsive": True,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Risk Heat Matrix
# ─────────────────────────────────────────────────────────────────────────────

# Static baseline risk matrix [product_row][category_col]
# Values 0-100: 0=low, 50=medium, 100=high
# Rows:  消费电子 / 玩具 / 食品接触 / 纺织品 / 锂电池
# Cols:  电气安全 / EMC / 化学物质 / 标签要求 / 环保法规 / 认证要求
BASE_RISK_MATRIX = [
    # 电气安全  EMC   化学物质  标签   环保    认证
    [85,        80,   45,       55,    60,     80],  # 消费电子
    [50,        35,   85,       65,    55,     70],  # 玩具
    [15,        10,   90,       70,    50,     60],  # 食品接触
    [10,        10,   75,       60,    55,     40],  # 纺织品
    [80,        55,   70,       65,    85,     85],  # 锂电池
]

# Hover text templates per cell
_RISK_TOOLTIPS = {
    # (product, category): tooltip_text
    ("消费电子", "电气安全"): "IEC 62368-1 / LVD 2014/35/EU / GB 4943.1<br>风险：高压/过热/电击防护",
    ("消费电子", "EMC"):      "FCC Part 15 / EN 55032 / RED 2014/53/EU<br>风险：无线干扰、辐射超标",
    ("消费电子", "化学物质"): "RoHS 2011/65/EU / REACH SVHC<br>风险：限用有害物质",
    ("消费电子", "标签要求"): "CE标志 / FCC ID / 能效标签<br>风险：标识缺失或错误",
    ("消费电子", "环保法规"): "WEEE 2012/19/EU / EU Ecodesign<br>风险：未注册EPR计划",
    ("消费电子", "认证要求"): "CCC / CE / FCC / PSE / TELEC<br>风险：多市场多认证叠加",

    ("玩具", "电气安全"):     "EN 62115 / IEC 62115 电动玩具<br>风险：适用于含电子元件玩具",
    ("玩具", "EMC"):          "EN 62115 (EMC part) / FCC Part 15<br>风险：有限，部分电子玩具需要",
    ("玩具", "化学物质"):     "EN 71-3 重金属 / REACH / GB 6675<br>风险：涂料、填充物有害物质超标",
    ("玩具", "标签要求"):     "年龄警告 / CE / ASTM F963<br>风险：警示语缺失影响市场准入",
    ("玩具", "环保法规"):     "RoHS / REACH / 包装指令<br>风险：中等，视材质而定",
    ("玩具", "认证要求"):     "EN 71 / ASTM F963 / GB 6675 / ST Mark<br>风险：强制第三方测试",

    ("食品接触", "电气安全"): "仅适用于电热产品<br>风险：通常不涉及",
    ("食品接触", "EMC"):      "通常不涉及<br>风险：极低",
    ("食品接触", "化学物质"): "FDA 21 CFR / EU 1935/2004 / GB 4806<br>风险：迁移量超标是核心风险",
    ("食品接触", "标签要求"): "食品安全标识 / 材质声明<br>风险：合规声明缺失",
    ("食品接触", "环保法规"): "包装指令 / EPR<br>风险：中等",
    ("食品接触", "认证要求"): "FDA注册 / EU符合性声明 / GB 4806<br>风险：需提供迁移测试报告",

    ("纺织品", "电气安全"):   "通常不涉及<br>风险：极低",
    ("纺织品", "EMC"):        "通常不涉及<br>风险：极低",
    ("纺织品", "化学物质"):   "REACH SVHC / OEKO-TEX / GB 18401<br>风险：禁用偶氮染料、甲醛超标",
    ("纺织品", "标签要求"):   "成分标签 / 洗涤标签 / GB 5296<br>风险：标签不规范",
    ("纺织品", "环保法规"):   "REACH / 包装指令<br>风险：中等",
    ("纺织品", "认证要求"):   "OEKO-TEX / GB 18401 / GOTS<br>风险：相对宽松，视目标市场",

    ("锂电池", "电气安全"):   "IEC 62133 / UL 2054 / GB 31241<br>风险：过充/过放/短路/热失控",
    ("锂电池", "EMC"):        "FCC Part 15 / CE RED<br>风险：含BMS电路需EMC测试",
    ("锂电池", "化学物质"):   "RoHS / 电解液成分<br>风险：锂盐、溶剂有害物质",
    ("锂电池", "标签要求"):   "UN号 / 危险品标识 / 瓦时标注<br>风险：运输标签错误导致扣货",
    ("锂电池", "环保法规"):   "EU Battery Regulation 2023/1542<br>风险：碳足迹、回收率要求最严",
    ("锂电池", "认证要求"):   "UN38.3 / IEC 62133 / KC / MSDS<br>风险：多认证叠加，周期长成本高",
}


def _get_risk_color(value: float) -> str:
    """Map 0-100 value to red/yellow/green color."""
    if value >= 70:
        return COLOR_DANGER       # High risk: red
    elif value >= 40:
        return COLOR_WARNING      # Medium risk: orange/amber
    else:
        return COLOR_SUCCESS      # Low risk: green


def _adjust_matrix_for_report(report_text: str, product: str, markets: list) -> list:
    """
    Adjust the base risk matrix based on actual report content.
    Detects which product category is relevant and scales values accordingly.

    Returns 5×6 risk matrix.
    """
    matrix = [row[:] for row in BASE_RISK_MATRIX]  # deep copy

    # Detect if report mentions specific risk factors and boost/reduce scores
    boosts = {
        "电气安全": _count_regex_hits(report_text, [
            r"IEC\s*6[0-9]+", r"LVD", r"电气安全", r"过压", r"漏电", r"绝缘"
        ]) * 3,
        "EMC": _count_regex_hits(report_text, [
            r"EMC", r"FCC.*Part.*15", r"EN\s*55", r"TELEC", r"辐射", r"干扰"
        ]) * 3,
        "化学物质": _count_regex_hits(report_text, [
            r"RoHS", r"REACH", r"SVHC", r"重金属", r"phthalate", r"邻苯"
        ]) * 4,
        "标签要求": _count_regex_hits(report_text, [
            r"标签", r"label", r"标识", r"marking", r"警告"
        ]) * 2,
        "环保法规": _count_regex_hits(report_text, [
            r"WEEE", r"RoHS", r"EU Battery", r"ErP", r"Ecodesign", r"碳足迹"
        ]) * 3,
        "认证要求": _count_regex_hits(report_text, [
            r"CCC", r"CE.*认证", r"FCC.*认证", r"PSE", r"TELEC", r"UN38\.3"
        ]) * 4,
    }

    # Map column index to dimension name
    col_map = {0: "电气安全", 1: "EMC", 2: "化学物质", 3: "标签要求", 4: "环保法规", 5: "认证要求"}

    # Determine most relevant product row from report/product string
    product_lower = (product or "").lower() + report_text[:500].lower()
    row_weights = [0.0] * 5
    if any(kw in product_lower for kw in ["电子", "电器", "耳机", "充电", "蓝牙", "无线", "electronic"]):
        row_weights[0] += 3  # 消费电子
    if any(kw in product_lower for kw in ["玩具", "toy", "儿童"]):
        row_weights[1] += 3  # 玩具
    if any(kw in product_lower for kw in ["食品", "杯", "餐", "food", "cup", "保温"]):
        row_weights[2] += 3  # 食品接触
    if any(kw in product_lower for kw in ["纺织", "布", "面料", "服装", "textile", "fabric"]):
        row_weights[3] += 3  # 纺织品
    if any(kw in product_lower for kw in ["锂", "电池", "battery", "充电宝", "移动电源"]):
        row_weights[4] += 3  # 锂电池

    # Apply boosts to all rows, weighted
    for col_idx, dim_name in col_map.items():
        boost = min(boosts.get(dim_name, 0), 20)  # cap at 20
        for row_idx in range(5):
            w = 1.0 + row_weights[row_idx] * 0.1
            new_val = matrix[row_idx][col_idx] + boost * w
            matrix[row_idx][col_idx] = min(100.0, new_val)

    return matrix


def generate_risk_matrix(
    product: str = "",
    markets: list = None,
    report_text: str = "",
) -> str:
    """
    Generate an interactive Plotly risk heat matrix.

    Args:
        product: Product description string
        markets: List of target market strings
        report_text: Full compliance report text for score adjustment

    Returns:
        HTML string (Plotly figure, no full_html wrapper)
    """
    if markets is None:
        markets = []

    # Build adjusted matrix
    matrix = _adjust_matrix_for_report(report_text, product, markets)

    # Build hover text
    hover_text = []
    for r_idx, prod in enumerate(MATRIX_PRODUCTS):
        row_hovers = []
        for c_idx, cat in enumerate(MATRIX_CATEGORIES):
            val = matrix[r_idx][c_idx]
            key = (prod, cat)
            detail = _RISK_TOOLTIPS.get(key, "")
            risk_label = "高风险🔴" if val >= 70 else ("中风险🟡" if val >= 40 else "低风险🟢")
            tip = (
                f"<b>{prod} × {cat}</b><br>"
                f"风险等级：{risk_label}<br>"
                f"评分：{val:.0f}/100<br>"
                + (f"<br>{detail}" if detail else "")
            )
            row_hovers.append(tip)
        hover_text.append(row_hovers)

    # Color scale: green → yellow → red
    colorscale = [
        [0.0,  "#0f7a60"],   # 0  → success green
        [0.4,  "#27ae60"],   # 40
        [0.5,  "#e8a838"],   # 50 → warning amber
        [0.7,  "#e67e22"],   # 70 → orange
        [1.0,  "#c0392b"],   # 100 → danger red
    ]

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=MATRIX_CATEGORIES,
        y=MATRIX_PRODUCTS,
        colorscale=colorscale,
        zmin=0,
        zmax=100,
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="风险指数", font=dict(size=11, color=COLOR_TEXT_MUTED)),
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0", "25", "50", "75", "100"],
            thickness=14,
            len=0.85,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
            outlinecolor=COLOR_BORDER,
            outlinewidth=1,
        ),
        xgap=3,
        ygap=3,
    ))

    # Annotate each cell with value
    annotations = []
    for r_idx in range(len(MATRIX_PRODUCTS)):
        for c_idx in range(len(MATRIX_CATEGORIES)):
            val = matrix[r_idx][c_idx]
            text_color = "#fff" if val >= 55 else COLOR_TEXT
            annotations.append(dict(
                x=MATRIX_CATEGORIES[c_idx],
                y=MATRIX_PRODUCTS[r_idx],
                text=f"{val:.0f}",
                showarrow=False,
                font=dict(size=11, color=text_color, family="'Segoe UI', sans-serif"),
            ))

    fig.update_layout(
        annotations=annotations,
        xaxis=dict(
            tickfont=dict(size=12, color=COLOR_PRIMARY),
            side="bottom",
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            tickfont=dict(size=12, color=COLOR_PRIMARY),
            autorange="reversed",
            linecolor=COLOR_BORDER,
        ),
        paper_bgcolor=COLOR_SURFACE,
        plot_bgcolor=COLOR_SURFACE,
        margin=dict(l=80, r=80, t=60, b=60),
        height=340,
        title=dict(
            text="产品×法规领域 风险热力矩阵",
            font=dict(size=14, color=COLOR_PRIMARY, family="'Segoe UI', sans-serif"),
            x=0.5, xanchor="center",
            y=0.97,
        ),
        hoverlabel=dict(
            bgcolor=COLOR_PRIMARY,
            font=dict(color="#fff", size=12),
            bordercolor=COLOR_ACCENT,
        ),
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=False, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "displaylogo": False,
        "responsive": True,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Multi-market comparison helpers
# ─────────────────────────────────────────────────────────────────────────────

# Market → certification catalogue (base data, supplemented by report text)
MARKET_CERT_DB = {
    "欧盟": [
        {"cert": "CE认证 (RED)", "standard": "2014/53/EU", "year": 2014,
         "mandatory": "强制", "body": "Notified Body / TCB",
         "cost_test": 3500, "cost_cert": 2000, "cost_annual": 500,
         "weeks_min": 6, "weeks_max": 10,
         "cost_currency": "USD"},
        {"cert": "CE认证 (LVD)", "standard": "2014/35/EU", "year": 2014,
         "mandatory": "强制", "body": "Notified Body",
         "cost_test": 2500, "cost_cert": 1500, "cost_annual": 300,
         "weeks_min": 4, "weeks_max": 8,
         "cost_currency": "USD"},
        {"cert": "RoHS合规", "standard": "2011/65/EU (修订2015/863)", "year": 2015,
         "mandatory": "强制", "body": "第三方实验室",
         "cost_test": 1200, "cost_cert": 0, "cost_annual": 0,
         "weeks_min": 2, "weeks_max": 4,
         "cost_currency": "USD"},
        {"cert": "REACH/SVHC", "standard": "REACH Regulation No.1907/2006", "year": 2023,
         "mandatory": "强制", "body": "ECHA认可实验室",
         "cost_test": 800, "cost_cert": 0, "cost_annual": 0,
         "weeks_min": 2, "weeks_max": 3,
         "cost_currency": "USD"},
        {"cert": "WEEE注册", "standard": "2012/19/EU", "year": 2012,
         "mandatory": "强制", "body": "各国EPR机构",
         "cost_test": 0, "cost_cert": 500, "cost_annual": 300,
         "weeks_min": 1, "weeks_max": 2,
         "cost_currency": "USD"},
    ],
    "美国": [
        {"cert": "FCC认证 (Part 15B)", "standard": "47 CFR Part 15B", "year": 2021,
         "mandatory": "强制", "body": "FCC TCB",
         "cost_test": 3000, "cost_cert": 1500, "cost_annual": 0,
         "weeks_min": 4, "weeks_max": 8,
         "cost_currency": "USD"},
        {"cert": "FCC ID (无线)", "standard": "47 CFR Part 15C/D", "year": 2021,
         "mandatory": "强制", "body": "FCC授权实验室",
         "cost_test": 2000, "cost_cert": 1000, "cost_annual": 0,
         "weeks_min": 3, "weeks_max": 6,
         "cost_currency": "USD"},
        {"cert": "UL认证", "standard": "UL 62368-1 / UL 60950", "year": 2022,
         "mandatory": "自愿", "body": "UL Solutions",
         "cost_test": 5000, "cost_cert": 3000, "cost_annual": 1500,
         "weeks_min": 6, "weeks_max": 10,
         "cost_currency": "USD"},
        {"cert": "CPSC合规", "standard": "CPSA / 16 CFR", "year": 2023,
         "mandatory": "强制", "body": "CPSC认可实验室",
         "cost_test": 1500, "cost_cert": 0, "cost_annual": 0,
         "weeks_min": 2, "weeks_max": 4,
         "cost_currency": "USD"},
    ],
    "中国": [
        {"cert": "CCC认证 (3C)", "standard": "GB 4943.1 / GB 9254", "year": 2022,
         "mandatory": "强制", "body": "CNCA指定机构",
         "cost_test": 25000, "cost_cert": 8000, "cost_annual": 3000,
         "weeks_min": 8, "weeks_max": 14,
         "cost_currency": "CNY"},
        {"cert": "RoHS合规 (中国版)", "standard": "GB/T 26572 / SJ/T 11363", "year": 2016,
         "mandatory": "强制", "body": "CQC / 第三方实验室",
         "cost_test": 3000, "cost_cert": 0, "cost_annual": 0,
         "weeks_min": 2, "weeks_max": 4,
         "cost_currency": "CNY"},
        {"cert": "能效标识", "standard": "GB 24849 / GB 12021", "year": 2021,
         "mandatory": "强制", "body": "CECP平台注册",
         "cost_test": 2000, "cost_cert": 500, "cost_annual": 200,
         "weeks_min": 2, "weeks_max": 3,
         "cost_currency": "CNY"},
    ],
    "日本": [
        {"cert": "PSE认证 (电安法)", "standard": "电気用品安全法 / JIS C 62368-1", "year": 2022,
         "mandatory": "强制", "body": "登录检查机关",
         "cost_test": 4000, "cost_cert": 2000, "cost_annual": 500,
         "weeks_min": 5, "weeks_max": 10,
         "cost_currency": "USD"},
        {"cert": "TELEC认证", "standard": "电波法 / 技術基準適合証明", "year": 2023,
         "mandatory": "强制", "body": "MIC指定机关",
         "cost_test": 3500, "cost_cert": 1500, "cost_annual": 0,
         "weeks_min": 4, "weeks_max": 8,
         "cost_currency": "USD"},
        {"cert": "PSC认证 (消安法)", "standard": "消費生活用製品安全法", "year": 2019,
         "mandatory": "强制", "body": "第三方机关",
         "cost_test": 2500, "cost_cert": 1000, "cost_annual": 0,
         "weeks_min": 4, "weeks_max": 6,
         "cost_currency": "USD"},
    ],
}

# Market display colors (deep blue palette + amber accents)
MARKET_COLORS = {
    "欧盟":  "#1a3a5c",
    "美国":  "#2563a8",
    "中国":  "#d4830a",
    "日本":  "#0f7a60",
}

MARKET_COLORS_LIGHT = {
    "欧盟":  "rgba(26,58,92,0.18)",
    "美国":  "rgba(37,99,168,0.18)",
    "中国":  "rgba(212,131,10,0.18)",
    "日本":  "rgba(15,122,96,0.18)",
}

CNY_TO_USD = 0.138   # approximate conversion for mixed display


def _get_market_certs(report_text: str, market: str) -> list:
    """Return certification list for a market, filtering by report content when possible."""
    base = MARKET_CERT_DB.get(market, [])
    if not base:
        return []

    result = []
    for cert in base:
        # Always include if standard keyword found in report, else include anyway (general)
        keywords = cert["standard"].split("/")[0].strip().split()[0]
        found = bool(re.search(keywords, report_text, re.IGNORECASE))
        entry = dict(cert)
        entry["from_report"] = found
        result.append(entry)
    return result


def _normalize_cost_usd(cost: float, currency: str) -> float:
    """Normalize cost to USD for comparison."""
    if currency == "CNY":
        return cost * CNY_TO_USD
    return cost


# ─────────────────────────────────────────────────────────────────────────────
# New Chart 1: Comparison Table
# ─────────────────────────────────────────────────────────────────────────────

def generate_comparison_table(report_text: str, product: str, markets: list) -> str:
    """
    Generate a multi-market regulatory comparison table as styled HTML.

    Returns: HTML string (no full-page wrapper).
    """
    if not markets:
        return "<p style='color:#60748a;padding:16px'>请选择至少一个目标市场以生成对比表格。</p>"

    # Build rows
    rows = []
    for market in markets:
        certs = _get_market_certs(report_text, market)
        for cert in certs:
            currency = cert["cost_currency"]
            test_lo = cert["cost_test"] * 0.8
            test_hi = cert["cost_test"] * 1.4
            cert_lo = cert["cost_cert"] * 0.8
            cert_hi = cert["cost_cert"] * 1.4

            if currency == "CNY":
                cost_str = f"¥{test_lo:,.0f}–{test_hi:,.0f}测试 + ¥{cert_lo:,.0f}–{cert_hi:,.0f}认证"
                unit = "¥"
            else:
                cost_str = f"${test_lo:,.0f}–${test_hi:,.0f}测试 + ${cert_lo:,.0f}–${cert_hi:,.0f}认证"
                unit = "$"

            if cert["cost_annual"] > 0:
                cost_str += f" + {unit}{cert['cost_annual']:,.0f}/年"

            rows.append({
                "market": market,
                "cert": cert["cert"],
                "standard": cert["standard"],
                "year": str(cert["year"]),
                "mandatory": cert["mandatory"],
                "body": cert["body"],
                "cost": cost_str,
                "weeks": f"{cert['weeks_min']}–{cert['weeks_max']} 周",
                "from_report": cert["from_report"],
            })

    if not rows:
        return "<p style='color:#60748a;padding:16px'>暂无数据</p>"

    # Build HTML table
    tbody_rows = ""
    for r in rows:
        mc = MARKET_COLORS.get(r["market"], COLOR_PRIMARY)
        badge_bg = "background:#e8f5e9;color:#2e7d32;" if r["mandatory"] == "自愿" else "background:#fce4ec;color:#c62828;"
        source_badge = ""
        if r["from_report"]:
            source_badge = '<span style="font-size:0.68rem;background:#e3f2fd;color:#1565c0;border-radius:3px;padding:1px 5px;margin-left:4px;">报告确认</span>'
        else:
            source_badge = '<span style="font-size:0.68rem;background:#fff8e1;color:#f57f17;border-radius:3px;padding:1px 5px;margin-left:4px;">参考值</span>'

        tbody_rows += f"""
        <tr>
            <td style="white-space:nowrap;">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{mc};margin-right:6px;vertical-align:middle;"></span>
                <strong style="color:{mc}">{r['market']}</strong>
            </td>
            <td><strong>{r['cert']}</strong>{source_badge}</td>
            <td style="font-family:monospace;font-size:0.82rem;color:#1a3a5c">{r['standard']}</td>
            <td style="text-align:center">{r['year']}</td>
            <td style="text-align:center">
                <span style="font-size:0.75rem;padding:2px 8px;border-radius:10px;font-weight:600;{badge_bg}">{r['mandatory']}</span>
            </td>
            <td style="font-size:0.82rem;color:#60748a">{r['body']}</td>
            <td style="font-size:0.81rem;color:#1e2d3d">{r['cost']}</td>
            <td style="text-align:center;white-space:nowrap">
                <span style="background:#f0f4f8;border-radius:10px;padding:2px 8px;font-size:0.82rem">{r['weeks']}</span>
            </td>
        </tr>"""

    html = f"""
<div style="overflow-x:auto;margin-top:4px;">
  <table style="
    width:100%;border-collapse:collapse;font-size:0.84rem;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',sans-serif;
    box-shadow:0 2px 8px rgba(0,0,0,0.07);border-radius:8px;overflow:hidden;
  ">
    <thead>
      <tr style="background:#1a3a5c;color:#fff;">
        <th style="padding:10px 14px;text-align:left;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">适用市场</th>
        <th style="padding:10px 14px;text-align:left;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">认证 / 法规</th>
        <th style="padding:10px 14px;text-align:left;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">标准号</th>
        <th style="padding:10px 14px;text-align:center;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">版本年份</th>
        <th style="padding:10px 14px;text-align:center;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">强制/自愿</th>
        <th style="padding:10px 14px;text-align:left;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">认证机构</th>
        <th style="padding:10px 14px;text-align:left;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">预估费用区间</th>
        <th style="padding:10px 14px;text-align:center;font-weight:600;font-size:0.78rem;letter-spacing:0.04em">预估周期</th>
      </tr>
    </thead>
    <tbody>
      {tbody_rows}
    </tbody>
  </table>
  <div style="margin-top:10px;font-size:0.75rem;color:#60748a;display:flex;gap:14px;flex-wrap:wrap;align-items:center;">
    <span>⚠️ <strong>参考值</strong> 为行业常识估算，实际费用因实验室和产品复杂度而异</span>
    <span style="display:flex;align-items:center;gap:4px;">
      <span style="background:#e3f2fd;color:#1565c0;border-radius:3px;padding:1px 5px;font-size:0.72rem">报告确认</span>
      = 报告文本中检测到的标准
    </span>
    <span style="display:flex;align-items:center;gap:4px;">
      <span style="background:#fff8e1;color:#f57f17;border-radius:3px;padding:1px 5px;font-size:0.72rem">参考值</span>
      = 行业常识补充
    </span>
  </div>
</div>
"""
    return html


# ─────────────────────────────────────────────────────────────────────────────
# New Chart 2: Timeline Gantt Chart
# ─────────────────────────────────────────────────────────────────────────────

def generate_timeline_chart(report_text: str, markets: list) -> str:
    """
    Generate a horizontal Gantt chart showing parallel certification timelines
    for each selected market.

    Returns: HTML string (Plotly figure, no full_html wrapper).
    """
    if not markets:
        return "<p style='color:#60748a;padding:16px'>请选择至少一个目标市场以生成时间线图表。</p>"

    import datetime as dt

    start_date = dt.date(2025, 1, 6)  # Monday reference start

    tasks = []
    for market in markets:
        certs = _get_market_certs(report_text, market)
        # Running offset: tasks start one after another (parallel within market)
        offset_weeks = 0
        for cert in certs:
            start_w = offset_weeks
            end_w   = start_w + cert["weeks_max"]
            s = start_date + dt.timedelta(weeks=start_w)
            e = start_date + dt.timedelta(weeks=end_w)
            tasks.append({
                "market":  market,
                "cert":    cert["cert"],
                "start":   s.isoformat(),
                "end":     e.isoformat(),
                "weeks":   cert["weeks_max"],
                "color":   MARKET_COLORS.get(market, COLOR_PRIMARY),
            })
            # Stagger next cert by prep time (2 weeks overlap allowed)
            offset_weeks += max(cert["weeks_min"], 1)

    if not tasks:
        return "<p style='color:#60748a;padding:16px'>暂无时间线数据</p>"

    fig = go.Figure()

    # Plot one bar per task
    for task in tasks:
        mc = MARKET_COLORS.get(task["market"], COLOR_PRIMARY)
        fig.add_trace(go.Bar(
            name=task["market"],
            x=[task["weeks"]],
            y=[task["cert"]],
            orientation="h",
            marker=dict(
                color=mc,
                line=dict(color="#fff", width=1),
                opacity=0.85,
            ),
            base=[0],
            text=f"  {task['cert']} · {task['weeks']}周",
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(color="#fff", size=11),
            hovertemplate=(
                f"<b>{task['cert']}</b><br>"
                f"市场：{task['market']}<br>"
                f"预估周期：{task['weeks']}周<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    # Add invisible legend traces per market
    seen_markets = []
    for task in tasks:
        if task["market"] not in seen_markets:
            seen_markets.append(task["market"])
            mc = MARKET_COLORS.get(task["market"], COLOR_PRIMARY)
            fig.add_trace(go.Bar(
                name=task["market"],
                x=[0],
                y=[tasks[0]["cert"]],
                orientation="h",
                marker_color=mc,
                showlegend=True,
                visible="legendonly",
                opacity=0,
                hoverinfo="skip",
            ))

    # x-axis: weeks
    max_weeks = max(t["weeks"] for t in tasks) + 4
    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="预估周期（周）",
            range=[0, max_weeks],
            tickfont=dict(size=11, color=COLOR_TEXT_MUTED),
            gridcolor=COLOR_BORDER,
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color=COLOR_PRIMARY),
            autorange="reversed",
            linecolor=COLOR_BORDER,
        ),
        paper_bgcolor=COLOR_SURFACE,
        plot_bgcolor="#f7f9fc",
        height=max(280, len(tasks) * 36 + 100),
        margin=dict(l=20, r=80, t=55, b=50),
        title=dict(
            text="合规认证时间线（各市场并行展示）",
            font=dict(size=14, color=COLOR_PRIMARY, family="'Segoe UI', sans-serif"),
            x=0.5, xanchor="center",
            y=0.98,
        ),
        legend=dict(
            title=dict(text="市场", font=dict(size=11)),
            font=dict(size=11, color=COLOR_TEXT_MUTED),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=COLOR_BORDER,
            borderwidth=1,
            orientation="h",
            y=-0.15,
        ),
        hoverlabel=dict(
            bgcolor=COLOR_PRIMARY,
            font=dict(color="#fff", size=12),
            bordercolor=COLOR_ACCENT,
        ),
    )

    # Add market color bands in background
    y_vals = [t["cert"] for t in tasks]
    for i, task in enumerate(tasks):
        mc_light = MARKET_COLORS_LIGHT.get(task["market"], "rgba(26,58,92,0.08)")
        fig.add_shape(
            type="rect",
            xref="paper", yref="y",
            x0=0, x1=1,
            y0=i - 0.4, y1=i + 0.4,
            fillcolor=mc_light,
            line_width=0,
            layer="below",
        )

    return fig.to_html(include_plotlyjs="cdn", full_html=False, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "displaylogo": False,
        "responsive": True,
    })


# ─────────────────────────────────────────────────────────────────────────────
# New Chart 3: Cost Comparison Bar Chart
# ─────────────────────────────────────────────────────────────────────────────

def generate_cost_chart(report_text: str, markets: list) -> str:
    """
    Generate a stacked bar chart comparing certification costs across markets.
    All costs normalized to USD for comparison.

    Returns: HTML string (Plotly figure, no full_html wrapper).
    """
    if not markets:
        return "<p style='color:#60748a;padding:16px'>请选择至少一个目标市场以生成成本对比图。</p>"

    # Aggregate costs per market
    market_costs = {}  # market -> {test: float, cert: float, annual: float}
    for market in markets:
        certs = _get_market_certs(report_text, market)
        total_test   = sum(_normalize_cost_usd(c["cost_test"],   c["cost_currency"]) for c in certs)
        total_cert   = sum(_normalize_cost_usd(c["cost_cert"],   c["cost_currency"]) for c in certs)
        total_annual = sum(_normalize_cost_usd(c["cost_annual"], c["cost_currency"]) for c in certs)
        market_costs[market] = {
            "test":   round(total_test),
            "cert":   round(total_cert),
            "annual": round(total_annual),
            "total":  round(total_test + total_cert + total_annual),
        }

    if not market_costs:
        return "<p style='color:#60748a;padding:16px'>暂无成本数据</p>"

    x_labels = list(market_costs.keys())
    test_vals   = [market_costs[m]["test"]   for m in x_labels]
    cert_vals   = [market_costs[m]["cert"]   for m in x_labels]
    annual_vals = [market_costs[m]["annual"] for m in x_labels]
    total_vals  = [market_costs[m]["total"]  for m in x_labels]

    fig = go.Figure()

    # Stacked layers: test / certification / annual
    fig.add_trace(go.Bar(
        name="测试费",
        x=x_labels,
        y=test_vals,
        marker=dict(color=COLOR_PRIMARY, opacity=0.9,
                    line=dict(color="#fff", width=1)),
        hovertemplate="<b>%{x}</b><br>测试费：$%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="认证费",
        x=x_labels,
        y=cert_vals,
        marker=dict(color=COLOR_ACCENT, opacity=0.9,
                    line=dict(color="#fff", width=1)),
        hovertemplate="<b>%{x}</b><br>认证费：$%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="年审/维护费",
        x=x_labels,
        y=annual_vals,
        marker=dict(color=COLOR_ACCENT_LIGHT, opacity=0.9,
                    line=dict(color="#fff", width=1)),
        hovertemplate="<b>%{x}</b><br>年审费：$%{y:,.0f}<extra></extra>",
    ))

    # Total label annotations
    annotations = []
    for i, (market, total) in enumerate(zip(x_labels, total_vals)):
        annotations.append(dict(
            x=market,
            y=total,
            text=f"<b>${total:,}</b>",
            showarrow=False,
            yanchor="bottom",
            yshift=6,
            font=dict(size=12, color=COLOR_PRIMARY),
        ))

    fig.update_layout(
        barmode="stack",
        annotations=annotations,
        xaxis=dict(
            tickfont=dict(size=13, color=COLOR_PRIMARY),
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            title="预估总成本（USD）",
            tickformat="$,.0f",
            tickfont=dict(size=11, color=COLOR_TEXT_MUTED),
            gridcolor=COLOR_BORDER,
            linecolor=COLOR_BORDER,
        ),
        legend=dict(
            orientation="h",
            y=-0.15,
            font=dict(size=11, color=COLOR_TEXT_MUTED),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=COLOR_BORDER,
            borderwidth=1,
        ),
        paper_bgcolor=COLOR_SURFACE,
        plot_bgcolor="#f7f9fc",
        height=380,
        margin=dict(l=70, r=40, t=55, b=70),
        title=dict(
            text="各市场认证成本对比（USD，参考值）",
            font=dict(size=14, color=COLOR_PRIMARY, family="'Segoe UI', sans-serif"),
            x=0.5, xanchor="center",
            y=0.97,
        ),
        hoverlabel=dict(
            bgcolor=COLOR_PRIMARY,
            font=dict(color="#fff", size=12),
            bordercolor=COLOR_ACCENT,
        ),
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=False, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "displaylogo": False,
        "responsive": True,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Combined chart HTML (both charts + styling)
# ─────────────────────────────────────────────────────────────────────────────

PLACEHOLDER_HTML = """
<div style="
    background: #f7f9fc;
    border: 2px dashed #dce3ec;
    border-radius: 12px;
    padding: 40px 24px;
    text-align: center;
    color: #60748a;
    margin-top: 8px;
">
    <div style="font-size: 2.2rem; margin-bottom: 12px;">📊</div>
    <div style="font-size: 0.95rem; font-weight: 600; color: #1a3a5c; margin-bottom: 6px;">
        合规风险可视化
    </div>
    <div style="font-size: 0.82rem; line-height: 1.65; max-width: 340px; margin: 0 auto;">
        生成报告后，雷达图和风险矩阵将自动出现在此处。
    </div>
</div>
"""


def generate_charts_html(report_text: str, product: str = "", markets: list = None) -> str:
    """
    Generate combined HTML with ALL charts in a tabbed interface.

    Tabs:
      1. 风险概览  — Radar chart + Risk heat matrix  (original two)
      2. 法规对比  — Multi-market comparison table    (new)
      3. 时间线    — Gantt timeline chart             (new)
      4. 成本对比  — Stacked cost bar chart           (new)

    Args:
        report_text: Full compliance report text
        product: Product description
        markets: Target markets list

    Returns:
        Full HTML string ready for gr.HTML component
    """
    if not report_text or len(report_text.strip()) < 100:
        return PLACEHOLDER_HTML

    if markets is None:
        markets = []

    multi_market = len(markets) > 1

    # ── Generate all panels ──────────────────────────────────────────────────
    try:
        radar_html = generate_radar_chart(report_text)
    except Exception as e:
        radar_html = f"<p style='color:#c0392b'>雷达图生成失败：{e}</p>"

    try:
        matrix_html = generate_risk_matrix(product, markets, report_text)
    except Exception as e:
        matrix_html = f"<p style='color:#c0392b'>矩阵图生成失败：{e}</p>"

    try:
        table_html = generate_comparison_table(report_text, product, markets)
    except Exception as e:
        table_html = f"<p style='color:#c0392b'>对比表格生成失败：{e}</p>"

    try:
        timeline_html = generate_timeline_chart(report_text, markets)
    except Exception as e:
        timeline_html = f"<p style='color:#c0392b'>时间线图生成失败：{e}</p>"

    try:
        cost_html = generate_cost_chart(report_text, markets)
    except Exception as e:
        cost_html = f"<p style='color:#c0392b'>成本图生成失败：{e}</p>"

    # Legend for risk matrix
    legend_html = """
        <div style="display:flex;gap:16px;justify-content:center;margin-top:14px;font-size:0.78rem;color:#60748a;">
            <span style="display:flex;align-items:center;gap:5px;">
                <span style="width:12px;height:12px;border-radius:2px;background:#0f7a60;display:inline-block;"></span>低风险 (&lt;40)
            </span>
            <span style="display:flex;align-items:center;gap:5px;">
                <span style="width:12px;height:12px;border-radius:2px;background:#e8a838;display:inline-block;"></span>中风险 (40-70)
            </span>
            <span style="display:flex;align-items:center;gap:5px;">
                <span style="width:12px;height:12px;border-radius:2px;background:#c0392b;display:inline-block;"></span>高风险 (&gt;70)
            </span>
        </div>"""

    new_badge = ('<span style="font-size:0.68rem;background:#d4830a;color:#fff;'
                 'border-radius:3px;padding:1px 6px;margin-left:6px;vertical-align:middle;'
                 'font-weight:700;letter-spacing:0.05em;">多市场</span>'
                 if multi_market else "")

    # Unique ID prefix to avoid JS collisions if embedded multiple times
    uid = "tic_tabs"

    html = f"""
<style>
.{uid}-tabs {{
    display: flex;
    gap: 0;
    border-bottom: 2px solid #dce3ec;
    margin-bottom: 0;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}}
.{uid}-tab-btn {{
    padding: 10px 18px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #60748a;
    border: none;
    background: #f7f9fc;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: color 0.18s, border-color 0.18s, background 0.18s;
    white-space: nowrap;
    letter-spacing: 0.03em;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.{uid}-tab-btn:hover {{
    color: #1a3a5c;
    background: #eef4fb;
}}
.{uid}-tab-btn.active {{
    color: #1a3a5c;
    border-bottom-color: #d4830a;
    background: #ffffff;
}}
.{uid}-panel {{
    display: none;
    padding: 16px 12px 12px;
}}
.{uid}-panel.active {{
    display: block;
}}
</style>

<div style="margin-top:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',sans-serif;">

  <!-- Section header -->
  <div style="
    background:linear-gradient(90deg,#f7f9fc 0%,#fff 100%);
    border:1px solid #dce3ec;
    border-bottom:2px solid #d4830a;
    border-radius:12px 12px 0 0;
    padding:14px 20px;
    display:flex;align-items:center;gap:10px;
  ">
    <div style="font-size:1rem;width:28px;height:28px;display:flex;align-items:center;
                justify-content:center;background:#fef3dc;border-radius:4px;flex-shrink:0;">📊</div>
    <div style="font-size:0.82rem;font-weight:700;color:#1a3a5c;
                letter-spacing:0.04em;text-transform:uppercase;">
      合规风险可视化
      {new_badge}
    </div>
  </div>

  <!-- Tab bar + body -->
  <div style="background:#fff;border:1px solid #dce3ec;border-top:none;
              border-radius:0 0 12px 12px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">

    <!-- Tab buttons -->
    <div class="{uid}-tabs" id="{uid}-tab-bar">
      <button class="{uid}-tab-btn active" onclick="ticSwitchTab('{uid}',0)" id="{uid}-btn-0">
        📈 风险概览
      </button>
      <button class="{uid}-tab-btn" onclick="ticSwitchTab('{uid}',1)" id="{uid}-btn-1">
        📋 法规对比{new_badge}
      </button>
      <button class="{uid}-tab-btn" onclick="ticSwitchTab('{uid}',2)" id="{uid}-btn-2">
        🗓️ 认证时间线{new_badge}
      </button>
      <button class="{uid}-tab-btn" onclick="ticSwitchTab('{uid}',3)" id="{uid}-btn-3">
        💰 成本对比{new_badge}
      </button>
    </div>

    <!-- Tab panels -->

    <!-- Panel 0: 风险概览 -->
    <div class="{uid}-panel active" id="{uid}-panel-0">
      <div style="background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:8px;margin-bottom:14px;">
        {radar_html}
      </div>
      <div style="height:1px;background:#dce3ec;margin:0 0 14px;"></div>
      <div style="background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:8px;">
        {matrix_html}
      </div>
      {legend_html}
      <div style="margin-top:12px;padding:10px 14px;background:#f0f7ff;border:1px solid #c3d8ef;
                  border-left:4px solid #2563a8;border-radius:6px;font-size:0.78rem;color:#1a3355;line-height:1.6;">
        <strong>📌 图表说明</strong>：雷达图基于报告中检测到的法规类型和数量推算合规复杂度（0-100）；
        热力矩阵展示当前产品在各法规领域的风险等级，颜色深浅反映风险高低。
        Hover 单元格可查看具体法规和风险说明。
      </div>
    </div>

    <!-- Panel 1: 法规对比 -->
    <div class="{uid}-panel" id="{uid}-panel-1">
      <div style="margin-bottom:10px;font-size:0.78rem;color:#60748a;">
        以下表格汇总各目标市场的主要认证要求，供横向比较。
        <span style="color:#f57f17;font-weight:600;">参考值</span> 为行业常识估算，实际请咨询认证机构。
      </div>
      {table_html}
    </div>

    <!-- Panel 2: 时间线 -->
    <div class="{uid}-panel" id="{uid}-panel-2">
      <div style="margin-bottom:10px;font-size:0.78rem;color:#60748a;">
        各市场认证流程预估时间（基于典型周期，并行展示）。实际进度受实验室排期影响。
      </div>
      <div style="background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:8px;">
        {timeline_html}
      </div>
    </div>

    <!-- Panel 3: 成本对比 -->
    <div class="{uid}-panel" id="{uid}-panel-3">
      <div style="margin-bottom:10px;font-size:0.78rem;color:#60748a;">
        各市场认证总成本估算（均换算为 USD 对比）。CNY费用按 1 CNY ≈ $0.138 换算。
      </div>
      <div style="background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:8px;">
        {cost_html}
      </div>
    </div>

  </div>
</div>

<script>
function ticSwitchTab(uid, idx) {{
  var panels = document.querySelectorAll('.' + uid + '-panel');
  var btns   = document.querySelectorAll('.' + uid + '-tab-btn');
  panels.forEach(function(p, i) {{ p.classList.toggle('active', i === idx); }});
  btns.forEach(function(b, i)   {{ b.classList.toggle('active', i === idx); }});
}}
</script>
"""
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SAMPLE_REPORT = """
    蓝牙无线耳机 (TWS) 合规检查报告
    目标市场：欧盟、美国

    ## 适用法规清单

    ### 欧盟 (EU)
    - **RED 2014/53/EU** 无线设备指令：蓝牙5.3属于无线设备，强制CE认证
    - **LVD 2014/35/EU** 低压指令：额定充电5W适用
    - **RoHS 2011/65/EU**：限制铅、镉、汞、六价铬等有害物质
    - **REACH SVHC**：候选物质清单检查
    - **WEEE 2012/19/EU**：废弃电子设备回收标志

    ### 美国 (US)
    - **FCC Part 15B** EMC要求
    - **FCC ID** 蓝牙无线认证（BT 5.3需要）
    - **CPSC** 消费品安全要求

    ## 合规检查清单

    | 测试项目 | 标准 | 风险等级 |
    |---------|------|---------|
    | 电气安全 | IEC 62368-1 | 高 |
    | EMC辐射 | EN 55032, CISPR 32 | 高 |
    | 蓝牙认证 | FCC ID, CE RED | 高 |
    | RoHS有害物质 | EN 50581 | 中 |
    | 电池安全 | IEC 62133-2 | 中 |
    | 标签合规 | CE标志, FCC ID标识 | 低 |
    | WEEE标志 | 2012/19/EU | 低 |

    ## 特别注意事项
    - 锂电池250mAh需要UN38.3运输认证
    - REACH SVHC高度关注物质超过0.1%需要申报
    - 欧盟市场需要在EPREL平台注册能效数据
    """

    print("Testing extract_scores_from_report...")
    result = extract_scores_from_report(SAMPLE_REPORT)
    print("Scores:", result["scores"])
    print("Dims:  ", RADAR_DIMS_SHORT)

    print("\nTesting generate_radar_chart...")
    html = generate_radar_chart(SAMPLE_REPORT)
    print(f"Radar chart HTML length: {len(html)} chars")

    print("\nTesting generate_risk_matrix...")
    html2 = generate_risk_matrix("蓝牙无线耳机", ["欧盟", "美国"], SAMPLE_REPORT)
    print(f"Risk matrix HTML length: {len(html2)} chars")

    print("\nTesting generate_charts_html...")
    combined = generate_charts_html(SAMPLE_REPORT, "蓝牙无线耳机", ["欧盟", "美国"])
    with open("test_charts.html", "w", encoding="utf-8") as f:
        f.write(f"<html><body>{combined}</body></html>")
    print("Saved test_charts.html")
    print("✅ All tests passed.")
