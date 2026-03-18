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
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# ── Project imports ─────────────────────────────────────────────────────────
from agent import run_agent_stream, follow_up_stream, MODEL
from knowledge_base import get_regulations_for_product
from export_pdf import generate_pdf

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
async def analyze(req: AnalyzeRequest):
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
        get_next = _sync_gen_to_async(
            run_agent_stream(req.product, req.markets, req.extra_info)
        )

        try:
            while True:
                chunk = await get_next()
                if chunk is _SENTINEL:
                    break

                event, data = _classify_chunk(chunk)

                # Accumulate non-viz, non-status text into full report
                if event == "chunk":
                    full_report_parts.append(chunk)

                yield {"event": event, "data": data}

            # Send done event with complete report text
            full_report = "".join(full_report_parts)
            yield {
                "event": "done",
                "data": json.dumps({"report": full_report}, ensure_ascii=False),
            }

        except Exception as exc:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(exc)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


# ── 2. POST /api/followup ───────────────────────────────────────────────────

@app.post("/api/followup")
async def followup(req: FollowUpRequest):
    """
    Answer a follow-up question based on existing conversation context.

    Events:
      chunk  — text fragment
      done   — streaming complete
      error  — error message
    """

    async def event_generator() -> AsyncGenerator:
        get_next = _sync_gen_to_async(
            follow_up_stream(req.messages, req.question)
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
# Dev entry point
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
