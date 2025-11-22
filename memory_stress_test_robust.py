#!/usr/bin/env python3
"""
Robust Memory Stress Test Suite
Tests system memory limits, protection mechanisms, and performance under pressure
"""

import sys
import os
import time
import gc
import psutil
import threading
import multiprocessing
import tempfile
import json
import random
import weakref
import traceback
import resource
import mmap
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class MemoryTestResult:
    test_name: str
    success: bool
    allocation_size: int
    time_taken: float
    memory_used: int
    error_message: Optional[str] = None
    system_recovered: bool = True
    protection_triggered: bool = False

class RobustMemoryStressTester:
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.system_info = psutil.virtual_memory()
        self.results: List[MemoryTestResult] = []
        self.start_time = time.time()
        self.memory_snapshots = []

    def get_current_memory(self) -> int:
        """Get current memory usage in bytes"""
        return self.process.memory_info().rss

    def log_system_state(self, label: str):
        """Log current system memory state"""
        mem = self.process.memory_info()
        virt = psutil.virtual_memory()
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'label': label,
            'process_memory_mb': mem.rss / 1024 / 1024,
            'system_memory_percent': virt.percent,
            'system_available_mb': virt.available / 1024 / 1024,
            'elapsed_time': time.time() - self.start_time
        }
        self.memory_snapshots.append(snapshot)
        print(f"[{label}] Process: {mem.rss/1024/1024:.1f}MB, System: {virt.percent}% ({virt.available/1024/1024:.1f}MB available)")

    def test_boundary_conditions(self) -> List[MemoryTestResult]:
        """Test memory allocation boundary conditions"""
        print("\n=== Testing Memory Boundary Conditions ===")
        boundary_tests = []

        # Test 1: Zero-byte allocation
        try:
            start_time = time.time()
            data = bytearray(0)
            end_time = time.time()
            boundary_tests.append(MemoryTestResult(
                test_name="zero_byte_allocation",
                success=True,
                allocation_size=0,
                time_taken=end_time - start_time,
                memory_used=0,
                system_recovered=True
            ))
            del data
        except Exception as e:
            boundary_tests.append(MemoryTestResult(
                test_name="zero_byte_allocation",
                success=False,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                error_message=str(e)
            ))

        # Test 2: Single byte allocation
        try:
            start_time = time.time()
            data = bytearray(1)
            end_time = time.time()
            boundary_tests.append(MemoryTestResult(
                test_name="single_byte_allocation",
                success=True,
                allocation_size=1,
                time_taken=end_time - start_time,
                memory_used=1,
                system_recovered=True
            ))
            del data
        except Exception as e:
            boundary_tests.append(MemoryTestResult(
                test_name="single_byte_allocation",
                success=False,
                allocation_size=1,
                time_taken=0,
                memory_used=0,
                error_message=str(e)
            ))

        # Test 3: Page size allocation (4KB)
        try:
            page_size = 4096
            start_time = time.time()
            data = bytearray(page_size)
            end_time = time.time()
            boundary_tests.append(MemoryTestResult(
                test_name="page_size_allocation",
                success=True,
                allocation_size=page_size,
                time_taken=end_time - start_time,
                memory_used=page_size,
                system_recovered=True
            ))
            del data
        except Exception as e:
            boundary_tests.append(MemoryTestResult(
                test_name="page_size_allocation",
                success=False,
                allocation_size=4096,
                time_taken=0,
                memory_used=0,
                error_message=str(e)
            ))

        # Test 4: Negative size handling (should fail gracefully)
        try:
            start_time = time.time()
            data = bytearray(-1)  # This should raise an exception
            end_time = time.time()
            boundary_tests.append(MemoryTestResult(
                test_name="negative_size_allocation",
                success=False,  # Should not succeed
                allocation_size=-1,
                time_taken=end_time - start_time,
                memory_used=0,
                error_message="Negative size allocation unexpectedly succeeded"
            ))
            del data
        except (ValueError, MemoryError, OverflowError) as e:
            boundary_tests.append(MemoryTestResult(
                test_name="negative_size_allocation",
                success=True,  # Correctly failed
                allocation_size=-1,
                time_taken=0,
                memory_used=0,
                error_message=f"Correctly rejected: {e}",
                system_recovered=True
            ))
        except Exception as e:
            boundary_tests.append(MemoryTestResult(
                test_name="negative_size_allocation",
                success=False,
                allocation_size=-1,
                time_taken=0,
                memory_used=0,
                error_message=f"Unexpected error: {e}"
            ))

        # Test 5: Extremely large allocation (should fail)
        try:
            size = 10**12  # 1TB
            start_time = time.time()
            data = bytearray(size)
            end_time = time.time()
            boundary_tests.append(MemoryTestResult(
                test_name="extremely_large_allocation",
                success=False,  # Should not succeed on typical systems
                allocation_size=size,
                time_taken=end_time - start_time,
                memory_used=0,
                error_message="Extremely large allocation unexpectedly succeeded"
            ))
            del data
        except MemoryError as e:
            boundary_tests.append(MemoryTestResult(
                test_name="extremely_large_allocation",
                success=True,  # Correctly failed
                allocation_size=10**12,
                time_taken=0,
                memory_used=0,
                error_message=f"Correctly rejected: {e}",
                protection_triggered=True,
                system_recovered=True
            ))
        except Exception as e:
            boundary_tests.append(MemoryTestResult(
                test_name="extremely_large_allocation",
                success=False,
                allocation_size=10**12,
                time_taken=0,
                memory_used=0,
                error_message=f"Unexpected error: {e}"
            ))

        return boundary_tests

    def test_progressive_allocation(self) -> List[MemoryTestResult]:
        """Test progressive allocation until system rejection"""
        print("\n=== Testing Progressive Memory Allocation ===")
        results = []

        # Start with small allocations and progressively increase
        size = 1024  # Start with 1KB
        allocations = []

        while time.time() - self.start_time < 25:  # Leave 5 seconds for other tests
            try:
                self.log_system_state(f"Allocating {size/1024:.1f}KB")
                start_time = time.time()

                # Allocate memory
                data = bytearray(size)
                allocations.append(data)

                # Fill with some data to ensure real allocation
                if size <= 100 * 1024 * 1024:  # Only fill smaller allocations
                    for i in range(0, min(size, 1024), 256):
                        data[i] = i % 256

                end_time = time.time()
                current_memory = self.get_current_memory()

                results.append(MemoryTestResult(
                    test_name=f"progressive_allocation_{size/1024:.0f}KB",
                    success=True,
                    allocation_size=size,
                    time_taken=end_time - start_time,
                    memory_used=current_memory,
                    system_recovered=True
                ))

                # Double the size for next iteration
                size *= 2
                if size > 512 * 1024 * 1024:  # Cap at 512MB per allocation
                    size = 512 * 1024 * 1024

            except MemoryError:
                results.append(MemoryTestResult(
                    test_name=f"progressive_allocation_{size/1024:.0f}KB",
                    success=False,
                    allocation_size=size,
                    time_taken=0,
                    memory_used=self.get_current_memory(),
                    error_message="MemoryError - System rejected allocation",
                    protection_triggered=True,
                    system_recovered=True
                ))
                break
            except Exception as e:
                results.append(MemoryTestResult(
                    test_name=f"progressive_allocation_{size/1024:.0f}KB",
                    success=False,
                    allocation_size=size,
                    time_taken=0,
                    memory_used=self.get_current_memory(),
                    error_message=str(e)
                ))
                break

        # Clean up
        try:
            del allocations
            gc.collect()
        except:
            pass

        return results

    def test_memory_thrashing(self) -> List[MemoryTestResult]:
        """Test rapid allocation/deallocation cycles"""
        print("\n=== Testing Memory Thrashing ===")
        results = []

        sizes = [1024, 10240, 102400, 1024000, 10240000]  # 1KB to 10MB
        iterations = min(200, int((25 - (time.time() - self.start_time)) * 4))  # Adaptive iterations

        for i in range(iterations):
            size = sizes[i % len(sizes)]

            try:
                # Allocate
                start_time = time.time()
                data = bytearray(size)

                # Fill with some data to ensure real allocation
                chunk_size = min(1024, size)
                for j in range(0, size, chunk_size):
                    data[j] = (i + j) % 256

                # Deallocate
                del data
                gc.collect()

                end_time = time.time()

                if i % 50 == 0:  # Log every 50 iterations
                    self.log_system_state(f"Thrashing iteration {i}")

                results.append(MemoryTestResult(
                    test_name=f"memory_thrashing_{i}",
                    success=True,
                    allocation_size=size,
                    time_taken=end_time - start_time,
                    memory_used=self.get_current_memory(),
                    system_recovered=True
                ))

            except Exception as e:
                results.append(MemoryTestResult(
                    test_name=f"memory_thrashing_{i}",
                    success=False,
                    allocation_size=size,
                    time_taken=0,
                    memory_used=self.get_current_memory(),
                    error_message=str(e)
                ))
                break

        return results

    def test_concurrent_memory_pressure(self) -> List[MemoryTestResult]:
        """Test memory pressure from concurrent operations"""
        print("\n=== Testing Concurrent Memory Pressure ===")
        results = []

        def memory_worker(worker_id: int, allocation_size: int, duration: float) -> MemoryTestResult:
            """Worker that allocates and holds memory"""
            try:
                allocations = []
                start_time = time.time()
                total_allocated = 0

                while time.time() - start_time < duration:
                    try:
                        data = bytearray(allocation_size)

                        # Fill with pattern to ensure real allocation
                        pattern_str = f"worker{worker_id}"
                        pattern = pattern_str.encode()
                        for j in range(0, len(data), len(pattern)):
                            data[j:j+len(pattern)] = pattern

                        allocations.append(data)
                        total_allocated += allocation_size

                        # Hold memory briefly
                        time.sleep(0.01)

                        # Release some allocations to prevent OOM
                        if len(allocations) > 10:
                            removed = allocations.pop(0)
                            total_allocated -= len(removed)
                            del removed

                    except MemoryError:
                        break

                # Clean up
                for alloc in allocations:
                    del alloc
                del allocations

                return MemoryTestResult(
                    test_name=f"concurrent_worker_{worker_id}",
                    success=True,
                    allocation_size=total_allocated,
                    time_taken=time.time() - start_time,
                    memory_used=allocation_size,
                    system_recovered=True
                )

            except Exception as e:
                return MemoryTestResult(
                    test_name=f"concurrent_worker_{worker_id}",
                    success=False,
                    allocation_size=0,
                    time_taken=0,
                    memory_used=0,
                    error_message=str(e)
                )

        # Start multiple workers with different allocation sizes
        num_workers = min(4, multiprocessing.cpu_count())
        duration = min(8, 30 - (time.time() - self.start_time))

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                allocation_size = (i + 1) * 5 * 1024 * 1024  # 5MB, 10MB, 15MB, 20MB
                future = executor.submit(memory_worker, i, allocation_size, duration)
                futures.append(future)

            for future in futures:
                try:
                    result = future.result(timeout=duration + 5)
                    results.append(result)
                except Exception as e:
                    results.append(MemoryTestResult(
                        test_name="concurrent_worker_timeout",
                        success=False,
                        allocation_size=0,
                        time_taken=0,
                        memory_used=0,
                        error_message=str(e)
                    ))

        return results

    def test_memory_isolation(self) -> List[MemoryTestResult]:
        """Test memory isolation between different regions"""
        print("\n=== Testing Memory Isolation ===")
        results = []

        try:
            # Test 1: Separate array allocations with unique patterns
            arrays = []
            sizes = [5*1024*1024, 10*1024*1024, 15*1024*1024]  # 5MB, 10MB, 15MB

            for i, size in enumerate(sizes):
                start_time = time.time()
                data = bytearray(size)

                # Fill with unique pattern for isolation testing
                pattern_str = f"isolation_test_{i}"
                pattern = pattern_str.encode()
                for j in range(0, len(data), len(pattern)):
                    data[j:j+len(pattern)] = pattern

                arrays.append(data)
                end_time = time.time()

                results.append(MemoryTestResult(
                    test_name=f"memory_isolation_array_{i}",
                    success=True,
                    allocation_size=size,
                    time_taken=end_time - start_time,
                    memory_used=self.get_current_memory(),
                    system_recovered=True
                ))

            # Test 2: Verify isolation by checking patterns
            isolation_success = True
            for i, data in enumerate(arrays):
                pattern_str = f"isolation_test_{i}"
                pattern = pattern_str.encode()
                # Check first few bytes for pattern integrity
                if len(data) >= len(pattern):
                    if data[:len(pattern)] != pattern:
                        isolation_success = False
                        break
                else:
                    isolation_success = False
                    break

            # Test 3: Memory corruption resistance
            try:
                # Attempt to modify one array and check others
                if arrays:
                    # Modify first array
                    arrays[0][:100] = b'X' * 100

                    # Check that other arrays are unaffected
                    for i in range(1, len(arrays)):
                        pattern_str = f"isolation_test_{i}"
                        pattern = pattern_str.encode()
                        if arrays[i][:len(pattern)] != pattern:
                            isolation_success = False
                            break

            except Exception as e:
                isolation_success = False

            results.append(MemoryTestResult(
                test_name="memory_isolation_verification",
                success=isolation_success,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                system_recovered=isolation_success,
                error_message="Memory isolation compromised" if not isolation_success else None
            ))

            # Clean up
            del arrays
            gc.collect()

        except Exception as e:
            results.append(MemoryTestResult(
                test_name="memory_isolation_test",
                success=False,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                error_message=str(e)
            ))

        return results

    def test_file_io_memory_pressure(self) -> List[MemoryTestResult]:
        """Test memory pressure during file I/O operations"""
        print("\n=== Testing File I/O Memory Pressure ===")
        results = []

        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Test concurrent file operations with memory pressure
                def file_worker(worker_id: int, file_size: int, num_files: int) -> MemoryTestResult:
                    try:
                        start_time = time.time()
                        total_processed = 0

                        for i in range(num_files):
                            file_path = os.path.join(temp_dir, f"worker_{worker_id}_file_{i}.dat")

                            # Write data with memory allocation
                            with open(file_path, 'wb') as f:
                                # Create and write large data chunks
                                chunk_size = min(1024 * 1024, file_size)  # 1MB chunks
                                remaining = file_size

                                while remaining > 0:
                                    chunk = bytearray(min(chunk_size, remaining))
                                    # Fill with pattern
                                    pattern_str = f"data{worker_id}_{i}"
                                    pattern = pattern_str.encode()
                                    for j in range(0, len(chunk), len(pattern)):
                                        chunk[j:j+len(pattern)] = pattern
                                    f.write(chunk)
                                    remaining -= len(chunk)
                                    total_processed += len(chunk)

                            # Read back to create memory pressure
                            with open(file_path, 'rb') as f:
                                data = f.read()
                                # Process data in memory to create pressure
                                if len(data) > 512:
                                    # Simple processing to ensure data is loaded
                                    checksum = sum(data[:512]) % 256
                                    # Create some additional memory pressure
                                    processed_data = bytearray(len(data))
                                    processed_data[:len(data)] = data
                                    del processed_data
                                    del data

                            # Clean up file early to save space
                            os.remove(file_path)

                        end_time = time.time()

                        return MemoryTestResult(
                            test_name=f"file_io_worker_{worker_id}",
                            success=True,
                            allocation_size=total_processed,
                            time_taken=end_time - start_time,
                            memory_used=self.get_current_memory(),
                            system_recovered=True
                        )

                    except Exception as e:
                        return MemoryTestResult(
                            test_name=f"file_io_worker_{worker_id}",
                            success=False,
                            allocation_size=0,
                            time_taken=0,
                            memory_used=0,
                            error_message=str(e)
                        )

                # Run concurrent file operations
                num_workers = min(3, multiprocessing.cpu_count())
                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    futures = []
                    for i in range(num_workers):
                        file_size = (i + 1) * 2 * 1024 * 1024  # 2MB, 4MB, 6MB
                        num_files = 3
                        future = executor.submit(file_worker, i, file_size, num_files)
                        futures.append(future)

                    for future in futures:
                        try:
                            result = future.result(timeout=10)
                            results.append(result)
                        except Exception as e:
                            results.append(MemoryTestResult(
                                test_name="file_io_worker_timeout",
                                success=False,
                                allocation_size=0,
                                time_taken=0,
                                memory_used=0,
                                error_message=str(e)
                            ))

        except Exception as e:
            results.append(MemoryTestResult(
                test_name="file_io_test_setup",
                success=False,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                error_message=str(e)
            ))

        return results

    def test_memory_protection_mechanisms(self) -> List[MemoryTestResult]:
        """Test memory protection and error handling"""
        print("\n=== Testing Memory Protection Mechanisms ===")
        results = []

        # Test 1: Stack overflow protection
        def recursive_function(depth: int = 0):
            if depth > 10000:  # Should hit recursion limit first
                return
            return recursive_function(depth + 1)

        try:
            start_time = time.time()
            recursive_function()
            end_time = time.time()
            results.append(MemoryTestResult(
                test_name="stack_overflow_test",
                success=False,  # Should not succeed
                allocation_size=0,
                time_taken=end_time - start_time,
                memory_used=0,
                error_message="Stack overflow protection failed"
            ))
        except RecursionError:
            results.append(MemoryTestResult(
                test_name="stack_overflow_test",
                success=True,  # Correctly caught stack overflow
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                protection_triggered=True,
                system_recovered=True,
                error_message="Stack overflow correctly caught"
            ))
        except Exception as e:
            results.append(MemoryTestResult(
                test_name="stack_overflow_test",
                success=False,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                error_message=f"Unexpected error: {e}"
            ))

        # Test 2: Memory limits enforcement
        try:
            import resource

            # Set a reasonable memory limit (100MB)
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, hard))

            start_time = time.time()

            # Try to allocate more than the limit
            big_data = []
            for i in range(100):
                big_data.append(bytearray(10 * 1024 * 1024))  # 10MB each

            end_time = time.time()

            # If we get here, limit wasn't enforced
            results.append(MemoryTestResult(
                test_name="memory_limit_test",
                success=False,
                allocation_size=len(big_data) * 10 * 1024 * 1024,
                time_taken=end_time - start_time,
                memory_used=self.get_current_memory(),
                error_message="Memory limit not enforced"
            ))

        except MemoryError:
            results.append(MemoryTestResult(
                test_name="memory_limit_test",
                success=True,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                protection_triggered=True,
                system_recovered=True,
                error_message="Memory limit correctly enforced"
            ))
        except (ImportError, ValueError) as e:
            results.append(MemoryTestResult(
                test_name="memory_limit_test",
                success=False,
                allocation_size=0,
                time_taken=0,
                memory_used=0,
                error_message=f"Memory limit test failed: {e}"
            ))
        finally:
            try:
                # Restore original limits
                resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
            except:
                pass

        return results

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive memory stress test"""
        print(f"\n🧠 Starting Comprehensive Memory Stress Test")
        print(f"Initial Memory: {self.initial_memory/1024/1024:.1f}MB")
        print(f"System Memory: {self.system_info.total/1024/1024:.1f}MB total, {self.system_info.available/1024/1024:.1f}MB available")
        print(f"Test Duration: 30 seconds")

        self.log_system_state("Test Start")

        # Run all test suites
        all_results = []

        try:
            # Test 1: Boundary conditions
            boundary_results = self.test_boundary_conditions()
            all_results.extend(boundary_results)
            self.log_system_state("Boundary Conditions Complete")

            if time.time() - self.start_time > 28:
                print("Time limit reached, skipping remaining tests")
                return self.generate_report(all_results)

            # Test 2: Progressive allocation
            progressive_results = self.test_progressive_allocation()
            all_results.extend(progressive_results)
            self.log_system_state("Progressive Allocation Complete")

            if time.time() - self.start_time > 28:
                print("Time limit reached, skipping remaining tests")
                return self.generate_report(all_results)

            # Test 3: Memory thrashing
            thrashing_results = self.test_memory_thrashing()
            all_results.extend(thrashing_results)
            self.log_system_state("Memory Thrashing Complete")

            if time.time() - self.start_time > 28:
                print("Time limit reached, skipping remaining tests")
                return self.generate_report(all_results)

            # Test 4: Concurrent memory pressure
            concurrent_results = self.test_concurrent_memory_pressure()
            all_results.extend(concurrent_results)
            self.log_system_state("Concurrent Pressure Complete")

            if time.time() - self.start_time > 28:
                print("Time limit reached, skipping remaining tests")
                return self.generate_report(all_results)

            # Test 5: File I/O memory pressure
            file_results = self.test_file_io_memory_pressure()
            all_results.extend(file_results)
            self.log_system_state("File I/O Pressure Complete")

            if time.time() - self.start_time > 28:
                print("Time limit reached, skipping remaining tests")
                return self.generate_report(all_results)

            # Test 6: Memory isolation
            isolation_results = self.test_memory_isolation()
            all_results.extend(isolation_results)
            self.log_system_state("Memory Isolation Complete")

            if time.time() - self.start_time > 28:
                print("Time limit reached, skipping remaining tests")
                return self.generate_report(all_results)

            # Test 7: Memory protection mechanisms
            protection_results = self.test_memory_protection_mechanisms()
            all_results.extend(protection_results)
            self.log_system_state("Memory Protection Complete")

        except Exception as e:
            print(f"Error during testing: {e}")
            traceback.print_exc()

        return self.generate_report(all_results)

    def generate_report(self, results: List[MemoryTestResult]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = time.time()
        total_time = end_time - self.start_time

        # Calculate statistics
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]

        total_allocated = sum(r.allocation_size for r in successful_tests)
        max_allocation = max([r.allocation_size for r in successful_tests], default=0)

        # Memory protection effectiveness
        memory_errors = [r for r in failed_tests if "MemoryError" in str(r.error_message)]
        protection_triggered_tests = [r for r in results if r.protection_triggered]
        protection_effectiveness = len(memory_errors) > 0 or len(protection_triggered_tests) > 0

        # System recovery
        recovered_tests = [r for r in results if r.system_recovered]
        recovery_rate = len(recovered_tests) / len(results) if results else 0

        # Performance metrics
        avg_allocation_time = sum(r.time_taken for r in successful_tests) / len(successful_tests) if successful_tests else 0

        final_memory = self.get_current_memory()
        final_system = psutil.virtual_memory()

        # Boundary condition analysis
        boundary_tests = [r for r in results if "boundary" in r.test_name or "allocation" in r.test_name]
        boundary_passed = len([r for r in boundary_tests if r.success]) / len(boundary_tests) if boundary_tests else 0

        report = {
            "test_summary": {
                "duration_seconds": total_time,
                "total_tests": len(results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(results) if results else 0,
                "boundary_condition_pass_rate": boundary_passed
            },
            "memory_metrics": {
                "initial_process_memory_mb": self.initial_memory / 1024 / 1024,
                "final_process_memory_mb": final_memory / 1024 / 1024,
                "peak_memory_estimated_mb": max_allocation / 1024 / 1024,
                "total_allocated_gb": total_allocated / 1024 / 1024 / 1024,
                "memory_leak_detected": final_memory > self.initial_memory * 1.5,
                "memory_efficiency": (total_allocated / (1024 * 1024 * 1024)) / max(final_memory / (1024 * 1024 * 1024), 0.1)
            },
            "system_metrics": {
                "initial_system_memory_gb": self.system_info.total / 1024 / 1024 / 1024,
                "final_system_available_gb": final_system.available / 1024 / 1024 / 1024,
                "final_system_percent": final_system.percent,
                "system_memory_degradation": final_system.percent - self.system_info.percent
            },
            "protection_analysis": {
                "memory_protection_triggered": len(protection_triggered_tests) > 0,
                "protection_effectiveness": "EFFECTIVE" if protection_effectiveness else "NOT_TESTED",
                "memory_errors_handled": len(memory_errors),
                "boundary_conditions_passed": boundary_passed > 0.8,
                "system_recovery_rate": recovery_rate,
                "isolation_maintained": any("isolation" in r.test_name and r.success for r in results)
            },
            "performance_analysis": {
                "average_allocation_time_ms": avg_allocation_time * 1000,
                "max_allocation_size_gb": max_allocation / 1024 / 1024 / 1024,
                "concurrent_operations_handled": len([r for r in results if "concurrent" in r.test_name]),
                "thrashing_cycles_completed": len([r for r in results if "thrashing" in r.test_name and r.success])
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "allocation_size_mb": r.allocation_size / 1024 / 1024,
                    "time_taken_ms": r.time_taken * 1000,
                    "error": r.error_message,
                    "protection_triggered": r.protection_triggered,
                    "system_recovered": r.system_recovered
                }
                for r in results
            ],
            "memory_snapshots": self.memory_snapshots
        }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report"""
        print("\n" + "="*80)
        print("🧠 COMPREHENSIVE MEMORY STRESS TEST REPORT")
        print("="*80)

        # Summary
        summary = report["test_summary"]
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']} ({summary['success_rate']:.1%})")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Boundary Condition Pass Rate: {summary['boundary_condition_pass_rate']:.1%}")

        # Memory Metrics
        mem = report["memory_metrics"]
        print(f"\n💾 MEMORY METRICS:")
        print(f"   Initial Process Memory: {mem['initial_process_memory_mb']:.1f} MB")
        print(f"   Final Process Memory: {mem['final_process_memory_mb']:.1f} MB")
        print(f"   Peak Estimated Memory: {mem['peak_memory_estimated_mb']:.1f} MB")
        print(f"   Total Allocated: {mem['total_allocated_gb']:.2f} GB")
        print(f"   Memory Leak Detected: {'⚠️ YES' if mem['memory_leak_detected'] else '✅ NO'}")
        print(f"   Memory Efficiency: {mem['memory_efficiency']:.2f}")

        # System Metrics
        sys = report["system_metrics"]
        print(f"\n🖥️  SYSTEM METRICS:")
        print(f"   System Memory: {sys['initial_system_memory_gb']:.1f} GB total")
        print(f"   Available Memory: {sys['final_system_available_gb']:.1f} GB")
        print(f"   Memory Usage: {sys['final_system_percent']:.1f}%")
        print(f"   System Memory Degradation: {sys['system_memory_degradation']:+.1f}%")

        # Protection Analysis
        prot = report["protection_analysis"]
        print(f"\n🛡️  MEMORY PROTECTION:")
        print(f"   Protection Triggered: {'✅ YES' if prot['memory_protection_triggered'] else '⚠️ NO'}")
        print(f"   Protection Effectiveness: {prot['protection_effectiveness']}")
        print(f"   Memory Errors Handled: {prot['memory_errors_handled']}")
        print(f"   Boundary Conditions: {'✅ PASSED' if prot['boundary_conditions_passed'] else '❌ FAILED'}")
        print(f"   System Recovery Rate: {prot['system_recovery_rate']:.1%}")
        print(f"   Memory Isolation Maintained: {'✅ YES' if prot['isolation_maintained'] else '❌ NO'}")

        # Performance Analysis
        perf = report["performance_analysis"]
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        print(f"   Average Allocation Time: {perf['average_allocation_time_ms']:.2f} ms")
        print(f"   Max Allocation Size: {perf['max_allocation_size_gb']:.2f} GB")
        print(f"   Concurrent Operations: {perf['concurrent_operations_handled']}")
        print(f"   Thrashing Cycles: {perf['thrashing_cycles_completed']}")

        # Key Findings
        print(f"\n🔍 KEY FINDINGS:")

        # Memory limits
        if mem['total_allocated_gb'] > 0.5:
            print(f"   ✅ Successfully allocated significant memory ({mem['total_allocated_gb']:.2f}GB)")
        else:
            print(f"   ⚠️  Conservative memory allocation ({mem['total_allocated_gb']:.2f}GB)")

        # System stability
        if prot['system_recovery_rate'] > 0.9:
            print(f"   ✅ Excellent system recovery ({prot['system_recovery_rate']:.1%})")
        elif prot['system_recovery_rate'] > 0.7:
            print(f"   ⚠️  Good system recovery ({prot['system_recovery_rate']:.1%})")
        else:
            print(f"   ❌ Poor system recovery ({prot['system_recovery_rate']:.1%})")

        # Memory protection
        if prot['memory_protection_triggered'] or prot['memory_errors_handled'] > 0:
            print(f"   ✅ Memory protection mechanisms are active and working")
        else:
            print(f"   ⚠️  Memory protection not triggered (insufficient pressure or unavailable)")

        # Boundary conditions
        if prot['boundary_conditions_passed']:
            print(f"   ✅ Boundary conditions properly handled")
        else:
            print(f"   ❌ Boundary condition handling issues detected")

        # Memory isolation
        if prot['isolation_maintained']:
            print(f"   ✅ Memory isolation properly maintained")
        else:
            print(f"   ⚠️  Memory isolation issues detected")

        # Performance under pressure
        if perf['average_allocation_time_ms'] < 5:
            print(f"   ✅ Excellent performance under memory pressure")
        elif perf['average_allocation_time_ms'] < 20:
            print(f"   ⚠️  Moderate performance degradation")
        else:
            print(f"   ❌ Significant performance degradation")

        # System impact
        if sys['system_memory_degradation'] < 5:
            print(f"   ✅ Minimal impact on system memory")
        elif sys['system_memory_degradation'] < 15:
            print(f"   ⚠️  Moderate system memory impact")
        else:
            print(f"   ❌ High system memory impact")

        print(f"\n" + "="*80)

def main():
    """Main test execution"""
    print("🚀 Initializing Robust Memory Stress Test Suite...")

    # Create tester and run tests
    tester = RobustMemoryStressTester()

    try:
        # Run comprehensive test with 30-second limit
        report = tester.run_comprehensive_test()

        # Print detailed report
        tester.print_report(report)

        # Save report to file
        report_file = "/Users/docravikumar/Code/skill-test/Skill_Seekers/memory_stress_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        return report

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()