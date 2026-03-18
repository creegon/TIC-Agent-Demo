# app.py - Gradio frontend for TIC Compliance Agent
# Usage: python app.py

import json
from datetime import datetime
import gradio as gr
from agent import run_agent_stream, follow_up_stream
from charts import generate_charts_html, PLACEHOLDER_HTML
from knowledge_base import build_kb_recommendation_html
from export_pdf import generate_pdf

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — Enterprise SaaS Dashboard (Deep Navy + Amber Gold)
# ─────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* ══════════════════════════════════════════════════
   DESIGN TOKENS
══════════════════════════════════════════════════ */
:root {
    --primary:        #1a3a5c;   /* Deep navy — brand anchor */
    --primary-mid:    #1e4976;   /* Mid navy */
    --primary-light:  #2563a8;   /* Bright blue — hover */
    --accent:         #d4830a;   /* Amber gold — CTA & highlights */
    --accent-light:   #e8a838;   /* Soft gold */
    --accent-pale:    #fef3dc;   /* Gold tint background */
    --bg:             #f0f4f8;   /* Page background */
    --surface:        #ffffff;   /* Card surface */
    --surface-2:      #f7f9fc;   /* Secondary surface */
    --border:         #dce3ec;   /* Subtle border */
    --border-strong:  #b8c8dc;   /* Stronger border */
    --text:           #1e2d3d;   /* Primary text */
    --text-muted:     #60748a;   /* Muted text */
    --text-light:     #8fa4bb;   /* Light label text */
    --danger:         #c0392b;
    --success:        #0f7a60;
    --info:           #1d6fa4;
    --radius-sm:      4px;
    --radius:         8px;
    --radius-lg:      12px;
    --shadow-sm:      0 1px 3px rgba(0,0,0,0.07);
    --shadow:         0 2px 8px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
    --shadow-hover:   0 6px 20px rgba(26,58,92,0.15), 0 0 0 1px rgba(26,58,92,0.08);
    --transition:     all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ══════════════════════════════════════════════════
   GLOBAL RESET & BASE
══════════════════════════════════════════════════ */
body, .gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter',
                 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    font-size: 14px;
}
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
}
footer { display: none !important; }

/* ══════════════════════════════════════════════════
   TOP NAVIGATION BAR
══════════════════════════════════════════════════ */
.tic-navbar {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-mid) 100%);
    border-bottom: 3px solid var(--accent);
    padding: 0 32px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 16px rgba(26,58,92,0.3);
}
.tic-navbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.tic-navbar-logo {
    font-size: 1.5rem;
    line-height: 1;
}
.tic-navbar-brand {
    display: flex;
    flex-direction: column;
    gap: 1px;
}
.tic-navbar-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.02em;
    line-height: 1.2;
}
.tic-navbar-subtitle {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.6);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.tic-navbar-divider {
    width: 1px;
    height: 28px;
    background: rgba(255,255,255,0.2);
    margin: 0 4px;
}
.tic-badge-demo {
    background: var(--accent);
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.tic-navbar-right {
    display: flex;
    align-items: center;
    gap: 20px;
}
.tic-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.25);
    animation: pulse-dot 2.5s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 0 2px rgba(34,197,94,0.25); }
    50%       { box-shadow: 0 0 0 5px rgba(34,197,94,0.1); }
}
.tic-status-label {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    gap: 7px;
}
.tic-nav-links {
    display: flex;
    gap: 24px;
}
.tic-nav-link {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.65);
    text-decoration: none;
    letter-spacing: 0.04em;
    transition: var(--transition);
    cursor: default;
}
.tic-nav-link:hover { color: rgba(255,255,255,0.95); }

/* ══════════════════════════════════════════════════
   PAGE WRAPPER & HERO BAND
══════════════════════════════════════════════════ */
.tic-hero {
    background: linear-gradient(180deg, #1a3a5c 0%, #203d5a 60%, #f0f4f8 100%);
    padding: 28px 32px 48px;
    color: white;
}
.tic-hero-inner {
    max-width: 1200px;
    margin: 0 auto;
}
.tic-hero-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent-light);
    font-weight: 600;
    margin-bottom: 8px;
}
.tic-hero-headline {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 8px;
    line-height: 1.25;
}
.tic-hero-desc {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.65);
    max-width: 520px;
    line-height: 1.6;
}

/* ══════════════════════════════════════════════════
   MAIN CONTENT AREA
══════════════════════════════════════════════════ */
.tic-main {
    max-width: 1200px;
    margin: -24px auto 0;
    padding: 0 32px 40px;
}

/* ══════════════════════════════════════════════════
   CARD BASE
══════════════════════════════════════════════════ */
.tic-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
    transition: var(--transition);
}
.tic-card:hover {
    box-shadow: var(--shadow-hover);
}
.tic-card-header {
    background: linear-gradient(90deg, var(--surface-2) 0%, var(--surface) 100%);
    border-bottom: 1px solid var(--border);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.tic-card-icon {
    font-size: 1rem;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-pale);
    border-radius: var(--radius-sm);
    flex-shrink: 0;
}
.tic-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.tic-card-body {
    padding: 20px;
}

/* ══════════════════════════════════════════════════
   FIELD SECTIONS INSIDE CARD
══════════════════════════════════════════════════ */
.field-label {
    font-size: 0.73rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 5px;
}
.field-label .req {
    color: var(--accent);
    font-size: 0.9em;
}
.field-divider {
    height: 1px;
    background: var(--border);
    margin: 18px 0;
}

/* ══════════════════════════════════════════════════
   INPUT FIELD OVERRIDES
══════════════════════════════════════════════════ */
.gradio-container input[type="text"],
.gradio-container textarea,
.gradio-container select {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--surface-2) !important;
    color: var(--text) !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
    padding: 10px 12px !important;
}
.gradio-container input[type="text"]:focus,
.gradio-container textarea:focus {
    border-color: var(--primary-light) !important;
    background: var(--surface) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 168, 0.12) !important;
}
.gradio-container input[type="text"]::placeholder,
.gradio-container textarea::placeholder {
    color: var(--text-light) !important;
    font-style: italic;
}

