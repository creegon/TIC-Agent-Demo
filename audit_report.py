"""Run a real analysis and audit every aspect of the output"""
import requests, json

r = requests.post('http://127.0.0.1:8001/api/analyze',
    json={'product': '儿童蓝牙耳机', 'markets': ['US', 'EU'], 'extra_info': '适用年龄3-12岁'},
    stream=True, headers={'Content-Type': 'application/json'})

print('Status:', r.status_code)

status_lines = []
search_events = []
chunk_lines = []
done_data = None
current_event = None

for line in r.iter_lines(decode_unicode=True):
    if line.startswith('event:'):
        current_event = line.split(':', 1)[1].strip()
    elif line.startswith('data:'):
        payload = line[5:].strip()
        if current_event == 'status':
            status_lines.append(payload)
        elif current_event == 'chunk':
            chunk_lines.append(payload)
        elif current_event == 'viz' and payload.startswith('{'):
            try:
                d = json.loads(payload)
                if d.get('type') == 'search_results':
                    search_events.append(d)
            except: pass
        elif current_event == 'done' and payload.startswith('{'):
            try:
                done_data = json.loads(payload)
            except: pass

print(f"\n{'='*60}")
print(f"AUDIT: 儿童蓝牙耳机 US+EU")
print(f"{'='*60}")

print(f"\n--- 搜索过程 ---")
print(f"搜索轮数: {len(search_events)}")
for i, se in enumerate(search_events):
    print(f"  Round {se.get('round')}: '{se.get('query','')[:60]}'")
    print(f"    原始结果: {se.get('raw_count')}, 过滤后: {se.get('filtered_count')}, 最终: {se.get('result_count')}")
    for src in se.get('sources', []):
        print(f"    - {src.get('domain')} [{src.get('tier','?')}]")

print(f"\n--- 报告内容 ---")
report = done_data.get('report', '') if done_data else ''
print(f"报告长度: {len(report)} chars")
# Count tables
table_count = report.count('| 字段 |')
print(f"法规表格数: {table_count}")
# Check for "待核实"
uncertain = report.count('待核实')
print(f"'待核实'出现次数: {uncertain}")
# Check for real standard numbers
import re
standards = re.findall(r'EN\s+\d+|IEC\s+\d+|ASTM\s+[A-Z]\d+|CPSIA|CPSC|FCC|47\s+CFR', report)
print(f"标准号提及: {len(standards)} ({list(set(standards))[:10]})")

print(f"\n--- 图表数据审查 ---")
if done_data:
    charts = done_data.get('charts', {})
    
    print(f"\n  Radar (评分):")
    radar = charts.get('radar', [])
    for r in radar:
        print(f"    {r['subject']}: {r['score']}/100 — 依据: {r.get('reason','?')}")
    if radar:
        print(f"  ⚠️ 问题: 评分是基于关键词命中数量，不是真实评估！")
    
    print(f"\n  Cost (费用):")
    costs = charts.get('costs')
    if costs:
        for c in costs:
            print(f"    {c['market']}: testing={c.get('testingFee')}, cert={c.get('certFee')}, annual={c.get('annualFee')}")
        print(f"  ⚠️ 问题: 费用是写死的默认值还是从报告提取的？")
    else:
        print(f"    无费用数据")
    
    print(f"\n  Timeline (时间线):")
    timeline = charts.get('timeline', [])
    for t in (timeline or []):
        print(f"    {t.get('name')}: week {t.get('start')}-{t.get('start',0)+t.get('duration',0)}")
    if timeline:
        print(f"  ⚠️ 问题: 时间线是写死模板还是从报告提取的？")

print(f"\n--- 专业人士会质疑的点 ---")
print("1. 雷达图评分没有评分方法论说明")
print("2. 费用数据没有标注来源（哪篇文章/哪个机构报价）")
print("3. 搜索结果没有标注哪些是官方来源、哪些是商业文章")
print("4. 报告里的标准号是否真实存在、版本是否最新？")
print("5. '行业参考'太模糊，专业人士需要知道参考的是什么")
print("6. 缺少：法规原文链接、认证机构官网链接")
print("7. 缺少：该产品的特殊要求（儿童产品的额外安全标准）")
