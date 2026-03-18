# backend/main.py - TIC-Agent FastAPI backend
# Exposes agent logic as REST API with SSE streaming
#
# Usage:
#   cd D:\TIC-Agent-Demo
#   uvicorn backend.main:app --reload --port 8000

import sys
import os
import json
import asyncio
from typing import AsyncGenerator

# ── Ensure parent directory is importable ──────────────────────────────────
# This file lives in backend/, but agent.py etc. are in the parent dir.
_PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

# ── FastAPI + SSE imports ──────────────────────────────────────────────────
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# ── Project imports ─────────────────────────────────────────────────────────
from agent import run_agent_stream, follow_up_stream, MODEL
from knowledge_base import get_regulations_for_product
from export_pdf import generate_pdf

# ────────────────────────────────────────────────────────────────────────────
# Report data extraction — parse structured data from LLM report text
# ────────────────────────────────────────────────────────────────────────────

import re


def _extract_radar_scores(report_text: str) -> list[dict]:
    """
    Extract compliance coverage indicators from report text.
    Returns list of {subject, score, fullMark, reason, coverage} dicts, or [] if insufficient data.

    Coverage score reflects how thoroughly the report discusses each compliance dimension,
    NOT whether the product is actually compliant. Score = fraction of relevant terms mentioned
    (capped at 100), scaled to a readable range. The 'coverage' field gives a symbolic indicator.
    """
    text = report_text.lower()

    # Each dimension has a set of signal terms; more unique hits = better coverage in the report
    DIMENSION_KEYWORDS: dict[str, list[str]] = {
        "电气安全": [
            "iec 60950", "iec 60065", "iec 62368", "ul 60950", "ul 62368",
            "lvd", "电气安全", "electrical safety", "绝缘", "接地", "漏电",
            "过载保护", "en 60950", "en 62368", "bs en", "安全标准",
        ],
        "EMC": [
            "emc", "电磁兼容", "fcc part 15", "fcc part 18", "cispr",
            "en 55032", "en 55035", "en 61000", "iec 61000", "辐射发射",
            "传导发射", "电磁干扰", "抗扰度", "esd", "浪涌",
        ],
        "化学物质": [
            "rohs", "reach", "svhc", "有害物质", "卤素", "铅", "汞", "镉",
            "六价铬", "多溴联苯", "pbb", "pbde", "erp", "化学品",
        ],
        "标签要求": [
            "标签", "标识", "label", "marking", "ce标志", "fcc id",
            "ccc标志", "pse标志", "能效标识", "警告", "说明书", "包装标注",
        ],
        "环保法规": [
            "weee", "能效", "energy star", "碳排放", "环保", "回收",
            "可持续", "绿色", "低功耗", "待机功耗", "环境保护",
        ],
        "认证要求": [
            "ce认证", "fcc认证", "ccc认证", "pse认证", "kc认证",
            "srrc", "型式认证", "自我声明", "doc", "合格声明",
            "认证机构", "测试报告", "技术文件",
        ],
    }

    # Thresholds for coverage symbols: hits / total_keywords_in_dim
    # ≥ 0.4 → ✅ 充分覆盖, 0.15–0.4 → ⚠️ 部分覆盖, < 0.15 → ❌ 未充分覆盖
    def _coverage_symbol(fraction: float) -> str:
        if fraction >= 0.4:
            return "✅"
        elif fraction >= 0.15:
            return "⚠️"
        else:
            return "❌"

    results = []
    total_hits = 0
    for subject, keywords in DIMENSION_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        total_hits += hits
        fraction = hits / max(len(keywords), 1)
        # Scale to 0–100 for radar chart display; minimum 10 to keep chart readable
        score = max(10, round(fraction * 100))
        symbol = _coverage_symbol(fraction)
        results.append({
            "subject": subject,
            "score": score,
            "fullMark": 100,
            "reason": f"{symbol} 基于报告中相关法规的提及数量评估覆盖度，不代表产品合规状态",
            "coverage": symbol,
        })

    # If no hits at all, return empty to signal "insufficient data"
    if total_hits == 0:
        return []
    return results


