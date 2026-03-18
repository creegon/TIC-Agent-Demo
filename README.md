# TIC-Agent | 智能合规检查助手

> TIC（Testing, Inspection & Certification）行业合规法规检查工具  
> 输入产品描述和目标市场，AI 自动搜索适用法规标准，生成结构化合规报告

![TODO: 截图占位](_docs/screenshot.png)

---

## ✨ 功能列表

| 功能 | 说明 |
|------|------|
| 🤖 AI 驱动分析 | 基于 Gemini 2.0 Flash，多轮搜索推理 |
| 🌍 多市场覆盖 | EU / US / CN / JP / KR / AU 六大市场 |
| 📋 结构化报告 | Markdown 表格，含风险等级（高/中/低） |
| 📊 数据可视化 | 合规雷达图、认证成本对比、时间线甘特图 |
| 💬 追问功能 | 基于报告上下文的多轮对话 |
| 📥 PDF 导出 | 一键导出合规报告为 PDF |
| 🗄️ 知识库 | 内置法规知识库（CE/FCC/CCC/RoHS/REACH 等） |
| ⚡ 实时流式输出 | SSE 流式传输，实时显示搜索和分析进度 |

---

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 15 + Tailwind CSS + shadcn/ui v4 + Recharts |
| 后端 | FastAPI + SSE (sse-starlette) + Uvicorn |
| AI 模型 | Gemini 2.0 Flash（via Google AI API） |
| 搜索 | Brave Search API |
| PDF | fpdf2 |
| 部署 | Vercel（前端）+ Railway / Render（后端） |

---

## 🚀 本地开发

### 环境要求

- Python 3.12+
- Node.js 18+
- Google AI API Key（Gemini 2.0 Flash）
- Brave Search API Key

### 1. 克隆项目

```bash
git clone https://github.com/creegon/TIC-Agent-Demo.git
cd TIC-Agent-Demo
```

### 2. 启动后端

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 配置环境变量（复制示例文件后填入真实 Key）
cp .env.example .env
# 编辑 .env，填入 GOOGLE_AI_API_KEY 和 BRAVE_API_KEY

# 启动后端
uvicorn backend.main:app --reload --port 8000
```

后端运行在 `http://localhost:8000`，API 文档：`http://localhost:8000/docs`

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量（本地开发默认指向 localhost:8000）
# .env.local 已预设，无需修改

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:3000`

---

## 📦 部署

### 前端 → Vercel

1. 将 `frontend/` 目录推送到 GitHub
2. 在 [Vercel Dashboard](https://vercel.com) 导入项目
3. Framework Preset 选 **Next.js**，Root Directory 设为 `frontend`
4. 在 Vercel 项目设置 → Environment Variables，添加：
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```
5. 点击 Deploy

### 后端 → Railway

1. 在 [Railway](https://railway.app) 新建项目，连接 GitHub 仓库
2. Railway 会自动检测根目录的 `Dockerfile`
3. 在 Railway 环境变量中添加：
   ```
   GOOGLE_AI_API_KEY=your_google_ai_api_key
   BRAVE_API_KEY=your_brave_api_key
   ```
4. 部署完成后，复制后端 URL 填入 Vercel 的 `NEXT_PUBLIC_API_URL`

### 后端 → Render（备选）

1. 在 [Render](https://render.com) 新建 Web Service
2. 连接仓库，Render 会读取根目录的 `render.yaml`
3. 在 Render 环境变量中添加 `GOOGLE_AI_API_KEY` 和 `BRAVE_API_KEY`

---

## 🔑 环境变量

| 变量 | 位置 | 说明 |
|------|------|------|
| `GOOGLE_AI_API_KEY` | 后端（.env / Railway） | Google AI Studio API Key，用于 Gemini 2.0 Flash |
| `BRAVE_API_KEY` | 后端（.env / Railway） | Brave Search API Key，用于合规信息检索 |
| `NEXT_PUBLIC_API_URL` | 前端（.env.local / Vercel） | 后端 API 地址，默认 `http://127.0.0.1:8000` |

---

## 📁 项目结构

```
TIC-Agent-Demo/
├── agent.py              # Agent 核心逻辑（Gemini function calling）
├── tools.py              # 搜索工具 + 网页抓取
├── prompts.py            # System prompt + 搜索模板
├── knowledge_base.py     # 内置法规知识库
├── export_pdf.py         # PDF 导出
├── requirements.txt      # 根目录依赖（可选）
├── Dockerfile            # 后端 Docker 镜像（项目根为工作目录）
├── railway.toml          # Railway 部署配置
├── render.yaml           # Render 部署配置
├── backend/
│   ├── main.py           # FastAPI 应用 + SSE 端点
│   └── requirements.txt  # 后端依赖
└── frontend/
    ├── src/
    │   ├── app/page.tsx  # 主页面
    │   ├── components/   # UI 组件
    │   └── lib/          # API 客户端 + 工具函数
    └── package.json
```

---

## 📸 截图

> TODO: 添加截图

---

## ⚠️ 免责声明

本工具仅供演示和参考使用。**最终合规判定必须由 SGS、BV、TÜV Rheinland 等经认可的第三方检测机构进行专业评估。** 法规要求持续更新，请以官方最新版本为准。

---

*Powered by Gemini 2.0 Flash · Brave Search · Demo Purpose Only*
