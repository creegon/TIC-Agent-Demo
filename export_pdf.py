# export_pdf.py - Professional PDF report generator for TIC-Agent
# Generates consulting-grade compliance reports from markdown text
# Usage: generate_pdf(report_text, product, markets) -> PDF file path

import os
import re
import logging
import tempfile
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Suppress fpdf2 internal font-subsetting noise
logging.getLogger("fpdf").setLevel(logging.ERROR)

# ─────────────────────────────────────────────────────────────────────────────
# Design constants — matches TIC-Agent UI (Deep Navy + Amber Gold)
# ─────────────────────────────────────────────────────────────────────────────
COLOR_PRIMARY      = (26,  58,  92)   # Deep navy  #1a3a5c
COLOR_PRIMARY_MID  = (30,  73, 118)   # Mid navy   #1e4976
COLOR_ACCENT       = (212, 131,  10)  # Amber gold #d4830a
COLOR_ACCENT_LIGHT = (232, 168,  56)  # Soft gold  #e8a838
COLOR_ACCENT_PALE  = (254, 243, 220)  # Gold tint  #fef3dc
COLOR_BG           = (240, 244, 248)  # Page bg    #f0f4f8
COLOR_SURFACE      = (255, 255, 255)  # White
COLOR_SURFACE_2    = (247, 249, 252)  # Light gray #f7f9fc
COLOR_BORDER       = (220, 227, 236)  # Border     #dce3ec
COLOR_TEXT         = ( 30,  45,  61)  # Dark text  #1e2d3d
COLOR_TEXT_MUTED   = ( 96, 116, 138)  # Gray text  #60748a

FONT_PATH_REGULAR  = r"C:\Windows\Fonts\msyh.ttc"
FONT_PATH_BOLD     = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_NAME          = "MSYaHei"

# Fallback fonts if msyh not available
FALLBACK_FONTS = [
    (r"C:\Windows\Fonts\simsun.ttc",   r"C:\Windows\Fonts\simhei.ttf"),
    (r"C:\Windows\Fonts\msjh.ttc",     r"C:\Windows\Fonts\msjhbd.ttc"),
]

A4_W, A4_H = 210, 297  # mm
MARGIN_L, MARGIN_R = 22, 22
MARGIN_T, MARGIN_B = 22, 22
CONTENT_W = A4_W - MARGIN_L - MARGIN_R