def _parse_currency_value(raw: str) -> int | None:
    """Parse a raw numeric string (with commas/汉字万/千) to an integer USD/RMB amount."""
    clean = raw.replace(",", "").replace("，", "").strip()
    # Handle "万" suffix: 1.5万 = 15000
    if "万" in clean:
        clean = clean.replace("万", "").strip()
        try:
            return int(float(clean) * 10000)
        except ValueError:
            return None
    # Handle "千" suffix: 8千 = 8000
    if "千" in clean:
        clean = clean.replace("千", "").strip()
        try:
            return int(float(clean) * 1000)
        except ValueError:
            return None
    try:
        val = float(clean)
        return int(val)
    except ValueError:
        return None


def _extract_cost_data(report_text: str, markets: list[str]) -> list[dict] | None:
    """
    Extract cost estimates directly from report text using regex.
    Returns list of {market, testingFee, certFee, annualFee, source} or None if no data found.

    NO hardcoded fallback costs. If extraction fails, returns None so the UI shows
    "费用数据未在报告中明确提及" instead of fabricated numbers.
    """
    MARKET_ALIASES: dict[str, list[str]] = {
        "欧盟": ["eu", "europe", "欧盟", "ce认证", "ce"],
        "美国": ["us", "usa", "fcc", "美国", "北美"],
        "中国": ["cn", "china", "中国", "ccc", "3c"],
        "日本": ["jp", "japan", "日本", "pse"],
        "韩国": ["kr", "korea", "韩国", "kc"],
        "英国": ["uk", "ukca", "英国"],
        "澳大利亚": ["au", "australia", "澳大利亚"],
        "巴西": ["br", "brazil", "巴西", "anatel"],
        "印度": ["in", "india", "印度", "bis"],
        "东南亚": ["sea", "asean", "东南亚"],
    }

    # Patterns that capture fee type + numeric range from report text
    # Tries to capture: "测试费 USD 3,000–8,000" / "认证费约 $5,000" / "RMB 15,000 – 30,000" etc.
    FEE_TYPE_PATTERNS = [
        # Range: USD/RMB X,XXX – Y,YYY
        (r'(?:测试费|testing fee)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)\s*[–\-~～至到]\s*([\d,，]+)', "testingFee"),
        (r'(?:认证费|cert(?:ification)? fee)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)\s*[–\-~～至到]\s*([\d,，]+)', "certFee"),
        (r'(?:年费|年审费|annual fee)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)\s*[–\-~～至到]\s*([\d,，]+)', "annualFee"),
        # Single value
        (r'(?:测试费|testing fee)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)', "testingFee"),
        (r'(?:认证费|cert(?:ification)? fee)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)', "certFee"),
        (r'(?:年费|年审费|annual fee)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)', "annualFee"),
        # Generic "预估费用 USD X,XXX–Y,YYY" lines
        (r'(?:预估费用|估计费用|参考费用|费用参考|合计费用)[^\d\n]{0,40}?(?:USD|RMB|CNY|\$|¥|美元|元)\s*([\d,，]+)\s*[–\-~～至到]\s*([\d,，]+)', "totalFee"),
        (r'(?:USD|RMB|CNY|\$)\s*([\d,，]+)\s*[–\-~～至到]\s*([\d,，]+)', "rangeFee"),
    ]

    # Split text into paragraphs/sections per market to localise extraction
    # We look for section headers like "## 🇺🇸 美国" or "## 欧盟"
    result = []
    found_any = False

    for market in markets:
        # Find canonical key for this market label
        canon = None
        for key, aliases in MARKET_ALIASES.items():
            if market == key or market.lower() in aliases or any(a in market.lower() for a in aliases):
                canon = key
                break
        canon = canon or market

        # Extract the market-specific section from the report
        # Look for section header and take text until next section or end
        section_header_patterns = [
            re.escape(market),
            re.escape(canon) if canon != market else None,
        ]
        # Build regex to find the section
        section_text = report_text  # fallback: search full text
        for alias in (MARKET_ALIASES.get(canon, []) + [canon, market]):
            # Try to find a markdown section for this market
            m = re.search(
                rf'(?:##\s*[^\n]*{re.escape(alias)}[^\n]*\n)(.*?)(?=\n##\s|\Z)',
                report_text,
                re.IGNORECASE | re.DOTALL,
            )
            if m:
                section_text = m.group(1)
                break

        # Now extract fee values from section_text
        extracted: dict[str, tuple[int, str]] = {}  # field -> (value, source_snippet)
        for pattern, field in FEE_TYPE_PATTERNS:
            m = re.search(pattern, section_text, re.IGNORECASE)
            if m:
                groups = [g for g in m.groups() if g is not None]
                if len(groups) >= 2:
                    lo = _parse_currency_value(groups[0])
                    hi = _parse_currency_value(groups[1])
                    if lo and hi:
                        mid = (lo + hi) // 2
                        snippet = m.group(0)[:60].strip()
                        if field not in extracted:
                            extracted[field] = (mid, snippet)
                            found_any = True
                elif len(groups) == 1:
                    val = _parse_currency_value(groups[0])
                    if val:
                        snippet = m.group(0)[:60].strip()
                        if field not in extracted:
                            extracted[field] = (val, snippet)
                            found_any = True

        # If we only found a totalFee/rangeFee but no breakdown,
        # show it as a single "总费用" — do NOT fabricate a split.
        # The old 55/35/10 split was made-up data with zero basis.
        has_breakdown = "testingFee" in extracted or "certFee" in extracted or "annualFee" in extracted
        has_total = "totalFee" in extracted or "rangeFee" in extracted

        if has_breakdown:
            entry: dict = {"market": market}
            entry["testingFee"] = extracted.get("testingFee", (0, ""))[0]
            entry["certFee"] = extracted.get("certFee", (0, ""))[0]
            entry["annualFee"] = extracted.get("annualFee", (0, ""))[0]
            snippets = list({v[1] for v in extracted.values() if v[1]})
            entry["source"] = snippets[0] if snippets else "报告原文"
            result.append(entry)
            found_any = True
        elif has_total:
            # Only show the total fee — no fake breakdown
            fee_key = "totalFee" if "totalFee" in extracted else "rangeFee"
            total_val, snippet = extracted[fee_key]
            entry = {
                "market": market,
                "totalFee": total_val,
                "testingFee": 0,
                "certFee": 0,
                "annualFee": 0,
                "source": snippet,
                "isTotal": True,  # flag for frontend to display differently
            }
            result.append(entry)
            found_any = True

    return result if (result and found_any) else None


