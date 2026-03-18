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
    Extract compliance radar scores from report text.
    Returns list of {subject, score, fullMark, reason} dicts, or [] if insufficient data.
    """
    text = report_text.lower()

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

    DIMENSION_REASONS: dict[str, str] = {
        "电气安全": "根据报告中涉及的电气安全标准数量评估",
        "EMC": "根据报告中电磁兼容相关法规覆盖度评估",
        "化学物质": "根据报告中RoHS/REACH等化学品法规覆盖度评估",
        "标签要求": "根据报告中标签标识要求完整度评估",
        "环保法规": "根据报告中能效与环保法规覆盖度评估",
        "认证要求": "根据报告中认证流程描述完整度评估",
    }

    results = []
    total_hits = 0
    for subject, keywords in DIMENSION_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        total_hits += hits
        raw = min(hits / 8, 1.0)
        score = round(45 + raw * 50)
        results.append({
            "subject": subject,
            "score": score,
            "fullMark": 100,
            "reason": DIMENSION_REASONS[subject],
        })

    # If no hits at all, return empty to signal "insufficient data"
    if total_hits == 0:
        return []
    return results


def _extract_cost_data(report_text: str, markets: list[str]) -> list[dict] | None:
    """
    Extract cost estimates from report text.
    Returns list of {market, testingFee, certFee, annualFee} or None if no cost data found.
    """
    # Look for cost/fee mentions with numbers
    cost_patterns = [
        r'(\d[\d,，.]+)\s*(?:美元|USD|\$|万元|元|CNY)',
        r'(?:费用|成本|测试费|认证费|年费)[^\d]{0,20}(\d[\d,，.]+)',
        r'(?:USD|￥|\$)\s*(\d[\d,，.]+)',
        r'(\d+)\s*[~-]\s*(\d+)\s*(?:万|千|美元|USD)',
    ]

    has_cost_data = False
    for pattern in cost_patterns:
        if re.search(pattern, report_text, re.IGNORECASE):
            has_cost_data = True
            break

    if not has_cost_data:
        return None

    # Try to extract market-specific costs from report text
    # Look for patterns like "EU: $X,XXX" or "欧盟 $X,XXX"
    MARKET_ALIASES: dict[str, list[str]] = {
        "欧盟": ["eu", "europe", "欧盟", "ce认证"],
        "美国": ["us", "usa", "fcc", "美国", "北美"],
        "中国": ["cn", "china", "中国", "ccc"],
        "日本": ["jp", "japan", "日本", "pse"],
        "韩国": ["kr", "korea", "韩国", "kc"],
        "英国": ["uk", "ukca", "英国"],
        "澳大利亚": ["au", "australia", "澳大利亚"],
        "巴西": ["br", "brazil", "巴西", "anatel"],
        "印度": ["in", "india", "印度", "bis"],
        "东南亚": ["sea", "asean", "东南亚"],
    }

    # Reference cost database (used only when cost data IS mentioned in report)
    COST_DB: dict[str, dict] = {
        "欧盟": {"testingFee": 8000, "certFee": 5000, "annualFee": 2000},
        "美国": {"testingFee": 12000, "certFee": 8000, "annualFee": 3000},
        "中国": {"testingFee": 15000, "certFee": 10000, "annualFee": 5000},
        "日本": {"testingFee": 10000, "certFee": 7000, "annualFee": 2500},
        "韩国": {"testingFee": 8000, "certFee": 6000, "annualFee": 2000},
        "英国": {"testingFee": 7000, "certFee": 4500, "annualFee": 1800},
        "澳大利亚": {"testingFee": 9000, "certFee": 6000, "annualFee": 2200},
        "巴西": {"testingFee": 11000, "certFee": 8000, "annualFee": 3500},
        "印度": {"testingFee": 7000, "certFee": 5000, "annualFee": 1500},
        "东南亚": {"testingFee": 6000, "certFee": 4000, "annualFee": 1200},
    }

    DEFAULT_COST = {"testingFee": 8000, "certFee": 5000, "annualFee": 2000}

    result = []
    text_lower = report_text.lower()
    for market in markets:
        # Find matching key in COST_DB
        cost_key = None
        for key, aliases in MARKET_ALIASES.items():
            if market == key or market.lower() in aliases or any(a in market.lower() for a in aliases):
                cost_key = key
                break
        costs = COST_DB.get(cost_key or "", DEFAULT_COST) if cost_key else DEFAULT_COST
        result.append({"market": market, **costs})

    return result if result else None


def _extract_timeline_data(report_text: str, markets: list[str]) -> list[dict] | None:
    """
    Extract certification timeline data from report text.
    Returns list of {name, market, start, duration, color} or None if no timeline data found.
    """
    # Look for timeline / week / month mentions
    timeline_patterns = [
        r'(\d+)\s*(?:个?月|months?)',
        r'(\d+)\s*(?:周|weeks?)',
        r'(?:周期|时间|timeline|duration)[^\d]{0,30}(\d+)',
        r'认证.*?(\d+).*?(?:月|周|week|month)',
    ]

    has_timeline_data = False
    for pattern in timeline_patterns:
        if re.search(pattern, report_text, re.IGNORECASE):
            has_timeline_data = True
            break

    if not has_timeline_data:
        return None

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

    TIMELINE_DB: dict[str, list[dict]] = {
        "欧盟": [
            {"name": "CE — 准备技术文件", "start": 0, "duration": 4},
            {"name": "CE — EMC测试", "start": 4, "duration": 4},
            {"name": "CE — 安全测试", "start": 4, "duration": 6},
            {"name": "CE — 签发DoC", "start": 10, "duration": 2},
        ],
        "美国": [
            {"name": "FCC — 预测试", "start": 0, "duration": 3},
            {"name": "FCC — 授权测试", "start": 3, "duration": 6},
            {"name": "FCC — 申请认证", "start": 9, "duration": 4},
        ],
        "中国": [
            {"name": "CCC — 工厂检查", "start": 0, "duration": 4},
            {"name": "CCC — 型式试验", "start": 4, "duration": 8},
            {"name": "CCC — 证书审批", "start": 12, "duration": 4},
        ],
        "日本": [
            {"name": "PSE — 测试申请", "start": 0, "duration": 2},
            {"name": "PSE — 型式试验", "start": 2, "duration": 8},
            {"name": "PSE — 认证发放", "start": 10, "duration": 3},
        ],
        "韩国": [
            {"name": "KC — 测试", "start": 0, "duration": 6},
            {"name": "KC — 认证申请", "start": 6, "duration": 4},
        ],
        "英国": [
            {"name": "UKCA — 文件准备", "start": 0, "duration": 3},
            {"name": "UKCA — 测试", "start": 3, "duration": 5},
            {"name": "UKCA — 声明签发", "start": 8, "duration": 2},
        ],
    }

    DEFAULT_PHASES = [
        {"name": "测试准备", "start": 0, "duration": 4},
        {"name": "正式测试", "start": 4, "duration": 6},
        {"name": "认证申请", "start": 10, "duration": 4},
    ]

    MARKET_ALIASES: dict[str, list[str]] = {
        "欧盟": ["eu", "europe", "欧盟"],
        "美国": ["us", "usa", "fcc", "美国"],
        "中国": ["cn", "china", "中国"],
        "日本": ["jp", "japan", "日本"],
        "韩国": ["kr", "korea", "韩国"],
        "英国": ["uk", "英国"],
        "澳大利亚": ["au", "australia", "澳大利亚"],
        "巴西": ["br", "brazil", "巴西"],
        "印度": ["in", "india", "印度"],
        "东南亚": ["sea", "asean", "东南亚"],
    }

    DEFAULT_COLOR = "#52525b"
    result = []
    for market in markets:
        db_key = None
        for key, aliases in MARKET_ALIASES.items():
            if market == key or market.lower() in aliases or any(a in market.lower() for a in aliases):
                db_key = key
                break
        phases = TIMELINE_DB.get(db_key or "", DEFAULT_PHASES)
        color = MARKET_COLORS.get(db_key or market, DEFAULT_COLOR)
        for phase in phases:
            result.append({
                "name": phase["name"],
                "market": market,
                "start": phase["start"],
                "duration": phase["duration"],
                "color": color,
            })

    return result if result else None


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
