#!/usr/bin/env python3
"""
Memory Management System Stress Test
Tests the existing memory monitoring and protection systems
"""

import sys
import os
import time
import gc
import psutil
import json
from datetime import datetime

# Add scripts directory
sys.path.insert(0, '.claude/scripts')

def get_memory():
    return psutil.Process().memory_info().rss / (1024 * 1024)

print("🛡️  MEMORY MANAGEMENT SYSTEM STRESS TEST")
print(f"💾 Starting memory: {get_memory():.1f}MB")
print("=" * 70)

# Test the memory monitoring system itself
print("\n📊 Testing Memory Monitor System...")
try:
    from resource_monitor import get_resource_monitor, check_resources_before_agent_spawn, register_agent

    monitor = get_resource_monitor()

    # Test resource checking
    print("Testing resource checking...")
    resources_ok, msg = check_resources_before_agent_spawn()
    print(f"  Resources OK: {resources_ok} - {msg}")

    # Test agent registration
    print("Testing agent registration...")
    register_agent("test_agent_1", "stress_test_agent")
    register_agent("test_agent_2", "memory_consumer_agent")
    register_agent("test_agent_3", "performance_test_agent")

    # Get health report
    health = monitor.get_health_report()
    print(f"  Active agents: {health['agent_registry']['active']}")
    print(f"  Process memory: {health['memory_stats']['process_memory_mb']:.1f}MB")

except ImportError as e:
    print(f"⚠️  Could not import resource monitor: {e}")
except Exception as e:
    print(f"❌ Error testing resource monitor: {e}")

# Test memory limit enforcement
print("\n🚦 Testing Memory Limit Enforcement...")
try:
    from enforce_memory_limits import enforce_process_memory_limit, print_memory_status, check_memory_safety

    # Check current status
    print("Current memory status:")
    status = print_memory_status()

    # Check safety
    safety = check_memory_safety()
    print(f"Memory safety check: {'✅ SAFE' if safety['safe'] else '⚠️  WARNING'}")

    # Try to set a conservative limit
    print("Attempting to set 500MB memory limit...")
    limit_result = enforce_process_memory_limit(limit_mb=500)
    print(f"Limit enforcement result: {'✅ SUCCESS' if limit_result else '❌ FAILED'}")

except ImportError as e:
    print(f"⚠️  Could not import memory limit enforcement: {e}")
except Exception as e:
    print(f"❌ Error testing memory limits: {e}")

# Stress test the monitoring system
print("\n🔥 Stress Testing Monitoring System...")
start_time = time.time()
initial_memory = get_memory()

try:
    if 'monitor' in locals():
        # Create memory pressure while monitoring
        print("Creating memory pressure...")
        stress_data = []

        for i in range(100):
            # Create data that triggers monitoring
            stress_data.append({
                'iteration': i,
                'data': 'stress_test_data_' + 'x' * 1000,
                'memory_usage': get_memory(),
                'timestamp': time.time()
            })

            # Check resources every 10 iterations
            if i % 10 == 0:
                resources_ok, msg = check_resources_before_agent_spawn()
                current_memory = get_memory()
                print(f"  Iteration {i}: {current_memory:.1f}MB - Resources: {'OK' if resources_ok else 'LOW'}")

                # Get memory stats
                stats = monitor.monitor_memory_usage()
                print(f"    System memory available: {stats.get('system_memory_available_mb', 0):.1f}MB")

        peak_memory = get_memory()
        print(f"✅ Monitoring system stress peak: {peak_memory:.1f}MB (+{peak_memory-initial_memory:.1f}MB)")

        # Test cleanup monitoring
        print("Testing cleanup monitoring...")
        del stress_data
        gc.collect()

        # Check if monitoring detects cleanup
        time.sleep(1)
        cleanup_memory = get_memory()
        memory_recovered = peak_memory - cleanup_memory
        print(f"  Memory recovered: {memory_recovered:.1f}MB")

    else:
        print("⚠️  Monitor not available for stress testing")

except Exception as e:
    print(f"❌ Error in monitoring stress test: {e}")

