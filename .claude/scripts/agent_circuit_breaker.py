#!/usr/bin/env python3
"""
Circuit Breaker for Agent Resource Management
Prevents resource exhaustion through intelligent throttling
"""

import time
import threading
import queue
import logging
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from resource_monitor import get_resource_monitor

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Rejecting requests
    HALF_OPEN = "half_open"  # Testing if system recovered

@dataclass
class ExecutionResult:
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

class ResourceCircuitBreaker:
    """Circuit breaker that trips on resource exhaustion"""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        expected_exception: type = Exception,
        memory_threshold_mb: int = 500
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.memory_threshold_mb = memory_threshold_mb

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

        self._lock = threading.RLock()
        self._resource_monitor = get_resource_monitor()

    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker functionality"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper

    def call(self, func: Callable, *args, **kwargs) -> ExecutionResult:
        """Execute function with circuit breaker protection"""
        start_time = time.time()

        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    return ExecutionResult(
                        success=False,
                        error=f"Circuit breaker OPEN (retry in {self._time_until_retry():.1f}s)",
                        execution_time=time.time() - start_time
                    )

        # Check resources before execution
        resources_ok, resource_msg = self._check_resources()
        if not resources_ok:
            with self._lock:
                self._on_failure()
            return ExecutionResult(
                success=False,
                error=f"Resource check failed: {resource_msg}",
                execution_time=time.time() - start_time
            )

        # Execute the function
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            with self._lock:
                self._on_success()

            return ExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time
            )

        except self.expected_exception as e:
            execution_time = time.time() - start_time
            with self._lock:
                self._on_failure()

            logger.warning(f"Circuit breaker caught exception: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

        except Exception as e:
            # Unexpected exception - don't trip circuit breaker
            execution_time = time.time() - start_time
            logger.error(f"Unexpected exception in circuit breaker: {e}")
            return ExecutionResult(
                success=False,
                error=f"Unexpected error: {e}",
                execution_time=execution_time
            )

    def _check_resources(self) -> tuple[bool, str]:
        """Check if system resources are adequate"""
        try:
            # Get resource stats
            stats = self._resource_monitor.monitor_memory_usage()

            # Check memory threshold
            if stats.get('process_memory_mb', 0) > self.memory_threshold_mb:
                return False, f"Memory usage {stats['process_memory_mb']}MB exceeds threshold {self.memory_threshold_mb}MB"

            # Use resource monitor's built-in checks
            return self._resource_monitor.check_system_resources()

        except Exception as e:
            logger.error(f"Error checking resources: {e}")
            return False, f"Resource check error: {e}"

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _time_until_retry(self) -> float:
        """Calculate time until circuit breaker can retry"""
        if not self.last_failure_time:
            return 0.0
        elapsed = time.time() - self.last_failure_time
        return max(0.0, self.recovery_timeout - elapsed)

    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.debug("Circuit breaker: Success recorded")

    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        with self._lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time,
                'time_until_retry': self._time_until_retry() if self.state == CircuitState.OPEN else 0.0,
                'memory_threshold_mb': self.memory_threshold_mb
            }

    def force_open(self):
        """Force circuit breaker into OPEN state"""
        with self._lock:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            logger.warning("Circuit breaker forced OPEN")

    def force_close(self):
        """Force circuit breaker into CLOSED state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            logger.info("Circuit breaker forced CLOSED")

class AgentThrottler:
    """Throttles agent execution based on system resources"""

    def __init__(
        self,
        max_concurrent_agents: int = 2,
        resource_check_interval: float = 1.0,
        queue_timeout: float = 30.0
    ):
        self.max_concurrent_agents = max_concurrent_agents
        self.resource_check_interval = resource_check_interval
        self.queue_timeout = queue_timeout

        self.execution_queue = queue.Queue()
        self.active_agents = 0
        self._shutdown = False

        self._lock = threading.RLock()
        self._resource_monitor = get_resource_monitor()

        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def submit_agent_task(self, agent_id: str, agent_func: Callable, *args, **kwargs) -> ExecutionResult:
        """Submit agent task for throttled execution"""
        task = {
            'agent_id': agent_id,
            'func': agent_func,
            'args': args,
            'kwargs': kwargs,
            'submitted_time': time.time(),
            'result': None
        }

        try:
            # Add to queue with timeout
            self.execution_queue.put(task, timeout=self.queue_timeout)
            logger.info(f"Submitted agent task {agent_id} to throttler")

            # Wait for completion (blocking)
            return self._wait_for_completion(agent_id)

        except queue.Full:
            return ExecutionResult(
                success=False,
                error=f"Throttler queue full after {self.queue_timeout}s"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Throttler error: {e}"
            )

    def _wait_for_completion(self, agent_id: str, timeout: float = 120.0) -> ExecutionResult:
        """Wait for agent task completion"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if task completed (would need to implement result tracking)
            time.sleep(0.1)

        return ExecutionResult(
            success=False,
            error="Timeout waiting for agent completion"
        )

    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._shutdown:
            try:
                self._process_queue()
                time.sleep(self.resource_check_interval)
            except Exception as e:
                logger.error(f"Error in throttler monitor loop: {e}")
                time.sleep(1.0)

    def _process_queue(self):
        """Process pending agent tasks"""
        with self._lock:
            # Check if we can execute more agents
            if self.active_agents >= self.max_concurrent_agents:
                return

            # Check resources
            resources_ok, resource_msg = self._resource_monitor.check_system_resources()
            if not resources_ok:
                logger.debug(f"Cannot execute more agents: {resource_msg}")
                return

            # Try to get next task
            try:
                task = self.execution_queue.get_nowait()
                self._execute_agent_task(task)
            except queue.Empty:
                pass

    def _execute_agent_task(self, task: Dict[str, Any]):
        """Execute a single agent task"""
        agent_id = task['agent_id']
        func = task['func']
        args = task['args']
        kwargs = task['kwargs']

        logger.info(f"Executing agent {agent_id}")
        self.active_agents += 1

        # Execute in thread
        def execute():
            try:
                result = func(*args, **kwargs)
                logger.info(f"Agent {agent_id} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Agent {agent_id} failed: {e}")
                raise
            finally:
                with self._lock:
                    self.active_agents -= 1

        thread = threading.Thread(target=execute, daemon=True)
        thread.start()

    def shutdown(self):
        """Shutdown throttler gracefully"""
        self._shutdown = True
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)

    def get_status(self) -> Dict[str, Any]:
        """Get throttler status"""
        with self._lock:
            return {
                'active_agents': self.active_agents,
                'max_concurrent_agents': self.max_concurrent_agents,
                'queue_size': self.execution_queue.qsize(),
                'shutdown': self._shutdown
            }

# Global instances
_circuit_breaker = None
_throttler = None

def get_circuit_breaker() -> ResourceCircuitBreaker:
    """Get global circuit breaker instance"""
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = ResourceCircuitBreaker()
    return _circuit_breaker

def get_throttler() -> AgentThrottler:
    """Get global throttler instance"""
    global _throttler
    if _throttler is None:
        _throttler = AgentThrottler()
    return _throttler

def with_circuit_breaker(func: Callable) -> Callable:
    """Decorator to apply circuit breaker to function"""
    breaker = get_circuit_breaker()
    return breaker(func)