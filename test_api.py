import requests, json

r = requests.post('http://127.0.0.1:8000/api/analyze',
    json={'product': 'TWS蓝牙耳机', 'markets': ['EU', 'US'], 'extra_info': ''},
    stream=True, headers={'Content-Type': 'application/json'})

print('Status:', r.status_code)

done_data = None
search_events = []
status_lines = []

for line in r.iter_lines(decode_unicode=True):
    if line.startswith('data:'):
        payload = line[5:].strip()
        if payload.startswith('{'):
            try:
                d = json.loads(payload)
                if 'report' in d and 'charts' in d:
                    done_data = d
                if d.get('type') == 'search_results':
                    search_events.append(d)
            except:
                pass
        else:
            status_lines.append(payload[:100])

print(f"\n=== Status lines: {len(status_lines)}")
for s in status_lines[:10]:
    print(f"  {s}")

print(f"\n=== Search events: {len(search_events)}")
for s in search_events[:5]:
    q = s.get('query', '')[:60]
    rc = s.get('result_count', 0)
    sources = s.get('sources', [])
    print(f"  Round {s.get('round')}: '{q}' -> {rc} results")
    for src in sources[:3]:
        print(f"    - {src.get('domain')} ({src.get('tier')})")

print()
if done_data:
    charts = done_data.get('charts', {})
    print("=== Charts data:")
    radar = charts.get('radar', [])
    print(f"  Radar items: {len(radar)}")
    for item in radar:
        print(f"    {item}")
    costs = charts.get('costs', [])
    print(f"  Cost items: {len(costs)}")
    for item in costs[:5]:
        print(f"    {item}")
    timeline = charts.get('timeline', [])
    print(f"  Timeline items: {len(timeline)}")
    for item in timeline[:5]:
        print(f"    {item}")
    report = done_data.get('report', '')
    print(f"  Report length: {len(report)} chars")
    print(f"  Report preview: {report[:200]}")
else:
    print("NO done_data found!")