/* Gradio label text above inputs */
.gradio-container .block label > span:first-child {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

/* ══════════════════════════════════════════════════
   CHECKBOX GROUP (MARKET SELECTOR)
══════════════════════════════════════════════════ */
.gradio-container .wrap {
    gap: 8px !important;
    flex-wrap: wrap !important;
}
.gradio-container .wrap label {
    border: 1.5px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 6px 16px !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    background: var(--surface-2) !important;
    color: var(--text-muted) !important;
    user-select: none;
}
.gradio-container .wrap label:hover {
    border-color: var(--accent) !important;
    background: var(--accent-pale) !important;
    color: var(--accent) !important;
}
.gradio-container .wrap label.selected,
.gradio-container .wrap input[type="checkbox"]:checked + span {
    border-color: var(--primary) !important;
    background: var(--primary) !important;
    color: white !important;
}

/* ══════════════════════════════════════════════════
   EXAMPLE CARDS GRID
══════════════════════════════════════════════════ */
.examples-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 4px;
}
.example-card-btn {
    background: var(--surface-2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 12px 14px !important;
    text-align: left !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
    color: var(--text) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    line-height: 1.35 !important;
    display: block !important;
    width: 100% !important;
    position: relative;
    overflow: hidden;
}
.example-card-btn::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: var(--accent);
    opacity: 0;
    transition: opacity 0.2s;
}
.example-card-btn:hover {
    border-color: var(--primary-light) !important;
    background: #f0f6ff !important;
    box-shadow: var(--shadow-hover) !important;
    transform: translateY(-1px);
    color: var(--primary) !important;
}
.example-card-btn:hover::before {
    opacity: 1;
}
.example-card-btn:active {
    transform: translateY(0) scale(0.99);
}
.ex-title {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--primary);
    margin-bottom: 3px;
}
.ex-meta {
    font-size: 0.74rem;
    color: var(--text-muted);
    font-weight: 400;
}

/* ══════════════════════════════════════════════════
   ACTION BUTTONS
══════════════════════════════════════════════════ */
.gradio-container button.primary,
.gradio-container .gr-button-primary {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%) !important;
    border: none !important;
    color: #fff !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    padding: 11px 20px !important;
    transition: var(--transition) !important;
    box-shadow: 0 2px 8px rgba(212, 131, 10, 0.35) !important;
    position: relative;
    overflow: hidden;
}
.gradio-container button.primary::after {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(255,255,255,0);
    transition: background 0.15s;
}
.gradio-container button.primary:hover {
    background: linear-gradient(135deg, #c07508 0%, var(--accent) 100%) !important;
    box-shadow: 0 4px 16px rgba(212, 131, 10, 0.45) !important;
    transform: translateY(-1px) !important;
}
.gradio-container button.primary:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: 0 1px 4px rgba(212, 131, 10, 0.3) !important;
}

.gradio-container button.secondary {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: var(--transition) !important;
}
.gradio-container button.secondary:hover {
    border-color: var(--border-strong) !important;
    color: var(--text) !important;
    background: var(--surface-2) !important;
}
.gradio-container button.secondary:active {
    transform: scale(0.98) !important;
}

/* ══════════════════════════════════════════════════
   INFO / TIP BOX
══════════════════════════════════════════════════ */
.tic-tip {
    background: linear-gradient(135deg, #f0f7ff 0%, #e8f3fe 100%);
    border: 1px solid #c3d8ef;
    border-left: 4px solid var(--primary-light);
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #1a3355;
    line-height: 1.65;
    margin-top: 4px;
}
.tic-tip strong { color: var(--primary); }

/* ══════════════════════════════════════════════════
   OUTPUT PANEL — SPLIT LAYOUT
══════════════════════════════════════════════════ */
.output-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    gap: 0;
}

/* Search status mini-bar */
.tic-status-band {
    background: linear-gradient(90deg, var(--primary) 0%, #22405e 100%);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid var(--accent);
}
.tic-status-band-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: rgba(255,255,255,0.6);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.tic-status-band-live {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.75);
}
.tic-live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent-light);
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.2; }
}
.tic-progress-bar {
    height: 2px;
    background: rgba(255,255,255,0.1);
    border-radius: 1px;
    overflow: hidden;
    margin-top: 8px;
}
.tic-progress-fill {
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, var(--accent), var(--accent-light));
    border-radius: 1px;
    animation: progress-sweep 2.2s ease-in-out infinite;
}
@keyframes progress-sweep {
    0%   { transform: translateX(-100%); width: 45%; }
    100% { transform: translateX(280%); width: 45%; }
}

/* Report body card */
.tic-report-area {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    box-shadow: var(--shadow);
    flex: 1;
    overflow: hidden;
}

