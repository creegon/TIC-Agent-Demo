"""End-to-end test v2: capture ALL SSE event types"""
import requests
import json
import sys

url = "http://127.0.0.1:8000/api/analyze"
payload = {
    "product": "蓝牙耳机",
    "markets": ["欧盟", "美国"],
    "detail_level": "standard"
}

print(f"Calling {url}...")

resp = requests.post(url, json=payload, stream=True, timeout=300)
resp.raise_for_status()

all_events = []
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
    
    all_events.append(evt)
    etype = evt.get("type", "")
    
    # Capture report from whichever field has it
    if "report" in evt and evt["report"]:
        report_text = evt["report"]
    elif etype == "report_chunk" and "text" in evt:
        report_text += evt["text"]

print(f"Total events: {len(all_events)}")
print(f"Event types: {[e.get('type','?') for e in all_events]}")
print(f"Report length: {len(report_text)} chars")

if report_text:
    with open("test_report_output.md", "w", encoding="utf-8") as f:
        f.write(report_text)
    print("Saved to test_report_output.md")
    
    # Extract chartsData from the report event
    for evt in all_events:
        if "chartsData" in evt:
            cd = evt["chartsData"]
            print(f"\nchartsData:")
            if cd:
                for k, v in cd.items():
                    if v is None:
                        print(f"  {k}: None")
                    elif isinstance(v, list):
                        print(f"  {k}: {len(v)} items")
                        for item in v[:5]:
                            print(f"    {json.dumps(item, ensure_ascii=False)}")
                    else:
                        print(f"  {k}: {v}")
            break
else:
    print("NO REPORT CAPTURED")
    # Dump all events for debug
    for i, evt in enumerate(all_events):
        print(f"\nEvent {i}: type={evt.get('type','?')}")
        s = json.dumps(evt, ensure_ascii=False)
        print(s[:300])
