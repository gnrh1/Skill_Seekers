#!/usr/bin/env python3
"""
Aggressive Memory Stress Test
Tests memory limits until system rejection or protection triggers
"""

import sys
import time
import gc
import psutil
import threading
import json
import random
import os
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
    protection_triggered: bool = False

class AggressiveMemoryTester:
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.results: List[MemoryTestResult] = []
        self.system_info = psutil.virtual_memory()

    def get_memory_mb(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024

    def get_system_memory_info(self):
        virt = psutil.virtual_memory()
        return {
            'total_gb': virt.total / 1024 / 1024 / 1024,
            'available_gb': virt.available / 1024 / 1024 / 1024,
            'percent': virt.percent,
            'used_gb': virt.used / 1024 / 1024 / 1024
        }

    def test_progressive_allocation_limits(self):
        """Progressive allocation until failure"""
        print("🧪 Testing Progressive Memory Limits...")

        initial_memory = self.get_memory_mb()
        size_mb = 100  # Start with 100MB
        allocations = []
        max_reached = False

        while time.time() - self.start_time < 25 and not max_reached:  # Leave 5 seconds buffer
            try:
                print(f"  Allocating {size_mb}MB...")
                start_time = time.time()

                data = bytearray(size_mb * 1024 * 1024)
                allocations.append(data)

                # Fill with pattern to ensure real allocation
                chunk_size = min(1024 * 1024, len(data))
                for i in range(0, len(data), chunk_size):
                    data[i] = (i // chunk_size) % 256

                end_time = time.time()
                current_memory = self.get_memory_mb()
                system_info = self.get_system_memory_info()

                print(f"    ✅ Success: {current_memory:.1f}MB process, {system_info['available_gb']:.2f}GB available")

                self.results.append(MemoryTestResult(
                    test_name=f"progressive_{size_mb}MB",
                    success=True,
                    allocation_mb=current_memory,
                    time_seconds=end_time - start_time
                ))

                # Increase allocation size
                size_mb = min(size_mb * 2, 2000)  # Cap at 2GB per allocation

                # Stop if system memory is critically low
                if system_info['available_gb'] < 1.0:
                    print(f"    ⚠️  Low system memory ({system_info['available_gb']:.2f}GB), stopping allocations")
                    break

                # Stop if process memory is very high (avoid system crash)
                if current_memory > 1000:  # 1GB process memory limit
                    print(f"    ⚠️  High process memory ({current_memory:.1f}MB), stopping allocations")
                    max_reached = True
                    break

            except MemoryError as e:
                print(f"    ❌ MemoryError at {size_mb}MB: System protection triggered")
                self.results.append(MemoryTestResult(
                    test_name=f"progressive_{size_mb}MB",
                    success=False,
                    allocation_mb=self.get_memory_mb(),
                    time_seconds=0,
                    error=f"MemoryError: {str(e)}",
                    protection_triggered=True
                ))
                break
            except Exception as e:
                print(f"    ❌ Error at {size_mb}MB: {e}")
                self.results.append(MemoryTestResult(
                    test_name=f"progressive_{size_mb}MB",
                    success=False,
                    allocation_mb=self.get_memory_mb(),
                    time_seconds=0,
                    error=str(e)
                ))
                break

        # Clean up aggressively
        print("  Cleaning up allocations...")
        for data in allocations:
            del data
        allocations.clear()
        gc.collect()

        final_memory = self.get_memory_mb()
        print(f"  ✅ Cleanup complete: {final_memory:.1f}MB final")

    def test_rapid_pressure_cycling(self):
        """Test rapid memory pressure cycles"""
        print("\n🔄 Testing Rapid Memory Pressure Cycling...")

        cycles = 200
        pressure_size = 50 * 1024 * 1024  # 50MB

        start_time = time.time()
        successful_cycles = 0

        for i in range(cycles):
            if time.time() - self.start_time > 25:  # Time buffer
                break

            try:
                # Allocate
                data = bytearray(pressure_size)

                # Fill with unique pattern
                for j in range(0, len(data), 1024):
                    data[j] = (i + j) % 256

                # Immediate deallocation
                del data

                successful_cycles += 1

                # Periodic GC
                if i % 20 == 0:
                    gc.collect()

                if i % 50 == 0:
                    current_memory = self.get_memory_mb()
                    print(f"    Cycle {i}: {current_memory:.1f}MB, {successful_cycles} successful")

            except MemoryError:
                print(f"    ❌ MemoryError at cycle {i}: Protection triggered")
                self.results.append(MemoryTestResult(
                    test_name="rapid_pressure_cycling",
                    success=False,
                    allocation_mb=self.get_memory_mb(),
                    time_seconds=0,
                    error="MemoryError during pressure cycling",
                    protection_triggered=True
                ))
                return
            except Exception as e:
                print(f"    ❌ Error at cycle {i}: {e}")
                break

        end_time = time.time()
        final_memory = self.get_memory_mb()

        self.results.append(MemoryTestResult(
            test_name="rapid_pressure_cycling",
            success=True,
            allocation_mb=final_memory,
            time_seconds=end_time - start_time
        ))

        print(f"  ✅ {successful_cycles}/{cycles} cycles completed: {end_time - start_time:.3f}s")

    def test_concurrent_memory_pressure(self):
        """Test concurrent memory pressure"""
        print("\n🔀 Testing Concurrent Memory Pressure...")

        def worker(worker_id: int, duration: float):
            """Worker that creates memory pressure"""
            allocations = []
            start_time = time.time()
            successful_allocs = 0

            while time.time() - start_time < duration:
                try:
                    size = random.randint(10, 50) * 1024 * 1024  # 10-50MB
                    data = bytearray(size)

                    # Fill with worker-specific pattern
                    pattern = worker_id.to_bytes(1, 'big') * len(data)
                    for j in range(0, len(data), len(pattern)):
                        data[j:j+len(pattern)] = pattern[:len(data)-j]

                    allocations.append(data)
                    successful_allocs += 1

                    # Limit allocations per worker
                    if len(allocations) > 5:
                        # Remove oldest
                        del allocations[0]

                    time.sleep(0.1)  # Brief pause

                except MemoryError:
                    break
                except Exception:
                    break

            # Clean up
            for data in allocations:
                del data

            return successful_allocs

        # Start concurrent workers
        num_workers = 3
        duration = 8  # 8 seconds of pressure

        print(f"  Starting {num_workers} workers for {duration}s...")
        start_time = time.time()

        threads = []
        for i in range(num_workers):
            thread = threading.Thread(target=worker, args=(i, duration))
            thread.start()
            threads.append(thread)

        # Wait for completion
        for thread in threads:
            thread.join()

        end_time = time.time()
        final_memory = self.get_memory_mb()
        system_info = self.get_system_memory_info()

        self.results.append(MemoryTestResult(
            test_name="concurrent_memory_pressure",
            success=True,
            allocation_mb=final_memory,
            time_seconds=end_time - start_time
        ))

        print(f"  ✅ Concurrent pressure: {final_memory:.1f}MB, {system_info['available_gb']:.2f}GB available")

    def test_extreme_boundary_conditions(self):
        """Test extreme boundary conditions"""
        print("\n🎯 Testing Extreme Boundary Conditions...")

        # Test 1: Extremely large allocation (should fail)
        try:
            size_gb = 100  # 100GB
            print(f"  Testing {size_gb}GB allocation...")
            start_time = time.time()
            data = bytearray(size_gb * 1024 * 1024 * 1024)
            end_time = time.time()
            print(f"    ❌ Unexpectedly succeeded: {end_time - start_time:.3f}s")
            del data
        except MemoryError:
            print(f"    ✅ Correctly rejected 100GB allocation")
            self.results.append(MemoryTestResult(
                test_name="extreme_large_allocation",
                success=True,
                allocation_mb=0,
                time_seconds=0,
                error="Correctly rejected extreme allocation",
                protection_triggered=True
            ))
        except Exception as e:
            print(f"    ⚠️  Error: {e}")

        # Test 2: Thousands of small allocations
        try:
            print("  Testing thousands of small allocations...")
            start_time = time.time()
            allocations = []
            for i in range(10000):
                size = random.randint(1, 100) * 1024  # 1KB-100KB
                data = bytearray(size)
                data[0] = i % 256
                allocations.append(data)

                if i % 1000 == 0:
                    print(f"    {i} allocations...")

            end_time = time.time()
            print(f"    ✅ {len(allocations)} allocations: {end_time - start_time:.3f}s")

            # Clean up
            for data in allocations:
                del data
            allocations.clear()

        except MemoryError:
            print(f"    ❌ MemoryError during small allocations")
            self.results.append(MemoryTestResult(
                test_name="many_small_allocations",
                success=False,
                allocation_mb=self.get_memory_mb(),
                time_seconds=0,
                error="MemoryError during small allocations",
                protection_triggered=True
            ))
        except Exception as e:
            print(f"    ❌ Error: {e}")

        # Test 3: Negative and zero sizes
        test_sizes = [-1, -1000, 0]
        for size in test_sizes:
            try:
                data = bytearray(size)
                if size <= 0:
                    print(f"    ❌ Unexpectedly succeeded with size {size}")
                    del data
                else:
                    print(f"    ✅ Size {size}: Success")
                    del data
            except (ValueError, MemoryError):
                if size <= 0:
                    print(f"    ✅ Size {size}: Correctly rejected")
                else:
                    print(f"    ❌ Size {size}: Unexpectedly failed")
            except Exception as e:
                print(f"    ⚠️  Size {size}: {e}")

    def test_memory_isolation_under_pressure(self):
        """Test memory isolation under pressure"""
        print("\n🛡️ Testing Memory Isolation Under Pressure...")

        try:
            # Create isolated regions
            regions = []
            sizes = [50, 100, 150]  # MB

            for i, size_mb in enumerate(sizes):
                data = bytearray(size_mb * 1024 * 1024)
                # Fill with unique pattern
                pattern = f"region_{i}_".encode()
                for j in range(0, len(data), len(pattern)):
                    data[j:j+len(pattern)] = pattern[:len(data)-j]
                regions.append(data)

            print(f"  Created {len(regions)} isolated regions")

            # Test isolation by modifying one region
            original_values = [region[0] for region in regions]
            regions[0][:100] = b'X' * 100

            # Verify other regions unchanged
            isolation_maintained = True
            for i in range(1, len(regions)):
                if regions[i][0] != original_values[i]:
                    isolation_maintained = False
                    break

            if isolation_maintained:
                print("  ✅ Memory isolation maintained under pressure")
            else:
                print("  ❌ Memory isolation compromised")

            # Clean up
            for region in regions:
                del region
            regions.clear()

        except MemoryError:
            print("  ❌ MemoryError during isolation test")
            self.results.append(MemoryTestResult(
                test_name="memory_isolation_pressure",
                success=False,
                allocation_mb=self.get_memory_mb(),
                time_seconds=0,
                error="MemoryError during isolation test",
                protection_triggered=True
            ))
        except Exception as e:
            print(f"  ❌ Error during isolation test: {e}")

    def run_test(self, duration_seconds: int = 30):
        """Run the aggressive memory test"""
        print(f"🚀 Aggressive Memory Stress Test")
        print(f"⏱️  Duration: {duration_seconds} seconds")
        print(f"💾 Initial memory: {self.get_memory_mb():.1f}MB")

        system_info = self.get_system_memory_info()
        print(f"🖥️  System: {system_info['total_gb']:.1f}GB total, {system_info['available_gb']:.1f}GB available")
        print("=" * 60)

        try:
            # Run aggressive tests
            self.test_extreme_boundary_conditions()

            if time.time() - self.start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_progressive_allocation_limits()

            if time.time() - self.start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_rapid_pressure_cycling()

            if time.time() - self.start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_concurrent_memory_pressure()

            if time.time() - self.start_time > duration_seconds - 5:
                print("\n⏰ Time limit reached")
                return self.generate_report()

            self.test_memory_isolation_under_pressure()

        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = time.time()
        total_time = end_time - self.start_time
        final_memory = self.get_memory_mb()
        final_system_info = self.get_system_memory_info()

        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        protection_triggered = [r for r in self.results if r.protection_triggered]

        report = {
            "test_summary": {
                "duration_seconds": total_time,
                "total_tests": len(self.results),
                "successful": len(successful_tests),
                "failed": len(failed_tests),
                "protection_triggered": len(protection_triggered),
                "success_rate": len(successful_tests) / len(self.results) if self.results else 0
            },
            "memory_metrics": {
                "initial_process_memory_mb": self.get_memory_mb() if not hasattr(self, 'initial_memory') else 0,
                "final_process_memory_mb": final_memory,
                "peak_estimated_mb": max([r.allocation_mb for r in successful_tests], default=final_memory)
            },
            "system_metrics": {
                "final_system_memory_gb": final_system_info['total_gb'],
                "final_system_available_gb": final_system_info['available_gb'],
                "final_system_percent": final_system_info['percent']
            },
            "protection_analysis": {
                "protection_triggered_count": len(protection_triggered),
                "protection_effective": len(protection_triggered) > 0,
                "memory_errors_detected": len([r for r in failed_tests if "MemoryError" in str(r.error)])
            },
            "results": [
                {
                    "test": r.test_name,
                    "success": r.success,
                    "memory_mb": r.allocation_mb,
                    "time_seconds": r.time_seconds,
                    "error": r.error,
                    "protection_triggered": r.protection_triggered
                }
                for r in self.results
            ]
        }

        # Print comprehensive summary
        print("\n" + "=" * 60)
        print("📊 AGGRESSIVE MEMORY TEST REPORT")
        print("=" * 60)

        print(f"\n🎯 EXECUTION SUMMARY:")
        print(f"   Duration: {total_time:.2f} seconds")
        print(f"   Tests Run: {len(self.results)}")
        print(f"   Successful: {len(successful_tests)} ({len(successful_tests)/len(self.results)*100:.1f}%)")
        print(f"   Failed: {len(failed_tests)}")
        print(f"   Protection Triggered: {len(protection_triggered)} times")

        print(f"\n💾 MEMORY ANALYSIS:")
        print(f"   Final Process Memory: {final_memory:.1f}MB")
        if successful_tests:
            print(f"   Peak Memory Reached: {max([r.allocation_mb for r in successful_tests]):.1f}MB")

        print(f"\n🖥️  SYSTEM STATE:")
        print(f"   System Memory: {final_system_info['total_gb']:.1f}GB")
        print(f"   Available: {final_system_info['available_gb']:.1f}GB ({final_system_info['percent']}% used)")

        print(f"\n🛡️  PROTECTION ANALYSIS:")
        if len(protection_triggered) > 0:
            print(f"   ✅ Memory protection mechanisms are ACTIVE")
            print(f"   ✅ System successfully prevented over-allocation")
            for test in protection_triggered:
                print(f"      - {test.test_name}")
        else:
            print(f"   ⚠️  Memory protection not triggered (conservative test or insufficient pressure)")

        # Key findings
        print(f"\n🔍 KEY FINDINGS:")

        if final_memory > 500:
            print(f"   ✅ Successfully allocated significant memory (>500MB)")
        else:
            print(f"   ⚠️  Conservative memory allocation")

        if len(protection_triggered) > 0:
            print(f"   ✅ System memory protection is working correctly")
        else:
            print(f"   ⚠️  Memory protection not exercised")

        if final_system_info['available_gb'] > 1.0:
            print(f"   ✅ System remained stable with adequate memory available")
        else:
            print(f"   ⚠️  Low system memory availability")

        memory_leak_detected = final_memory > 100  # Arbitrary threshold
        if memory_leak_detected:
            print(f"   ⚠️  Potential memory retention ({final_memory:.1f}MB)")
        else:
            print(f"   ✅ Good memory cleanup")

        return report

def main():
    """Main execution"""
    print("🧠 Aggressive Memory Stress Test Agent")
    print("Testing memory limits, protection mechanisms, and system recovery...")

    tester = AggressiveMemoryTester()

    try:
        report = tester.run_test(duration_seconds=30)

        # Save report
        report_file = "/Users/docravikumar/Code/skill-test/Skill_Seekers/aggressive_memory_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")
        return report

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()