/* ══════════════════════════════════════════════════
   SEARCH VISUALIZATION PANEL
══════════════════════════════════════════════════ */
.tic-viz-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
    overflow: hidden;
}
.tic-viz-header {
    background: linear-gradient(90deg, #1a3a5c 0%, #22405e 100%);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid var(--accent);
}
.tic-viz-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: rgba(255,255,255,0.8);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.tic-viz-body {
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}

/* ── Keyword tags (search rounds) ── */
.tic-kw-section {}
.tic-kw-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.tic-kw-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.tic-kw-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px 3px 8px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 500;
    white-space: nowrap;
    max-width: 260px;
    overflow: hidden;
    text-overflow: ellipsis;
    border: 1px solid transparent;
}
/* Round colours — 8 variants cycling */
.tic-kw-r1 { background:#e8f3fe; color:#1a4a7a; border-color:#c3d8ef; }
.tic-kw-r2 { background:#fef3dc; color:#7a4a00; border-color:#f0d090; }
.tic-kw-r3 { background:#e8f8ef; color:#0f5a3a; border-color:#a8dfc0; }
.tic-kw-r4 { background:#f5eafe; color:#5a1a7a; border-color:#d8b8f0; }
.tic-kw-r5 { background:#fff0e8; color:#7a3010; border-color:#f0c8a0; }
.tic-kw-r6 { background:#e8fafc; color:#0a4a5a; border-color:#a0dce8; }
.tic-kw-r7 { background:#fce8e8; color:#7a1010; border-color:#f0b8b8; }
.tic-kw-r8 { background:#f0f8e8; color:#2a5a0a; border-color:#b8e0a0; }
.tic-kw-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    font-size: 0.6rem;
    font-weight: 700;
    background: rgba(0,0,0,0.12);
    flex-shrink: 0;
}

/* ── Source credibility chips ── */
.tic-src-section {}
.tic-src-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.tic-src-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-height: 180px;
    overflow-y: auto;
}
.tic-src-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
    color: var(--text);
    line-height: 1.3;
}
.tic-src-badge {
    flex-shrink: 0;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    white-space: nowrap;
}
.tic-src-official { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.tic-src-standard { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.tic-src-tic      { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.tic-src-ref      { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.tic-src-domain {
    font-family: 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.73rem;
    color: var(--text-muted);
    flex-shrink: 0;
}
.tic-src-title {
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
}

/* ── Funnel stats ── */
.tic-funnel-section {}
.tic-funnel-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 10px;
}
.tic-funnel {
    display: flex;
    align-items: center;
    gap: 0;
    justify-content: flex-start;
}
.tic-funnel-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
}
.tic-funnel-box {
    background: var(--primary);
    color: white;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 1rem;
    font-weight: 700;
    min-width: 52px;
    text-align: center;
    line-height: 1;
}
.tic-funnel-box.step2 { background: var(--primary-mid); }
.tic-funnel-box.step3 { background: var(--accent); }
.tic-funnel-desc {
    font-size: 0.68rem;
    color: var(--text-muted);
    text-align: center;
    line-height: 1.3;
}
.tic-funnel-arrow {
    font-size: 1.1rem;
    color: var(--border-strong);
    padding: 0 6px;
    margin-top: -12px;
}

/* placeholder state */
.tic-viz-placeholder {
    padding: 20px 16px;
    text-align: center;
    color: var(--text-light);
    font-size: 0.82rem;
}

/* ══════════════════════════════════════════════════
   MARKDOWN OUTPUT STYLING
══════════════════════════════════════════════════ */
.output-area .prose,
.output-area .markdown-body,
.output-area [data-testid="markdown"] {
    font-size: 0.91rem !important;
    line-height: 1.75 !important;
    color: var(--text) !important;
    padding: 24px !important;
}

/* Headings in output */
.output-area h1, .output-area h2 {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--accent) !important;
    padding-bottom: 8px !important;
    margin-top: 24px !important;
    font-weight: 700 !important;
}
.output-area h3, .output-area h4 {
    color: var(--primary-mid) !important;
    font-weight: 600 !important;
    margin-top: 18px !important;
}

/* Tables */
.output-area table {
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 0.86rem !important;
    margin: 16px 0 !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}
.output-area th {
    background: var(--primary) !important;
    color: white !important;
    padding: 10px 14px !important;
    text-align: left !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
}
.output-area td {
    padding: 9px 14px !important;
    border-bottom: 1px solid var(--border) !important;
    vertical-align: top !important;
}
.output-area tr:nth-child(even) td {
    background: var(--surface-2) !important;
}
.output-area tr:hover td {
    background: #f0f6ff !important;
}

/* Code blocks */
.output-area code {
    background: #eef2f7 !important;
    padding: 2px 6px !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.84em !important;
    color: var(--primary) !important;
    font-family: 'Fira Code', 'Cascadia Code', monospace !important;
    border: 1px solid var(--border) !important;
}
.output-area pre {
    background: #f0f4f8 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 14px !important;
    overflow-x: auto !important;
}
.output-area pre code {
    border: none !important;
    padding: 0 !important;
    background: none !important;
}

/* Blockquotes */
.output-area blockquote {
    border-left: 4px solid var(--accent) !important;
    background: var(--accent-pale) !important;
    padding: 10px 16px !important;
    border-radius: 0 var(--radius) var(--radius) 0 !important;
    margin: 14px 0 !important;
    color: #5a3a00 !important;
}

/* Lists */
.output-area ul li, .output-area ol li {
    margin-bottom: 4px !important;
}

/* ══════════════════════════════════════════════════
   FOOTER BAR
══════════════════════════════════════════════════ */
.tic-footer {
    background: var(--primary);
    border-top: 3px solid var(--accent);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 32px;
}
.tic-footer-left {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}
.tic-tech-tag {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    font-weight: 600;
    color: rgba(255,255,255,0.8);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    transition: var(--transition);
}
.tic-tech-tag:hover {
    background: rgba(255,255,255,0.18);
    color: #fff;
}
.tic-footer-right {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.45);
    line-height: 1.5;
    text-align: right;
}

/* ══════════════════════════════════════════════════
   STATS ROW (mini KPI cards between hero and main)
══════════════════════════════════════════════════ */
.tic-stats-row {
    display: flex;
    gap: 12px;
    margin: 0 32px;
    margin-top: -16px;
    margin-bottom: 20px;
}
.tic-stat-card {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 18px;
    box-shadow: var(--shadow);
    display: flex;
    align-items: center;
    gap: 12px;
    transition: var(--transition);
}
.tic-stat-card:hover {
    box-shadow: var(--shadow-hover);
    border-color: var(--border-strong);
}
.tic-stat-icon {
    font-size: 1.3rem;
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-pale);
    border-radius: var(--radius-sm);
    flex-shrink: 0;
}
.tic-stat-info {}
.tic-stat-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1.1;
}
.tic-stat-desc {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 1px;
}

/* ══════════════════════════════════════════════════
   LOADING / STREAMING ANIMATION OVERLAY
══════════════════════════════════════════════════ */
.tic-analyzing {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 500;
}
.tic-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(212,131,10,0.25);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    flex-shrink: 0;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}

/* generating class used by Gradio during streaming */
.generating {
    color: var(--accent) !important;
    font-style: italic;
    animation: fade-pulse 1.6s ease-in-out infinite;
}
@keyframes fade-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.55; }
}

/* ══════════════════════════════════════════════════
   KNOWLEDGE BASE RECOMMENDATION PANEL
══════════════════════════════════════════════════ */
.kb-panel-wrap {
    margin-bottom: 16px;
}
.kb-detail {
    display: none;
}

/* ══════════════════════════════════════════════════
   RESPONSIVE ADJUSTMENTS
══════════════════════════════════════════════════ */
@media (max-width: 900px) {
    .tic-navbar  { padding: 0 16px; }
    .tic-hero    { padding: 20px 16px 40px; }
    .tic-main    { padding: 0 16px 32px; margin-top: -16px; }
    .tic-stats-row { margin: 0 16px; flex-wrap: wrap; margin-top: -12px; }
    .tic-stat-card { min-width: calc(50% - 6px); }
    .examples-grid { grid-template-columns: 1fr; }
    .tic-footer  { padding: 16px; flex-direction: column; align-items: flex-start; }
    .tic-footer-right { text-align: left; }
    .tic-nav-links { display: none; }
}
@media (max-width: 600px) {
    .tic-stat-card { min-width: 100%; }
    .tic-navbar-subtitle { display: none; }
}

