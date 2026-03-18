# app.py - Gradio frontend for TIC Compliance Agent
# Usage: python app.py

import gradio as gr
from agent import run_agent_stream

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS - Clean enterprise SaaS style (NOT Gradio default purple/rainbow)
# ─────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* ── Global reset ── */
:root {
    --primary:      #1a3a5c;   /* Deep navy */
    --primary-light:#2563a8;   /* Accent blue */
    --accent:       #0d7a5f;   /* Trust green (TIC color) */
    --bg:           #f8f9fb;   /* Off-white background */
    --surface:      #ffffff;   /* Card white */
    --border:       #dce3ec;   /* Subtle border */
    --text:         #1e2d3d;   /* Dark text */
    --text-muted:   #64748b;   /* Muted text */
    --danger:       #c0392b;
    --warning:      #d97706;
    --success:      #0d7a5f;
    --radius:       6px;
    --shadow:       0 1px 4px rgba(0,0,0,0.08);
}

body, .gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
                 'Microsoft YaHei', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Kill Gradio's default theme colors ── */
.gradio-container .gr-button-primary,
button.primary {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #fff !important;
    border-radius: var(--radius) !important;
    font-weight: 500 !important;
    transition: background 0.15s !important;
}
button.primary:hover {
    background: var(--primary-light) !important;
    border-color: var(--primary-light) !important;
}

button.secondary {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
    font-weight: 400 !important;
}
button.secondary:hover {
    border-color: var(--primary-light) !important;
    color: var(--primary-light) !important;
    background: #f0f5ff !important;
}

/* ── Header ── */
.tic-header {
    background: var(--primary);
    color: white;
    padding: 18px 28px;
    border-radius: var(--radius);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.tic-header h1 {
    margin: 0;
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: white !important;
}
.tic-header .tagline {
    font-size: 0.82rem;
    opacity: 0.75;
    margin-top: 3px;
}
.tic-badge {
    background: var(--accent);
    color: white;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 3px;
    font-weight: 600;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

/* ── Panel cards ── */
.panel-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow);
}

/* ── Section labels ── */
.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
    margin-top: 16px;
}

/* ── Input fields ── */
.gradio-container input[type="text"],
.gradio-container textarea,
.gradio-container select {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    font-size: 0.92rem !important;
    transition: border-color 0.15s !important;
}
.gradio-container input[type="text"]:focus,
.gradio-container textarea:focus {
    border-color: var(--primary-light) !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 168, 0.12) !important;
}

/* ── Checkboxgroup ── */
.gradio-container .wrap {
    gap: 8px !important;
}
.gradio-container .wrap label {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 5px 12px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    font-size: 0.88rem !important;
    background: var(--surface) !important;
    color: var(--text) !important;
}
.gradio-container .wrap label:hover {
    border-color: var(--primary-light) !important;
    background: #f0f5ff !important;
}

/* ── Example buttons row ── */
.example-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 8px;
}
.example-chip {
    font-size: 0.82rem !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    border: 1px solid var(--border) !important;
    background: #f0f5ff !important;
    color: var(--primary) !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    font-weight: 500 !important;
}
.example-chip:hover {
    background: var(--primary) !important;
    color: white !important;
    border-color: var(--primary) !important;
}

/* ── Output area ── */
.output-area .prose,
.output-area .markdown-body {
    font-size: 0.92rem !important;
    line-height: 1.7 !important;
    color: var(--text) !important;
}

/* Tables in output */
.output-area table {
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 0.88rem !important;
    margin: 12px 0 !important;
}
.output-area th {
    background: var(--primary) !important;
    color: white !important;
    padding: 8px 12px !important;
    text-align: left !important;
    font-weight: 500 !important;
}
.output-area td {
    padding: 7px 12px !important;
    border-bottom: 1px solid var(--border) !important;
}
.output-area tr:nth-child(even) td {
    background: var(--bg) !important;
}

/* Code blocks in output */
.output-area code {
    background: #f0f4f8 !important;
    padding: 2px 5px !important;
    border-radius: 3px !important;
    font-size: 0.85em !important;
    color: var(--primary) !important;
}

/* ── Status indicator ── */
.status-bar {
    font-size: 0.8rem;
    color: var(--text-muted);
    padding: 8px 0;
    border-top: 1px solid var(--border);
    margin-top: 12px;
}

/* ── Footer ── */
.tic-footer {
    text-align: center;
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 20px;
    padding: 12px;
    border-top: 1px solid var(--border);
}

/* ── Hide Gradio footer ── */
footer { display: none !important; }