def _weeks_from_text(text: str) -> int | None:
    """Extract a week duration from text like '3-5周', '约4周', '6 weeks', '2个月' etc.
    
    Handles all Unicode dash variants: - – — ~ ～ 至 到
    """
    # Normalize all dash-like characters to ASCII hyphen for simpler matching
    normalized = text
    for ch in ['–', '—', '～', '~', '至', '到']:
        normalized = normalized.replace(ch, '-')
    
    # 月 → multiply by 4
    m = re.search(r'(\d+)\s*-\s*(\d+)\s*(?:个?月|months?)', normalized, re.IGNORECASE)
    if m:
        return int((int(m.group(1)) + int(m.group(2))) / 2 * 4)
    m = re.search(r'(\d+)\s*(?:个?月|months?)', normalized, re.IGNORECASE)
    if m:
        return int(int(m.group(1)) * 4)
    # 周 / weeks
    m = re.search(r'(\d+)\s*-\s*(\d+)\s*(?:周|weeks?)', normalized, re.IGNORECASE)
    if m:
        return int((int(m.group(1)) + int(m.group(2))) / 2)
    m = re.search(r'(\d+)\s*(?:周|weeks?)', normalized, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _extract_timeline_data(report_text: str, markets: list[str]) -> list[dict] | None:
    """
    Extract certification timeline data directly from report text.
    Returns list of {name, market, start, duration, color, source} or None if no data found.

    NO hardcoded timeline templates. If a market's timeline can't be parsed from the report,
    it is simply omitted. Returns None if nothing could be extracted.
    """
    MARKET_COLORS: dict[str, str] = {
        "欧盟": "#3b82f6",
        "美国": "#10a37f",
        "中国": "#f59e0b",
        "日本": "#6366f1",
        "韩国": "#8b5cf6",
        "英国": "#06b6d4",
        "澳大利亚": "#ef4444",
        "巴西": "#22c55e",
        "印度": "#f97316",
        "东南亚": "#ec4899",
    }

    MARKET_ALIASES: dict[str, list[str]] = {
        "欧盟": ["eu", "europe", "欧盟", "ce"],
        "美国": ["us", "usa", "fcc", "美国"],
        "中国": ["cn", "china", "中国", "ccc", "3c"],
        "日本": ["jp", "japan", "日本", "pse"],
        "韩国": ["kr", "korea", "韩国", "kc"],
        "英国": ["uk", "英国", "ukca"],
        "澳大利亚": ["au", "australia", "澳大利亚"],
        "巴西": ["br", "brazil", "巴西"],
        "印度": ["in", "india", "印度"],
        "东南亚": ["sea", "asean", "东南亚"],
    }

    # Certification phase name patterns to look for in each market section
    PHASE_PATTERNS = [
        # e.g. "预测试：3–4周" / "预测试 约3周"
        (r'(?:预测试|pre[\-\s]?test)[^\n]{0,60}', "预测试"),
        (r'(?:正式测试|授权测试|型式试验|EMC测试|安全测试|full[\s\-]?test|type[\s\-]?test)[^\n]{0,60}', "正式测试"),
        (r'(?:申请|认证申请|证书申请|application|申报)[^\n]{0,60}', "认证申请"),
        (r'(?:审批|审核|证书审批|review|审查)[^\n]{0,60}', "证书审批"),
        (r'(?:工厂检查|factory inspection|现场审查)[^\n]{0,60}', "工厂检查"),
        (r'(?:准备技术文件|技术文件|technical documentation|文件准备)[^\n]{0,60}', "技术文件准备"),
        (r'(?:签发|DoC|合格声明|declaration)[^\n]{0,60}', "签发DoC"),
        # Generic phase: "认证周期：X周" line
        (r'(?:预估周期|认证周期|总周期|合计)[^\n]{0,60}', "认证总周期"),
    ]

    DEFAULT_COLOR = "#52525b"
    result = []
    found_any = False

    for market in markets:
        canon = None
        for key, aliases in MARKET_ALIASES.items():
            if market == key or market.lower() in aliases or any(a in market.lower() for a in aliases):
                canon = key
                break
        canon = canon or market
        color = MARKET_COLORS.get(canon, DEFAULT_COLOR)

        # Extract market section
        # Strip emoji flags from headers before matching (they break regex)
        _clean_report = report_text
        for flag in ['🇺🇸', '🇪🇺', '🇨🇳', '🇯🇵', '🇰🇷', '🇬🇧', '🇦🇺', '🇧🇷', '🇮🇳', '🇩🇪', '🇫🇷',
                      '🇮🇹', '🇪🇸', '🇷🇺', '🇹🇼', '🇭🇰', '🇸🇬', '🇲🇾', '🇹🇭', '🇻🇳', '🇮🇩', '🇵🇭']:
            _clean_report = _clean_report.replace(flag, '')
        
        section_text = report_text
        for alias in (MARKET_ALIASES.get(canon, []) + [canon, market]):
            # Try on cleaned text first (no emoji), then on original
            for text_to_search in [_clean_report, report_text]:
                m = re.search(
                    rf'(?:##\s*[^\n]*{re.escape(alias)}[^\n]*\n)(.*?)(?=\n##\s|\Z)',
                    text_to_search,
                    re.IGNORECASE | re.DOTALL,
                )
                if m:
                    section_text = m.group(1)
                    break
            if section_text != report_text:
                break

        # Find the "预估周期" field row in a markdown table or bullet list
        # Pattern: | 预估周期 | 6–10周 |  or  - 预估周期：6–10周
        timeline_rows: list[tuple[str, int]] = []  # (phase_name, duration_weeks)

        # First try: look for table row with 预估周期
        m = re.search(
            r'预估周期[^\n|]{0,10}[|\s]+([\d\s\-–~～~至到个月周weeks]+)',
            section_text,
            re.IGNORECASE,
        )
        if m:
            dur = _weeks_from_text(m.group(1))
            if dur:
                cert_name = canon
                # Try to get certification name from context
                cert_m = re.search(r'###\s*([^\n]+)', section_text)
                if cert_m:
                    cert_name = cert_m.group(1).strip()
                timeline_rows.append((cert_name, dur))
                found_any = True

        # Second try: look for each phase pattern
        # Collect specific phases and total separately
        specific_phases: list[tuple[str, int]] = []
        total_phase: tuple[str, int] | None = None
        
        for pat, phase_name in PHASE_PATTERNS:
            m = re.search(pat, section_text, re.IGNORECASE)
            if m:
                snippet = m.group(0)
                dur = _weeks_from_text(snippet)
                if dur:
                    cert_prefix = ""
                    cert_m = re.search(r'###\s*([^\n]+)', section_text)
                    if cert_m:
                        label = cert_m.group(1).strip()
                        cert_prefix = label.split()[0] + " — " if label.split() else ""
                    label = f"{cert_prefix}{phase_name}"
                    
                    if phase_name == "认证总周期":
                        total_phase = (label, dur)
                    else:
                        specific_phases.append((label, dur))
                    found_any = True
        
        # Only use total_phase if no specific phases were found (avoid double-counting)
        if specific_phases:
            timeline_rows.extend(specific_phases)
        elif total_phase:
            timeline_rows.append(total_phase)

        # Build Gantt phases from extracted rows
        if timeline_rows:
            cursor = 0
            for phase_label, dur in timeline_rows[:6]:  # cap at 6 phases per market
                result.append({
                    "name": phase_label,
                    "market": market,
                    "start": cursor,
                    "duration": dur,
                    "color": color,
                    "source": f"数据来源：报告中{market}认证预估周期",
                })
                cursor += dur

    return result if (result and found_any) else None


def extract_report_data(report_text: str, product: str, markets: list[str]) -> dict:
    """
    Parse report text and extract structured chart data.
    Returns dict with keys: radar, costs, timeline.
    Each may be None/[] to signal "insufficient data".
    """
    radar = _extract_radar_scores(report_text)
    costs = _extract_cost_data(report_text, markets)
    timeline = _extract_timeline_data(report_text, markets)

    return {
        "radar": radar,          # list[dict] or []
        "costs": costs,           # list[dict] or None
        "timeline": timeline,     # list[dict] or None
    }

# ────────────────────────────────────────────────────────────────────────────
# App setup
# ────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="TIC-Agent API",
    description="TIC compliance analysis API with SSE streaming",
    version="1.0.0",
)