/* ══════════════════════════════════════════════════
   GRADIO STRUCTURAL CLEANUP
══════════════════════════════════════════════════ */
/* Remove extra Gradio padding from top-level container */
.gradio-container > .main > .wrap {
    padding: 0 !important;
}
/* Remove double borders from gr.Row inside tic-card */
.tic-card .gap-4, .tic-card .gap-2 {
    gap: 0 !important;
}
/* Flatten Gradio column borders */
.tic-card .gr-box,
.tic-card .border {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* ══════════════════════════════════════════════════
   FOLLOW-UP SECTION
══════════════════════════════════════════════════ */
.followup-section {
    margin-top: 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
}
.followup-header {
    background: linear-gradient(90deg, #1a4060 0%, #1e4976 100%);
    border-bottom: 2px solid var(--accent-light);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.followup-header-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: rgba(255,255,255,0.85);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.followup-header-hint {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.5);
    margin-left: auto;
}
.followup-body {
    padding: 16px 20px;
}
.followup-answer {
    margin-top: 12px;
    padding: 16px;
    background: linear-gradient(135deg, #f8fbff 0%, #f0f6ff 100%);
    border: 1px solid #c3d8ef;
    border-left: 4px solid var(--primary-light);
    border-radius: var(--radius);
}
.followup-answer-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary-mid);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ══════════════════════════════════════════════════
   HISTORY PANEL
══════════════════════════════════════════════════ */
.history-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
    margin-bottom: 16px;
}
.history-header {
    background: linear-gradient(90deg, #1a3a5c 0%, #22405e 100%);
    border-bottom: 2px solid var(--accent);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.history-header-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: rgba(255,255,255,0.8);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.history-list {
    padding: 8px;
    max-height: 280px;
    overflow-y: auto;
}
.history-item {
    padding: 10px 12px;
    border-radius: var(--radius);
    cursor: pointer;
    transition: var(--transition);
    border: 1px solid transparent;
    margin-bottom: 4px;
}
.history-item:hover {
    background: var(--accent-pale);
    border-color: var(--border);
}
.history-item-product {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.history-item-meta {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 2px;
    display: flex;
    gap: 8px;
}
.history-empty {
    padding: 20px 16px;
    text-align: center;
    color: var(--text-light);
    font-size: 0.8rem;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Example presets
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES = [
    {
        "label": "蓝牙耳机 → 欧盟",
        "product": "蓝牙无线耳机（TWS真无线耳塞）",
        "markets": ["欧盟"],
        "extra": "额定充电功率5W，内置锂电池250mAh，支持蓝牙5.3",
    },
    {
        "label": "儿童毛绒玩具 → 美国",
        "product": "儿童毛绒玩具（3岁以上）",
        "markets": ["美国"],
        "extra": "填充材料为聚酯纤维，面料为涤纶，无电子元件，表面有小配件",
    },
    {
        "label": "锂电移动电源 → 中+欧",
        "product": "锂电池移动电源（充电宝）",
        "markets": ["中国", "欧盟"],
        "extra": "容量20000mAh，电芯为18650，支持PD 65W快充，重量约400g",
    },
    {
        "label": "不锈钢保温杯 → 日本",
        "product": "不锈钢双层真空保温杯",
        "markets": ["日本"],
        "extra": "材质：食品级304不锈钢（内胆）+ 316不锈钢（外壳），容量500ml",
    },
]

MARKET_CHOICES = ["中国", "美国", "欧盟", "日本"]


# ─────────────────────────────────────────────────────────────────────────────
# Search Visualization HTML builders
# ─────────────────────────────────────────────────────────────────────────────

# Round colour class cycling
_ROUND_COLORS = ["r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"]

_TIER_LABEL = {
    "official": ("官方", "tic-src-official"),
    "standard": ("标准", "tic-src-standard"),
    "tic":      ("TIC",  "tic-src-tic"),
    "ref":      ("参考", "tic-src-ref"),
}


def _build_viz_html(
    keywords: list,     # list of {"query": str, "round": int}
    sources: list,      # list of {"domain": str, "title": str, "tier": str}
    funnel: dict | None,  # {"total_raw": int, "total_filtered": int, "total_cited": int} or None
    is_done: bool = False,
) -> str:
    """Build the full search-process visualization HTML panel."""

    has_content = keywords or sources or funnel

    if not has_content:
        return """
<div class="tic-viz-panel">
  <div class="tic-viz-header">
    <span class="tic-viz-title">🔎 搜索过程可视化</span>
  </div>
  <div class="tic-viz-placeholder">等待搜索开始…</div>
</div>"""

    # ── Keyword tags ──
    kw_html = ""
    if keywords:
        tags = ""
        for kw in keywords:
            r = kw["round"]
            color_cls = "tic-kw-" + _ROUND_COLORS[(r - 1) % 8]
            # Truncate long queries
            label = kw["query"]
            if len(label) > 50:
                label = label[:48] + "…"
            label_escaped = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            tags += f"""<span class="tic-kw-tag {color_cls}" title="{label_escaped}">
              <span class="tic-kw-num">{r}</span>
              {label_escaped}
            </span>"""

        kw_html = f"""
<div class="tic-kw-section">
  <div class="tic-kw-label">🏷 已搜索关键词（共 {len(keywords)} 次）</div>
  <div class="tic-kw-tags">{tags}</div>
</div>"""

    # ── Source credibility list ──
    src_html = ""
    if sources:
        # Deduplicate by domain, keep first occurrence
        seen_domains = set()
        unique_sources = []
        for s in sources:
            if s["domain"] not in seen_domains:
                seen_domains.add(s["domain"])
                unique_sources.append(s)

        rows = ""
        for s in unique_sources[:20]:  # cap at 20
            tier = s.get("tier", "ref")
            badge_text, badge_cls = _TIER_LABEL.get(tier, ("参考", "tic-src-ref"))
            domain_escaped = s["domain"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            title_escaped = s.get("title", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            rows += f"""<div class="tic-src-row">
  <span class="tic-src-badge {badge_cls}">{badge_text}</span>
  <span class="tic-src-domain">{domain_escaped}</span>
  <span class="tic-src-title" title="{title_escaped}">{title_escaped}</span>
</div>"""

        src_html = f"""
<div class="tic-src-section">
  <div class="tic-src-label">📡 信息源可信度（{len(unique_sources)} 个来源）</div>
  <div class="tic-src-list">{rows}</div>
</div>"""

    # ── Funnel stats ──
    funnel_html = ""
    if funnel:
        n = funnel.get("total_raw", 0)
        m = funnel.get("total_filtered", 0)
        k = funnel.get("total_cited", 0)
        funnel_html = f"""
<div class="tic-funnel-section">
  <div class="tic-funnel-label">📊 搜索筛选漏斗</div>
  <div class="tic-funnel">
    <div class="tic-funnel-step">
      <div class="tic-funnel-box step1">{n}</div>
      <div class="tic-funnel-desc">搜索到<br>原始结果</div>
    </div>
    <div class="tic-funnel-arrow">→</div>
    <div class="tic-funnel-step">
      <div class="tic-funnel-box step2">{m}</div>
      <div class="tic-funnel-desc">过滤后<br>保留</div>
    </div>
    <div class="tic-funnel-arrow">→</div>
    <div class="tic-funnel-step">
      <div class="tic-funnel-box step3">{k}</div>
      <div class="tic-funnel-desc">报告中<br>引用</div>
    </div>
  </div>
</div>"""

    # Status badge
    if is_done:
        status_badge = '<span style="font-size:0.7rem;background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-weight:700;">✓ 完成</span>'
    else:
        status_badge = '<span style="font-size:0.7rem;background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.8);padding:2px 8px;border-radius:4px;font-weight:700;animation:blink 1.4s ease-in-out infinite;">● 分析中</span>'

    dividers = '<div style="height:1px;background:#eee;margin:4px 0;"></div>'

    body_parts = []
    if kw_html:
        body_parts.append(kw_html)
    if src_html:
        body_parts.append(dividers + src_html)
    if funnel_html:
        body_parts.append(dividers + funnel_html)

    body = "\n".join(body_parts)

    return f"""
<div class="tic-viz-panel">
  <div class="tic-viz-header">
    <span class="tic-viz-title">🔎 搜索过程可视化</span>
    {status_badge}
  </div>
  <div class="tic-viz-body">
    {body}
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# History helpers
# ─────────────────────────────────────────────────────────────────────────────
def _build_history_html(history: list) -> str:
    """Build the HTML for the query history panel."""
    if not history:
        return """
<div class="history-panel">
  <div class="history-header">
    <span style="font-size:0.9rem">🕘</span>
    <span class="history-header-title">查询历史</span>
  </div>
  <div class="history-empty">暂无历史记录<br>生成报告后会显示在这里</div>
</div>"""

    items_html = ""
    for i, entry in enumerate(history[:20]):  # cap at 20 entries
        product_escaped = entry.get("product", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        markets_str = "、".join(entry.get("markets", []))
        ts = entry.get("timestamp", "")
        # Truncate product name for display
        display_product = product_escaped[:30] + ("…" if len(product_escaped) > 30 else "")
        items_html += f"""<div class="history-item" title="{product_escaped} → {markets_str}">
  <div class="history-item-product">{display_product}</div>
  <div class="history-item-meta">
    <span>🌍 {markets_str}</span>
    <span>⏰ {ts}</span>
  </div>
</div>"""

    return f"""
<div class="history-panel">
  <div class="history-header">
    <span style="font-size:0.9rem">🕘</span>
    <span class="history-header-title">查询历史（{len(history)} 条）</span>
  </div>
  <div class="history-list">{items_html}</div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Follow-up streaming handler
# ─────────────────────────────────────────────────────────────────────────────
def run_follow_up(question: str, conv_messages: list, current_answer: str):
    """
    Gradio generator for follow-up questions.
    Streams the answer and appends it below any previous answers.
    Yields: (followup_answer_text,)
    """
    if not question or not question.strip():
        yield current_answer
        return

    if not conv_messages:
        yield current_answer + "\n\n> ⚠️ 请先生成合规报告，再进行追问。"
        return

    # Build a separator header for this follow-up
    q_escaped = question.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    header = f"\n\n---\n\n**🙋 追问**：{question.strip()}\n\n**💬 回答**：\n\n"

    accumulated_answer = current_answer + header
    yield accumulated_answer

    try:
        for chunk in follow_up_stream(conv_messages, question.strip()):
            accumulated_answer += chunk
            yield accumulated_answer
    except Exception as e:
        accumulated_answer += f"\n❌ 追问失败：{str(e)}"
        yield accumulated_answer


# ─────────────────────────────────────────────────────────────────────────────
# Agent streaming wrapper for Gradio
# ─────────────────────────────────────────────────────────────────────────────
def run_compliance_check(product: str, markets: list, extra_info: str, history: list):
    """
    Gradio generator function - yields incremental text for streaming display,
    then yields updated charts HTML after report is complete.
    Outputs: (report_markdown, viz_html, charts_html, kb_html, conv_messages_state,
              followup_section_visible, followup_answer, history_state, history_html)
    """
    # Defaults for new outputs
    empty_followup = ""
    followup_visible = gr.update(visible=False)

    if not product or not product.strip():
        yield ("❌ 请输入产品描述", _build_viz_html([], [], None), PLACEHOLDER_HTML,
               build_kb_recommendation_html("", markets), [], followup_visible, empty_followup,
               history, _build_history_html(history))
        return

    if not markets:
        yield ("❌ 请选择至少一个目标市场", _build_viz_html([], [], None), PLACEHOLDER_HTML,
               build_kb_recommendation_html(product, markets), [], followup_visible, empty_followup,
               history, _build_history_html(history))
        return

    # Show loading state for charts immediately
    loading_html = """
<div style="
    background: #f7f9fc;
    border: 2px dashed #dce3ec;
    border-radius: 12px;
    padding: 40px 24px;
    text-align: center;
    color: #60748a;
    margin-top: 8px;
">
    <div style="font-size: 2.2rem; margin-bottom: 12px;">⏳</div>
    <div style="font-size: 0.95rem; font-weight: 600; color: #1a3a5c; margin-bottom: 6px;">
        合规风险可视化
    </div>
    <div style="font-size: 0.82rem; line-height: 1.65; max-width: 340px; margin: 0 auto;">
        正在生成合规报告，图表将在分析完成后自动更新…
    </div>
</div>
"""

    # Viz state
    viz_keywords = []    # {query, round}
    viz_sources = []     # {domain, title, tier}
    viz_funnel = None
    viz_done = False

    # KB recommendation: build immediately (before search starts)
    kb_html_current = build_kb_recommendation_html(product, markets)
    cross_validation_html = ""  # filled after agent completes

    # Messages snapshot: captured from __VIZ__ messages_snapshot event
    conv_messages = []

    accumulated = ""
    try:
        for chunk in run_agent_stream(product, markets, extra_info or ""):
            # Strip and process __VIZ__ events; don't add them to the report text
            lines = chunk.split("\n")
            report_lines = []
            viz_updated = False

            for line in lines:
                stripped = line.strip()
                if stripped.startswith("__VIZ__:"):
                    # Parse viz event
                    try:
                        payload = json.loads(stripped[len("__VIZ__:"):])
                        etype = payload.get("type")

                        if etype == "search_start":
                            # Add keyword tag
                            viz_keywords.append({
                                "query": payload.get("query", ""),
                                "round": payload.get("round", len(viz_keywords) + 1),
                            })
                            viz_updated = True

                        elif etype == "search_results":
                            # Add source rows
                            for src in payload.get("sources", []):
                                viz_sources.append(src)
                            viz_updated = True

                        elif etype == "funnel_summary":
                            viz_funnel = {
                                "total_raw": payload.get("total_raw", 0),
                                "total_filtered": payload.get("total_filtered", 0),
                                "total_cited": payload.get("total_cited", 0),
                            }
                            viz_done = True
                            viz_updated = True

                        elif etype == "cross_validation":
                            # Append cross-validation HTML below KB recommendations
                            cross_validation_html = payload.get("html", "")
                            if cross_validation_html:
                                kb_html_current = (
                                    build_kb_recommendation_html(product, markets)
                                    + cross_validation_html
                                )
                            viz_updated = True

                        elif etype == "messages_snapshot":
                            # Capture conversation messages for follow-up use
                            conv_messages = payload.get("messages", [])

                    except (json.JSONDecodeError, Exception):
                        pass  # Silently skip malformed viz events
                else:
                    report_lines.append(line)

            # Rebuild report text without viz lines
            report_chunk = "\n".join(report_lines)
            # Avoid adding spurious blank lines from stripped viz-only chunks
            if report_chunk.strip():
                accumulated += report_chunk
            elif report_chunk and not report_chunk.strip():
                # It's whitespace — keep to preserve formatting, but only if there's
                # actual surrounding content (don't prepend whitespace to empty reports)
                if accumulated:
                    accumulated += report_chunk

            if viz_updated:
                viz_html = _build_viz_html(viz_keywords, viz_sources, viz_funnel, viz_done)
                yield (accumulated, viz_html, loading_html, kb_html_current,
                       conv_messages, gr.update(visible=False), "",
                       history, _build_history_html(history))
            else:
                yield (accumulated, _build_viz_html(viz_keywords, viz_sources, viz_funnel, viz_done),
                       loading_html, kb_html_current,
                       conv_messages, gr.update(visible=False), "",
                       history, _build_history_html(history))

    except Exception as e:
        error_text = (
            f"\n\n❌ **运行出错**：{str(e)}\n\n"
            "请检查：\n1. 本地代理是否运行（http://127.0.0.1:8046）\n"
            "2. BRAVE_API_KEY 是否配置"
        )
        yield (accumulated + error_text,
               _build_viz_html(viz_keywords, viz_sources, viz_funnel, viz_done),
               PLACEHOLDER_HTML, kb_html_current,
               conv_messages, gr.update(visible=False), "",
               history, _build_history_html(history))
        return

    # Report complete — generate charts based on actual report content
    try:
        charts_html = generate_charts_html(accumulated, product, markets)
    except Exception as e:
        charts_html = f"<p style='color:#c0392b;padding:16px'>图表生成失败：{e}</p>"

    # Add to history
    timestamp = datetime.now().strftime("%m-%d %H:%M")
    new_entry = {
        "product": product,
        "markets": markets,
        "timestamp": timestamp,
    }
    updated_history = [new_entry] + history  # newest first

    # Final yield with done state + follow-up section visible
    viz_html_final = _build_viz_html(viz_keywords, viz_sources, viz_funnel, is_done=True)
    followup_visible_update = gr.update(visible=True)
    yield (accumulated, viz_html_final, charts_html, kb_html_current,
           conv_messages, followup_visible_update, "",
           updated_history, _build_history_html(updated_history))


def export_report_pdf(report_text: str, product: str, markets: list):
    """Generate and return a PDF file for download."""
    if not report_text or not report_text.strip():
        # Return None — Gradio File component handles None as no-file
        return None
    try:
        pdf_path = generate_pdf(report_text, product or "未知产品", markets or [])
        return pdf_path
    except Exception as e:
        print(f"[PDF Export Error] {e}")
        return None


def fill_example(example_idx: int):
    """Fill form with example data."""
    if 0 <= example_idx < len(EXAMPLES):
        ex = EXAMPLES[example_idx]
        return ex["product"], ex["markets"], ex["extra"]
    return "", [], ""


def update_kb_recommendations(product: str, markets: list):
    """Called when product text or markets change to update KB sidebar immediately."""
    return build_kb_recommendation_html(product or "", markets or [])


# Shared empty-state HTML used by clear button
EMPTY_REPORT_HTML = """
<div style="padding: 40px 32px; text-align: center; color: #8fa4bb;">
<div style="font-size: 3rem; margin-bottom: 16px;">📊</div>
<div style="font-size: 1rem; font-weight: 600; color: #1a3a5c; margin-bottom: 8px;">等待分析输入</div>
<div style="font-size: 0.85rem; line-height: 1.7; max-width: 360px; margin: 0 auto;">
    在左侧填写产品描述和目标市场，<br>点击 <strong style="color: #d4830a;">「生成合规报告」</strong> 启动 AI 分析。
</div>
</div>"""

VIZ_EMPTY_HTML = _build_viz_html([], [], None)


# ─────────────────────────────────────────────────────────────────────────────
# Build Gradio UI
# ─────────────────────────────────────────────────────────────────────────────
def build_ui():
    with gr.Blocks(
        title="TIC-Agent | 智能合规检查助手",
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
        ),
    ) as demo:

        # ══════════════════════════════════════════════
        # TOP NAVIGATION BAR
        # ══════════════════════════════════════════════
        gr.HTML("""
        <div class="tic-navbar">
            <div class="tic-navbar-left">
                <div class="tic-navbar-logo">🔬</div>
                <div class="tic-navbar-brand">
                    <div class="tic-navbar-title">TIC-Agent</div>
                    <div class="tic-navbar-subtitle">Intelligent Compliance Platform</div>
                </div>
                <div class="tic-navbar-divider"></div>
                <span class="tic-badge-demo">DEMO</span>
            </div>
            <div class="tic-navbar-right">
                <div class="tic-nav-links">
                    <span class="tic-nav-link">合规检查</span>
                    <span class="tic-nav-link">法规数据库</span>
                    <span class="tic-nav-link">关于</span>
                </div>
                <div class="tic-status-label">
                    <div class="tic-status-dot"></div>
                    系统就绪
                </div>
            </div>
        </div>
        """)

        # ══════════════════════════════════════════════
        # HERO BAND
        # ══════════════════════════════════════════════
        gr.HTML("""
        <div class="tic-hero">
            <div class="tic-hero-inner">
                <div class="tic-hero-eyebrow">Testing · Inspection · Certification</div>
                <div class="tic-hero-headline">智能 TIC 合规检查助手</div>
                <div class="tic-hero-desc">
                    输入产品描述与目标市场，AI Agent 自动检索全球法规数据库，
                    生成结构化合规报告——覆盖中国、美国、欧盟、日本四大市场。
                </div>
            </div>
        </div>
        """)

        # ══════════════════════════════════════════════
        # STATS MINI-CARDS ROW
        # ══════════════════════════════════════════════
        gr.HTML("""
        <div class="tic-stats-row">
            <div class="tic-stat-card">
                <div class="tic-stat-icon">🌐</div>
                <div class="tic-stat-info">
                    <div class="tic-stat-value">4</div>
                    <div class="tic-stat-desc">覆盖目标市场</div>
                </div>
            </div>
            <div class="tic-stat-card">
                <div class="tic-stat-icon">📋</div>
                <div class="tic-stat-info">
                    <div class="tic-stat-value">实时</div>
                    <div class="tic-stat-desc">法规搜索更新</div>
                </div>
            </div>
            <div class="tic-stat-card">
                <div class="tic-stat-icon">⚡</div>
                <div class="tic-stat-info">
                    <div class="tic-stat-value">1-3 min</div>
                    <div class="tic-stat-desc">平均分析时长</div>
                </div>
            </div>
            <div class="tic-stat-card">
                <div class="tic-stat-icon">🏭</div>
                <div class="tic-stat-info">
                    <div class="tic-stat-value">SGS 级</div>
                    <div class="tic-stat-desc">报告结构标准</div>
                </div>
            </div>
        </div>
        """)

        # ══════════════════════════════════════════════
        # MAIN CONTENT — TWO COLUMNS
        # ══════════════════════════════════════════════
        with gr.Row(equal_height=False, elem_classes=["tic-main"]):

            # ──────────────────────────────────────────
            # LEFT: INPUT CARD
            # ──────────────────────────────────────────
            with gr.Column(scale=4, min_width=300):

                # INPUT CARD
                gr.HTML("""
                <div class="tic-card-header" style="
                    background: linear-gradient(90deg, #f7f9fc 0%, #fff 100%);
                    border: 1px solid #dce3ec;
                    border-bottom: 2px solid #d4830a;
                    border-radius: 12px 12px 0 0;
                    padding: 14px 20px;
                    display: flex; align-items: center; gap: 10px;
                ">
                    <div class="tic-card-icon">📦</div>
                    <div>
                        <div class="tic-card-title">产品信息录入</div>
                    </div>
                </div>
                """)

                with gr.Column(elem_classes=["tic-card-body"], elem_id="input-card-body"):
                    gr.HTML('<div class="field-label">产品描述 <span class="req">*</span></div>')
                    product_input = gr.Textbox(
                        label="",
                        placeholder="例如：蓝牙无线耳机（TWS真无线耳塞）…",
                        lines=2,
                        max_lines=4,
                        show_label=False,
                    )

                    gr.HTML('<div class="field-divider"></div>')
                    gr.HTML('<div class="field-label">目标市场 <span class="req">*</span></div>')
                    market_input = gr.CheckboxGroup(
                        choices=MARKET_CHOICES,
                        label="",
                        value=[],
                        show_label=False,
                    )

                    gr.HTML('<div class="field-divider"></div>')
                    gr.HTML('<div class="field-label">补充信息 <span style="color:var(--text-light);font-weight:400;text-transform:none;letter-spacing:0">（可选）</span></div>')
                    extra_input = gr.Textbox(
                        label="",
                        placeholder="材质、额定功率、电池容量、目标用户群等技术参数…",
                        lines=2,
                        max_lines=4,
                        show_label=False,
                    )

                    gr.HTML('<div class="field-divider"></div>')

                    # Action buttons
                    with gr.Row():
                        submit_btn = gr.Button(
                            "🚀 生成合规报告",
                            variant="primary",
                            scale=3,
                        )
                        clear_btn = gr.Button(
                            "清空",
                            variant="secondary",
                            scale=1,
                        )

                    with gr.Row():
                        export_btn = gr.Button(
                            "📥 导出PDF报告",
                            variant="secondary",
                            scale=1,
                        )
                        pdf_download = gr.File(
                            label="",
                            visible=False,
                            scale=2,
                        )

                    # Tip box
                    gr.HTML("""
                    <div class="tic-tip">
                        <strong>📌 分析流程</strong><br>
                        Agent 将自动：分析产品类别 → 检索适用法规 → 抓取标准详情 → 输出结构化报告。
                        全流程约 <strong>1–3 分钟</strong>，搜索进度将实时流式输出。
                    </div>
                    """)

                # ── EXAMPLE CARDS ──
                gr.HTML("""
                <div style="margin-top: 16px;">
                <div class="tic-card-header" style="
                    background: linear-gradient(90deg, #f7f9fc 0%, #fff 100%);
                    border: 1px solid #dce3ec;
                    border-bottom: 2px solid #d4830a;
                    border-radius: 12px 12px 0 0;
                    padding: 12px 20px;
                    display: flex; align-items: center; gap: 10px;
                ">
                    <div class="tic-card-icon">💡</div>
                    <div class="tic-card-title">快速示例</div>
                </div>
                </div>
                """)

                with gr.Column(elem_classes=["tic-card-body"]):
                    gr.HTML('<div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:10px;">点击任意示例，自动填入产品信息</div>')
                    with gr.Row(elem_classes=["examples-grid"]):
                        ex_btns = []
                        ex_meta = [
                            ("蓝牙耳机 → 欧盟", "CE · EMC · RoHS"),
                            ("儿童玩具 → 美国", "ASTM F963 · CPSC"),
                            ("充电宝 → 中国+欧盟", "GB/T · CE · UN38.3"),
                            ("保温杯 → 日本", "食品安全法 · ST"),
                        ]
                        for i, (label, regs) in enumerate(ex_meta):
                            btn = gr.Button(
                                f"**{label}**\n{regs}",
                                variant="secondary",
                                elem_classes=["example-card-btn"],
                            )
                            ex_btns.append(btn)

            # ──────────────────────────────────────────
            # MIDDLE: OUTPUT PANEL
            # ──────────────────────────────────────────
            with gr.Column(scale=6, min_width=380, elem_classes=["output-area"]):

                # ── SEARCH VISUALIZATION PANEL (new in iter-5) ──
                viz_output = gr.HTML(
                    value=VIZ_EMPTY_HTML,
                    label="",
                    show_label=False,
                )

                # Status band header
                gr.HTML("""
                <div class="tic-status-band">
                    <div>
                        <div class="tic-status-band-title">合规分析报告</div>
                        <div class="tic-progress-bar" id="tic-progress">
                            <div class="tic-progress-fill"></div>
                        </div>
                    </div>
                    <div class="tic-status-band-live">
                        <div class="tic-live-dot"></div>
                        LIVE · Brave Search + Gemini Flash
                    </div>
                </div>
                """)

                # Report markdown area
                with gr.Column(elem_classes=["tic-report-area"]):
                    output = gr.Markdown(
                        value="""
<div style="padding: 40px 32px; text-align: center; color: #8fa4bb;">

<div style="font-size: 3rem; margin-bottom: 16px;">📊</div>

<div style="font-size: 1rem; font-weight: 600; color: #1a3a5c; margin-bottom: 8px;">
    等待分析输入
</div>

<div style="font-size: 0.85rem; line-height: 1.7; max-width: 360px; margin: 0 auto;">
    在左侧填写产品描述和目标市场，<br>点击 <strong style="color: #d4830a;">「生成合规报告」</strong> 启动 AI 分析。<br><br>
    报告将包含：<br>
    <span style="color: #1a3a5c;">✓</span> 适用法规清单 &nbsp;
    <span style="color: #1a3a5c;">✓</span> 认证要求列表<br>
    <span style="color: #1a3a5c;">✓</span> 测试项目说明 &nbsp;
    <span style="color: #1a3a5c;">✓</span> 合规建议摘要
</div>

</div>
""",
                        height=680,
                        show_label=False,
                    )

                # ── CHARTS AREA ──
                charts_output = gr.HTML(
                    value=PLACEHOLDER_HTML,
                    label="",
                    show_label=False,
                )

                # ── FOLLOW-UP SECTION (hidden until report is ready) ──
                with gr.Column(visible=False, elem_classes=["followup-section"]) as followup_section:
                    gr.HTML("""
                    <div class="followup-header">
                        <span style="font-size:1rem">💬</span>
                        <span class="followup-header-title">继续追问</span>
                        <span class="followup-header-hint">基于报告内容追问，无需重新搜索</span>
                    </div>
                    """)
                    with gr.Column(elem_classes=["followup-body"]):
                        followup_input = gr.Textbox(
                            label="",
                            placeholder="例如：CE认证具体需要哪些测试？RoHS限制的有害物质有哪些？",
                            lines=2,
                            max_lines=4,
                            show_label=False,
                        )
                        with gr.Row():
                            followup_btn = gr.Button(
                                "📨 发送追问",
                                variant="primary",
                                scale=2,
                            )
                            clear_followup_btn = gr.Button(
                                "清空追问",
                                variant="secondary",
                                scale=1,
                            )
                        gr.HTML("""
                        <div style="font-size:0.75rem;color:var(--text-light);margin-top:4px;">
                        💡 追问将直接基于已搜索的法规内容回答，流式输出，无需等待。
                        </div>
                        """)
                    # Follow-up answer area (Markdown, styled differently)
                    with gr.Column(elem_classes=["followup-answer"]):
                        gr.HTML('<div class="followup-answer-label">🤖 AI 追问回答</div>')
                        followup_answer = gr.Markdown(
                            value="",
                            show_label=False,
                            height=300,
                        )

            # ──────────────────────────────────────────
            # RIGHT SIDEBAR: HISTORY + KB RECOMMENDATIONS
            # ──────────────────────────────────────────
            with gr.Column(scale=3, min_width=260, elem_classes=["kb-panel-wrap"]):
                # History panel (top of sidebar)
                history_output = gr.HTML(
                    value=_build_history_html([]),
                    label="",
                    show_label=False,
                )
                kb_output = gr.HTML(
                    value=build_kb_recommendation_html("", []),
                    label="",
                    show_label=False,
                )

        # ══════════════════════════════════════════════
        # STATE COMPONENTS (invisible)
        # ══════════════════════════════════════════════
        # Stores the conversation messages for follow-up use
        conv_messages_state = gr.State([])
        # Stores the query history list
        history_state = gr.State([])

        # ══════════════════════════════════════════════
        # FOOTER BAR
        # ══════════════════════════════════════════════
        gr.HTML("""
        <div class="tic-footer">
            <div class="tic-footer-left">
                <span style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin-right:4px;">POWERED BY</span>
                <span class="tic-tech-tag">Gemini Flash</span>
                <span class="tic-tech-tag">Brave Search</span>
                <span class="tic-tech-tag">Gradio 5</span>
                <span class="tic-tech-tag">OpenAI Function Calling</span>
            </div>
            <div class="tic-footer-right">
                ⚠️ 本工具仅供演示与参考，不构成正式合规认证意见。<br>
                最终合规判定请联系 SGS、Intertek、TÜV 等认可检测机构。
            </div>
        </div>
        """)

        # ══════════════════════════════════════════════
        # EVENT HANDLERS
        # ══════════════════════════════════════════════

        # Submit → streaming: yields (report, viz, charts, kb, conv_messages,
        #                              followup_section_visible, followup_answer,
        #                              history_state, history_html)
        submit_btn.click(
            fn=run_compliance_check,
            inputs=[product_input, market_input, extra_input, history_state],
            outputs=[output, viz_output, charts_output, kb_output,
                     conv_messages_state, followup_section, followup_answer,
                     history_state, history_output],
        )

        # Clear — reset report, form, charts, viz, kb, follow-up, and history
        def _do_clear():
            return (
                "", [], "",             # product, markets, extra
                EMPTY_REPORT_HTML,      # output
                VIZ_EMPTY_HTML,         # viz
                PLACEHOLDER_HTML,       # charts
                build_kb_recommendation_html("", []),  # kb
                gr.File(visible=False, value=None),    # pdf_download
                [],                     # conv_messages_state
                gr.update(visible=False),  # followup_section
                "",                     # followup_answer
            )

        clear_btn.click(
            fn=_do_clear,
            inputs=[],
            outputs=[product_input, market_input, extra_input,
                     output, viz_output, charts_output, kb_output,
                     pdf_download, conv_messages_state,
                     followup_section, followup_answer],
        )

        # PDF Export — generate PDF from current report and show download
        def _do_export(report_text, product, markets):
            path = export_report_pdf(report_text, product, markets)
            if path:
                return gr.File(value=path, visible=True)
            return gr.File(visible=False, value=None)

        export_btn.click(
            fn=_do_export,
            inputs=[output, product_input, market_input],
            outputs=[pdf_download],
        )

        # Follow-up: send question and stream response
        followup_btn.click(
            fn=run_follow_up,
            inputs=[followup_input, conv_messages_state, followup_answer],
            outputs=[followup_answer],
        ).then(
            fn=lambda: "",  # clear the input after submission
            inputs=[],
            outputs=[followup_input],
        )

        # Also allow Enter in follow-up textbox to submit
        followup_input.submit(
            fn=run_follow_up,
            inputs=[followup_input, conv_messages_state, followup_answer],
            outputs=[followup_answer],
        ).then(
            fn=lambda: "",
            inputs=[],
            outputs=[followup_input],
        )

        # Clear follow-up answers
        clear_followup_btn.click(
            fn=lambda: "",
            inputs=[],
            outputs=[followup_answer],
        )

        # KB live update: product text change → instantly show KB recommendations
        product_input.change(
            fn=update_kb_recommendations,
            inputs=[product_input, market_input],
            outputs=[kb_output],
        )

        # KB live update: market checkbox change → update KB recommendations
        market_input.change(
            fn=update_kb_recommendations,
            inputs=[product_input, market_input],
            outputs=[kb_output],
        )

        # Example buttons → fill form + update KB immediately
        for i, btn in enumerate(ex_btns):
            idx = i
            btn.click(
                fn=lambda i=idx: fill_example(i),
                inputs=[],
                outputs=[product_input, market_input, extra_input],
            ).then(
                fn=update_kb_recommendations,
                inputs=[product_input, market_input],
                outputs=[kb_output],
            )

    return demo


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False,
        show_error=True,
        inbrowser=False,
    )
