#!/usr/bin/env python3
"""
Rapid Memory Stress Test - Aggressive 30-second test
"""

import gc
import psutil
import time
import sys
import json
from datetime import datetime

process = psutil.Process()
start_time = time.time()

def get_memory():
    return process.memory_info().rss / (1024 * 1024)

print("🚀 RAPID MEMORY STRESS TEST - 30 SECONDS")
print(f"💾 Starting memory: {get_memory():.1f}MB")
print("=" * 60)

try:
    # Test 1: Massive list creation (10 seconds)
    print("\n📊 Test 1: Massive list allocation...")
    start_mem = get_memory()
    huge_lists = []

    for i in range(200):
        lst = [0] * 50000  # 50K elements
        huge_lists.append(lst)
        if i % 20 == 0:
            current = get_memory()
            print(f"  Lists {i}: {current:.1f}MB (+{current-start_mem:.1f}MB)")

        if time.time() - start_time > 10:
            break

    peak1 = get_memory()
    print(f"✅ Peak after lists: {peak1:.1f}MB (+{peak1-start_mem:.1f}MB)")

    # Test 2: Deep recursion (8 seconds)
    print("\n🔁 Test 2: Deep recursion...")
    rec_start = get_memory()

    def deep_recursion(depth):
        if depth <= 0:
            return [0] * 1000
        return [deep_recursion(depth-1) for _ in range(2)]

    try:
        result = deep_recursion(15)  # 2^15 = 32768 leaf nodes
        rec_peak = get_memory()
        print(f"✅ Recursion peak: {rec_peak:.1f}MB (+{rec_peak-rec_start:.1f}MB)")
        del result
    except (RecursionError, MemoryError):
        print("⚠️  Recursion limit/memory error")

    # Test 3: Circular references (7 seconds)
    print("\n🔄 Test 3: Circular references...")
    circ_start = get_memory()
    circular_objects = []

    for i in range(100):
        obj1 = {'data': 'x' * 1000, 'ref': None}
        obj2 = {'data': 'y' * 1000, 'ref': obj1}
        obj1['ref'] = obj2  # Circular reference
        circular_objects.append(obj1)

    circ_peak = get_memory()
    print(f"✅ Circular refs peak: {circ_peak:.1f}MB (+{circ_peak-circ_start:.1f}MB)")

    # Test 4: Rapid allocation/deallocation cycles (5 seconds)
    print("\n⚡ Test 4: Rapid cycles...")
    cycle_start = get_memory()

    for cycle in range(50):
        temp_data = []
        for j in range(100):
            temp_data.extend([
                [0] * 1000,
                {'key': 'value' * 50},
                'string_data' * 100
            ])
        del temp_data
        if cycle % 10 == 0:
            gc.collect()

    cycle_peak = get_memory()
    print(f"✅ Cycles peak: {cycle_peak:.1f}MB (+{cycle_peak-cycle_start:.1f}MB)")

except MemoryError:
    print("❌ MEMORY ERROR - System protected!")
except Exception as e:
    print(f"❌ Error: {e}")

# Cleanup phase
print("\n🧹 Cleanup and analysis...")
cleanup_start = get_memory()

try:
    del huge_lists
    del circular_objects
except:
    pass

gc.collect()
final_memory = get_memory()

print(f"📈 FINAL ANALYSIS:")
print(f"   Starting: {start_time:.1f}MB")
print(f"   Peak: {max(start_mem, peak1, rec_peak, circ_peak, cycle_peak):.1f}MB")
print(f"   Final: {final_memory:.1f}MB")
print(f"   Duration: {time.time() - start_time:.1f}s")

memory_leak = final_memory - start_mem
if memory_leak > 10:
    print(f"   ⚠️  MEMORY LEAK: {memory_leak:.1f}MB")
else:
    print(f"   ✅ Memory stable: {memory_leak:+.1f}MB")

# Test completed
print("\n🎯 STRESS TEST COMPLETED")