# CORS — allow Next.js dev server and Vercel deployments
_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# Add extra origins from environment variable (comma-separated)
_extra = os.getenv("CORS_ORIGINS", "")
if _extra:
    _CORS_ORIGINS.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ────────────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    product: str
    markets: list[str]
    extra_info: str = ""


class FollowUpRequest(BaseModel):
    messages: list[dict]
    question: str


class ExportPDFRequest(BaseModel):
    report_text: str
    product: str
    markets: list[str]


# ────────────────────────────────────────────────────────────────────────────
# SSE helpers
# ────────────────────────────────────────────────────────────────────────────

STATUS_INDICATORS = ("🔎", "📄", "✅", "⚠️", "❌", "🔍", "🌍", "---")


def _classify_chunk(text: str) -> tuple[str, str]:
    """
    Classify a yielded chunk from run_agent_stream() into an SSE event type.

    Returns (event_name, data_payload).
    - __VIZ__:{json}  → ("viz",  json_string)
    - status line     → ("status", text)
    - other text      → ("chunk", text)
    """
    stripped = text.strip()

    # VIZ protocol line
    if stripped.startswith("__VIZ__:"):
        json_part = stripped[len("__VIZ__:"):]
        try:
            # Validate it's real JSON
            json.loads(json_part)
            return "viz", json_part
        except json.JSONDecodeError:
            # Malformed VIZ line — pass through as chunk
            return "chunk", text

    # Status indicator line (contains emoji status markers)
    for indicator in STATUS_INDICATORS:
        if indicator in text:
            return "status", text

    # Regular report text chunk
    return "chunk", text


