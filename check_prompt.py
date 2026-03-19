from prompts import SYSTEM_PROMPT
print(f"SYSTEM_PROMPT length: {len(SYSTEM_PROMPT)} chars")
print(f"Contains SAR: {'SAR' in SYSTEM_PROMPT}")
print(f"Contains 参考来源: {'参考来源' in SYSTEM_PROMPT}")
print(f"Contains 2026年8月: {'2026年8月' in SYSTEM_PROMPT}")
print(f"\n--- Last 300 chars ---")
print(SYSTEM_PROMPT[-300:])
