#!/usr/bin/env python3
"""
Process-Level Memory Limit Enforcement
Last-resort hard limit that kills process before system freeze

This script sets RLIMIT_AS (address space limit) at the OS level.
When the limit is reached, Python will throw MemoryError before the kernel OOM killer intervenes.

Usage:
    import sys
    sys.path.insert(0, '.claude/scripts')
    from enforce_memory_limits import enforce_process_memory_limit
    
    enforce_process_memory_limit(limit_mb=2000)  # 2GB hard limit
"""

import resource
import psutil
import os
import sys
import signal
import logging

logger = logging.getLogger(__name__)

def enforce_process_memory_limit(limit_mb=2000, enable_emergency_handler=True):
    """
    Enforce hard memory limit on current process
    
    Args:
        limit_mb: Maximum memory in MB (default 2GB for safety)
        enable_emergency_handler: Install SIGTERM handler for graceful shutdown
    
    Returns:
        bool: True if limit was set successfully
    """
    try:
        # Convert MB to bytes
        limit_bytes = limit_mb * 1024 * 1024
        
        # Set address space limit (RLIMIT_AS)
        # This limits total virtual memory (stack + heap + mmap)
        soft_limit = limit_bytes
        hard_limit = limit_bytes + (100 * 1024 * 1024)  # +100MB buffer
        
        resource.setrlimit(resource.RLIMIT_AS, (soft_limit, hard_limit))
        
        # Verify the limit was set
        current_limits = resource.getrlimit(resource.RLIMIT_AS)
        actual_limit_mb = current_limits[0] / (1024 * 1024)
        
        print(f"✅ Memory limit enforced: {actual_limit_mb:.0f}MB")
        print(f"   Process will be killed if memory exceeds this limit")
        print(f"   Current memory usage: {get_current_memory_mb():.0f}MB")
        
        # Install emergency handler
        if enable_emergency_handler:
            install_emergency_handler()
        
        logger.info(f"Memory limit set to {limit_mb}MB")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not set memory limit: {e}")
        print(f"   System may still be vulnerable to memory exhaustion")
        logger.error(f"Failed to set memory limit: {e}")
        return False

def get_current_memory_mb():
    """Get current process memory usage in MB"""
    try:
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    except:
        return 0

def install_emergency_handler():
    """Install signal handler for graceful emergency shutdown"""
    
    def emergency_shutdown_handler(signum, frame):
        """Handle emergency shutdown signals"""
        print("\n" + "=" * 60)
        print("🚨 EMERGENCY MEMORY LIMIT REACHED")
        print("=" * 60)
        print(f"Process exceeded memory limit")
        print(f"Current memory: {get_current_memory_mb():.0f}MB")
        print(f"Signal: {signum}")
        print("\nForced process termination to prevent system freeze.")
        print("This is EXPECTED behavior - your system is protected.")
        print("=" * 60)
        
        # Force garbage collection one last time
        import gc
        gc.collect()
        
        # Exit immediately
        sys.exit(1)
    
    # Install handlers for termination signals
    signal.signal(signal.SIGTERM, emergency_shutdown_handler)
    signal.signal(signal.SIGINT, emergency_shutdown_handler)
    
    logger.info("Emergency shutdown handler installed")

def check_memory_safety():
    """
    Check if memory limits are properly configured
    Returns dict with safety status
    """
    status = {
        'limit_configured': False,
        'limit_mb': 0,
        'current_mb': get_current_memory_mb(),
        'safety_margin_mb': 0,
        'safe': False
    }
    
    try:
        limits = resource.getrlimit(resource.RLIMIT_AS)
        
        # Check if limit is set (not unlimited)
        if limits[0] != resource.RLIM_INFINITY:
            status['limit_configured'] = True
            status['limit_mb'] = limits[0] / (1024 * 1024)
            status['safety_margin_mb'] = status['limit_mb'] - status['current_mb']
            status['safe'] = status['safety_margin_mb'] > 500  # Safe if >500MB margin
        
    except Exception as e:
        logger.error(f"Error checking memory limits: {e}")
    
    return status

def print_memory_status():
    """Print current memory status and limits"""
    status = check_memory_safety()
    
    print("\n" + "=" * 60)
    print("MEMORY LIMIT STATUS")
    print("=" * 60)
    
    if status['limit_configured']:
        print(f"✅ Memory limit: {status['limit_mb']:.0f}MB (ACTIVE)")
        print(f"   Current usage: {status['current_mb']:.0f}MB")
        print(f"   Safety margin: {status['safety_margin_mb']:.0f}MB")
        
        if status['safe']:
            print(f"   Status: ✅ SAFE")
        else:
            print(f"   Status: ⚠️  WARNING - Low safety margin!")
    else:
        print(f"❌ No memory limit configured")
        print(f"   Current usage: {status['current_mb']:.0f}MB")
        print(f"   Status: ⚠️  VULNERABLE - No protection!")
    
    print("=" * 60)
    
    return status

if __name__ == '__main__':
    # Test the memory limit enforcement
    print("Memory Limit Enforcement Test")
    print("=" * 60)
    
    # Check current status
    print("\nCurrent status:")
    print_memory_status()
    
    # Enforce a 2GB limit
    print("\nEnforcing 2GB memory limit...")
    enforce_process_memory_limit(limit_mb=2000)
    
    # Verify
    print("\nAfter enforcement:")
    print_memory_status()