def _sync_gen_to_async(sync_gen):
    """
    Wrap a synchronous generator to be iterable in an async context
    without blocking the event loop (runs in thread executor).
    """
    loop = asyncio.get_event_loop()
    gen_iter = iter(sync_gen)

    async def _next():
        return await loop.run_in_executor(None, lambda: next(gen_iter, _SENTINEL))

    return _next


_SENTINEL = object()  # signals StopIteration from executor


# ────────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────────

# ── 1. POST /api/analyze ────────────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest, request: Request):
    """
    Run compliance analysis and stream results as Server-Sent Events.

    Events:
      status  — search/progress status lines
      viz     — VIZ protocol JSON payloads (search graphs, funnel, cross-validation)
      chunk   — report text fragments
      done    — analysis complete; data = full report text
      error   — error message
    """

    async def event_generator() -> AsyncGenerator:
        full_report_parts: list[str] = []
        in_report = False  # Once report starts, everything is chunk
        # Read API keys from request headers (frontend settings)
        # If no header → empty string → agent uses its default client (Vertex proxy)
        google_key = request.headers.get("x-google-ai-key", "")
        brave_key = request.headers.get("x-brave-api-key") or os.environ.get("BRAVE_API_KEY") or ""
        get_next = _sync_gen_to_async(
            run_agent_stream(req.product, req.markets, req.extra_info, api_key=google_key, brave_api_key=brave_key)
        )

        try:
            while True:
                chunk = await get_next()
                if chunk is _SENTINEL:
                    break

                # Detect report start — after this, all non-VIZ content is report
                stripped = chunk.strip()
                if stripped.startswith("# 合规检查报告") or stripped.startswith("# 合规"):
                    in_report = True

                if in_report and not stripped.startswith("__VIZ__:"):
                    event, data = "chunk", chunk
                else:
                    event, data = _classify_chunk(chunk)

                # Accumulate report text
                if event == "chunk":
                    full_report_parts.append(chunk)

                yield {"event": event, "data": data}

            # Send done event with complete report text + extracted chart data
            full_report = "".join(full_report_parts)
            charts = extract_report_data(full_report, req.product, req.markets)
            yield {
                "event": "done",
                "data": json.dumps(
                    {"report": full_report, "charts": charts},
                    ensure_ascii=False,
                ),
            }

        except Exception as exc:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(exc)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


