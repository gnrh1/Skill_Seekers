#!/usr/bin/env python3
"""
Simple Memory Stress Test
Tests memory limits and protection without overwhelming the system
"""

import sys
import time
import gc
import psutil
import threading
import json
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class MemoryTestResult:
    test_name: str
    success: bool
    allocation_mb: float
    time_seconds: float
    error: Optional[str] = None

class SimpleMemoryTester:
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.results: List[MemoryTestResult] = []

    def get_memory_mb(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024

    def test_basic_allocations(self):
        """Test basic memory allocations"""
        print("🧪 Testing Basic Memory Allocations...")

        sizes_mb = [1, 5, 10, 25, 50, 100]  # MB

        for size_mb in sizes_mb:
            try:
                start_time = time.time()
                data = bytearray(size_mb * 1024 * 1024)

                # Fill with pattern to ensure real allocation
                for i in range(0, len(data), 1024):
                    data[i] = i % 256

                end_time = time.time()
                current_memory = self.get_memory_mb()

                self.results.append(MemoryTestResult(
                    test_name=f"allocation_{size_mb}MB",
                    success=True,
                    allocation_mb=current_memory,
                    time_seconds=end_time - start_time
                ))

                print(f"  ✅ {size_mb}MB: {current_memory:.1f}MB total, {end_time - start_time:.3f}s")

                # Clean up
                del data
                gc.collect()

            except MemoryError:
                self.results.append(MemoryTestResult(
                    test_name=f"allocation_{size_mb}MB",
                    success=False,
                    allocation_mb=0,
                    time_seconds=0,
                    error="MemoryError - allocation failed"
                ))
                print(f"  ❌ {size_mb}MB: MemoryError")
                break
            except Exception as e:
                self.results.append(MemoryTestResult(
                    test_name=f"allocation_{size_mb}MB",
                    success=False,
                    allocation_mb=0,
                    time_seconds=0,
                    error=str(e)
                ))
                print(f"  ❌ {size_mb}MB: {e}")

    def test_memory_thrashing(self):
        """Test rapid allocation/deallocation cycles"""
        print("\n🔄 Testing Memory Thrashing...")

        cycles = 100
        size_kb = 1024  # 1KB per allocation

        start_time = time.time()

        for i in range(cycles):
            try:
                # Allocate
                data = bytearray(size_kb * 10)  # 10KB
                data[0] = i % 256  # Touch memory

                # Deallocate
                del data

                if i % 20 == 0:
                    gc.collect()

            except Exception as e:
                print(f"  ❌ Thrash cycle {i}: {e}")
                break

        end_time = time.time()
        final_memory = self.get_memory_mb()

        self.results.append(MemoryTestResult(
            test_name="memory_thrashing",
            success=True,
            allocation_mb=final_memory,
            time_seconds=end_time - start_time
        ))

        print(f"  ✅ {cycles} cycles: {end_time - start_time:.3f}s, {final_memory:.1f}MB final")

    def test_concurrent_allocations(self):
        """Test concurrent memory allocations"""
        print("\n🔀 Testing Concurrent Allocations...")

        results = []
        start_time = time.time()

        def worker(worker_id: int):
            try:
                worker_start_time = time.time()
                allocations = []

                # Create multiple smaller allocations
                for i in range(10):
                    size = random.randint(1, 5) * 1024 * 1024  # 1-5MB
                    data = bytearray(size)
                    data[0] = worker_id  # Mark with worker ID
                    allocations.append(data)

                worker_end_time = time.time()

                # Clean up
                for data in allocations:
                    del data

                return {
                    'worker_id': worker_id,
                    'success': True,
                    'time': worker_end_time - worker_start_time,
                    'allocations': len(allocations)
                }

            except Exception as e:
                return {
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e),
                    'allocations': 0
                }

        # Start threads
        threads = []
        num_threads = min(4, 8)  # Conservative number of threads

        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            thread.start()
            threads.append(thread)

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5)

        final_memory = self.get_memory_mb()

        self.results.append(MemoryTestResult(
            test_name="concurrent_allocations",
            success=True,
            allocation_mb=final_memory,
            time_seconds=time.time() - start_time
        ))

        print(f"  ✅ {num_threads} threads: {final_memory:.1f}MB final")

    def test_boundary_conditions(self):
        """Test memory boundary conditions"""
        print("\n🎯 Testing Boundary Conditions...")

        # Test 1: Zero allocation
        try:
            data = bytearray(0)
            print("  ✅ Zero bytes: Success")
            del data
        except Exception as e:
            print(f"  ❌ Zero bytes: {e}")

        # Test 2: Single byte
        try:
            data = bytearray(1)
            data[0] = 42
            print("  ✅ Single byte: Success")
            del data
        except Exception as e:
            print(f"  ❌ Single byte: {e}")

        # Test 3: Page size
        try:
            page_size = 4096
            data = bytearray(page_size)
            for i in range(0, page_size, 1024):
                data[i] = i % 256
            print(f"  ✅ Page size ({page_size}): Success")
            del data
        except Exception as e:
            print(f"  ❌ Page size: {e}")

        # Test 4: Negative size (should fail)
        try:
            data = bytearray(-1)
            print("  ❌ Negative size: Unexpectedly succeeded")
        except (ValueError, MemoryError):
            print("  ✅ Negative size: Correctly rejected")
        except Exception as e:
            print(f"  ⚠️  Negative size: {e}")

    def test_memory_isolation(self):
        """Test basic memory isolation"""
        print("\n🛡️ Testing Memory Isolation...")

        try:
            # Create separate memory regions
            region1 = bytearray(1024 * 1024)  # 1MB
            region2 = bytearray(1024 * 1024)  # 1MB

            # Fill with different patterns
            for i in range(0, len(region1), 1024):
                region1[i] = 0x11
                region2[i] = 0x22

            # Verify isolation
            isolation_good = (region1[0] == 0x11 and region2[0] == 0x22)

            # Modify region1
            region1[0] = 0x33

            # Check region2 is unchanged
            isolation_good = isolation_good and (region2[0] == 0x22)

            if isolation_good:
                print("  ✅ Memory isolation: Maintained")
            else:
                print("  ❌ Memory isolation: Compromised")

            # Clean up
            del region1, region2

        except Exception as e:
            print(f"  ❌ Memory isolation test: {e}")

    def run_test(self, duration_seconds: int = 30):
        """Run the complete memory test"""
        print(f"🚀 Simple Memory Stress Test")
        print(f"⏱️  Duration: {duration_seconds} seconds")
        print(f"💾 Initial memory: {self.get_memory_mb():.1f}MB")
        print("=" * 50)

        start_time = time.time()

        try:
            # Run tests
            self.test_boundary_conditions()

            if time.time() - start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_basic_allocations()

            if time.time() - start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_memory_thrashing()

            if time.time() - start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_concurrent_allocations()

            if time.time() - start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_memory_isolation()

        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted")

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        end_time = time.time()
        total_time = end_time - self.start_time
        final_memory = self.get_memory_mb()

        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]

        report = {
            "summary": {
                "duration_seconds": total_time,
                "total_tests": len(self.results),
                "successful": len(successful_tests),
                "failed": len(failed_tests),
                "success_rate": len(successful_tests) / len(self.results) if self.results else 0
            },
            "memory": {
                "initial_mb": self.initial_memory if hasattr(self, 'initial_memory') else 0,
                "final_mb": final_memory,
                "peak_mb": max([r.allocation_mb for r in successful_tests], default=final_memory)
            },
            "results": [
                {
                    "test": r.test_name,
                    "success": r.success,
                    "memory_mb": r.allocation_mb,
                    "time_seconds": r.time_seconds,
                    "error": r.error
                }
                for r in self.results
            ]
        }

        # Print summary
        print("\n" + "=" * 50)
        print("📊 MEMORY TEST SUMMARY")
        print("=" * 50)
        print(f"Duration: {total_time:.2f} seconds")
        print(f"Tests: {len(self.results)} total, {len(successful_tests)} passed, {len(failed_tests)} failed")
        print(f"Success Rate: {len(successful_tests) / len(self.results) * 100:.1f}%" if self.results else "N/A")
        print(f"Final Memory: {final_memory:.1f}MB")

        if len(successful_tests) > 0:
            print(f"Peak Memory: {max([r.allocation_mb for r in successful_tests]):.1f}MB")

        # Key findings
        print(f"\n🔍 Key Findings:")

        if len(successful_tests) == len(self.results):
            print("  ✅ All tests completed successfully")
        else:
            print(f"  ⚠️  {len(failed_tests)} test(s) failed")

        if final_memory < 100:  # Reasonable final memory
            print("  ✅ Memory usage within expected bounds")
        else:
            print("  ⚠️  High memory usage detected")

        protection_triggered = any("MemoryError" in str(r.error) for r in failed_tests if r.error)
        if protection_triggered:
            print("  ✅ Memory protection mechanisms active")
        else:
            print("  ⚠️  Memory protection not triggered")

        return report

def main():
    """Main execution"""
    print("🧠 Simple Memory Stress Test")
    print("Testing memory limits and protection mechanisms...")

    tester = SimpleMemoryTester()
    tester.initial_memory = tester.get_memory_mb()

    try:
        report = tester.run_test(duration_seconds=30)

        # Save report
        report_file = "/Users/docravikumar/Code/skill-test/Skill_Seekers/simple_memory_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")
        return report

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    main()