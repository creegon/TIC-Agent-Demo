"""Test with port 8001 (new backend with updated prompts)"""
import requests
import json

url = "http://127.0.0.1:8001/api/analyze"
payload = {"product": "蓝牙耳机", "markets": ["欧盟", "美国"], "detail_level": "standard"}

print(f"Calling {url}...")
resp = requests.post(url, json=payload, stream=True, timeout=300)
resp.raise_for_status()

report_text = ""
for line in resp.iter_lines(decode_unicode=True):
    if not line or not line.startswith("data: "):
        continue
    raw = line[6:]
    if raw == "[DONE]":
        break
    try:
        evt = json.loads(raw)
    except json.JSONDecodeError:
        continue
    if "report" in evt and evt["report"]:
        report_text = evt["report"]

with open("test_report_8001.md", "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"Report: {len(report_text)} chars")
print(f"Has SAR: {'SAR' in report_text}")
print(f"Has RF Exposure: {'RF Exposure' in report_text or 'RF exposure' in report_text or 'rf exposure' in report_text.lower()}")
print(f"Has references: {'参考来源' in report_text or 'References' in report_text}")
print(f"Has 2026: {'2026' in report_text}")
print(f"Has IEC 62136: {'62136' in report_text}")