# ── 2. POST /api/followup ───────────────────────────────────────────────────

@app.post("/api/followup")
async def followup(req: FollowUpRequest, request: Request):
    """
    Answer a follow-up question based on existing conversation context.

    Events:
      chunk  — text fragment
      done   — streaming complete
      error  — error message
    """

    async def event_generator() -> AsyncGenerator:
        google_key = request.headers.get("x-google-ai-key", "")
        get_next = _sync_gen_to_async(
            follow_up_stream(req.messages, req.question, api_key=google_key)
        )

        try:
            while True:
                chunk = await get_next()
                if chunk is _SENTINEL:
                    break
                yield {"event": "chunk", "data": chunk}

            yield {"event": "done", "data": ""}

        except Exception as exc:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(exc)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


# ── 3. GET /api/knowledge ───────────────────────────────────────────────────

@app.get("/api/knowledge")
async def knowledge(
    product: str = Query(..., description="Product description"),
    markets: str = Query("", description="Comma-separated market codes, e.g. EU,US,CN"),
):
    """
    Query the built-in knowledge base for a product + market combination.

    Returns structured regulation data from the local KB (no network calls).
    """
    market_list = [m.strip() for m in markets.split(",") if m.strip()] if markets else []

    try:
        result = get_regulations_for_product(product, market_list)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "regulations": result.get("regulations", []),
        "category": result.get("category_label", result.get("category")),
        "category_key": result.get("category"),
        "category_icon": result.get("category_icon", "📦"),
        "markets": result.get("markets", []),
    }


# ── 4. POST /api/export-pdf ─────────────────────────────────────────────────

@app.post("/api/export-pdf")
async def export_pdf(req: ExportPDFRequest):
    """
    Generate a PDF from the provided report text and return it as a download.
    """
    if not req.report_text.strip():
        raise HTTPException(status_code=400, detail="report_text cannot be empty")
    if not req.product.strip():
        raise HTTPException(status_code=400, detail="product cannot be empty")

    try:
        # generate_pdf is CPU-bound; run in thread executor to avoid blocking
        loop = asyncio.get_event_loop()
        pdf_path = await loop.run_in_executor(
            None,
            lambda: generate_pdf(req.report_text, req.product, req.markets),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(exc)}")

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF file was not created")

    filename = os.path.basename(pdf_path)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── 5. GET /api/health ──────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "model": MODEL}


@app.get("/health")
async def health_root():
    """Root health check (used by Railway/Render)."""
    return {"status": "ok"}


# ────────────────────────────────────────────────────────────────────────────
# Serve Next.js static export (for tunnel / single-origin deployment)
# ────────────────────────────────────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse as StarletteFileResponse

_STATIC_DIR = os.path.join(_PARENT_DIR, "frontend", "out")

if os.path.isdir(_STATIC_DIR):
    # Serve static assets (JS/CSS/images) under /_next etc.
    app.mount("/_next", StaticFiles(directory=os.path.join(_STATIC_DIR, "_next")), name="next-static")

    # Catch-all: serve index.html for any non-API route (SPA fallback)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Try to serve the exact file first
        file_path = os.path.join(_STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return StarletteFileResponse(file_path)
        # Fallback to index.html
        index = os.path.join(_STATIC_DIR, "index.html")
        if os.path.isfile(index):
            return StarletteFileResponse(index)
        raise HTTPException(404, "Not found")


# ────────────────────────────────────────────────────────────────────────────
# Dev entry point
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
