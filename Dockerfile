# TIC-Agent Backend Dockerfile
# Build context: project root (D:\TIC-Agent-Demo\)
# Usage:
#   docker build -t tic-agent-backend .
#   docker run -p 8000:8000 \
#     -e GOOGLE_AI_API_KEY=... \
#     -e BRAVE_API_KEY=... \
#     tic-agent-backend

FROM python:3.12-slim

# Set working directory to project root (backend/main.py imports from parent dir)
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (layer caching)
COPY backend/requirements.txt backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.111.0 \
    "uvicorn[standard]>=0.29.0" \
    sse-starlette>=1.8.2 \
    pydantic>=2.0.0 \
    openai>=1.30.0 \
    requests>=2.31.0 \
    beautifulsoup4>=4.12.0 \
    fpdf2>=2.7.9 \
    python-dotenv>=1.0.0 \
    lxml>=5.1.0

# Copy entire project (agent.py, tools.py, etc. are in root)
COPY . .

# Expose port
EXPOSE 8000

# Run backend — module path: backend.main, working dir: /app (project root)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
