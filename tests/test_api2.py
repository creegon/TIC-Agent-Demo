import requests, json

r = requests.post('http://127.0.0.1:8000/api/analyze',
    json={'product': 'USB充电器', 'markets': ['EU'], 'extra_info': ''},
    stream=True, headers={'Content-Type': 'application/json'})

print('Status:', r.status_code)

all_lines = []
for line in r.iter_lines(decode_unicode=True):
    all_lines.append(line)

# Parse SSE properly
current_event = None
events = []
for line in all_lines:
    if line.startswith('event:'):
        current_event = line.split(':', 1)[1].strip()
    elif line.startswith('data:'):
        payload = line[5:].strip()
        events.append({'event': current_event, 'data': payload[:200]})
    elif line == '':
        current_event = None

print(f"\nTotal events: {len(events)}")
for e in events:
    print(f"  [{e['event']}] {e['data'][:150]}")

# Find done event
for e in events:
    if e['event'] == 'done':
        print(f"\n=== DONE event data (full):")
        # re-parse from all_lines
        for i, line in enumerate(all_lines):
            if line.startswith('data:') and '"report"' in line and '"charts"' in line:
                try:
                    d = json.loads(line[5:].strip())
                    charts = d.get('charts', {})
                    print(f"  charts keys: {list(charts.keys())}")
                    for k, v in charts.items():
                        if isinstance(v, list):
                            print(f"  {k}: {len(v)} items")
                            for item in v[:3]:
                                print(f"    {item}")
                        else:
                            print(f"  {k}: {v}")
                except Exception as ex:
                    print(f"  Parse error: {ex}")
        break
