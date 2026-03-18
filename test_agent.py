# -*- coding: utf-8 -*-
# test_agent.py - Quick test script

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from agent import run_agent_stream

def test_case(product, markets, extra="", label=""):
    print(f"\n{'='*60}")
    print(f"TEST: {label or product} + {markets}")
    print('='*60)
    
    output_parts = []
    for chunk in run_agent_stream(product, markets, extra):
        print(chunk, end='', flush=True)
        output_parts.append(chunk)
        if len(''.join(output_parts)) > 12000:
            print("\n... [output truncated for test] ...")
            break
    
    full_output = ''.join(output_parts)
    
    # Check for real standard numbers
    import re
    standard_pattern = re.compile(
        r'\b(EN|IEC|ISO|GB|UL|ASTM|ANSI|JIS)\s*\d+[\d\-/\.]*\b|'
        r'\b\d{4}/\d+/EC\b|'
        r'\b\d{4}/\d+/EU\b',
        re.IGNORECASE
    )
    standards_found = standard_pattern.findall(full_output)
    
    print(f"\n\n[TEST RESULT]")
    print(f"  Output length: {len(full_output)} chars")
    print(f"  Standard numbers found: {standards_found[:10]}")
    print(f"  PASS: {'YES' if len(full_output) > 1000 else 'NO - output too short'}")
    return full_output


if __name__ == '__main__':
    test_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    if test_num == 1:
        test_case(
            "蓝牙无线耳机（TWS真无线耳塞）",
            ["欧盟"],
            "支持蓝牙5.3，内置锂电池250mAh，5W充电",
            "蓝牙耳机+欧盟"
        )
    elif test_num == 2:
        test_case(
            "儿童毛绒玩具（3岁以上）",
            ["美国"],
            "填充聚酯纤维，面料涤纶，无电子元件",
            "儿童毛绒玩具+美国"
        )
    elif test_num == 3:
        test_case(
            "锂电池移动电源（充电宝）",
            ["中国", "欧盟"],
            "容量20000mAh，支持PD 65W快充",
            "锂电移动电源+中国+欧盟"
        )
    elif test_num == 4:
        test_case(
            "不锈钢双层真空保温杯",
            ["日本"],
            "食品级304不锈钢，容量500ml",
            "不锈钢保温杯+日本"
        )