/* ── Progress / streaming ── */
.generating {
    color: var(--accent) !important;
    font-style: italic;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 16px 0 !important;
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
# Agent streaming wrapper for Gradio
# ─────────────────────────────────────────────────────────────────────────────
def run_compliance_check(product: str, markets: list, extra_info: str):
    """
    Gradio generator function - yields incremental text for streaming display.
    """
    if not product or not product.strip():
        yield "❌ 请输入产品描述"
        return
    
    if not markets:
        yield "❌ 请选择至少一个目标市场"
        return
    
    accumulated = ""
    try:
        for chunk in run_agent_stream(product, markets, extra_info or ""):
            accumulated += chunk
            yield accumulated
    except Exception as e:
        error_text = f"\n\n❌ **运行出错**：{str(e)}\n\n请检查：\n1. 本地代理是否运行（http://127.0.0.1:8046）\n2. BRAVE_API_KEY 是否配置"
        yield accumulated + error_text


def fill_example(example_idx: int):
    """Fill form with example data."""
    if 0 <= example_idx < len(EXAMPLES):
        ex = EXAMPLES[example_idx]
        return ex["product"], ex["markets"], ex["extra"]
    return "", [], ""


# ─────────────────────────────────────────────────────────────────────────────
# Build Gradio UI
# ─────────────────────────────────────────────────────────────────────────────
def build_ui():
    with gr.Blocks(title="TIC-Agent | 智能合规检查助手") as demo:
        
        # ── Header ──
        gr.HTML("""
        <div class="tic-header">
            <div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <h1>TIC-Agent &nbsp;|&nbsp; 智能合规检查助手</h1>
                    <span class="tic-badge">DEMO</span>
                </div>
                <div class="tagline">
                    输入产品描述和目标市场，自动搜索适用法规，生成结构化合规报告
                </div>
            </div>
        </div>
        """)
        
        # ── Main layout: left input | right output ──
        with gr.Row(equal_height=False):
            
            # ── Left Panel: Inputs ──
            with gr.Column(scale=4, min_width=320):
                
                gr.HTML('<div class="section-label">产品信息</div>')
                
                product_input = gr.Textbox(
                    label="产品描述",
                    placeholder="例如：蓝牙无线耳机、儿童毛绒玩具、锂电池移动电源...",
                    lines=2,
                    max_lines=4,
                )
                
                market_input = gr.CheckboxGroup(
                    choices=MARKET_CHOICES,
                    label="目标市场",
                    value=[],
                )
                
                extra_input = gr.Textbox(
                    label="补充信息（可选）",
                    placeholder="材质、功率、电池容量、目标用户群等...",
                    lines=2,
                    max_lines=3,
                )
                
                # ── Example quick-fill buttons ──
                gr.HTML('<div class="section-label" style="margin-top:20px;">快速示例</div>')
                
                with gr.Row():
                    ex_btns = []
                    for i, ex in enumerate(EXAMPLES):
                        btn = gr.Button(
                            ex["label"],
                            variant="secondary",
                            size="sm",
                            elem_classes=["example-chip"],
                        )
                        ex_btns.append(btn)
                
                gr.HTML('<div style="margin-top: 20px;"></div>')
                
                # ── Action buttons ──
                with gr.Row():
                    submit_btn = gr.Button(
                        "生成合规报告",
                        variant="primary",
                        scale=3,
                    )
                    clear_btn = gr.Button(
                        "清空",
                        variant="secondary",
                        scale=1,
                    )
                
                # ── Info box ──
                gr.HTML("""
                <div style="
                    margin-top: 20px;
                    padding: 12px 14px;
                    background: #f0f7ff;
                    border-left: 3px solid #2563a8;
                    border-radius: 4px;
                    font-size: 0.82rem;
                    color: #1e3a5c;
                    line-height: 1.6;
                ">
                    <strong>使用说明</strong><br>
                    Agent 将自动：分析产品类别 → 搜索适用法规 → 抓取标准详情 → 生成合规报告。
                    完整分析约需 1-3 分钟，搜索过程会实时显示进度。
                </div>
                """)
            
            # ── Right Panel: Output ──
            with gr.Column(scale=6, min_width=400, elem_classes=["output-area"]):
                
                gr.HTML('<div class="section-label">合规分析报告</div>')
                
                output = gr.Markdown(
                    value="*在左侧填写产品信息，点击「生成合规报告」开始分析...*",
                    height=700,
                    show_label=False,
                )
        
        # ── Footer ──
        gr.HTML("""
        <div class="tic-footer">
            Powered by Gemini Flash &nbsp;·&nbsp; Brave Search &nbsp;·&nbsp; Demo Purpose Only
            &nbsp;&nbsp;|&nbsp;&nbsp;
            ⚠️ 本工具仅供参考，最终合规判定请联系认可检测机构
        </div>
        """)
        
        # ─────────────────────────────────────────────────
        # Event handlers
        # ─────────────────────────────────────────────────
        
        # Submit button → streaming generation
        submit_btn.click(
            fn=run_compliance_check,
            inputs=[product_input, market_input, extra_input],
            outputs=output,
        )
        
        # Clear button
        clear_btn.click(
            fn=lambda: ("", [], "", "*在左侧填写产品信息，点击「生成合规报告」开始分析...*"),
            inputs=[],
            outputs=[product_input, market_input, extra_input, output],
        )
        
        # Example buttons → fill form
        for i, btn in enumerate(ex_btns):
            idx = i  # capture by value
            btn.click(
                fn=lambda i=idx: fill_example(i),
                inputs=[],
                outputs=[product_input, market_input, extra_input],
            )
    
    return demo


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
        ),
    )
