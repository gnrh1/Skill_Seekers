#!/usr/bin/env python3
"""
Resource Monitor Test Suite
Validates that resource checking works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resource_monitor import get_resource_monitor, check_resources_before_agent_spawn

def test_resource_monitor():
    """Test resource monitor functionality"""
    print("=" * 60)
    print("RESOURCE MONITOR TEST")
    print("=" * 60)
    
    monitor = get_resource_monitor()
    
    # Test 1: Check system resources
    print("\n1. Testing system resource check...")
    ok, msg = monitor.check_system_resources()
    print(f"   Result: {ok}")
    print(f"   Message: {msg}")
    assert ok == True, f"Expected resources to be OK, got: {msg}"
    print("   ✅ PASS")
    
    # Test 2: Check agent count (should be 0)
    print("\n2. Testing agent count (should be 0)...")
    count = monitor.get_active_agent_count()
    print(f"   Active agents: {count}")
    assert count == 0, f"Expected 0 agents, got {count}"
    print("   ✅ PASS")
    
    # Test 3: Register a test agent
    print("\n3. Testing agent registration...")
    monitor.register_agent("test-agent-1", "test-generator")
    count_after = monitor.get_active_agent_count()
    print(f"   Active agents after registration: {count_after}")
    assert count_after == 1, f"Expected 1 agent after registration, got {count_after}"
    print("   ✅ PASS")
    
    # Test 4: Check resources with active agent
    print("\n4. Testing resource check with 1 active agent...")
    ok2, msg2 = monitor.check_system_resources()
    print(f"   Result: {ok2}")
    print(f"   Message: {msg2}")
    assert ok2 == True, f"Should still be OK with 1 agent, got: {msg2}"
    print("   ✅ PASS")
    
    # Test 5: Register second agent
    print("\n5. Testing with 2 agents (at limit - should pass)...")
    monitor.register_agent("test-agent-2", "security-analyst")
    count_two = monitor.get_active_agent_count()
    print(f"   Active agents: {count_two}")
    assert count_two == 2, f"Expected 2 agents, got {count_two}"
    
    ok3, msg3 = monitor.check_system_resources()
    print(f"   Result: {ok3}")
    print(f"   Message: {msg3}")
    # At exactly 2 agents (the limit), resources should be OK
    assert ok3 == True, f"Should be OK with 2 agents (at limit), got: {msg3}"
    print("   ✅ PASS")
    
    # Test 6: Try to exceed limit
    print("\n6. Testing with 3 agents (over limit - should fail)...")
    monitor.register_agent("test-agent-3", "code-analyzer")
    count_three = monitor.get_active_agent_count()
    print(f"   Active agents: {count_three}")
    
    ok4, msg4 = monitor.check_system_resources()
    print(f"   Result: {ok4}")
    print(f"   Message: {msg4}")
    assert ok4 == False, f"Should fail with 3 agents, but got OK"
    assert "Too many agents" in msg4, f"Expected 'Too many agents' message, got: {msg4}"
    print("   ✅ PASS - Correctly rejected!")
    
    # Test 7: Cleanup and verify
    print("\n7. Testing agent cleanup...")
    monitor.update_agent_status("test-agent-1", "completed")
    monitor.update_agent_status("test-agent-2", "completed")
    monitor.update_agent_status("test-agent-3", "completed")
    monitor.cleanup_completed_agents()
    
    count_after_cleanup = monitor.get_active_agent_count()
    print(f"   Active agents after cleanup: {count_after_cleanup}")
    assert count_after_cleanup == 0, f"Expected 0 agents after cleanup, got {count_after_cleanup}"
    print("   ✅ PASS")
    
    # Test 8: Memory monitoring
    print("\n8. Testing memory monitoring...")
    mem_stats = monitor.monitor_memory_usage()
    print(f"   Process memory: {mem_stats['process_memory_mb']:.0f}MB")
    print(f"   System memory available: {mem_stats['system_memory_available_mb']:.0f}MB")
    assert mem_stats['process_memory_mb'] > 0, "Memory usage should be > 0"
    print("   ✅ PASS")
    
    # Test 9: Helper function
    print("\n9. Testing check_resources_before_agent_spawn()...")
    ok5, msg5 = check_resources_before_agent_spawn()
    print(f"   Result: {ok5}")
    print(f"   Message: {msg5}")
    assert ok5 == True, f"Expected resources OK, got: {msg5}"
    print("   ✅ PASS")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
    print("\nResource monitor is working correctly:")
    print("  • Agent counting fixed (no false positives from system processes)")
    print("  • Resource checks pass when agents < 2")
    print("  • Resource checks fail when agents >= 3")
    print("  • Agent registration and cleanup work properly")
    print("  • Memory monitoring operational")
    
    return True

if __name__ == '__main__':
    try:
        test_resource_monitor()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
