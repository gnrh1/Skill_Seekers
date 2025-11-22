#!/usr/bin/env python3
"""
Advanced Memory Stress Test Suite
Tests sophisticated memory management scenarios and edge cases
"""

import gc
import os
import sys
import threading
import time
import random
import weakref
import traceback
import psutil
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
# import objgraph  # Optional: commented out to avoid dependency issues

@dataclass
class MemoryMetrics:
    """Memory test metrics collection"""
    timestamp: float
    rss_mb: float
    vms_mb: float
    percent: float
    heap_objects: int
    gc_collect_time: float

class MemoryStressTester:
    """Advanced memory stress testing suite"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.test_duration = 30  # 30 seconds test
        self.results = defaultdict(list)
        self.memory_leaks_detected = 0
        self.fragmentation_events = []
        self.coherency_violations = 0

        # Test configuration
        self.large_object_size = 10 * 1024 * 1024  # 10MB
        self.fragmentation_cycles = 1000
        self.concurrent_threads = 8
        self.access_pattern_iterations = 10000

    def get_memory_snapshot(self) -> MemoryMetrics:
        """Capture detailed memory metrics"""
        start_gc = time.time()
        gc.collect()
        gc_time = time.time() - start_gc

        memory_info = self.process.memory_info()
        return MemoryMetrics(
            timestamp=time.time(),
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            percent=self.process.memory_percent(),
            heap_objects=len(gc.get_objects()),
            gc_collect_time=gc_time
        )

    def create_cyclic_references(self, depth: int = 50) -> List:
        """Create complex cyclic reference chains for leak testing"""
        objects = []

        for i in range(depth):
            obj = {
                'id': i,
                'data': [random.random() for _ in range(100)],
                'children': [],
                'parent': None,
                'metadata': {
                    'timestamp': time.time(),
                    'nested': {
                        'level1': {'level2': {'level3': [j for j in range(20)]}}
                    }
                }
            }
            objects.append(obj)

        # Create complex web of references
        for i in range(depth):
            if i > 0:
                objects[i]['parent'] = objects[i-1]
                objects[i-1]['children'].append(objects[i])

            # Create cross-references for complexity
            if i > 2:
                objects[i]['cross_ref'] = objects[i-2]
                # Create a separate object for weak reference testing
                weak_obj = type('WeakRefObject', (), {})()
                weak_obj.data = f"weak_data_{i}"
                objects[i]['weak_ref'] = weakref.ref(weak_obj)

        # Add some objects with hidden references
        hidden_refs = []
        for i in range(10):
            hidden_obj = {
                'data': bytearray(1024 * 100),  # 100KB
                'callback': lambda: self.hidden_callback(i),
                'circular': None
            }
            hidden_obj['circular'] = hidden_obj  # Self-reference
            hidden_refs.append(hidden_obj)

        return objects + hidden_refs

    def hidden_callback(self, x):
        """Hidden callback to maintain object references"""
        return x * 2

    def test_memory_leak_detection(self):
        """Test 1: Advanced memory leak detection"""
        print("🔍 Testing memory leak detection...")

        initial_metrics = self.get_memory_snapshot()
        leaked_objects = []

        # Phase 1: Create objects with various leak patterns
        for cycle in range(20):
            # Pattern 1: Cyclic references
            cyclic_objects = self.create_cyclic_references(30)

            # Pattern 2: Global registry pattern
            if not hasattr(self, '_global_registry'):
                self._global_registry = []
            self._global_registry.extend(cyclic_objects)

            # Pattern 3: Callback closures
            def make_leaky_closure():
                data = [random.random() for _ in range(1000)]
                return lambda: data[0] if data else None

            closures = [make_leaky_closure() for _ in range(50)]

            # Pattern 4: Weakref callback keeping objects alive
            class LeakyObject:
                def __init__(self, size=1024):
                    self.data = bytearray(size)
                    self.id = id(self)

                def __del__(self):
                    pass

            leaky_objects = []
            for i in range(30):
                obj = LeakyObject(2048)
                weak_ref = weakref.ref(obj, lambda ref: leaky_objects.append(ref))
                leaky_objects.append(weak_ref)

            leaked_objects.extend([cyclic_objects, closures, leaky_objects])

        # Force GC to see what survives
        gc.collect()
        time.sleep(1)

        after_gc_metrics = self.get_memory_snapshot()

        # Calculate leak metrics
        memory_growth = after_gc_metrics.rss_mb - initial_metrics.rss_mb
        object_growth = after_gc_metrics.heap_objects - initial_metrics.heap_objects

        leak_detected = memory_growth > 50 or object_growth > 1000

        self.results['leak_detection'].append({
            'memory_growth_mb': memory_growth,
            'object_growth': object_growth,
            'objects_in_registry': len(self._global_registry) if hasattr(self, '_global_registry') else 0,
            'leak_detected': leak_detected,
            'gc_time': after_gc_metrics.gc_collect_time
        })

        if leak_detected:
            self.memory_leaks_detected += 1

        # Clean up
        if hasattr(self, '_global_registry'):
            self._global_registry.clear()
        del leaked_objects

        return leak_detected

    def test_memory_fragmentation(self):
        """Test 2: Memory fragmentation analysis"""
        print("🧩 Testing memory fragmentation...")

        fragmentation_scores = []
        allocation_sizes = []

        for cycle in range(self.fragmentation_cycles):
            # Create allocation patterns that cause fragmentation
            allocations = []

            # Pattern 1: Random size allocations
            for i in range(50):
                size = random.choice([
                    1024,        # 1KB
                    4096,        # 4KB
                    16384,       # 16KB
                    65536,       # 64KB
                    262144,      # 256KB
                    1048576      # 1MB
                ])
                allocation_sizes.append(size)
                allocations.append(bytearray(size))

            # Pattern 2: Allocate, deallocate in non-LIFO order
            keep_indices = random.sample(range(len(allocations)), len(allocations) // 3)
            deallocated = []

            for i in range(len(allocations)):
                if i not in keep_indices:
                    deallocated.append(allocations[i])
                    allocations[i] = None

            # Pattern 3: Reallocate with slightly different sizes
            for i in keep_indices:
                new_size = allocation_sizes[i] + random.randint(-512, 512)
                if new_size > 0:
                    allocations[i] = bytearray(new_size)

            # Calculate fragmentation score
            if allocations:
                total_allocated = sum(len(a) for a in allocations if a)
                avg_size = total_allocated / len([a for a in allocations if a])
                size_variance = np.var([len(a) for a in allocations if a]) if allocations else 0
                fragmentation_score = size_variance / (avg_size ** 2) if avg_size > 0 else 0
                fragmentation_scores.append(fragmentation_score)

            # Measure memory efficiency
            metrics = self.get_memory_snapshot()
            self.fragmentation_events.append({
                'cycle': cycle,
                'fragmentation_score': fragmentation_score,
                'rss_mb': metrics.rss_mb,
                'heap_objects': metrics.heap_objects
            })

            # Partial cleanup
            allocations = [a for a in allocations if a is not None]

        avg_fragmentation = np.mean(fragmentation_scores) if fragmentation_scores else 0
        max_fragmentation = max(fragmentation_scores) if fragmentation_scores else 0

        self.results['fragmentation'].append({
            'avg_fragmentation_score': avg_fragmentation,
            'max_fragmentation_score': max_fragmentation,
            'cycles_tested': self.fragmentation_cycles,
            'allocation_size_variance': np.var(allocation_sizes) if allocation_sizes else 0
        })

        return avg_fragmentation

    def test_memory_compaction(self):
        """Test 3: Memory compaction and defragmentation"""
        print("🗜️ Testing memory compaction efficiency...")

        # Create heavily fragmented memory
        fragmented_allocations = []
        compaction_metrics = []

        # Phase 1: Create fragmentation
        for phase in range(10):
            phase_allocations = []

            # Create allocations of varying sizes
            for i in range(100):
                size = random.randint(1024, 1024 * 1024)  # 1KB to 1MB
                phase_allocations.append(bytearray(size))

            # Randomly deallocate to create holes
            deallocate_count = len(phase_allocations) // 2
            deallocate_indices = random.sample(range(len(phase_allocations)), deallocate_count)

            for idx in deallocate_indices:
                phase_allocations[idx] = None

            fragmented_allocations.extend(phase_allocations)

            # Measure pre-compaction
            pre_compaction = self.get_memory_snapshot()

            # Force garbage collection to attempt compaction
            gc.collect()

            # Measure post-compaction
            post_compaction = self.get_memory_snapshot()

            compaction_efficiency = (pre_compaction.rss_mb - post_compaction.rss_mb) / pre_compaction.rss_mb

            compaction_metrics.append({
                'phase': phase,
                'pre_compaction_rss': pre_compaction.rss_mb,
                'post_compaction_rss': post_compaction.rss_mb,
                'compaction_efficiency': compaction_efficiency,
                'gc_time': post_compaction.gc_collect_time
            })

        # Phase 2: Test manual compaction by reallocating
        surviving_objects = [obj for obj in fragmented_allocations if obj is not None]

        # Create new compact allocations
        compact_allocations = []
        for obj in surviving_objects:
            new_size = len(obj)
            compact_allocations.append(bytearray(new_size))

        # Clean up old fragmented allocations
        fragmented_allocations.clear()

        # Final measurement
        final_metrics = self.get_memory_snapshot()

        avg_compaction_efficiency = np.mean([m['compaction_efficiency'] for m in compaction_metrics])

        self.results['compaction'].append({
            'avg_compaction_efficiency': avg_compaction_efficiency,
            'max_compaction_efficiency': max([m['compaction_efficiency'] for m in compaction_metrics]),
            'total_objects_compacted': len(compact_allocations),
            'final_rss_mb': final_metrics.rss_mb,
            'avg_gc_time': np.mean([m['gc_time'] for m in compaction_metrics])
        })

        return avg_compaction_efficiency

    def test_memory_access_patterns(self):
        """Test 4: Memory access pattern performance"""
        print("⚡ Testing memory access patterns...")

        access_pattern_results = {}

        # Create test data
        data_size = 1000000  # 1M elements
        test_data = np.random.random(data_size).astype(np.float64)

        # Pattern 1: Sequential access
        start_time = time.time()
        for i in range(self.access_pattern_iterations):
            idx = i % data_size
            _ = test_data[idx] * 2
        sequential_time = time.time() - start_time

        # Pattern 2: Random access
        start_time = time.time()
        random_indices = np.random.randint(0, data_size, self.access_pattern_iterations)
        for idx in random_indices:
            _ = test_data[idx] * 2
        random_time = time.time() - start_time

        # Pattern 3: Stride access (every nth element)
        stride = 1000
        start_time = time.time()
        for i in range(self.access_pattern_iterations):
            idx = (i * stride) % data_size
            _ = test_data[idx] * 2
        stride_time = time.time() - start_time

        # Pattern 4: Localized access (small range repeated)
        range_size = 1000
        start_time = time.time()
        for i in range(self.access_pattern_iterations):
            idx = random.randint(0, range_size)
            _ = test_data[idx] * 2
        localized_time = time.time() - start_time

        access_pattern_results = {
            'sequential_time_ms': sequential_time * 1000,
            'random_time_ms': random_time * 1000,
            'stride_time_ms': stride_time * 1000,
            'localized_time_ms': localized_time * 1000,
            'random_vs_sequential_ratio': random_time / sequential_time,
            'stride_vs_sequential_ratio': stride_time / sequential_time,
            'localized_vs_sequential_ratio': localized_time / sequential_time
        }

        self.results['access_patterns'].append(access_pattern_results)

        return access_pattern_results

    def test_memory_coherency(self):
        """Test 5: Memory coherency under concurrent modification"""
        print("🔄 Testing memory coherency under concurrency...")

        # Shared data structure
        shared_data = {
            'counters': [0] * 1000,
            'locks': [threading.Lock() for _ in range(100)],
            'data_matrix': [[0 for _ in range(100)] for _ in range(100)]
        }

        # Coherency validation data
        coherency_log = []
        inconsistency_detected = threading.Event()

        def concurrent_reader(reader_id: int):
            """Reader thread that checks data consistency"""
            for iteration in range(1000):
                # Sample different parts of shared data
                sample_indices = random.sample(range(1000), 10)

                for idx in sample_indices:
                    value = shared_data['counters'][idx]
                    # Check for corruption (negative values, extreme values)
                    if value < 0 or value > 1000000:
                        coherency_log.append({
                            'reader_id': reader_id,
                            'iteration': iteration,
                            'index': idx,
                            'corrupt_value': value,
                            'timestamp': time.time()
                        })
                        inconsistency_detected.set()
                        return

                # Validate matrix consistency
                for i in random.sample(range(100), 5):
                    for j in random.sample(range(100), 5):
                        val = shared_data['data_matrix'][i][j]
                        if val < 0 or val > 1000:
                            coherency_log.append({
                                'reader_id': reader_id,
                                'iteration': iteration,
                                'type': 'matrix_corruption',
                                'coords': (i, j),
                                'corrupt_value': val,
                                'timestamp': time.time()
                            })
                            inconsistency_detected.set()
                            return

                time.sleep(0.001)  # Small delay

        def concurrent_writer(writer_id: int):
            """Writer thread that modifies shared data"""
            for iteration in range(1000):
                if inconsistency_detected.is_set():
                    break

                # Update counters
                for _ in range(10):
                    idx = random.randint(0, 999)
                    with shared_data['locks'][idx % 100]:
                        shared_data['counters'][idx] += 1

                # Update matrix
                for _ in range(5):
                    i, j = random.randint(0, 99), random.randint(0, 99)
                    shared_data['data_matrix'][i][j] = (shared_data['data_matrix'][i][j] + 1) % 1000

                time.sleep(0.002)

        def concurrent_deallocator(deallocator_id: int):
            """Thread that creates and destroys objects"""
            objects = []
            for iteration in range(200):
                if inconsistency_detected.is_set():
                    break

                # Create objects
                for _ in range(50):
                    obj = {
                        'id': random.randint(0, 1000000),
                        'data': bytearray(1024),
                        'timestamp': time.time(),
                        'references': []
                    }
                    objects.append(obj)

                # Create some cross-references
                if len(objects) > 2:
                    objects[-2]['references'].append(objects[-1])
                    objects[-1]['references'].append(objects[-2])

                # Deallocate some objects
                if len(objects) > 100:
                    objects_to_remove = random.sample(objects, 20)
                    for obj in objects_to_remove:
                        if obj in objects:
                            objects.remove(obj)
                            del obj

                time.sleep(0.005)

        # Start concurrent operations
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.concurrent_threads) as executor:
            futures = []

            # Launch 2 readers, 2 writers, 2 deallocators per available thread
            for i in range(self.concurrent_threads // 3):
                futures.append(executor.submit(concurrent_reader, f"reader_{i}"))
                futures.append(executor.submit(concurrent_writer, f"writer_{i}"))
                futures.append(executor.submit(concurrent_deallocator, f"deallocator_{i}"))

            # Wait for completion or timeout
            for future in as_completed(futures, timeout=25):
                try:
                    future.result()
                except Exception as e:
                    coherency_log.append({
                        'type': 'thread_exception',
                        'error': str(e),
                        'timestamp': time.time()
                    })

        test_duration = time.time() - start_time

        # Calculate final consistency checks
        final_counters_sum = sum(shared_data['counters'])
        final_matrix_sum = sum(sum(row) for row in shared_data['data_matrix'])

        coherency_results = {
            'test_duration_seconds': test_duration,
            'inconsistencies_detected': len(coherency_log),
            'inconsistency_event_set': inconsistency_detected.is_set(),
            'final_counters_sum': final_counters_sum,
            'final_matrix_sum': final_matrix_sum,
            'threads_launched': len(futures),
            'coherency_violations': len([log for log in coherency_log if 'corrupt' in str(log)])
        }

        self.coherency_violations += coherency_results['coherency_violations']
        self.results['coherency'].append(coherency_results)

        return coherency_results

    def run_comprehensive_test(self):
        """Run all memory stress tests"""
        print(f"\n🚀 Starting comprehensive memory stress test (30 seconds)...")
        print("=" * 60)

        test_start = time.time()
        results_summary = {}

        # Run tests in sequence with timing
        try:
            # Test 1: Memory Leak Detection
            leak_start = time.time()
            leak_detected = self.test_memory_leak_detection()
            leak_time = time.time() - leak_start
            results_summary['leak_detection'] = {
                'leaks_detected': leak_detected,
                'total_leak_detections': self.memory_leaks_detected,
                'test_time': leak_time
            }

            # Test 2: Memory Fragmentation
            frag_start = time.time()
            avg_fragmentation = self.test_memory_fragmentation()
            frag_time = time.time() - frag_start
            results_summary['fragmentation'] = {
                'avg_fragmentation_score': avg_fragmentation,
                'fragmentation_events': len(self.fragmentation_events),
                'test_time': frag_time
            }

            # Test 3: Memory Compaction
            comp_start = time.time()
            compaction_efficiency = self.test_memory_compaction()
            comp_time = time.time() - comp_start
            results_summary['compaction'] = {
                'compaction_efficiency': compaction_efficiency,
                'test_time': comp_time
            }

            # Test 4: Access Patterns
            access_start = time.time()
            access_results = self.test_memory_access_patterns()
            access_time = time.time() - access_start
            results_summary['access_patterns'] = {
                'pattern_performance': access_results,
                'test_time': access_time
            }

            # Test 5: Memory Coherency
            coherency_start = time.time()
            coherency_results = self.test_memory_coherency()
            coherency_time = time.time() - coherency_start
            results_summary['coherency'] = {
                'coherency_results': coherency_results,
                'test_time': coherency_time
            }

        except Exception as e:
            print(f"❌ Error during testing: {e}")
            traceback.print_exc()

        total_test_time = time.time() - test_start

        # Generate final report
        self.generate_comprehensive_report(results_summary, total_test_time)

        return results_summary

    def generate_comprehensive_report(self, results: Dict, total_time: float):
        """Generate comprehensive memory stress test report"""
        print("\n" + "=" * 60)
        print("📊 MEMORY STRESS TEST REPORT")
        print("=" * 60)

        # Memory Leak Detection Results
        leak_results = results.get('leak_detection', {})
        print(f"\n🔍 MEMORY LEAK DETECTION")
        print(f"   Leaks Detected: {'YES' if leak_results.get('leaks_detected', False) else 'NO'}")
        print(f"   Total Detections: {leak_results.get('total_leak_detections', 0)}")
        print(f"   Test Time: {leak_results.get('test_time', 0):.2f}s")

        # Fragmentation Results
        frag_results = results.get('fragmentation', {})
        print(f"\n🧩 MEMORY FRAGMENTATION")
        print(f"   Avg Fragmentation Score: {frag_results.get('avg_fragmentation_score', 0):.4f}")
        print(f"   Fragmentation Events: {frag_results.get('fragmentation_events', 0)}")
        print(f"   Test Time: {frag_results.get('test_time', 0):.2f}s")

        # Compaction Results
        comp_results = results.get('compaction', {})
        print(f"\n🗜️ MEMORY COMPACTION")
        print(f"   Compaction Efficiency: {comp_results.get('compaction_efficiency', 0):.2%}")
        print(f"   Test Time: {comp_results.get('test_time', 0):.2f}s")

        # Access Pattern Results
        access_results = results.get('access_patterns', {}).get('pattern_performance', {})
        if access_results:
            print(f"\n⚡ ACCESS PATTERNS")
            print(f"   Sequential: {access_results.get('sequential_time_ms', 0):.2f}ms")
            print(f"   Random: {access_results.get('random_time_ms', 0):.2f}ms ({access_results.get('random_vs_sequential_ratio', 0):.2f}x slower)")
            print(f"   Stride: {access_results.get('stride_time_ms', 0):.2f}ms ({access_results.get('stride_vs_sequential_ratio', 0):.2f}x slower)")
            print(f"   Localized: {access_results.get('localized_time_ms', 0):.2f}ms ({access_results.get('localized_vs_sequential_ratio', 0):.2f}x slower)")
            print(f"   Test Time: {results.get('access_patterns', {}).get('test_time', 0):.2f}s")

        # Coherency Results
        coherency_results = results.get('coherency', {}).get('coherency_results', {})
        if coherency_results:
            print(f"\n🔄 MEMORY COHERENCY")
            print(f"   Inconsistencies Detected: {coherency_results.get('inconsistencies_detected', 0)}")
            print(f"   Coherency Violations: {coherency_results.get('coherency_violations', 0)}")
            print(f"   Threads Launched: {coherency_results.get('threads_launched', 0)}")
            print(f"   Test Duration: {coherency_results.get('test_duration_seconds', 0):.2f}s")
            print(f"   Test Time: {results.get('coherency', {}).get('test_time', 0):.2f}s")

        # Overall Assessment
        print(f"\n🎯 OVERALL ASSESSMENT")
        print(f"   Total Test Duration: {total_time:.2f}s")

        # Calculate overall memory health score
        health_score = 100
        if leak_results.get('leaks_detected', False):
            health_score -= 30
        if frag_results.get('avg_fragmentation_score', 0) > 1.0:
            health_score -= 20
        if comp_results.get('compaction_efficiency', 0) < 0.1:
            health_score -= 15
        if coherency_results.get('coherency_violations', 0) > 0:
            health_score -= 35

        health_score = max(0, health_score)
        print(f"   Memory Health Score: {health_score}/100")

        if health_score >= 80:
            print("   Status: ✅ EXCELLENT - Memory management is robust")
        elif health_score >= 60:
            print("   Status: ⚠️ GOOD - Minor memory issues detected")
        elif health_score >= 40:
            print("   Status: ⚠️ FAIR - Significant memory issues present")
        else:
            print("   Status: ❌ POOR - Critical memory management issues")

        print(f"\n📈 ADVANCED MEMORY FEATURES TESTED")
        print(f"   ✅ Cyclic reference leak detection")
        print(f"   ✅ Global registry pattern leaks")
        print(f"   ✅ Callback closure memory retention")
        print(f"   ✅ Weakref callback analysis")
        print(f"   ✅ Multi-size allocation fragmentation")
        print(f"   ✅ Non-LIFO deallocation patterns")
        print(f"   ✅ GC-induced compaction efficiency")
        print(f"   ✅ Memory access pattern optimization")
        print(f"   ✅ Concurrent modification coherency")
        print(f"   ✅ Cross-thread memory consistency")

def main():
    """Main execution function"""
    print("🧠 Advanced Memory Stress Test Agent")
    print("Testing sophisticated memory management edge cases...")

    tester = MemoryStressTester()

    try:
        results = tester.run_comprehensive_test()
        return results

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()