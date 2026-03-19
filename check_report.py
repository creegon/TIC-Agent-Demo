# -*- coding: utf-8 -*-
import sys

with open('D:/TIC-Agent-Demo/test_report_output.md', encoding='utf-8') as f:
    content = f.read()

print("=== Report length:", len(content), "chars ===\n")

# Check 1: SAR / RF Exposure in FCC section
has_sar = 'SAR' in content
has_rf_exposure = 'RF Exposure' in content
print(f"[1] SAR present: {has_sar}")
print(f"[1] RF Exposure present: {has_rf_exposure}")

# Check 2: References section
has_refs = any(x in content for x in ['参考来源', '参考文献', '[1]', '[2]', '[3]'])
print(f"\n[2] References present: {has_refs}")
# Show relevant lines
for line in content.split('\n'):
    if any(x in line for x in ['参考', '[1]', '[2]', '[3]']):
        print(f"  -> {repr(line)}")

# Check 3: RED cybersecurity date
has_2026_aug = '2026年8月' in content or ('2026' in content and '8月' in content)
has_2024 = '2024年起' in content or '2024年8月' in content
print(f"\n[3] Has 2026年8月: {has_2026_aug}")
print(f"[3] Has 2024年起/2024年8月: {has_2024}")
# Show relevant lines with 2026 or dates
for line in content.split('\n'):
    if '2026' in line or '网络安全' in line or 'Cyber' in line.lower():
        print(f"  -> {repr(line)}")

# Check 4: Fake standard IEC 62136
has_fake = '62136' in content
print(f"\n[4] IEC 62136 present (fake standard): {has_fake}")

print("\n=== DONE ===")
