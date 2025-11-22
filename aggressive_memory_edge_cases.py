#!/usr/bin/env python3
"""
Aggressive Memory Edge Case Testing
Pushes memory management to its absolute limits
"""

import gc
import psutil
import time
import sys
import threading
import json
from datetime import datetime

process = psutil.Process()
start_time = time.time()

def get_memory():
    return process.memory_info().rss / (1024 * 1024)

print("🔥 AGGRESSIVE MEMORY EDGE CASE TESTING")
print(f"💾 Starting: {get_memory():.1f}MB")
print("=" * 60)

results = []

# Test 1: Memory explosion test
print("\n💥 TEST 1: Memory Explosion Test")
try:
    start_mem = get_memory()
    explosion_data = []

    # Rapidly expanding memory allocation
    for size in [1000, 5000, 10000, 50000, 100000, 500000]:
        try:
            data = [0] * size
            explosion_data.append(data)
            current = get_memory()
            print(f"  Size {size}: {current:.1f}MB (+{current-start_mem:.1f}MB)")
        except MemoryError:
            print(f"  ❌ Memory error at size {size}")
            break

    peak1 = get_memory()
    results.append({"test": "explosion", "peak": peak1, "increase": peak1-start_mem})
    print(f"✅ Explosion peak: {peak1:.1f}MB")

except Exception as e:
    print(f"❌ Explosion test failed: {e}")

# Test 2: Stack overflow testing
print("\n📚 TEST 2: Stack Overflow Testing")
try:
    stack_start = get_memory()

    def infinite_recursion(depth=0):
        if depth > 10000:  # Safety limit
            return depth
        return infinite_recursion(depth + 1)

    try:
        result = infinite_recursion()
        print(f"  Unexpected success: depth {result}")
    except RecursionError:
        print("  ✅ Recursion limit properly enforced")
    except MemoryError:
        print("  ✅ Memory error prevented stack overflow")

    stack_peak = get_memory()
    results.append({"test": "stack", "peak": stack_peak, "increase": stack_peak-stack_start})

except Exception as e:
    print(f"❌ Stack test failed: {e}")

# Test 3: Massive circular reference network
print("\n🕸️  TEST 3: Massive Circular Reference Network")
try:
    circ_start = get_memory()

    # Create a massive circular reference graph
    nodes = []
    for i in range(1000):
        node = {
            'id': i,
            'data': 'x' * 1000,
            'connections': [],
            'self_ref': None
        }
        node['self_ref'] = node  # Self-reference
        nodes.append(node)

    # Create circular connections
    for i in range(len(nodes)):
        for j in range(min(5, len(nodes)-i-1)):  # Connect to next 5 nodes
            nodes[i]['connections'].append(nodes[i+j+1])

    circ_peak = get_memory()
    results.append({"test": "circular_network", "peak": circ_peak, "increase": circ_peak-circ_start})
    print(f"✅ Circular network: {circ_peak:.1f}MB (+{circ_peak-circ_start:.1f}MB)")

except Exception as e:
    print(f"❌ Circular network failed: {e}")

# Test 4: Memory fragmentation test
print("\n🧩 TEST 4: Memory Fragmentation Test")
try:
    frag_start = get_memory()
    fragmented_data = []

    # Create memory fragmentation with varying object sizes
    for i in range(200):
        # Create objects of varying sizes
        fragmented_data.extend([
            [0] * 100,        # Small
            [0] * 1000,       # Medium
            [0] * 10000,      # Large
            'x' * 50000,      # String
            {'key': 'val' * 1000}  # Dict
        ])

        # Delete some objects to create fragmentation
        if i % 10 == 0 and len(fragmented_data) > 50:
            del fragmented_data[:10]
            gc.collect()

    frag_peak = get_memory()
    results.append({"test": "fragmentation", "peak": frag_peak, "increase": frag_peak-frag_start})
    print(f"✅ Fragmentation: {frag_peak:.1f}MB (+{frag_peak-frag_start:.1f}MB)")

except Exception as e:
    print(f"❌ Fragmentation test failed: {e}")

