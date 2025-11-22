#!/usr/bin/env python3
"""
Agent Pool Management System
Reuses agent instances to minimize memory overhead and startup time
"""

import threading
import time
import weakref
import gc
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import psutil

from resource_monitor import get_resource_monitor

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    TERMINATED = "terminated"

@dataclass
class PooledAgent:
    """Represents an agent instance in the pool"""
    agent_id: str
    agent_type: str
    process: Any
    created_time: float
    last_used_time: float
    usage_count: int = 0
    status: AgentStatus = AgentStatus.IDLE
    memory_usage_mb: float = 0.0
    task_history: List[str] = field(default_factory=list)
    max_uses: int = 50  # Recreate agent after N uses
    max_idle_time: float = 300.0  # Recreate after 5 minutes idle

class AgentPool:
    """Manages a pool of reusable agent instances"""

    def __init__(
        self,
        max_pool_size: int = 4,
        max_idle_time: float = 300.0,
        cleanup_interval: float = 60.0,
        memory_threshold_mb: int = 100
    ):
        self.max_pool_size = max_pool_size
        self.max_idle_time = max_idle_time
        self.cleanup_interval = cleanup_interval
        self.memory_threshold_mb = memory_threshold_mb

        self._pool: Dict[str, PooledAgent] = {}
        self._type_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
        self._shutdown = False

        self._resource_monitor = get_resource_monitor()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

        logger.info(f"Agent pool initialized with max size {max_pool_size}")

    @contextmanager
    def get_agent(self, agent_type: str, task_id: Optional[str] = None):
        """Get an agent from the pool (context manager)"""
        agent = None
        try:
            agent = self._acquire_agent(agent_type, task_id)
            yield agent
        finally:
            if agent:
                self._release_agent(agent)

    def _acquire_agent(self, agent_type: str, task_id: Optional[str] = None) -> PooledAgent:
        """Acquire an agent of the specified type"""
        with self._lock:
            # Try to find an idle agent of the right type
            for agent_id, agent in self._pool.items():
                if agent.agent_type == agent_type and agent.status == AgentStatus.IDLE:
                    # Check if agent is still valid
                    if self._is_agent_valid(agent):
                        agent.status = AgentStatus.BUSY
                        agent.last_used_time = time.time()
                        agent.usage_count += 1
                        if task_id:
                            agent.task_history.append(task_id)
                        logger.debug(f"Reusing pooled agent {agent_id} ({agent_type})")
                        return agent
                    else:
                        # Remove invalid agent
                        self._terminate_agent(agent_id)

            # Create new agent if pool not full
            if len(self._pool) < self.max_pool_size:
                return self._create_agent(agent_type, task_id)

            # Pool full - wait for available agent or force cleanup
            logger.warning(f"Agent pool full for type {agent_type}, forcing cleanup")
            self._cleanup_idle_agents()

            # Try again
            for agent_id, agent in self._pool.items():
                if agent.agent_type == agent_type and agent.status == AgentStatus.IDLE:
                    if self._is_agent_valid(agent):
                        agent.status = AgentStatus.BUSY
                        agent.last_used_time = time.time()
                        agent.usage_count += 1
                        if task_id:
                            agent.task_history.append(task_id)
                        return agent

            # If still no agent available, create one (overcommit)
            logger.warning(f"Overcommitting agent pool for type {agent_type}")
            return self._create_agent(agent_type, task_id)

    def _release_agent(self, agent: PooledAgent):
        """Release an agent back to the pool"""
        with self._lock:
            if agent.status == AgentStatus.BUSY:
                agent.status = AgentStatus.IDLE
                agent.last_used_time = time.time()
                logger.debug(f"Released agent {agent.agent_id} back to pool")

    def _create_agent(self, agent_type: str, task_id: Optional[str] = None) -> PooledAgent:
        """Create a new agent instance"""
        agent_id = f"{agent_type}_pooled_{int(time.time() * 1000)}"

        try:
            # Update memory usage estimate
            memory_mb = self._estimate_agent_memory(agent_type)

            agent = PooledAgent(
                agent_id=agent_id,
                agent_type=agent_type,
                process=None,  # Would be actual agent process
                created_time=time.time(),
                last_used_time=time.time(),
                usage_count=1,
                status=AgentStatus.BUSY,
                memory_usage_mb=memory_mb,
                task_history=[task_id] if task_id else []
            )

            self._pool[agent_id] = agent
            self._type_counts[agent_type] = self._type_counts.get(agent_type, 0) + 1

            # Register with resource monitor
            self._resource_monitor.register_agent(agent_id, agent_type)

            logger.info(f"Created new pooled agent {agent_id} ({agent_type})")
            return agent

        except Exception as e:
            logger.error(f"Failed to create agent {agent_type}: {e}")
            raise

    def _is_agent_valid(self, agent: PooledAgent) -> bool:
        """Check if agent is still valid for reuse"""
        # Check usage count
        if agent.usage_count >= agent.max_uses:
            logger.debug(f"Agent {agent.agent_id} exceeded max uses ({agent.usage_count})")
            return False

        # Check idle time
        idle_time = time.time() - agent.last_used_time
        if idle_time > agent.max_idle_time:
            logger.debug(f"Agent {agent.agent_id} idle too long ({idle_time:.1f}s)")
            return False

        # Check memory usage
        if agent.memory_usage_mb > self.memory_threshold_mb:
            logger.debug(f"Agent {agent.agent_id} using too much memory ({agent.memory_usage_mb}MB)")
            return False

        # Check if process is still alive (if we have a process handle)
        if agent.process and hasattr(agent.process, 'is_alive'):
            if not agent.process.is_alive():
                logger.debug(f"Agent {agent.agent_id} process is dead")
                return False

        return True

    def _terminate_agent(self, agent_id: str):
        """Terminate and remove an agent from the pool"""
        if agent_id not in self._pool:
            return

        agent = self._pool[agent_id]
        agent.status = AgentStatus.TERMINATED

        # Update resource monitor
        self._resource_monitor.update_agent_status(agent_id, 'terminated')

        # Terminate process if exists
        if agent.process and hasattr(agent.process, 'terminate'):
            try:
                agent.process.terminate()
                logger.debug(f"Terminated process for agent {agent_id}")
            except Exception as e:
                logger.warning(f"Failed to terminate process for {agent_id}: {e}")

        # Remove from pool
        del self._pool[agent_id]
        self._type_counts[agent.agent_type] -= 1

        logger.info(f"Removed agent {agent_id} from pool")

    def _cleanup_idle_agents(self):
        """Clean up idle or invalid agents"""
        with self._lock:
            agents_to_remove = []

            for agent_id, agent in self._pool.items():
                if agent.status == AgentStatus.IDLE:
                    if not self._is_agent_valid(agent):
                        agents_to_remove.append(agent_id)

            for agent_id in agents_to_remove:
                self._terminate_agent(agent_id)

            if agents_to_remove:
                logger.info(f"Cleaned up {len(agents_to_remove)} idle agents")

    def _cleanup_loop(self):
        """Periodic cleanup loop"""
        while not self._shutdown:
            try:
                self._cleanup_idle_agents()
                self._force_garbage_collection()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(10)

    def _force_garbage_collection(self):
        """Force garbage collection to reclaim memory"""
        try:
            # Force Python garbage collection
            collected = gc.collect()
            if collected > 0:
                logger.debug(f"Garbage collected {collected} objects")

            # Update memory usage for all agents
            for agent in self._pool.values():
                agent.memory_usage_mb = self._estimate_agent_memory(agent.agent_type)

        except Exception as e:
            logger.error(f"Error during garbage collection: {e}")

    def _estimate_agent_memory(self, agent_type: str) -> float:
        """Estimate memory usage for an agent type"""
        # Base memory usage estimates (can be refined)
        estimates = {
            'precision-editor': 50,
            'security-analyst': 40,
            'test-generator': 60,
            'performance-auditor': 45,
            'code-analyzer': 55,
            'architectural-critic': 50,
            'cognitive-resonator': 45,
            'possibility-weaver': 40
        }
        return estimates.get(agent_type, 50)  # Default 50MB

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics"""
        with self._lock:
            stats = {
                'total_agents': len(self._pool),
                'max_pool_size': self.max_pool_size,
                'agents_by_type': self._type_counts.copy(),
                'agents_by_status': {},
                'total_memory_usage_mb': 0,
                'oldest_agent_age': 0,
                'average_usage_count': 0
            }

            usage_counts = []
            current_time = time.time()

            for agent in self._pool.values():
                # Count by status
                status = agent.status.value
                stats['agents_by_status'][status] = stats['agents_by_status'].get(status, 0) + 1

                # Memory usage
                stats['total_memory_usage_mb'] += agent.memory_usage_mb

                # Age tracking
                age = current_time - agent.created_time
                stats['oldest_agent_age'] = max(stats['oldest_agent_age'], age)

                # Usage statistics
                usage_counts.append(agent.usage_count)

            if usage_counts:
                stats['average_usage_count'] = sum(usage_counts) / len(usage_counts)

            return stats

    def shutdown(self):
        """Shutdown the agent pool gracefully"""
        logger.info("Shutting down agent pool...")
        self._shutdown = True

        with self._lock:
            # Terminate all agents
            for agent_id in list(self._pool.keys()):
                self._terminate_agent(agent_id)

        # Wait for cleanup thread
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=10.0)

        # Final garbage collection
        gc.collect()
        logger.info("Agent pool shutdown complete")

    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.shutdown()
        except:
            pass

# Global pool instance
_agent_pool = None

def get_agent_pool() -> AgentPool:
    """Get global agent pool instance"""
    global _agent_pool
    if _agent_pool is None:
        _agent_pool = AgentPool()
    return _agent_pool

def with_pooled_agent(agent_type: str):
    """Decorator for functions that need a pooled agent"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            pool = get_agent_pool()
            with pool.get_agent(agent_type) as agent:
                kwargs['pooled_agent'] = agent
                return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test agent pool
    pool = AgentPool(max_pool_size=2)

    print("Agent Pool Test")
    print("=" * 50)

    # Test acquiring and releasing agents
    with pool.get_agent("precision-editor") as agent:
        print(f"Acquired agent: {agent.agent_id}")
        time.sleep(1)

    # Show stats
    stats = pool.get_pool_stats()
    print(f"Pool stats: {stats}")

    pool.shutdown()