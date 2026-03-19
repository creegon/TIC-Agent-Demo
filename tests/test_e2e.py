"""End-to-end test: call /api/analyze and collect SSE output"""
import requests
import json
import sys

url = "http://127.0.0.1:8000/api/analyze"
payload = {
    "product": "蓝牙耳机",
    "markets": ["欧盟", "美国"],
    "detail_level": "standard"
}

print(f"=== Calling {url} ===")
print(f"Product: {payload['product']}, Markets: {payload['markets']}")
print()

try:
    resp = requests.post(url, json=payload, stream=True, timeout=180)
    resp.raise_for_status()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

report_text = ""
search_steps = []
charts_data = None
errors = []

for line in resp.iter_lines(decode_unicode=True):
    if not line or not line.startswith("data: "):
        continue
    raw = line[6:]
    if raw == "[DONE]":
        print("\n=== [DONE] ===")
        break
    try:
        evt = json.loads(raw)
    except json.JSONDecodeError:
        continue
    
    etype = evt.get("type", "")
    
    if etype == "search_step":
        step = evt.get("step", {})
        msg = step.get("message", "")
        search_steps.append(msg)
        print(f"[search] {msg}")
    elif etype == "report_chunk":
        chunk = evt.get("text", "")
        report_text += chunk
        sys.stdout.write(".")
        sys.stdout.flush()
    elif etype == "report_done":
        charts_data = evt.get("chartsData")
        print(f"\n[report_done] chartsData keys: {list(charts_data.keys()) if charts_data else 'None'}")
    elif etype == "error":
        errors.append(evt.get("message", "unknown"))
        print(f"\n[ERROR] {evt.get('message')}")
    else:
        print(f"[{etype}] {json.dumps(evt, ensure_ascii=False)[:100]}")

print(f"\n{'='*60}")
print(f"Search steps: {len(search_steps)}")
print(f"Report length: {len(report_text)} chars")
print(f"Charts data: {bool(charts_data)}")
print(f"Errors: {errors}")

if report_text:
    # Save report for inspection
    with open("test_report_output.md", "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nReport saved to test_report_output.md")
    
    # Show first 500 chars
    print(f"\n--- Report preview (first 500 chars) ---")
    print(report_text[:500])
    
    # Show charts summary
    if charts_data:
        print(f"\n--- Charts Data Summary ---")
        for k, v in charts_data.items():
            if v is None:
                print(f"  {k}: None (no data extracted)")
            elif isinstance(v, list):
                print(f"  {k}: {len(v)} items")
                for item in v[:3]:
                    print(f"    {json.dumps(item, ensure_ascii=False)[:120]}")
            else:
                print(f"  {k}: {type(v).__name__}")
