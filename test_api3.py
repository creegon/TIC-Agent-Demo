"""Capture full error message from SSE"""
import requests

r = requests.post('http://127.0.0.1:8000/api/analyze',
    json={'product': 'USB充电器', 'markets': ['EU'], 'extra_info': ''},
    stream=True, headers={'Content-Type': 'application/json'})

print('Status:', r.status_code)
for line in r.iter_lines(decode_unicode=True):
    if line.startswith('data:'):
        payload = line[5:].strip()
        if '模型调用失败' in payload or 'error' in payload.lower() or 'INVALID' in payload:
            print("ERROR LINE:", payload)