# ─────────────────────────────────────────────────────────────────────────────
# Font detection
# ─────────────────────────────────────────────────────────────────────────────
def _find_fonts():
    """Return (regular_path, bold_path) for available Chinese font."""
    if os.path.exists(FONT_PATH_REGULAR):
        bold = FONT_PATH_BOLD if os.path.exists(FONT_PATH_BOLD) else FONT_PATH_REGULAR
        return FONT_PATH_REGULAR, bold
    for reg, bold in FALLBACK_FONTS:
        if os.path.exists(reg):
            b = bold if os.path.exists(bold) else reg
            return reg, b
    # No Chinese font — return None, will use DejaVu (no Chinese)
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# PDF class with header/footer
# ─────────────────────────────────────────────────────────────────────────────
class TICReport(FPDF):
    def __init__(self, product: str, markets: list, report_date: str):
        super().__init__(format="A4")
        self.product_title = product[:60] + "…" if len(product) > 60 else product
        self.markets_label = "、".join(markets) if markets else "—"
        self.report_date = report_date
        self._page_counter_start = 2  # Cover = page 1, content starts page 2

        # Register fonts
        reg, bold = _find_fonts()
        if reg:
            self.add_font(FONT_NAME, "", reg)
            self.add_font(FONT_NAME, "B", bold)
            self._font_name = FONT_NAME
        else:
            self._font_name = "helvetica"

        self.set_auto_page_break(auto=True, margin=MARGIN_B + 14)
        self.set_margins(MARGIN_L, MARGIN_T, MARGIN_R)

    def set_f(self, style="", size=10):
        self.set_font(self._font_name, style, size)

    def header(self):
        # Skip header on cover page (page 1) and TOC (page 2)
        if self.page_no() <= 2:
            return
        self.set_y(8)
        # Left: report title
        self.set_f("", 7.5)
        self.set_text_color(*COLOR_TEXT_MUTED)
        self.cell(CONTENT_W * 0.75, 5, "TIC-Agent 智能合规检查报告", new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Right: product name (truncated)
        prod = self.product_title[:30] + "…" if len(self.product_title) > 30 else self.product_title
        self.set_f("", 7)
        self.set_text_color(*COLOR_TEXT_MUTED)
        self.cell(CONTENT_W * 0.25, 5, prod, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Gold separator line
        self.set_draw_color(*COLOR_ACCENT)
        self.set_line_width(0.4)
        self.line(MARGIN_L, 15, A4_W - MARGIN_R, 15)
        self.set_y(18)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-14)
        self.set_draw_color(*COLOR_BORDER)
        self.set_line_width(0.3)
        self.line(MARGIN_L, A4_H - 16, A4_W - MARGIN_R, 16)
        self.set_f("", 7.5)
        self.set_text_color(*COLOR_TEXT_MUTED)
        self.cell(CONTENT_W * 0.5, 6, f"© TIC-Agent Demo  ·  {self.report_date}", new_x=XPos.RIGHT, new_y=YPos.TOP)
        page_num = self.page_no() - 1  # page 1 (cover) not counted
        self.set_f("B", 7.5)
        self.set_text_color(*COLOR_PRIMARY)
        self.cell(CONTENT_W * 0.5, 6, f"第 {page_num} 页", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Helpers ──

    def fill_rect(self, x, y, w, h, color):
        self.set_fill_color(*color)
        self.rect(x, y, w, h, style="F")

    def draw_cover(self):
        """Draw the cover page."""
        # Full-page navy background (top 2/3)
        self.fill_rect(0, 0, A4_W, A4_H * 0.65, COLOR_PRIMARY)
        # Gold accent band
        self.fill_rect(0, A4_H * 0.65, A4_W, 4, COLOR_ACCENT)
        # Lower section
        self.fill_rect(0, A4_H * 0.65 + 4, A4_W, A4_H * 0.35 - 4, COLOR_SURFACE)

        # ── Logo/icon placeholder ──
        logo_size = 28
        logo_x = MARGIN_L
        logo_y = 32
        self.fill_rect(logo_x, logo_y, logo_size, logo_size, COLOR_ACCENT)
        self.set_f("B", 16)
        self.set_text_color(*COLOR_SURFACE)
        self.set_xy(logo_x, logo_y + 6)
        self.cell(logo_size, logo_size * 0.5, "TIC", align="C")

        # Brand name next to logo
        self.set_f("", 9)
        self.set_text_color(232, 168, 56)
        self.set_xy(logo_x + logo_size + 8, logo_y + 2)
        self.cell(80, 6, "INTELLIGENT COMPLIANCE PLATFORM")
        self.set_xy(logo_x + logo_size + 8, logo_y + 9)
        self.set_f("", 7)
        self.set_text_color(180, 200, 220)
        self.cell(80, 5, "Testing · Inspection · Certification")

        # ── Eyebrow text ──
        self.set_xy(MARGIN_L, 82)
        self.set_f("", 8)
        self.set_text_color(180, 200, 220)
        self.cell(CONTENT_W, 6, "COMPLIANCE INTELLIGENCE REPORT")

        # ── Main title ──
        self.set_xy(MARGIN_L, 92)
        self.set_f("B", 26)
        self.set_text_color(*COLOR_SURFACE)
        self.cell(CONTENT_W, 14, "智能合规检查报告", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # ── Sub-title ──
        self.set_x(MARGIN_L)
        self.set_f("", 13)
        self.set_text_color(200, 220, 240)
        self.cell(CONTENT_W, 9, "TIC-Agent Compliance Assessment", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # ── Gold divider ──
        dy = self.get_y() + 8
        self.fill_rect(MARGIN_L, dy, 48, 1.5, COLOR_ACCENT)
        self.fill_rect(MARGIN_L + 52, dy + 0.25, CONTENT_W - 52, 1, COLOR_PRIMARY_MID)

        # ── Product name ──
        self.set_xy(MARGIN_L, dy + 10)
        self.set_f("", 8)
        self.set_text_color(180, 200, 220)
        self.cell(CONTENT_W, 5, "产品名称")
        self.set_xy(MARGIN_L, dy + 16)
        self.set_f("B", 14)
        self.set_text_color(*COLOR_SURFACE)
        # Multi-line product name
        self.multi_cell(CONTENT_W, 8, self.product_title)

        # ── Markets ──
        my = self.get_y() + 6
        self.set_xy(MARGIN_L, my)
        self.set_f("", 8)
        self.set_text_color(180, 200, 220)
        self.cell(CONTENT_W, 5, "目标市场")
        self.set_xy(MARGIN_L, my + 7)
        self.set_f("B", 12)
        self.set_text_color(*COLOR_ACCENT_LIGHT)
        self.cell(CONTENT_W, 7, self.markets_label)

        # ── Lower section (white) — date & disclaimer ──
        lower_y = A4_H * 0.65 + 14
        self.set_xy(MARGIN_L, lower_y)
        self.set_f("", 8)
        self.set_text_color(*COLOR_TEXT_MUTED)
        self.cell(CONTENT_W * 0.5, 6, f"报告日期：{self.report_date}")
        self.set_xy(MARGIN_L, lower_y + 8)
        self.set_f("", 7)
        self.set_text_color(*COLOR_TEXT_MUTED)
        self.multi_cell(CONTENT_W, 5,
            "本报告由 TIC-Agent AI 系统自动生成，仅供参考。"
            "最终合规认证需由 SGS、Intertek、TÜV 等认可检测机构确认。"
        )

        # ── Confidential stamp (bottom-right) ──
        self.set_xy(A4_W - MARGIN_R - 52, A4_H - 22)
        self.set_f("", 7)
        self.set_text_color(*COLOR_ACCENT)
        self.cell(50, 5, "CONFIDENTIAL · 仅供参考", align="R")


# ─────────────────────────────────────────────────────────────────────────────
# Markdown parser → PDF drawing commands
# ─────────────────────────────────────────────────────────────────────────────

def _strip_inline(text: str) -> str:
    """Remove markdown inline markers: **bold**, *italic*, `code`, links.
    Also strip emoji characters that Chinese fonts don't support."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Strip emoji/symbols not in CJK font (U+2600–U+27BF, U+FE00–U+FEFF, etc.)
    text = re.sub(
        r'[\U0001F300-\U0001FFFF'   # Supplementary symbols & emoji
        r'\u2600-\u27BF'            # Misc symbols
        r'\uFE00-\uFE0F'            # Variation selectors
        r'\u200D'                   # ZWJ
        r'\uFE10-\uFEFF'            # Halfwidth/fullwidth extras
        r']', '', text
    )
    return text.strip()


def _parse_table(lines: list) -> tuple[list, list]:
    """Parse markdown table lines into (headers, rows)."""
    headers = []
    rows = []
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if i == 0:
            headers = cells
        elif i == 1 and re.match(r'^[\s\-:|]+$', line):
            continue  # separator row
        else:
            rows.append(cells)
    return headers, rows


def _collect_links(text: str) -> list:
    """Extract all [title](url) markdown links."""
    return re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', text)


def _section_headings(text: str) -> list:
    """Return list of (level, title, char_offset) for TOC."""
    results = []
    for m in re.finditer(r'^(#{1,3})\s+(.+)$', text, re.MULTILINE):
        level = len(m.group(1))
        title = _strip_inline(m.group(2))
        results.append((level, title, m.start()))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Main renderer
# ─────────────────────────────────────────────────────────────────────────────

def _render_body(pdf: TICReport, text: str):
    """Render markdown body into PDF."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Skip empty lines ──
        if not stripped:
            pdf.ln(2)
            i += 1
            continue

        # ── H1 ──
        if stripped.startswith('# '):
            title = _strip_inline(stripped[2:])
            # Section header bar
            y = pdf.get_y()
            pdf.fill_rect(MARGIN_L, y, CONTENT_W, 10, COLOR_PRIMARY)
            pdf.set_xy(MARGIN_L + 3, y + 1.5)
            pdf.set_f("B", 13)
            pdf.set_text_color(*COLOR_SURFACE)
            pdf.cell(CONTENT_W - 6, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Gold underline
            pdf.fill_rect(MARGIN_L, pdf.get_y(), CONTENT_W, 1.2, COLOR_ACCENT)
            pdf.ln(5)
            i += 1
            continue

        # ── H2 ──
        if stripped.startswith('## '):
            title = _strip_inline(stripped[3:])
            pdf.ln(3)
            y = pdf.get_y()
            # Left gold accent bar + light navy bg
            pdf.fill_rect(MARGIN_L, y, CONTENT_W, 9, COLOR_SURFACE_2)
            pdf.fill_rect(MARGIN_L, y, 3, 9, COLOR_ACCENT)
            pdf.set_xy(MARGIN_L + 6, y + 1)
            pdf.set_f("B", 11)
            pdf.set_text_color(*COLOR_PRIMARY)
            pdf.cell(CONTENT_W - 9, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(*COLOR_BORDER)
            pdf.set_line_width(0.2)
            pdf.line(MARGIN_L, pdf.get_y(), A4_W - MARGIN_R, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue

        # ── H3 ──
        if stripped.startswith('### '):
            title = _strip_inline(stripped[4:])
            pdf.ln(2)
            y = pdf.get_y()
            pdf.fill_rect(MARGIN_L, y, 2, 7, COLOR_ACCENT_LIGHT)
            pdf.set_xy(MARGIN_L + 5, y)
            pdf.set_f("B", 10)
            pdf.set_text_color(*COLOR_PRIMARY_MID)
            pdf.cell(CONTENT_W - 5, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            i += 1
            continue

        # ── Horizontal rule ──
        if stripped in ('---', '***', '==='):
            pdf.set_draw_color(*COLOR_BORDER)
            pdf.set_line_width(0.3)
            pdf.line(MARGIN_L, pdf.get_y(), A4_W - MARGIN_R, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue

        # ── Blockquote ──
        if stripped.startswith('> '):
            content = _strip_inline(stripped[2:])
            y = pdf.get_y()
            pdf.fill_rect(MARGIN_L, y, CONTENT_W, 8, COLOR_ACCENT_PALE)
            pdf.fill_rect(MARGIN_L, y, 2.5, 8, COLOR_ACCENT)
            pdf.set_xy(MARGIN_L + 5, y + 1)
            pdf.set_f("", 9)
            pdf.set_text_color(90, 58, 0)
            pdf.multi_cell(CONTENT_W - 8, 5, content)
            pdf.ln(2)
            i += 1
            continue

        # ── Table detection ──
        if stripped.startswith('|') and '|' in stripped[1:]:
            # Collect table lines
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            _render_table(pdf, table_lines)
            pdf.ln(4)
            continue

        # ── Bullet list ──
        if stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('+ '):
            content = _strip_inline(stripped[2:])
            x = MARGIN_L
            y = pdf.get_y()
            # Bullet dot
            pdf.set_fill_color(*COLOR_ACCENT)
            pdf.ellipse(x + 1.5, y + 2.5, 2, 2, style="F")
            # Text
            pdf.set_xy(x + 6, y)
            pdf.set_f("", 9)
            pdf.set_text_color(*COLOR_TEXT)
            pdf.multi_cell(CONTENT_W - 8, 5, content, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            i += 1
            continue

        # ── Numbered list ──
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            num = m.group(1)
            content = _strip_inline(m.group(2))
            x = MARGIN_L
            y = pdf.get_y()
            # Number badge
            pdf.set_fill_color(*COLOR_PRIMARY)
            pdf.set_text_color(*COLOR_SURFACE)
            pdf.set_f("B", 7)
            pdf.set_xy(x, y)
            pdf.cell(6, 5, num, align="C")
            # Text
            pdf.set_xy(x + 8, y)
            pdf.set_f("", 9)
            pdf.set_text_color(*COLOR_TEXT)
            pdf.multi_cell(CONTENT_W - 10, 5, content, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            i += 1
            continue

        # ── Bold paragraph (leading **text**) ──
        if stripped.startswith('**') and '**' in stripped[2:]:
            # Render as semi-heading
            clean = _strip_inline(stripped)
            pdf.set_f("B", 9.5)
            pdf.set_text_color(*COLOR_PRIMARY_MID)
            pdf.multi_cell(CONTENT_W, 5.5, clean, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
            i += 1
            continue

        # ── Normal paragraph ──
        clean = _strip_inline(stripped)
        if clean:
            pdf.set_f("", 9)
            pdf.set_text_color(*COLOR_TEXT)
            pdf.multi_cell(CONTENT_W, 5.5, clean, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1.5)
        i += 1


def _render_table(pdf: TICReport, lines: list):
    """Render a markdown table as a styled PDF table."""
    headers, rows = _parse_table(lines)
    if not headers:
        return

    # Calculate column widths evenly
    n_cols = len(headers)
    col_w = CONTENT_W / n_cols

    # ── Header row ──
    pdf.set_fill_color(*COLOR_PRIMARY)
    pdf.set_text_color(*COLOR_SURFACE)
    pdf.set_f("B", 8.5)
    y = pdf.get_y()
    for j, hdr in enumerate(headers):
        x = MARGIN_L + j * col_w
        pdf.fill_rect(x, y, col_w, 8, COLOR_PRIMARY)
        # Add thin separator between columns
        if j > 0:
            pdf.set_draw_color(*COLOR_PRIMARY_MID)
            pdf.set_line_width(0.1)
            pdf.line(x, y, x, y + 8)
        pdf.set_xy(x + 2, y + 1)
        hdr_clean = _strip_inline(hdr)
        pdf.cell(col_w - 4, 6, hdr_clean[:30], new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_y(y + 8)

    # ── Data rows ──
    for r_idx, row in enumerate(rows):
        # Row height — estimate from content
        row_h = 6.5
        # Alternate background
        bg = COLOR_SURFACE_2 if r_idx % 2 == 0 else COLOR_SURFACE
        y = pdf.get_y()

        # Check if we need a page break
        if y + row_h > A4_H - MARGIN_B - 14:
            pdf.add_page()
            # Re-draw header on new page
            pdf.set_fill_color(*COLOR_PRIMARY)
            pdf.set_text_color(*COLOR_SURFACE)
            pdf.set_f("B", 8.5)
            y = pdf.get_y()
            for j, hdr in enumerate(headers):
                x = MARGIN_L + j * col_w
                pdf.fill_rect(x, y, col_w, 8, COLOR_PRIMARY)
                if j > 0:
                    pdf.set_draw_color(*COLOR_PRIMARY_MID)
                    pdf.set_line_width(0.1)
                    pdf.line(x, y, x, y + 8)
                pdf.set_xy(x + 2, y + 1)
                hdr_clean = _strip_inline(hdr)
                pdf.cell(col_w - 4, 6, hdr_clean[:30], new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.set_y(y + 8)
            y = pdf.get_y()

        for j in range(n_cols):
            cell_text = _strip_inline(row[j]) if j < len(row) else ""
            x = MARGIN_L + j * col_w
            # Cell background
            pdf.fill_rect(x, y, col_w, row_h, bg)
            # Bottom border
            pdf.set_draw_color(*COLOR_BORDER)
            pdf.set_line_width(0.15)
            pdf.line(x, y + row_h, x + col_w, y + row_h)
            # Text
            pdf.set_xy(x + 2, y + 1)
            pdf.set_f("", 8)
            pdf.set_text_color(*COLOR_TEXT)
            # Truncate to avoid overflow
            max_chars = int(col_w / 2.2)
            display = cell_text[:max_chars] + "…" if len(cell_text) > max_chars else cell_text
            pdf.cell(col_w - 4, row_h - 2, display, new_x=XPos.RIGHT, new_y=YPos.TOP)

        pdf.set_y(y + row_h)


def _render_toc(pdf: TICReport, headings: list):
    """Render a Table of Contents page."""
    pdf.add_page()
    # TOC title bar
    y = pdf.get_y()
    pdf.fill_rect(MARGIN_L, y, CONTENT_W, 12, COLOR_PRIMARY)
    pdf.fill_rect(MARGIN_L, y + 12, CONTENT_W, 1.5, COLOR_ACCENT)
    pdf.set_xy(MARGIN_L + 4, y + 2.5)
    pdf.set_f("B", 14)
    pdf.set_text_color(*COLOR_SURFACE)
    pdf.cell(CONTENT_W - 8, 8, "目  录", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    h1_count = 0
    h2_count = 0
    for level, title, _ in headings:
        if level == 1:
            h1_count += 1
            h2_count = 0
            num = f"{h1_count}."
            indent = 0
            pdf.set_f("B", 10.5)
            pdf.set_text_color(*COLOR_PRIMARY)
        elif level == 2:
            h2_count += 1
            num = f"  {h1_count}.{h2_count}"
            indent = 8
            pdf.set_f("", 9.5)
            pdf.set_text_color(*COLOR_TEXT)
        else:
            num = ""
            indent = 18
            pdf.set_f("", 9)
            pdf.set_text_color(*COLOR_TEXT_MUTED)

        # Gold dot for h1
        if level == 1:
            y = pdf.get_y()
            pdf.fill_rect(MARGIN_L, y + 2, 2.5, 2.5, COLOR_ACCENT)

        # Number + title
        x = MARGIN_L + indent + (4 if level == 1 else 0)
        pdf.set_x(x)
        pdf.cell(14, 7, num, new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Dot leaders
        title_w = CONTENT_W - indent - 14 - 14
        pdf.cell(title_w, 7, title[:60], new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Dots
        pdf.set_f("", 8)
        pdf.set_text_color(*COLOR_TEXT_MUTED)
        pdf.cell(10, 7, "···", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if level == 1:
            pdf.ln(1)

    pdf.ln(6)
    # Separator
    pdf.set_draw_color(*COLOR_ACCENT)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN_L, pdf.get_y(), MARGIN_L + 40, pdf.get_y())


def _render_appendix(pdf: TICReport, links: list):
    """Render appendix page with regulation links."""
    if not links:
        return

    pdf.add_page()
    y = pdf.get_y()
    pdf.fill_rect(MARGIN_L, y, CONTENT_W, 12, COLOR_PRIMARY)
    pdf.fill_rect(MARGIN_L, y + 12, CONTENT_W, 1.5, COLOR_ACCENT)
    pdf.set_xy(MARGIN_L + 4, y + 2.5)
    pdf.set_f("B", 14)
    pdf.set_text_color(*COLOR_SURFACE)
    pdf.cell(CONTENT_W - 8, 8, "附录：法规原文链接", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    pdf.set_f("", 8)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    pdf.multi_cell(CONTENT_W, 5, "以下为报告正文中引用的主要法规与标准文件原文链接，供进一步核查参考。", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    seen = set()
    idx = 1
    for title, url in links:
        if url in seen:
            continue
        seen.add(url)

        y = pdf.get_y()
        # Alternating background
        if idx % 2 == 0:
            pdf.fill_rect(MARGIN_L, y, CONTENT_W, 10, COLOR_SURFACE_2)

        # Index badge
        pdf.set_fill_color(*COLOR_PRIMARY_MID)
        pdf.set_text_color(*COLOR_SURFACE)
        pdf.set_f("B", 7)
        pdf.set_xy(MARGIN_L + 2, y + 2)
        pdf.cell(8, 6, str(idx), align="C")

        # Title
        pdf.set_xy(MARGIN_L + 13, y + 2)
        pdf.set_f("B", 8.5)
        pdf.set_text_color(*COLOR_PRIMARY)
        pdf.cell(CONTENT_W * 0.55, 6, title[:60], new_x=XPos.RIGHT, new_y=YPos.TOP)

        # URL (truncated)
        pdf.set_xy(MARGIN_L + 13 + CONTENT_W * 0.55 + 2, y + 2)
        pdf.set_f("", 7)
        pdf.set_text_color(*COLOR_ACCENT)
        url_display = url[:55] + "…" if len(url) > 55 else url
        pdf.cell(CONTENT_W * 0.4 - 15, 6, url_display)

        pdf.set_y(y + 10)
        idx += 1
        if idx > 50:  # cap at 50 links
            break

    # Note
    pdf.ln(8)
    pdf.set_f("", 7.5)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    pdf.multi_cell(CONTENT_W, 5,
        "注：以上链接仅供参考，法规内容可能已更新。请以各官方主管机构发布的最新版本为准。",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(report_text: str, product: str, markets: list) -> str:
    """
    Generate a professional PDF compliance report.

    Args:
        report_text: Markdown-formatted report text from TIC-Agent
        product:     Product description string
        markets:     List of target market strings

    Returns:
        Path to the generated PDF file (in system temp dir)
    """
    report_date = datetime.now().strftime("%Y年%m月%d日")
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Create PDF ──
    pdf = TICReport(product, markets, report_date)

    # ── Page 1: Cover ──
    pdf.add_page()
    pdf.draw_cover()

    # ── Parse headings for TOC ──
    headings = _section_headings(report_text)

    # ── Page 2: Table of Contents ──
    _render_toc(pdf, headings)

    # ── Page 3+: Report body ──
    pdf.add_page()

    # Page body header
    y = pdf.get_y()
    pdf.fill_rect(MARGIN_L, y, CONTENT_W, 10, COLOR_PRIMARY)
    pdf.fill_rect(MARGIN_L, y + 10, CONTENT_W, 1.5, COLOR_ACCENT)
    pdf.set_xy(MARGIN_L + 4, y + 2)
    pdf.set_f("B", 13)
    pdf.set_text_color(*COLOR_SURFACE)
    pdf.cell(CONTENT_W - 8, 7, "合规检查报告正文", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # Product info box
    y = pdf.get_y()
    pdf.fill_rect(MARGIN_L, y, CONTENT_W, 22, COLOR_ACCENT_PALE)
    pdf.fill_rect(MARGIN_L, y, 3, 22, COLOR_ACCENT)
    pdf.set_xy(MARGIN_L + 6, y + 3)
    pdf.set_f("", 8)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    pdf.cell(40, 5, "产品名称")
    pdf.set_xy(MARGIN_L + 6 + 40, y + 3)
    pdf.set_f("B", 9)
    pdf.set_text_color(*COLOR_PRIMARY)
    markets_str = "、".join(markets) if markets else "—"
    prod_display = product[:80] + "…" if len(product) > 80 else product
    pdf.cell(CONTENT_W - 50, 5, prod_display)
    pdf.set_xy(MARGIN_L + 6, y + 11)
    pdf.set_f("", 8)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    pdf.cell(40, 5, "目标市场")
    pdf.set_xy(MARGIN_L + 6 + 40, y + 11)
    pdf.set_f("B", 9)
    pdf.set_text_color(*COLOR_ACCENT)
    pdf.cell(CONTENT_W - 50, 5, markets_str)
    pdf.set_y(y + 22)
    pdf.ln(8)

    # Render markdown body
    _render_body(pdf, report_text)

    # ── Appendix: Links ──
    links = _collect_links(report_text)
    if links:
        _render_appendix(pdf, links)

    # ── Save to temp file ──
    safe_product = re.sub(r'[^\w\u4e00-\u9fff]', '_', product[:20])
    filename = f"TIC_Report_{safe_product}_{date_str}.pdf"
    out_path = os.path.join(tempfile.gettempdir(), filename)
    pdf.output(out_path)

    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# CLI test entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    TEST_REPORT = """
# 蓝牙无线耳机合规分析报告

## 一、产品概述

本报告针对**蓝牙无线耳机（TWS真无线耳塞）**在欧盟市场的合规要求进行系统性分析。

> ⚠️ 本报告由 AI 自动生成，仅供参考，不构成正式合规认证意见。

## 二、适用法规清单

| 法规/标准 | 类别 | 适用范围 | 备注 |
|---------|------|---------|------|
| RED 2014/53/EU | 无线电设备指令 | 蓝牙设备 | 强制 |
| RoHS 2011/65/EU | 有害物质限制 | 电子设备 | 强制 |
| EN 300 328 | 射频标准 | 2.4GHz | 测试 |
| EN 62368-1 | 音视频安全 | 音频设备 | 强制 |

## 三、主要认证要求

### 3.1 CE 认证

产品进入欧盟市场必须获得 CE 认证，涵盖以下三大指令：

1. RED（无线电设备指令）— 射频性能与安全
2. RoHS — 有害物质限制
3. WEEE — 废弃电器处理

### 3.2 测试项目

- 射频辐射（RF Emission）
- 电磁兼容（EMC）
- 电气安全（Electrical Safety）
- 音量限制（SAR / Volume Limiting）

## 四、合规建议

**建议优先认证路径：**

1. 委托第三方认证机构（SGS/TÜV/Intertek）进行预评估
2. 完成 EN 300 328 射频测试
3. 申请 CE 技术文件并签署符合性声明（DoC）

更多信息参见 [欧盟 RED 指令官方页面](https://ec.europa.eu/growth/sectors/electrical-engineering/red-directive_en) 和 [ETSI 标准下载](https://www.etsi.org/standards)。
"""
    out = generate_pdf(TEST_REPORT, "蓝牙无线耳机（TWS真无线耳塞）", ["欧盟"])
    print(f"PDF generated: {out}")