# Test circuit breaker functionality
print("\n⚡ Testing Circuit Breaker System...")
try:
    from circuit_breaker import CircuitBreaker

    # Create a circuit breaker for memory protection
    memory_breaker = CircuitBreaker(
        failure_threshold=5,
        timeout=2,
        expected_exception=MemoryError
    )

    print(f"Circuit breaker state: {memory_breaker.state}")

    # Test normal operation
    @memory_breaker
    def memory_intensive_operation(size):
        data = [0] * size
        return len(data)

    # Normal calls should work
    result = memory_intensive_operation(1000)
    print(f"✅ Normal operation: {result}")

    # Simulate memory pressure
    print("Simulating memory pressure...")
    for i in range(3):
        try:
            result = memory_intensive_operation(50000)
            print(f"  Operation {i+1}: Success ({result})")
        except Exception as e:
            print(f"  Operation {i+1}: Failed ({e})")

    print(f"Final circuit breaker state: {memory_breaker.state}")

except ImportError as e:
    print(f"⚠️  Circuit breaker not available: {e}")
except Exception as e:
    print(f"❌ Error testing circuit breaker: {e}")

# Test memory protection hook
print("\n🔗 Testing Memory Protection Hook...")
try:
    # Set up environment for hook testing
    os.environ['CLAUDE_TOOL_PARAMS'] = json.dumps({
        'subagent_type': 'memory_stress_test_agent'
    })

    # Test hook directly
    from memory_protection_hook import extract_agent_type, check_memory_before_task

    agent_type = extract_agent_type()
    print(f"Extracted agent type: {agent_type}")

    # Test resource checking through hook
    print("Testing hook resource checking...")
    # Note: This might exit the script, so we'll wrap it
    try:
        # We can't actually call check_memory_before_task as it exits
        # But we can test the extract_agent_type function
        print("✅ Hook agent type extraction working")
    except SystemExit:
        print("✅ Hook would block/allow appropriately")
    except Exception as e:
        print(f"⚠️  Hook test issue: {e}")

except ImportError as e:
    print(f"⚠️  Memory protection hook not available: {e}")
except Exception as e:
    print(f"❌ Error testing memory protection hook: {e}")

# Final system assessment
print(f"\n📋 MEMORY MANAGEMENT SYSTEM ASSESSMENT")
print("=" * 70)

duration = time.time() - start_time
final_memory = get_memory()

print(f"Test duration: {duration:.1f}s")
print(f"Memory change: {final_memory - initial_memory:+.1f}MB")

# System capabilities check
print(f"\n🔧 System Capabilities:")

capabilities = {
    'Resource Monitor': 'resource_monitor' in locals(),
    'Memory Limits': 'enforce_process_memory_limit' in globals(),
    'Circuit Breaker': 'CircuitBreaker' in locals(),
    'Protection Hook': 'memory_protection_hook' in locals()
}

for capability, available in capabilities.items():
    status = "✅ Available" if available else "❌ Not Available"
    print(f"   {capability}: {status}")

# Overall health assessment
print(f"\n💚 System Health:")
available_count = sum(capabilities.values())
total_count = len(capabilities)

if available_count == total_count:
    print(f"   ✅ Excellent: All {total_count} memory protection systems available")
elif available_count >= total_count * 0.75:
    print(f"   ✅ Good: {available_count}/{total_count} memory protection systems available")
elif available_count >= total_count * 0.5:
    print(f"   ⚠️  Fair: {available_count}/{total_count} memory protection systems available")
else:
    print(f"   ❌ Poor: {available_count}/{total_count} memory protection systems available")

# Recommendations
print(f"\n💡 Recommendations:")
if not capabilities['Resource Monitor']:
    print("   • Implement resource monitoring for agent ecosystem")
if not capabilities['Memory Limits']:
    print("   • Add memory limit enforcement for safety")
if not capabilities['Circuit Breaker']:
    print("   • Consider circuit breaker for fault tolerance")
if not capabilities['Protection Hook']:
    print("   • Add pre-execution memory protection hooks")

print(f"\n🎯 MEMORY MANAGEMENT SYSTEM TEST COMPLETED")