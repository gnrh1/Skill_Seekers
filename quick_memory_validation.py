#!/usr/bin/env python3
"""
Quick Memory Stress Test Validation
Additional validation for advanced memory management features
"""

import gc
import time
import threading
import random
import weakref
import psutil
from concurrent.futures import ThreadPoolExecutor

def test_advanced_memory_edge_cases():
    """Quick test for additional advanced memory scenarios"""
    print("🔬 Additional Advanced Memory Validation Tests")
    print("=" * 50)

    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024

    # Test 1: Memory pressure under extreme object creation
    print("🚨 Test 1: Extreme object creation pressure...")
    objects = []
    try:
        for i in range(100000):
            obj = {
                'id': i,
                'data': [random.random() for _ in range(100)],
                'nested': {
                    'level1': {'level2': {'level3': list(range(50))}}
                },
                'circular_ref': None
            }
            objects.append(obj)

            # Create some circular references
            if i > 0:
                objects[i]['circular_ref'] = objects[i-1]

            if i % 20000 == 0:
                current_mem = process.memory_info().rss / 1024 / 1024
                print(f"  Objects: {i:,}, Memory: {current_mem:.1f}MB (+{current_mem - start_memory:.1f}MB)")

    except MemoryError:
        print(f"  Memory limit reached at {len(objects):,} objects")

    peak_memory = process.memory_info().rss / 1024 / 1024
    print(f"  Peak: {peak_memory:.1f}MB, Growth: {peak_memory - start_memory:.1f}MB")

    # Cleanup
    del objects
    gc.collect()
    cleanup_memory = process.memory_info().rss / 1024 / 1024
    print(f"  After cleanup: {cleanup_memory:.1f}MB, Recovered: {peak_memory - cleanup_memory:.1f}MB")

    # Test 2: Thread-safe memory allocation patterns
    print("\n🧵 Test 2: Thread-safe memory allocation...")
    thread_results = []

    def memory_consumer(thread_id):
        """Thread that consumes and releases memory"""
        thread_objects = []
        for cycle in range(100):
            # Allocate
            for i in range(1000):
                thread_objects.append(bytearray(1024))

            # Deallocate half
            thread_objects = thread_objects[-500:]

            time.sleep(0.001)

        return thread_id, len(thread_objects)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(memory_consumer, i) for i in range(8)]
        for future in futures:
            result = future.result()
            thread_results.append(result)

    print(f"  Completed {len(thread_results)} threads")

    # Test 3: Weak reference edge cases
    print("\n🔗 Test 3: Weak reference edge cases...")

    class WeakRefTest:
        def __init__(self, value):
            self.value = value
            self.data = 'x' * 1000

    # Create objects with weak references
    strong_refs = []
    weak_refs = []

    for i in range(1000):
        obj = WeakRefTest(i)
        strong_refs.append(obj)
        weak_refs.append(weakref.ref(obj))

    print(f"  Created {len(strong_refs)} strong refs, {len(weak_refs)} weak refs")

    # Test weak reference callback
    callback_count = 0
    def callback(ref):
        global callback_count
        callback_count += 1

    weak_ref_with_callback = weakref.ref(WeakRefTest("callback_test"), callback)

    # Delete strong references
    del strong_refs
    gc.collect()

    # Check weak refs
    surviving_weak_refs = [ref for ref in weak_refs if ref() is not None]
    print(f"  Weak refs still valid: {len(surviving_weak_refs)}")
    print(f"  Callback executed: {callback_count}")

    # Final memory check
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"\n📊 Memory Summary:")
    print(f"  Start: {start_memory:.1f}MB")
    print(f"  Final: {final_memory:.1f}MB")
    print(f"  Net change: {final_memory - start_memory:+.1f}MB")

    # Memory efficiency score
    memory_efficiency = 100 - min(50, max(0, (final_memory - start_memory)))
    print(f"  Memory efficiency: {memory_efficiency}/100")

if __name__ == "__main__":
    test_advanced_memory_edge_cases()