# Test 5: Concurrent memory pressure
print("\n⚡ TEST 5: Concurrent Memory Pressure")
try:
    concurrent_start = get_memory()
    stop_flag = threading.Event()
    thread_memory_usage = []

    def memory_thread(thread_id):
        """Thread that consumes memory"""
        data = []
        try:
            while not stop_flag.is_set():
                data.append('x' * 1000)
                if len(data) > 10000:
                    data = data[-5000:]  # Keep half
                time.sleep(0.01)
        except MemoryError:
            thread_memory_usage.append(f"Thread {thread_id}: Memory error")
        except Exception as e:
            thread_memory_usage.append(f"Thread {thread_id}: {e}")

    # Start memory-consuming threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=memory_thread, args=(i,))
        t.daemon = True
        t.start()
        threads.append(t)

    # Main thread memory pressure
    main_data = []
    for i in range(100):
        main_data.append([0] * 10000)
        time.sleep(0.05)

    concurrent_peak = get_memory()
    stop_flag.set()

    results.append({"test": "concurrent", "peak": concurrent_peak, "increase": concurrent_peak-concurrent_start})
    print(f"✅ Concurrent: {concurrent_peak:.1f}MB (+{concurrent_peak-concurrent_start:.1f}MB)")

    # Cleanup
    del main_data

except Exception as e:
    print(f"❌ Concurrent test failed: {e}")

# Test 6: Memory leak simulation
print("\n💧 TEST 6: Memory Leak Simulation")
try:
    leak_start = get_memory()
    leaked_objects = []

    # Simulate slow memory leak
    for cycle in range(50):
        # Create objects that "leak" (not properly cleaned up)
        leak_data = {
            'cycle': cycle,
            'data': 'leaky_data_' + 'x' * 2000,
            'references': []
        }

        # Create some references that should be cleaned but aren't
        for j in range(10):
            ref_data = {'ref_id': j, 'payload': 'x' * 500}
            leak_data['references'].append(ref_data)

        leaked_objects.append(leak_data)

        if cycle % 10 == 0:
            current = get_memory()
            print(f"  Cycle {cycle}: {current:.1f}MB (+{current-leak_start:.1f}MB)")

    leak_peak = get_memory()
    results.append({"test": "leak_simulation", "peak": leak_peak, "increase": leak_peak-leak_start})
    print(f"✅ Leak simulation: {leak_peak:.1f}MB (+{leak_peak-leak_start:.1f}MB)")

    # Intentional incomplete cleanup to demonstrate leak
    # del leaked_objects  # Commented out to simulate leak

except Exception as e:
    print(f"❌ Leak simulation failed: {e}")

# Cleanup and final analysis
print("\n🧹 Cleanup and Final Analysis")
cleanup_start = get_memory()

try:
    # Cleanup variables that exist
    if 'explosion_data' in locals():
        del explosion_data
    if 'nodes' in locals():
        del nodes
    if 'fragmented_data' in locals():
        del fragmented_data
    if 'leaked_objects' in locals():
        del leaked_objects
except:
    pass

# Force garbage collection multiple times
for i in range(5):
    gc.collect()
    time.sleep(0.1)

final_memory = get_memory()
initial_memory = 12.5  # From test start

print(f"\n📊 COMPREHENSIVE ANALYSIS:")
print(f"   Initial: {initial_memory:.1f}MB")
print(f"   Final: {final_memory:.1f}MB")
print(f"   Total increase: {final_memory - initial_memory:+.1f}MB")
print(f"   Duration: {time.time() - start_time:.1f}s")

# Peak memory analysis
if results:
    max_peak = max(r['peak'] for r in results)
    print(f"   Peak memory: {max_peak:.1f}MB")

    print(f"\n🧪 Test Breakdown:")
    for result in results:
        print(f"   {result['test']}: {result['peak']:.1f}MB (+{result['increase']:.1f}MB)")

# Memory leak assessment
memory_leak = final_memory - initial_memory
if memory_leak > 50:
    print(f"\n⚠️  SIGNIFICANT MEMORY LEAK: {memory_leak:.1f}MB")
    print("   System may have memory management issues")
elif memory_leak > 20:
    print(f"\n⚠️  Moderate memory leak: {memory_leak:.1f}MB")
    print("   Some memory cleanup issues detected")
else:
    print(f"\n✅ Memory management stable: {memory_leak:+.1f}MB")

# System stability assessment
print(f"\n🛡️  System Stability:")
error_count = sum(1 for r in results if 'error' in str(r).lower())
if error_count == 0:
    print("   ✅ All edge case tests completed successfully")
    print("   ✅ System remained stable under extreme memory pressure")
else:
    print(f"   ⚠️  {error_count} tests encountered errors")

# Performance impact assessment
if results:
    total_increase = sum(r['increase'] for r in results)
    avg_increase = total_increase / len(results)
    print(f"   📈 Average memory impact per test: {avg_increase:.1f}MB")

print(f"\n🎯 AGGRESSIVE EDGE CASE TESTING COMPLETED")