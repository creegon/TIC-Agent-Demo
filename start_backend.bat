@echo off
cd /d D:\TIC-Agent-Demo
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
