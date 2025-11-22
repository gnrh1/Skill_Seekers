#!/usr/bin/env python3
import json
import re

content = open('.factory/OUTPUT_CONTRACTS.md').read()
json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)

print(f"Total JSON blocks: {len(json_blocks)}\n")

valid_count = 0
failed_blocks = []

for i, block in enumerate(json_blocks, 1):
    try:
        json.loads(block)
        valid_count += 1
        print(f"✅ Block {i:2d}: VALID")
    except json.JSONDecodeError as e:
        failed_blocks.append((i, e))
        print(f"❌ Block {i:2d}: {str(e)[:60]}")

print(f"\n{'='*60}")
print(f"Summary: {valid_count}/{len(json_blocks)} blocks are valid JSON")
print(f"{'='*60}")

if failed_blocks:
    print(f"\nFailed blocks details:")
    for block_num, error in failed_blocks:
        print(f"\nBlock {block_num}:")
        block = json_blocks[block_num - 1]
        lines = block.split('\n')
        error_line = error.lineno - 1
        
        # Show context around error
        start = max(0, error_line - 2)
        end = min(len(lines), error_line + 3)
        
        for j in range(start, end):
            marker = ">>> " if j == error_line else "    "
            print(f"{marker}{j+1:3d}: {lines[j][:70]}")
        
        print(f"       Error: {error}")
