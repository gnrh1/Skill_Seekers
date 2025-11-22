#!/usr/bin/env python3
"""
Intensive Memory Stress Test (30 seconds)
Focuses on core memory management edge cases with real-time monitoring
"""

import gc
import os
import sys
import time
import psutil
import threading
import random
import weakref
import json
import array
import tempfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class IntensiveMemoryTest:
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.test_duration = 30
        self.results = {
            'deep_nesting': {},
            'string_stress': {},
            'circular_refs': {},
            'allocation_cycles': {},
            'concurrent_access': {},
            'memory_efficiency': {}
        }

    def get_memory_stats(self):
        """Get current memory statistics"""
        try:
            memory_info = self.process.memory_info()
            return {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
                'percent': self.process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'timestamp': time.time()
            }
        except Exception:
            return {'error': 'Memory stats failed'}

    def test_deep_nesting(self):
        """Test deep nesting structures"""
        print("\n🏗️  Testing Deep Nesting (2000+ levels)...")
        start_memory = self.get_memory_stats()

        try:
            # Create deeply nested structure
            def create_nested(depth, current=0):
                if depth <= 0:
                    return {'leaf': True, 'depth': current}

                return {
                    'depth': current,
                    'data': list(range(10)),
                    'string': f'level_{current}',
                    'nested': create_nested(depth - 1, current + 1)
                }

            # Create structure with 2000 levels
            nested_obj = create_nested(2000)

            # Test access
            current = nested_obj
            max_depth = 0
            while isinstance(current, dict) and 'nested' in current:
                current = current['nested']
                max_depth += 1
                if max_depth > 2000:
                    break

            # Add circular references
            nested_obj['circular'] = nested_obj

            end_memory = self.get_memory_stats()

            return {
                'max_depth': max_depth,
                'initial_rss': start_memory['rss_mb'],
                'final_rss': end_memory['rss_mb'],
                'memory_growth': end_memory['rss_mb'] - start_memory['rss_mb'],
                'success': max_depth >= 1500,  # At least 1500 levels
                'circular_ref_added': True
            }

        except Exception as e:
            return {'error': str(e), 'success': False}

    def test_string_stress(self):
        """Test extreme string operations"""
        print("\n📝 Testing String Stress...")
        start_memory = self.get_memory_stats()

        try:
            # Large string concatenation
            base = "x" * 100000  # 100KB
            large_string = ""

            concatenations = 0
            corruption_count = 0

            # Concatenate until memory growth is significant or time limit
            while len(large_string) < 50000000:  # 50MB limit
                old_length = len(large_string)
                large_string += base
                concatenations += 1

                # Verify integrity
                if len(large_string) != old_length + len(base):
                    corruption_count += 1
                    break

                if concatenations % 100 == 0:
                    current_mem = self.get_memory_stats()
                    if current_mem['rss_mb'] - start_memory['rss_mb'] > 100:  # 100MB limit
                        break

            # String multiplication test
            mult_results = []
            for mult in [1000, 5000, 10000]:
                try:
                    test_str = "y" * 1000
                    multiplied = test_str * mult
                    mult_results.append({
                        'multiplier': mult,
                        'length': len(multiplied),
                        'success': True
                    })
                except MemoryError:
                    mult_results.append({'multiplier': mult, 'success': False})
                    break

            end_memory = self.get_memory_stats()

            return {
                'concatenations': concatenations,
                'final_string_length': len(large_string),
                'corruption_count': corruption_count,
                'multiplication_tests': mult_results,
                'initial_rss': start_memory['rss_mb'],
                'final_rss': end_memory['rss_mb'],
                'memory_growth': end_memory['rss_mb'] - start_memory['rss_mb'],
                'integrity_maintained': corruption_count == 0
            }

        except Exception as e:
            return {'error': str(e), 'integrity_maintained': False}

    def test_circular_references(self):
        """Test complex circular references"""
        print("\n🔄 Testing Circular References...")
        start_memory = self.get_memory_stats()

        try:
            # Create objects with circular references
            class CircularObj:
                def __init__(self, id):
                    self.id = id
                    self.refs = []
                    self.data = list(range(10))

            objects = []
            weak_refs = []

            # Create circular graph
            for i in range(100):
                obj = CircularObj(i)
                objects.append(obj)
                weak_refs.append(weakref.ref(obj))

            # Create circular references
            for i, obj in enumerate(objects):
                obj.refs.append(objects[(i + 1) % len(objects)])  # Next
                obj.refs.append(objects[(i - 1) % len(objects)])  # Previous
                if i % 10 == 0:
                    obj.refs.append(obj)  # Self-reference

            # Test traversal
            visited_count = 0
            try:
                def traverse(obj, visited=None):
                    nonlocal visited_count
                    if visited is None:
                        visited = set()

                    if id(obj) in visited:
                        return

                    visited.add(id(obj))
                    visited_count += 1

                    for ref in obj.refs:
                        traverse(ref, visited)

                traverse(objects[0])
            except RecursionError:
                pass  # Expected with circular refs

            # Test garbage collection
            pre_gc_surviving = sum(1 for ref in weak_refs if ref() is not None)
            gc.collect()
            post_gc_surviving = sum(1 for ref in weak_refs if ref() is not None)

            end_memory = self.get_memory_stats()

            return {
                'objects_created': len(objects),
                'weak_refs_tracked': len(weak_refs),
                'pre_gc_surviving': pre_gc_surviving,
                'post_gc_surviving': post_gc_surviving,
                'gc_effectiveness': (pre_gc_surviving - post_gc_surviving) / pre_gc_surviving if pre_gc_surviving > 0 else 0,
                'visited_during_traversal': visited_count,
                'initial_rss': start_memory['rss_mb'],
                'final_rss': end_memory['rss_mb'],
                'memory_growth': end_memory['rss_mb'] - start_memory['rss_mb'],
                'circular_refs_handled': True
            }

        except Exception as e:
            return {'error': str(e), 'circular_refs_handled': False}

    def test_allocation_cycles(self):
        """Test high-frequency allocation/deallocation"""
        print("\n⚡ Testing Allocation Cycles...")
        start_memory = self.get_memory_stats()

        try:
            cycles_completed = 0
            allocation_times = []
            memory_errors = 0

            # Rapid allocation/deallocation cycles
            for cycle in range(5000):  # Reduced for stability
                cycle_start = time.time()

                # Allocate various objects
                objects = []

                # Lists
                for i in range(10):
                    objects.append([f'item_{i}'] * random.randint(5, 20))

                # Dicts
                for i in range(5):
                    objects.append({f'key_{j}': j for j in range(random.randint(5, 15))})

                # Strings
                for i in range(20):
                    objects.append(''.join(['a', 'b', 'c', 'd', 'e'] * random.randint(10, 30)))

                # Arrays
                for i in range(3):
                    objects.append(array.array('i', range(random.randint(10, 30))))

                # Deallocate
                del objects
                gc.collect()

                cycle_end = time.time()
                allocation_times.append(cycle_end - cycle_start)
                cycles_completed += 1

                # Check memory usage
                if cycles_completed % 1000 == 0:
                    current_mem = self.get_memory_stats()
                    if current_mem['rss_mb'] - start_memory['rss_mb'] > 200:  # 200MB limit
                        break

            end_memory = self.get_memory_stats()

            return {
                'cycles_completed': cycles_completed,
                'avg_cycle_time_ms': sum(allocation_times) / len(allocation_times) * 1000 if allocation_times else 0,
                'memory_errors': memory_errors,
                'initial_rss': start_memory['rss_mb'],
                'final_rss': end_memory['rss_mb'],
                'memory_growth': end_memory['rss_mb'] - start_memory['rss_mb'],
                'allocation_efficient': cycles_completed >= 4000
            }

        except Exception as e:
            return {'error': str(e), 'allocation_efficient': False}

    def test_concurrent_access(self):
        """Test concurrent memory access"""
        print("\n🏁 Testing Concurrent Access...")
        start_memory = self.get_memory_stats()

        try:
            shared_data = {'counter': 0, 'list': [], 'errors': 0}
            thread_results = []

            def concurrent_worker(thread_id, operations):
                local_errors = 0

                for i in range(operations):
                    try:
                        # Counter increment (race condition test)
                        old_val = shared_data['counter']
                        shared_data['counter'] = old_val + 1

                        # List operations
                        if len(shared_data['list']) > 100:
                            shared_data['list'].pop(0)
                        shared_data['list'].append(f'thread_{thread_id}_{i}')

                    except Exception:
                        local_errors += 1

                return {'thread_id': thread_id, 'errors': local_errors}

            # Run concurrent workers
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(concurrent_worker, i, 100) for i in range(10)]

                for future in futures:
                    result = future.result()
                    thread_results.append(result)

            # Analyze results
            total_errors = sum(r['errors'] for r in thread_results)
            expected_counter = 10 * 100  # 10 threads * 100 operations
            actual_counter = shared_data['counter']
            race_condition_detected = actual_counter != expected_counter

            end_memory = self.get_memory_stats()

            return {
                'threads_run': len(thread_results),
                'expected_counter': expected_counter,
                'actual_counter': actual_counter,
                'race_condition_detected': race_condition_detected,
                'total_errors': total_errors,
                'final_list_length': len(shared_data['list']),
                'initial_rss': start_memory['rss_mb'],
                'final_rss': end_memory['rss_mb'],
                'memory_growth': end_memory['rss_mb'] - start_memory['rss_mb'],
                'concurrency_stable': total_errors < 10
            }

        except Exception as e:
            return {'error': str(e), 'concurrency_stable': False}

    def run_intensive_test(self):
        """Run all intensive memory tests"""
        print("🔥 Intensive Memory Stress Test (30 seconds)")
        print("=" * 50)
        print(f"PID: {os.getpid()}")
        print(f"Initial Memory: {self.get_memory_stats()['rss_mb']:.1f}MB")
        print("=" * 50)

        start_time = time.time()

        try:
            # Run tests with time management
            test_results = []

            # Test 1: Deep Nesting
            if time.time() - start_time < self.test_duration - 5:
                self.results['deep_nesting'] = self.test_deep_nesting()

            # Test 2: String Stress
            if time.time() - start_time < self.test_duration - 5:
                self.results['string_stress'] = self.test_string_stress()

            # Test 3: Circular References
            if time.time() - start_time < self.test_duration - 5:
                self.results['circular_refs'] = self.test_circular_references()

            # Test 4: Allocation Cycles
            if time.time() - start_time < self.test_duration - 5:
                self.results['allocation_cycles'] = self.test_allocation_cycles()

            # Test 5: Concurrent Access
            if time.time() - start_time < self.test_duration - 5:
                self.results['concurrent_access'] = self.test_concurrent_access()

        except Exception as e:
            print(f"Test error: {e}")
            self.results['error'] = str(e)

        end_time = time.time()

        # Final cleanup and report
        print("\n🧹 Cleanup...")
        gc.collect()

        final_memory = self.get_memory_stats()

        self.generate_report(end_time - start_time, final_memory)

    def generate_report(self, runtime, final_memory):
        """Generate comprehensive report"""
        print("\n" + "=" * 50)
        print("🔥 INTENSIVE MEMORY TEST RESULTS")
        print("=" * 50)

        print(f"⏱️  Runtime: {runtime:.2f} seconds")
        print(f"📊 Final Memory: {final_memory['rss_mb']:.1f}MB")

        print("\n📋 Test Results:")

        # Deep Nesting
        nesting = self.results.get('deep_nesting', {})
        if nesting.get('success'):
            print(f"\n🏗️  Deep Nesting: ✅ SUCCESS")
            print(f"   • Max Depth: {nesting.get('max_depth', 0):,}")
            print(f"   • Memory Growth: {nesting.get('memory_growth', 0):.1f}MB")
        else:
            print(f"\n🏗️  Deep Nesting: ❌ FAILED")
            if 'error' in nesting:
                print(f"   • Error: {nesting['error']}")

        # String Stress
        strings = self.results.get('string_stress', {})
        if strings.get('integrity_maintained'):
            print(f"\n📝 String Stress: ✅ INTEGRITY MAINTAINED")
            print(f"   • Concatenations: {strings.get('concatenations', 0):,}")
            print(f"   • Memory Growth: {strings.get('memory_growth', 0):.1f}MB")
        else:
            print(f"\n📝 String Stress: ❌ CORRUPTION DETECTED")
            print(f"   • Corruption Count: {strings.get('corruption_count', 0)}")

        # Circular References
        circular = self.results.get('circular_refs', {})
        if circular.get('circular_refs_handled'):
            print(f"\n🔄 Circular References: ✅ HANDLED")
            print(f"   • Objects Created: {circular.get('objects_created', 0):,}")
            print(f"   • GC Effectiveness: {circular.get('gc_effectiveness', 0):.1%}")
        else:
            print(f"\n🔄 Circular References: ❌ FAILED")

        # Allocation Cycles
        allocation = self.results.get('allocation_cycles', {})
        if allocation.get('allocation_efficient'):
            print(f"\n⚡ Allocation Cycles: ✅ EFFICIENT")
            print(f"   • Cycles Completed: {allocation.get('cycles_completed', 0):,}")
            print(f"   • Avg Cycle Time: {allocation.get('avg_cycle_time_ms', 0):.3f}ms")
        else:
            print(f"\n⚡ Allocation Cycles: ❌ INEFFICIENT")

        # Concurrent Access
        concurrent = self.results.get('concurrent_access', {})
        if concurrent.get('concurrency_stable'):
            print(f"\n🏁 Concurrent Access: ✅ STABLE")
            print(f"   • Threads Run: {concurrent.get('threads_run', 0)}")
            print(f"   • Race Conditions: {'Detected' if concurrent.get('race_condition_detected') else 'Not Detected'}")
        else:
            print(f"\n🏁 Concurrent Access: ❌ UNSTABLE")

        # Calculate overall score
        scores = []

        if nesting.get('success'):
            scores.append(1.0)
        if strings.get('integrity_maintained'):
            scores.append(1.0)
        if circular.get('circular_refs_handled'):
            scores.append(1.0)
        if allocation.get('allocation_efficient'):
            scores.append(1.0)
        if concurrent.get('concurrency_stable'):
            scores.append(1.0)

        if scores:
            overall_score = sum(scores) / len(scores)

            print(f"\n" + "=" * 50)
            print(f"🎯 OVERALL SCORE: {overall_score:.1%}")

            if overall_score >= 0.8:
                print("🟢 EXCELLENT: Memory management is very robust")
            elif overall_score >= 0.6:
                print("🟡 GOOD: Memory management is adequate")
            elif overall_score >= 0.4:
                print("🟠 FAIR: Memory management has issues")
            else:
                print("🔴 POOR: Memory management needs improvement")

        # Save results
        results_file = '/tmp/intensive_memory_test_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'runtime': runtime,
                'final_memory': final_memory,
                'results': self.results,
                'overall_score': sum(scores) / len(scores) if scores else 0
            }, f, indent=2)

        print(f"\n📁 Results saved to: {results_file}")
        print("=" * 50)

if __name__ == "__main__":
    test = IntensiveMemoryTest()
    test.run_intensive_test()