#!/usr/bin/env python3
"""
Advanced Memory Stress Test Agent
Tests sophisticated memory management scenarios and edge cases

Focus Areas:
1. Memory leak detection with hidden references
2. Memory fragmentation testing
3. Memory compaction and defragmentation efficiency
4. Memory access pattern performance (sequential, random, stride)
5. Memory coherency under concurrent modification
6. Advanced memory management feature effectiveness

Runtime: 30 seconds comprehensive testing
"""

import gc
import os
import sys
import time
import psutil
import threading
import random
import weakref
import traceback
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import array
import mmap
import tempfile

class MemoryStressTestAgent:
    """Advanced memory stress testing for edge cases"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.test_duration = 30  # seconds
        self.results = {
            'memory_leak_detection': {},
            'fragmentation_tests': {},
            'compaction_efficiency': {},
            'access_patterns': {},
            'concurrency_coherency': {},
            'advanced_features': {}
        }

        # Test configuration - increased for intensive testing
        self.leak_test_cycles = 500
        self.fragmentation_allocations = 5000
        self.access_pattern_test_size = 200000
        self.concurrent_threads = 12

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        try:
            memory_info = self.process.memory_info()
            memory_full = self.process.memory_full_info()

            return {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
                'shared_mb': getattr(memory_full, 'shared', 0) / (1024 * 1024),
                'text_mb': getattr(memory_full, 'text', 0) / (1024 * 1024),
                'lib_mb': getattr(memory_full, 'lib', 0) / (1024 * 1024),
                'data_mb': getattr(memory_full, 'data', 0) / (1024 * 1024),
                'dirty_mb': getattr(memory_full, 'dirty', 0) / (1024 * 1024),
                'uss_mb': getattr(memory_full, 'uss', 0) / (1024 * 1024),
                'percent': self.process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'timestamp': time.time()
            }
        except Exception as e:
            return {'error': str(e)}

    def test_memory_leak_detection(self) -> Dict[str, Any]:
        """Test 1: Memory leak detection with hidden references"""
        print("\n🔍 Testing Memory Leak Detection...")

        initial_memory = self.get_memory_stats()
        leak_objects = []
        weak_refs = []
        hidden_references = []

        try:
            # Test 1.1: Circular references
            print("  • Creating circular references...")
            for i in range(self.leak_test_cycles):
                # Create circular reference structures
                class CircularObj:
                    def __init__(self, value):
                        self.value = value
                        self.parent = None
                        self.children = []

                    def add_child(self, child):
                        child.parent = self
                        self.children.append(child)

                parent = CircularObj(f"parent_{i}")
                child1 = CircularObj(f"child1_{i}")
                child2 = CircularObj(f"child2_{i}")

                parent.add_child(child1)
                parent.add_child(child2)
                child1.parent = parent
                child2.parent = parent
                child1.sibling = child2
                child2.sibling = child1  # Circular reference

                leak_objects.append(parent)

                # Store weak references to track
                weak_refs.extend([weakref.ref(obj) for obj in [parent, child1, child2]])

                if i % 20 == 0:
                    # Measure memory growth
                    current_memory = self.get_memory_stats()
                    growth = current_memory['rss_mb'] - initial_memory['rss_mb']
                    print(f"    Cycle {i}: Memory growth: {growth:.1f}MB")

            # Test 1.2: Hidden references in closures
            print("  • Creating closure-based hidden references...")
            def create_closure_with_hidden_refs():
                hidden_data = []
                def closure():
                    # Closure holds reference to hidden_data
                    hidden_data.append(['x'] * 1000)
                    return len(hidden_data)
                return closure

            closures = []
            for i in range(50):
                closures.append(create_closure_with_hidden_refs())

            # Test 1.3: Global variable leaks
            print("  • Testing global variable reference leaks...")
            for i in range(100):
                var_name = f"leak_var_{i}"
                globals()[var_name] = ['leak_data'] * 1000
                hidden_references.append(var_name)

            # Force garbage collection
            print("  • Forcing garbage collection...")
            gc.collect()

            # Check what survived
            surviving_objects = sum(1 for ref in weak_refs if ref() is not None)

            final_memory = self.get_memory_stats()
            total_growth = final_memory['rss_mb'] - initial_memory['rss_mb']

            # Cleanup global variables
            for var_name in hidden_references:
                if var_name in globals():
                    del globals()[var_name]

            return {
                'initial_rss_mb': initial_memory['rss_mb'],
                'final_rss_mb': final_memory['rss_mb'],
                'memory_growth_mb': total_growth,
                'leak_objects_created': len(leak_objects),
                'weak_refs_tracked': len(weak_refs),
                'surviving_objects': surviving_objects,
                'closures_created': len(closures),
                'hidden_global_vars': len(hidden_references),
                'leak_detected': total_growth > 50,  # Significant growth indicates leak
                'gc_effectiveness': (len(weak_refs) - surviving_objects) / len(weak_refs) if weak_refs else 0
            }

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def test_memory_fragmentation(self) -> Dict[str, Any]:
        """Test 2: Memory fragmentation through varied allocation patterns"""
        print("\n🧩 Testing Memory Fragmentation...")

        initial_memory = self.get_memory_stats()
        allocated_objects = []
        fragmentation_patterns = []

        try:
            # Test 2.1: Fragmented allocation pattern
            print("  • Creating fragmented allocation pattern...")

            # Allocate many small objects, then delete every other one
            for i in range(self.fragmentation_allocations):
                # Vary allocation sizes to cause fragmentation
                if i % 3 == 0:
                    obj = ['x'] * 10     # Small
                elif i % 3 == 1:
                    obj = ['x'] * 100    # Medium
                else:
                    obj = ['x'] * 1000   # Large

                allocated_objects.append(obj)

                # Delete every 4th object to create holes
                if i % 4 == 3 and i > 0:
                    del allocated_objects[-1]  # Remove the last one

            # Test 2.2: Allocate large objects to test defragmentation
            print("  • Testing large object allocation after fragmentation...")
            large_objects = []
            for i in range(50):
                # Try to allocate large objects - this may trigger defragmentation
                try:
                    large_obj = ['y'] * 10000
                    large_objects.append(large_obj)
                except MemoryError:
                    print(f"    MemoryError at large object {i}")
                    break

            # Test 2.3: Pattern-based fragmentation
            print("  • Creating pattern-based fragmentation...")
            pattern_objects = []
            for pattern in ['small', 'medium', 'large']:
                size = {'small': 50, 'medium': 500, 'large': 5000}[pattern]
                for i in range(100):
                    obj = ['pattern_' + pattern] * size
                    pattern_objects.append(obj)

                    # Delete objects in specific pattern
                    if pattern == 'medium' and i % 2 == 1:
                        del pattern_objects[-1]

            fragmentation_memory = self.get_memory_stats()
            fragmentation_growth = fragmentation_memory['rss_mb'] - initial_memory['rss_mb']

            # Test 2.4: Measure allocation time after fragmentation
            print("  • Measuring allocation performance after fragmentation...")
            allocation_times = []
            for i in range(100):
                start = time.time()
                test_obj = ['perf_test'] * 1000
                end = time.time()
                allocation_times.append(end - start)
                del test_obj

            avg_allocation_time = sum(allocation_times) / len(allocation_times)

            # Test 2.5: Compact memory and measure improvement
            print("  • Testing memory compaction...")
            gc.collect()

            # Force compaction by allocating and freeing
            compactor = ['compactor'] * 100000
            del compactor
            gc.collect()

            post_compaction_memory = self.get_memory_stats()
            compaction_savings = fragmentation_memory['rss_mb'] - post_compaction_memory['rss_mb']

            return {
                'initial_rss_mb': initial_memory['rss_mb'],
                'fragmented_rss_mb': fragmentation_memory['rss_mb'],
                'post_compaction_rss_mb': post_compaction_memory['rss_mb'],
                'fragmentation_growth_mb': fragmentation_growth,
                'compaction_savings_mb': compaction_savings,
                'small_objects_allocated': self.fragmentation_allocations // 3,
                'medium_objects_allocated': self.fragmentation_allocations // 3,
                'large_objects_allocated': self.fragmentation_allocations // 3,
                'large_objects_after_frag': len(large_objects),
                'pattern_objects_created': len(pattern_objects),
                'avg_allocation_time_ms': avg_allocation_time * 1000,
                'compaction_effectiveness': compaction_savings / fragmentation_growth if fragmentation_growth > 0 else 0,
                'fragmentation_detected': fragmentation_growth > 100
            }

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def test_memory_compaction(self) -> Dict[str, Any]:
        """Test 3: Memory compaction and defragmentation efficiency"""
        print("\n🗜️  Testing Memory Compaction Efficiency...")

        initial_memory = self.get_memory_stats()

        try:
            # Test 3.1: Create severe fragmentation
            print("  • Creating severe memory fragmentation...")
            fragmented_blocks = []

            # Create alternating small/large blocks
            for i in range(200):
                if i % 2 == 0:
                    fragmented_blocks.append(['small_' + str(i)] * 100)
                else:
                    fragmented_blocks.append(['large_' + str(i)] * 10000)

            # Delete small blocks to create holes
            # Use reverse iteration to avoid index issues
            indices_to_delete = list(range(0, len(fragmented_blocks), 2))
            for i in reversed(indices_to_delete):
                if i < len(fragmented_blocks):
                    del fragmented_blocks[i]

            fragmented_memory = self.get_memory_stats()

            # Test 3.2: Manual compaction strategies
            print("  • Testing manual compaction strategies...")

            # Strategy 1: Simple garbage collection
            start_time = time.time()
            gc.collect()
            gc_time = time.time() - start_time

            after_gc_memory = self.get_memory_stats()

            # Strategy 2: Force reallocation
            start_time = time.time()
            temp_compactor = []
            for i in range(100):
                temp_compactor.append(['temp'] * 1000)
            del temp_compactor
            gc.collect()
            reallocation_time = time.time() - start_time

            after_reallocation_memory = self.get_memory_stats()

            # Strategy 3: Memory mapping compaction test
            print("  • Testing memory mapping compaction...")
            with tempfile.NamedTemporaryFile() as tmp:
                # Create memory-mapped file
                mmapped_data = []
                for i in range(10):
                    data = mmap.mmap(tmp.fileno(), 1024 * 1024)  # 1MB
                    mmapped_data.append(data)
                    data.write(b'm' * (1024 * 1024))

                mmap_memory = self.get_memory_stats()

                # Clean up memory maps
                for data in mmapped_data:
                    data.close()

            # Test 3.3: Measure compaction effectiveness
            final_memory = self.get_memory_stats()

            total_fragmentation = fragmented_memory['rss_mb'] - initial_memory['rss_mb']
            gc_savings = fragmented_memory['rss_mb'] - after_gc_memory['rss_mb']
            reallocation_savings = after_gc_memory['rss_mb'] - after_reallocation_memory['rss_mb']
            total_savings = fragmented_memory['rss_mb'] - final_memory['rss_mb']

            return {
                'initial_rss_mb': initial_memory['rss_mb'],
                'fragmented_rss_mb': fragmented_memory['rss_mb'],
                'after_gc_rss_mb': after_gc_memory['rss_mb'],
                'after_reallocation_rss_mb': after_reallocation_memory['rss_mb'],
                'final_rss_mb': final_memory['rss_mb'],
                'total_fragmentation_mb': total_fragmentation,
                'gc_savings_mb': gc_savings,
                'reallocation_savings_mb': reallocation_savings,
                'total_savings_mb': total_savings,
                'gc_time_ms': gc_time * 1000,
                'reallocation_time_ms': reallocation_time * 1000,
                'compaction_efficiency': total_savings / total_fragmentation if total_fragmentation > 0 else 0,
                'gc_efficiency': gc_savings / total_fragmentation if total_fragmentation > 0 else 0,
                'best_strategy': 'gc' if gc_savings > reallocation_savings else 'reallocation'
            }

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def test_memory_access_patterns(self) -> Dict[str, Any]:
        """Test 4: Memory access pattern performance differences"""
        print("\n📊 Testing Memory Access Patterns...")

        initial_memory = self.get_memory_stats()
        access_results = {}

        try:
            # Create test data
            test_size = min(self.access_pattern_test_size, 50000)  # Adjust for memory constraints
            test_data = list(range(test_size))

            # Test 4.1: Sequential access
            print("  • Testing sequential access pattern...")
            sequential_times = []
            for _ in range(10):
                start = time.time()
                total = 0
                for i in range(len(test_data)):
                    total += test_data[i]
                end = time.time()
                sequential_times.append(end - start)

            access_results['sequential_avg_time_ms'] = (sum(sequential_times) / len(sequential_times)) * 1000
            access_results['sequential_min_time_ms'] = min(sequential_times) * 1000
            access_results['sequential_max_time_ms'] = max(sequential_times) * 1000

            # Test 4.2: Random access
            print("  • Testing random access pattern...")
            random_indices = list(range(len(test_data)))
            random.shuffle(random_indices)

            random_times = []
            for _ in range(10):
                start = time.time()
                total = 0
                for idx in random_indices:
                    total += test_data[idx]
                end = time.time()
                random_times.append(end - start)

            access_results['random_avg_time_ms'] = (sum(random_times) / len(random_times)) * 1000
            access_results['random_min_time_ms'] = min(random_times) * 1000
            access_results['random_max_time_ms'] = max(random_times) * 1000

            # Test 4.3: Stride access (every nth element)
            print("  • Testing stride access patterns...")
            stride_results = {}
            for stride in [1, 2, 4, 8, 16, 32]:
                stride_times = []
                for _ in range(5):
                    start = time.time()
                    total = 0
                    for i in range(0, len(test_data), stride):
                        total += test_data[i]
                    end = time.time()
                    stride_times.append(end - start)

                stride_results[f'stride_{stride}_avg_ms'] = (sum(stride_times) / len(stride_times)) * 1000

            access_results.update(stride_results)

            # Test 4.4: Cache performance with different data structures
            print("  • Testing cache performance with different data structures...")

            # List access
            list_data = list(range(test_size))
            start = time.time()
            sum(list_data)
            list_access_time = (time.time() - start) * 1000

            # Array access
            array_data = array.array('i', range(test_size))
            start = time.time()
            sum(array_data)
            array_access_time = (time.time() - start) * 1000

            # Deque access
            deque_data = deque(range(test_size))
            start = time.time()
            sum(deque_data)
            deque_access_time = (time.time() - start) * 1000

            access_results['list_access_time_ms'] = list_access_time
            access_results['array_access_time_ms'] = array_access_time
            access_results['deque_access_time_ms'] = deque_access_time
            access_results['best_structure'] = min(['list', 'array', 'deque'],
                                                  key=lambda x: access_results[f'{x}_access_time_ms'])

            # Test 4.5: Memory bandwidth estimation
            print("  • Estimating memory bandwidth...")
            data_size_mb = (test_size * 8) / (1024 * 1024)  # Assuming 8 bytes per int

            # Read bandwidth
            start = time.time()
            total = sum(test_data)
            read_time = time.time() - start
            read_bandwidth_mb_s = data_size_mb / read_time

            access_results['estimated_data_size_mb'] = data_size_mb
            access_results['read_bandwidth_mb_s'] = read_bandwidth_mb_s

            # Write bandwidth
            start = time.time()
            write_data = [x * 2 for x in test_data]
            write_time = time.time() - start
            write_bandwidth_mb_s = data_size_mb / write_time

            access_results['write_bandwidth_mb_s'] = write_bandwidth_mb_s

            final_memory = self.get_memory_stats()
            access_results['memory_overhead_mb'] = final_memory['rss_mb'] - initial_memory['rss_mb']
            access_results['sequential_vs_random_ratio'] = (
                access_results['sequential_avg_time_ms'] / access_results['random_avg_time_ms']
            )

            return access_results

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def test_concurrent_memory_coherency(self) -> Dict[str, Any]:
        """Test 5: Memory coherency under concurrent modification"""
        print("\n🔄 Testing Concurrent Memory Coherency...")

        initial_memory = self.get_memory_stats()
        results = {}

        try:
            # Test 5.1: Concurrent allocation patterns
            print("  • Testing concurrent allocation patterns...")

            def concurrent_allocator(thread_id, allocations_per_thread, results_list):
                """Thread function for concurrent allocation"""
                local_objects = []
                inconsistencies = 0

                for i in range(allocations_per_thread):
                    try:
                        obj = [f'thread_{thread_id}_alloc_{i}'] * 100
                        local_objects.append(obj)

                        # Verify object integrity
                        if len(obj) != 100 or obj[0] != f'thread_{thread_id}_alloc_{i}':
                            inconsistencies += 1

                    except MemoryError:
                        break

                results_list.append({
                    'thread_id': thread_id,
                    'allocations': len(local_objects),
                    'inconsistencies': inconsistencies,
                    'final_memory': psutil.Process().memory_info().rss / (1024 * 1024)
                })

                return local_objects

            # Start concurrent allocation threads
            threads_results = []
            with ThreadPoolExecutor(max_workers=self.concurrent_threads) as executor:
                futures = []
                for i in range(self.concurrent_threads):
                    future = executor.submit(concurrent_allocator, i, 100, threads_results)
                    futures.append(future)

                # Wait for completion
                for future in as_completed(futures):
                    future.result()

            results['concurrent_allocation_results'] = threads_results
            results['total_concurrent_allocations'] = sum(r['allocations'] for r in threads_results)
            results['total_inconsistencies'] = sum(r['inconsistencies'] for r in threads_results)

            # Test 5.2: Shared data modification
            print("  • Testing shared data modification...")

            shared_data = [0] * 10000
            modification_errors = 0
            lock = threading.Lock()

            def shared_modifier(start_idx, end_idx, value, error_count_ref):
                """Modify shared data with potential race conditions"""
                local_errors = 0

                for i in range(start_idx, end_idx):
                    try:
                        with lock:
                            old_value = shared_data[i]
                            shared_data[i] = old_value + value

                            # Verify modification
                            if shared_data[i] != old_value + value:
                                local_errors += 1

                    except (IndexError, RuntimeError):
                        local_errors += 1

                error_count_ref.append(local_errors)

            # Start modification threads
            error_counts = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                chunk_size = len(shared_data) // 4

                for i in range(4):
                    start = i * chunk_size
                    end = (i + 1) * chunk_size if i < 3 else len(shared_data)
                    future = executor.submit(shared_modifier, start, end, i + 1, error_counts)
                    futures.append(future)

                for future in as_completed(futures):
                    future.result()

            results['shared_modification_errors'] = sum(error_counts)
            results['shared_data_integrity'] = sum(error_counts) == 0

            # Test 5.3: Memory pressure under concurrency
            print("  • Testing memory pressure under concurrency...")

            pressure_objects = []
            memory_pressure_errors = 0

            def memory_pressure_allocator(thread_id, pressure_results):
                """Allocate under memory pressure"""
                thread_objects = []
                errors = 0

                try:
                    for i in range(200):
                        obj = [f'pressure_{thread_id}_{i}'] * 1000
                        thread_objects.append(obj)

                        # Simulate some memory pressure
                        if i % 50 == 0:
                            # Try to allocate large object
                            try:
                                large_obj = ['large'] * 10000
                                thread_objects.append(large_obj)
                            except MemoryError:
                                errors += 1

                except Exception:
                    errors += 1

                pressure_results.append({
                    'thread_id': thread_id,
                    'objects': len(thread_objects),
                    'errors': errors
                })

                return thread_objects

            pressure_results = []
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                for i in range(6):
                    future = executor.submit(memory_pressure_allocator, i, pressure_results)
                    futures.append(future)

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception:
                        memory_pressure_errors += 1

            results['memory_pressure_errors'] = memory_pressure_errors
            results['pressure_test_results'] = pressure_results

            final_memory = self.get_memory_stats()
            memory_growth = final_memory['rss_mb'] - initial_memory['rss_mb']

            results['memory_growth_mb'] = memory_growth
            results['concurrent_threads'] = self.concurrent_threads
            results['coherency_passed'] = (results['total_inconsistencies'] == 0 and
                                         results['shared_modification_errors'] == 0)

            return results

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def test_advanced_memory_features(self) -> Dict[str, Any]:
        """Test 6: Advanced memory management feature effectiveness"""
        print("\n🚀 Testing Advanced Memory Management Features...")

        initial_memory = self.get_memory_stats()
        feature_results = {}

        try:
            # Test 6.1: Weak reference effectiveness
            print("  • Testing weak reference effectiveness...")

            weak_ref_objects = []
            weak_refs = []

            for i in range(100):
                # Use a custom class for weak reference support (strings don't support weak refs)
                class WeakRefTest:
                    def __init__(self, value):
                        self.value = value

                obj = WeakRefTest(f'weak_ref_test_{i}')
                weak_ref_objects.append(obj)
                weak_refs.append(weakref.ref(obj))

            # Verify weak references work
            pre_cleanup_surviving = sum(1 for ref in weak_refs if ref() is not None)

            # Delete strong references
            weak_ref_objects.clear()
            gc.collect()

            post_cleanup_surviving = sum(1 for ref in weak_refs if ref() is not None)

            feature_results['weak_refs_created'] = len(weak_refs)
            feature_results['weak_refs_pre_cleanup'] = pre_cleanup_surviving
            feature_results['weak_refs_post_cleanup'] = post_cleanup_surviving
            feature_results['weak_ref_effectiveness'] = (
                (pre_cleanup_surviving - post_cleanup_surviving) / pre_cleanup_surviving
                if pre_cleanup_surviving > 0 else 1.0
            )

            # Test 6.2: Memory pool efficiency
            print("  • Testing memory pool efficiency...")

            class SimpleMemoryPool:
                def __init__(self):
                    self._pool = []
                    self._created = 0
                    self._reused = 0

                def get_buffer(self, size):
                    for i, buf in enumerate(self._pool):
                        if len(buf) >= size:
                            self._pool.pop(i)
                            self._reused += 1
                            return buf[:size]
                    self._created += 1
                    return [None] * size

                def return_buffer(self, buf):
                    self._pool.append(buf)

            pool = SimpleMemoryPool()
            pool_buffers = []

            # Simulate buffer allocation/return cycle
            for cycle in range(50):
                buffers = []
                for i in range(10):
                    size = random.randint(100, 1000)
                    buf = pool.get_buffer(size)
                    buffers.append(buf)

                # Return buffers to pool
                for buf in buffers:
                    pool.return_buffer(buf)

            feature_results['pool_buffers_created'] = pool._created
            feature_results['pool_buffers_reused'] = pool._reused
            feature_results['pool_efficiency'] = (
                pool._reused / (pool._created + pool._reused) if (pool._created + pool._reused) > 0 else 0
            )

            # Test 6.3: Generator memory efficiency
            print("  • Testing generator memory efficiency...")

            def memory_intensive_generator(n):
                """Generator that yields data without storing all in memory"""
                for i in range(n):
                    yield [i] * 100

            # Compare generator vs list
            start_memory = self.get_memory_stats()

            # List approach
            list_data = []
            for i in range(1000):
                list_data.append([i] * 100)

            list_memory = self.get_memory_stats()
            list_memory_usage = list_memory['rss_mb'] - start_memory['rss_mb']

            del list_data
            gc.collect()

            # Generator approach
            gen_memory_start = self.get_memory_stats()
            gen_data = list(memory_intensive_generator(1000))  # Consume generator
            gen_memory = self.get_memory_stats()
            gen_memory_usage = gen_memory['rss_mb'] - gen_memory_start['rss_mb']

            feature_results['list_memory_usage_mb'] = list_memory_usage
            feature_results['generator_memory_usage_mb'] = gen_memory_usage
            feature_results['generator_efficiency_ratio'] = list_memory_usage / gen_memory_usage if gen_memory_usage > 0 else 1.0

            # Test 6.4: Memory-mapped file efficiency
            print("  • Testing memory-mapped file efficiency...")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_name = tmp.name
                # Write test data
                test_data = b'm' * (1024 * 1024)  # 1MB
                tmp.write(test_data)
                tmp.flush()

                # Memory map the file
                with open(tmp_name, 'r+b') as f:
                    mmapped_data = mmap.mmap(f.fileno(), 0)

                    mmap_memory_start = self.get_memory_stats()

                    # Access mapped memory
                    total = sum(mmapped_data[i] for i in range(min(1024, len(mmapped_data))))

                    mmap_memory = self.get_memory_stats()
                    mmap_overhead = mmap_memory['rss_mb'] - mmap_memory_start['rss_mb']

                    mmapped_data.close()

                os.unlink(tmp_name)

            feature_results['mmap_overhead_mb'] = mmap_overhead
            feature_results['mmap_efficient'] = mmap_overhead < 1.0  # Less than 1MB overhead is good

            # Test 6.5: Garbage collection tuning
            print("  • Testing garbage collection tuning...")

            # Test different GC thresholds
            gc.set_threshold(100, 10, 10)  # Aggressive GC

            gc_test_start = self.get_memory_stats()
            gc_objects = []

            for i in range(200):
                obj = [f'gc_test_{i}'] * 100
                gc_objects.append(obj)

                # Delete some objects to trigger GC
                if i % 10 == 9 and len(gc_objects) > 5:
                    for _ in range(5):
                        if gc_objects:
                            del gc_objects[0]

            gc_memory = self.get_memory_stats()
            gc_overhead = gc_memory['rss_mb'] - gc_test_start['rss_mb']

            feature_results['gc_tuning_overhead_mb'] = gc_overhead
            feature_results['gc_tuning_effective'] = gc_overhead < 10  # Less than 10MB overhead

            # Reset GC to defaults
            gc.set_threshold(700, 10, 10)

            final_memory = self.get_memory_stats()
            feature_results['total_feature_overhead_mb'] = final_memory['rss_mb'] - initial_memory['rss_mb']

            return feature_results

        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}

    def run_comprehensive_test(self):
        """Run all memory stress tests"""
        print("🧠 Advanced Memory Stress Test Agent")
        print("=" * 60)
        print(f"Test Duration: {self.test_duration} seconds")
        print(f"Process PID: {os.getpid()}")
        print(f"Initial Memory: {self.get_memory_stats()['rss_mb']:.1f}MB")
        print("=" * 60)

        start_time = time.time()
        test_start_memory = self.get_memory_stats()

        try:
            # Run all tests
            self.results['memory_leak_detection'] = self.test_memory_leak_detection()

            if time.time() - start_time < self.test_duration - 2:
                self.results['fragmentation_tests'] = self.test_memory_fragmentation()

            if time.time() - start_time < self.test_duration - 2:
                self.results['compaction_efficiency'] = self.test_memory_compaction()

            if time.time() - start_time < self.test_duration - 2:
                self.results['access_patterns'] = self.test_memory_access_patterns()

            if time.time() - start_time < self.test_duration - 2:
                self.results['concurrency_coherency'] = self.test_concurrent_memory_coherency()

            if time.time() - start_time < self.test_duration - 2:
                self.results['advanced_features'] = self.test_advanced_memory_features()

        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            self.results['error'] = str(e)

        end_time = time.time()
        test_end_memory = self.get_memory_stats()
        total_runtime = end_time - start_time

        # Final cleanup
        print("\n🧹 Performing final cleanup...")
        gc.collect()

        final_cleanup_memory = self.get_memory_stats()

        # Generate comprehensive report
        self.generate_test_report(
            test_start_memory,
            test_end_memory,
            final_cleanup_memory,
            total_runtime
        )

    def generate_test_report(self, start_mem, end_mem, cleanup_mem, runtime):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🧠 MEMORY STRESS TEST REPORT")
        print("=" * 60)

        print(f"⏱️  Total Runtime: {runtime:.2f} seconds")
        print(f"📊 Start Memory: {start_mem['rss_mb']:.1f}MB")
        print(f"📊 Peak Memory: {end_mem['rss_mb']:.1f}MB")
        print(f"📊 Final Memory: {cleanup_mem['rss_mb']:.1f}MB")
        print(f"📊 Memory Growth: {end_mem['rss_mb'] - start_mem['rss_mb']:.1f}MB")
        print(f"📊 Memory Recovered: {end_mem['rss_mb'] - cleanup_mem['rss_mb']:.1f}MB")

        print("\n📋 TEST RESULTS SUMMARY:")

        # Memory Leak Detection
        leak_results = self.results.get('memory_leak_detection', {})
        if 'error' not in leak_results:
            print(f"\n🔍 Memory Leak Detection:")
            print(f"   • Objects Created: {leak_results.get('leak_objects_created', 0):,}")
            print(f"   • Memory Growth: {leak_results.get('memory_growth_mb', 0):.1f}MB")
            print(f"   • GC Effectiveness: {leak_results.get('gc_effectiveness', 0):.1%}")
            print(f"   • Leak Detected: {'🚨 YES' if leak_results.get('leak_detected') else '✅ NO'}")

        # Fragmentation Tests
        frag_results = self.results.get('fragmentation_tests', {})
        if 'error' not in frag_results:
            print(f"\n🧩 Memory Fragmentation:")
            print(f"   • Fragmentation Growth: {frag_results.get('fragmentation_growth_mb', 0):.1f}MB")
            print(f"   • Compaction Savings: {frag_results.get('compaction_savings_mb', 0):.1f}MB")
            print(f"   • Compaction Efficiency: {frag_results.get('compaction_effectiveness', 0):.1%}")
            print(f"   • Fragmentation Detected: {'⚠️ YES' if frag_results.get('fragmentation_detected') else '✅ NO'}")

        # Compaction Efficiency
        compact_results = self.results.get('compaction_efficiency', {})
        if 'error' not in compact_results:
            print(f"\n🗜️  Memory Compaction:")
            print(f"   • Total Fragmentation: {compact_results.get('total_fragmentation_mb', 0):.1f}MB")
            print(f"   • Total Savings: {compact_results.get('total_savings_mb', 0):.1f}MB")
            print(f"   • GC Efficiency: {compact_results.get('gc_efficiency', 0):.1%}")
            print(f"   • Best Strategy: {compact_results.get('best_strategy', 'unknown')}")

        # Access Patterns
        access_results = self.results.get('access_patterns', {})
        if 'error' not in access_results:
            print(f"\n📊 Access Patterns:")
            print(f"   • Sequential Access: {access_results.get('sequential_avg_time_ms', 0):.2f}ms")
            print(f"   • Random Access: {access_results.get('random_avg_time_ms', 0):.2f}ms")
            print(f"   • Sequential/Random Ratio: {access_results.get('sequential_vs_random_ratio', 0):.2f}")
            print(f"   • Best Data Structure: {access_results.get('best_structure', 'unknown')}")
            print(f"   • Memory Bandwidth: {access_results.get('read_bandwidth_mb_s', 0):.1f}MB/s")

        # Concurrency Coherency
        concurrency_results = self.results.get('concurrency_coherency', {})
        if 'error' not in concurrency_results:
            print(f"\n🔄 Concurrent Memory Coherency:")
            print(f"   • Concurrent Allocations: {concurrency_results.get('total_concurrent_allocations', 0):,}")
            print(f"   • Inconsistencies: {concurrency_results.get('total_inconsistencies', 0):,}")
            print(f"   • Modification Errors: {concurrency_results.get('shared_modification_errors', 0):,}")
            print(f"   • Coherency Status: {'✅ PASSED' if concurrency_results.get('coherency_passed') else '❌ FAILED'}")

        # Advanced Features
        features_results = self.results.get('advanced_features', {})
        if 'error' not in features_results:
            print(f"\n🚀 Advanced Memory Features:")
            print(f"   • Weak Reference Effectiveness: {features_results.get('weak_ref_effectiveness', 0):.1%}")
            print(f"   • Memory Pool Efficiency: {features_results.get('pool_efficiency', 0):.1%}")
            print(f"   • Generator Efficiency Ratio: {features_results.get('generator_efficiency_ratio', 0):.1f}x")
            print(f"   • Memory Map Efficient: {'✅ YES' if features_results.get('mmap_efficient') else '❌ NO'}")
            print(f"   • GC Tuning Effective: {'✅ YES' if features_results.get('gc_tuning_effective') else '❌ NO'}")

        print("\n" + "=" * 60)
        print("🎯 OVERALL ASSESSMENT:")

        # Calculate overall scores
        scores = {}

        if 'memory_leak_detection' in self.results and 'error' not in self.results['memory_leak_detection']:
            leak_score = 1.0 - self.results['memory_leak_detection'].get('memory_growth_mb', 0) / 100
            scores['leak_detection'] = max(0, min(1, leak_score))

        if 'fragmentation_tests' in self.results and 'error' not in self.results['fragmentation_tests']:
            frag_score = 1.0 - self.results['fragmentation_tests'].get('compaction_effectiveness', 0)
            scores['fragmentation'] = max(0, min(1, 1 - self.results['fragmentation_tests'].get('fragmentation_growth_mb', 0) / 200))

        if 'concurrency_coherency' in self.results and 'error' not in self.results['concurrency_coherency']:
            scores['concurrency'] = 1.0 if self.results['concurrency_coherency'].get('coherency_passed') else 0.0

        if 'advanced_features' in self.results and 'error' not in self.results['advanced_features']:
            features_score = (
                self.results['advanced_features'].get('weak_ref_effectiveness', 0) * 0.3 +
                self.results['advanced_features'].get('pool_efficiency', 0) * 0.3 +
                (1.0 / max(1.0, self.results['advanced_features'].get('generator_efficiency_ratio', 1.0))) * 0.4
            )
            scores['advanced_features'] = max(0, min(1, features_score))

        if scores:
            overall_score = sum(scores.values()) / len(scores)
            print(f"   • Overall Score: {overall_score:.1%}")

            if overall_score >= 0.8:
                print("   • Status: 🟢 EXCELLENT - Memory management is very robust")
            elif overall_score >= 0.6:
                print("   • Status: 🟡 GOOD - Memory management is adequate with room for improvement")
            elif overall_score >= 0.4:
                print("   • Status: 🟠 FAIR - Memory management has some issues")
            else:
                print("   • Status: 🔴 POOR - Memory management needs significant improvement")

        print(f"\n📁 Detailed results saved to: /tmp/memory_stress_test_results.json")

        # Save detailed results
        with open('/tmp/memory_stress_test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'runtime_seconds': runtime,
                'memory_start': start_mem,
                'memory_end': end_mem,
                'memory_cleanup': cleanup_mem,
                'results': self.results,
                'scores': scores
            }, f, indent=2)

        print("=" * 60)

if __name__ == "__main__":
    # Run the memory stress test
    agent = MemoryStressTestAgent()
    agent.run_comprehensive_test()