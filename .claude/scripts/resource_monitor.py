#!/usr/bin/env python3
"""
Resource Monitor for Agent Ecosystem
Monitors memory, CPU, and agent count with automatic throttling
"""

import psutil
import os
import sys
import time
import json
import signal
import logging
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitor system resources and agent health"""

    # Configuration thresholds
    MEMORY_THRESHOLD_MB = 500  # Alert at 500MB usage
    CRITICAL_MEMORY_MB = 800   # Shutdown at 800MB
    MAX_CONCURRENT_AGENTS = 2   # Hard limit on concurrent agents
    CPU_THRESHOLD_PERCENT = 80  # Alert at 80% CPU usage

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.agent_registry: Dict[str, Dict] = {}
        self.shutdown_triggered = False

    def check_system_resources(self) -> Tuple[bool, str]:
        """Check if system has enough resources for new agents"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)

            # Check available memory
            if memory.available < self.MEMORY_THRESHOLD_MB * 1024 * 1024:
                return False, f"Low memory: {memory.available // (1024*1024)}MB available"

            # Check CPU usage
            if cpu_percent > self.CPU_THRESHOLD_PERCENT:
                return False, f"High CPU: {cpu_percent}% usage"

            # Check current agent count (allow up to MAX_CONCURRENT_AGENTS)
            active_agents = self.get_active_agent_count()
            if active_agents > self.MAX_CONCURRENT_AGENTS:
                return False, f"Too many agents: {active_agents} active (limit: {self.MAX_CONCURRENT_AGENTS})"

            return True, "Resources OK"

        except Exception as e:
            logger.error(f"Error checking resources: {e}")
            return False, f"Resource check failed: {e}"

    def get_active_agent_count(self) -> int:
        """Count currently active agent processes from registry only"""
        try:
            # FIXED: Only count agents we explicitly registered
            # Do NOT scan all processes (causes false positives from system agents)
            active_count = sum(
                1 for agent in self.agent_registry.values()
                if agent['status'] == 'active'
            )
            return active_count
        except Exception as e:
            logger.error(f"Error counting agents: {e}")
            return 0

    def register_agent(self, agent_id: str, agent_type: str, pid: Optional[int] = None):
        """Register a new agent for monitoring"""
        self.agent_registry[agent_id] = {
            'type': agent_type,
            'pid': pid or os.getpid(),
            'start_time': time.time(),
            'status': 'active',
            'memory_samples': []
        }
        logger.info(f"Registered agent {agent_id} ({agent_type})")

    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status"""
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id]['status'] = status
            self.agent_registry[agent_id]['end_time'] = time.time()

    def monitor_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()

            # System memory
            system_memory = psutil.virtual_memory()

            return {
                'process_memory_mb': memory_info.rss // (1024 * 1024),
                'process_memory_percent': memory_percent,
                'system_memory_available_mb': system_memory.available // (1024 * 1024),
                'system_memory_percent': system_memory.percent,
                'active_agents': self.get_active_agent_count(),
                'registered_agents': len([a for a in self.agent_registry.values() if a['status'] == 'active'])
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}

    def check_critical_thresholds(self) -> bool:
        """Check if critical thresholds are exceeded"""
        stats = self.monitor_memory_usage()

        # Critical memory threshold
        if stats.get('process_memory_mb', 0) > self.CRITICAL_MEMORY_MB:
            logger.critical(f"CRITICAL: Memory usage {stats['process_memory_mb']}MB exceeds threshold {self.CRITICAL_MEMORY_MB}MB")
            return True

        return False

    def cleanup_completed_agents(self):
        """Remove completed agents from registry and force garbage collection"""
        completed_agents = [
            agent_id for agent_id, agent_data in self.agent_registry.items()
            if agent_data['status'] in ['completed', 'failed', 'cancelled']
        ]

        for agent_id in completed_agents:
            del self.agent_registry[agent_id]
            logger.debug(f"Cleaned up agent {agent_id}")

        if completed_agents:
            import gc
            gc.collect()
            logger.info(f"Cleaned up {len(completed_agents)} completed agents")

    def emergency_shutdown(self, reason: str):
        """Emergency shutdown of all agents"""
        if self.shutdown_triggered:
            return

        self.shutdown_triggered = True
        logger.critical(f"EMERGENCY SHUTDOWN triggered: {reason}")

        # Mark all agents as cancelled
        for agent_id in self.agent_registry:
            self.update_agent_status(agent_id, 'cancelled')

        # Send shutdown signal to our process group
        try:
            os.killpg(os.getpgrp(), signal.SIGTERM)
        except:
            pass

        # Force exit if graceful shutdown fails
        sys.exit(1)

    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        stats = self.monitor_memory_usage()
        uptime = time.time() - self.start_time

        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'memory_stats': stats,
            'agent_registry': {
                'total_registered': len(self.agent_registry),
                'active': len([a for a in self.agent_registry.values() if a['status'] == 'active']),
                'completed': len([a for a in self.agent_registry.values() if a['status'] == 'completed']),
                'failed': len([a for a in self.agent_registry.values() if a['status'] == 'failed'])
            },
            'system_resources': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        }

# Global instance
_resource_monitor = None

def get_resource_monitor() -> ResourceMonitor:
    """Get global resource monitor instance"""
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor

def check_resources_before_agent_spawn() -> Tuple[bool, str]:
    """Convenience function to check resources before spawning new agent"""
    monitor = get_resource_monitor()
    return monitor.check_system_resources()

def register_agent(agent_id: str, agent_type: str, pid: Optional[int] = None):
    """Convenience function to register new agent"""
    monitor = get_resource_monitor()
    monitor.register_agent(agent_id, agent_type, pid)

def update_agent_status(agent_id: str, status: str):
    """Convenience function to update agent status"""
    monitor = get_resource_monitor()
    monitor.update_agent_status(agent_id, status)

if __name__ == "__main__":
    # Test resource monitoring
    monitor = ResourceMonitor()

    print("Resource Monitor Test")
    print("=" * 50)

    # Check resources
    ok, msg = monitor.check_system_resources()
    print(f"Resources OK: {ok} - {msg}")

    # Show current stats
    stats = monitor.monitor_memory_usage()
    print(f"Process Memory: {stats.get('process_memory_mb', 0)}MB")
    print(f"Active Agents: {stats.get('active_agents', 0)}")

    # Health report
    report = monitor.get_health_report()
    print(f"\nHealth Report:")
    print(json.dumps(report, indent=2))