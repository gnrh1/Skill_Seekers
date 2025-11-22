#!/usr/bin/env python3
"""
Memory-Enhanced Orchestrator Agent
Integrates resource monitoring, circuit breaking, and agent pooling
"""

import sys
import os
import time
import json
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add our custom modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resource_monitor import get_resource_monitor, check_resources_before_agent_spawn, register_agent, update_agent_status
from agent_circuit_breaker import get_circuit_breaker, get_throttler, with_circuit_breaker
from agent_pool import get_agent_pool, with_pooled_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/orchestrator_memory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AgentTask:
    """Represents a task to be delegated to an agent"""
    agent_type: str
    description: str
    prompt: str
    model: str = "haiku"
    timeout: float = 120.0
    priority: int = 1
    requires_resources: bool = True

@dataclass
class OrchestrationPlan:
    """Represents an orchestration plan"""
    tasks: List[AgentTask]
    max_parallel: int = 2
    resource_check: bool = True
    circuit_breaker_enabled: bool = True

class MemoryEnhancedOrchestrator:
    """Orchestrator with integrated memory management"""

    def __init__(self):
        self.resource_monitor = get_resource_monitor()
        self.circuit_breaker = get_circuit_breaker()
        self.throttler = get_throttler()
        self.agent_pool = get_agent_pool()

        self.active_tasks: Dict[str, Any] = {}
        self.task_results: Dict[str, Any] = {}
        self.orchestration_id = f"orch_{int(time.time())}"

        logger.info(f"Memory-enhanced orchestrator initialized: {self.orchestration_id}")

    def create_plan(self, user_prompt: str) -> OrchestrationPlan:
        """Create an orchestration plan from user prompt"""
        # Analyze prompt to determine required agents
        required_agents = self._analyze_prompt_requirements(user_prompt)

        # Create tasks for each agent
        tasks = []
        for agent_type, description in required_agents:
            task = AgentTask(
                agent_type=agent_type,
                description=description,
                prompt=self._create_agent_prompt(user_prompt, agent_type, description)
            )
            tasks.append(task)

        # Determine parallel execution capacity
        max_parallel = self._calculate_parallel_capacity(tasks)

        return OrchestrationPlan(
            tasks=tasks,
            max_parallel=max_parallel,
            resource_check=True,
            circuit_breaker_enabled=True
        )

    def _analyze_prompt_requirements(self, prompt: str) -> List[Tuple[str, str]]:
        """Analyze prompt to determine which agents are needed"""
        requirements = []

        # Security analysis keywords
        if any(word in prompt.lower() for word in ['security', 'vulnerability', 'auth', 'encryption', 'safe']):
            requirements.append(('security-analyst', 'Security analysis of the request'))

        # Performance analysis keywords
        if any(word in prompt.lower() for word in ['performance', 'optimize', 'memory', 'cpu', 'fast', 'efficient']):
            requirements.append(('performance-auditor', 'Performance analysis and optimization'))

        # Code generation/testing keywords
        if any(word in prompt.lower() for word in ['test', 'testing', 'unit test', 'coverage', 'validate']):
            requirements.append(('test-generator', 'Test generation and validation'))

        # Code precision/editing keywords
        if any(word in prompt.lower() for word in ['edit', 'modify', 'precise', 'surgical', 'refactor']):
            requirements.append(('precision-editor', 'Precise code modification'))

        # Default: include code analysis
        if not requirements:
            requirements.append(('code-analyzer', 'General code analysis'))

        return requirements

    def _create_agent_prompt(self, user_prompt: str, agent_type: str, description: str) -> str:
        """Create a specific prompt for an agent type"""
        return f"""
You are a {agent_type} agent working on the following user request:

USER REQUEST: {user_prompt}

YOUR SPECIFIC TASK: {description}

Please analyze this request and provide your specialized insights.
Focus on your domain expertise and provide actionable recommendations.
Output your analysis in a clear, structured format.
"""

    def _calculate_parallel_capacity(self, tasks: List[AgentTask]) -> int:
        """Calculate how many tasks can run in parallel based on resources"""
        resources_ok, msg = self.resource_monitor.check_system_resources()
        if not resources_ok:
            logger.warning(f"Limited resources: {msg}")
            return 1

        # Check current memory usage
        stats = self.resource_monitor.monitor_memory_usage()
        memory_usage = stats.get('process_memory_mb', 0)

        if memory_usage < 200:
            return min(3, len(tasks))  # Low memory usage - can run more
        elif memory_usage < 400:
            return min(2, len(tasks))  # Medium memory usage - limit parallelism
        else:
            return 1  # High memory usage - sequential execution

    def execute_plan(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Execute an orchestration plan with memory management"""
        logger.info(f"Executing orchestration plan with {len(plan.tasks)} tasks")

        # Initial resource check
        if plan.resource_check:
            resources_ok, msg = check_resources_before_agent_spawn()
            if not resources_ok:
                logger.error(f"Cannot start orchestration: {msg}")
                return {'success': False, 'error': f"Resource check failed: {msg}"}

        # Group tasks by priority and dependencies
        task_groups = self._group_tasks_by_priority(plan.tasks)

        results = {}
        for group_num, task_group in enumerate(task_groups):
            logger.info(f"Executing task group {group_num + 1} with {len(task_group)} tasks")

            # Execute tasks in parallel (with limits)
            group_results = self._execute_task_group(task_group, plan.max_parallel)
            # Handle ExecutionResult object properly
            if hasattr(group_results, 'result') and group_results.success:
                if isinstance(group_results.result, dict):
                    results.update(group_results.result)
                else:
                    results['task_result'] = group_results.result
            else:
                results['error'] = getattr(group_results, 'error', 'Unknown error')

            # Check resources between groups
            if group_num < len(task_groups) - 1:  # Not the last group
                resources_ok, msg = check_resources_before_agent_spawn()
                if not resources_ok:
                    logger.warning(f"Resources degraded after group {group_num + 1}: {msg}")
                    # Force cleanup before continuing
                    self.force_cleanup()

        return {
            'success': True,
            'results': results,
            'orchestration_id': self.orchestration_id
        }

    def _group_tasks_by_priority(self, tasks: List[AgentTask]) -> List[List[AgentTask]]:
        """Group tasks by priority for sequential execution"""
        # Sort by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)

        # Group by priority level
        groups = []
        current_priority = sorted_tasks[0].priority if sorted_tasks else 1
        current_group = []

        for task in sorted_tasks:
            if task.priority == current_priority:
                current_group.append(task)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [task]
                current_priority = task.priority

        if current_group:
            groups.append(current_group)

        return groups

    def _execute_task_group(self, tasks: List[AgentTask], max_parallel: int) -> Dict[str, Any]:
        """Execute a group of tasks with parallel limits"""
        # Always use circuit breaker for safety
        return self._execute_with_circuit_breaker(tasks, max_parallel)

    @with_circuit_breaker
    def _execute_with_circuit_breaker(self, tasks: List[AgentTask], max_parallel: int) -> Dict[str, Any]:
        """Execute tasks with circuit breaker protection"""
        return self._execute_direct(tasks, max_parallel)

    def _execute_direct(self, tasks: List[AgentTask], max_parallel: int) -> Dict[str, Any]:
        """Execute tasks directly with pooling"""
        results = {}

        # Use throttler for controlled execution
        for task in tasks:
            task_id = f"{task.agent_type}_{int(time.time())}"

            # Register task
            register_agent(task_id, task.agent_type)

            try:
                # Use pooled agent
                with self.agent_pool.get_agent(task.agent_type, task_id) as pooled_agent:
                    logger.info(f"Executing task {task_id} with {task.agent_type}")

                    # Execute the task (this would be the actual agent execution)
                    result = self._execute_single_task(task, pooled_agent)
                    results[task_id] = result

                    # Update agent status
                    update_agent_status(task_id, 'completed')

            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                update_agent_status(task_id, 'failed')
                results[task_id] = {'success': False, 'error': str(e)}

        return results

    def _execute_single_task(self, task: AgentTask, pooled_agent) -> Dict[str, Any]:
        """Execute a single agent task"""
        start_time = time.time()

        try:
            # CRITICAL: Check memory BEFORE execution
            mem_stats = self.resource_monitor.monitor_memory_usage()
            current_memory_mb = mem_stats['process_memory_mb']
            
            if current_memory_mb > 1500:  # Emergency threshold for macOS
                logger.critical(f"EMERGENCY: Memory usage {current_memory_mb}MB exceeds 1.5GB threshold")
                raise MemoryError(f"Process memory exceeded safe limit: {current_memory_mb}MB")
            
            # Simulate task execution (in real implementation, this would call the agent)
            logger.info(f"Task {task.agent_type}: {task.description} [Mem: {current_memory_mb:.0f}MB]")

            # In a real implementation, this would:
            # 1. Call the actual agent with the prompt
            # 2. Handle timeouts
            # 3. Capture output

            # For now, simulate with a brief pause
            time.sleep(0.1)

            # CRITICAL: Check memory AFTER execution
            mem_stats_after = self.resource_monitor.monitor_memory_usage()
            memory_delta = mem_stats_after['process_memory_mb'] - current_memory_mb
            
            if memory_delta > 100:  # If task increased memory by >100MB
                logger.warning(f"Task {task.agent_type} leaked {memory_delta:.0f}MB - forcing cleanup")
                self.force_cleanup()

            execution_time = time.time() - start_time

            return {
                'success': True,
                'agent_type': task.agent_type,
                'description': task.description,
                'execution_time': execution_time,
                'memory_usage': mem_stats_after['process_memory_mb'],
                'memory_delta': memory_delta
            }

        except MemoryError as e:
            # EMERGENCY: Force immediate cleanup
            logger.critical(f"MEMORY ERROR: {e}")
            self.force_cleanup()
            import gc
            gc.collect()
            
            execution_time = time.time() - start_time
            return {
                'success': False,
                'agent_type': task.agent_type,
                'error': f"MEMORY_LIMIT_EXCEEDED: {str(e)}",
                'execution_time': execution_time,
                'emergency_shutdown': True
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Task execution failed: {e}")

            return {
                'success': False,
                'agent_type': task.agent_type,
                'error': str(e),
                'execution_time': execution_time
            }

    def force_cleanup(self):
        """Force cleanup of resources"""
        logger.info("Forcing resource cleanup...")

        # Cleanup completed agents
        self.resource_monitor.cleanup_completed_agents()

        # Force garbage collection
        import gc
        collected = gc.collect()
        logger.info(f"Force garbage collection: {collected} objects collected")

        # Cleanup idle agents in pool
        self.agent_pool._cleanup_idle_agents()

    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        return {
            'orchestration_id': self.orchestration_id,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.task_results),
            'resource_stats': self.resource_monitor.monitor_memory_usage(),
            'circuit_breaker': self.circuit_breaker.get_state(),
            'agent_pool': self.agent_pool.get_pool_stats(),
            'throttler': self.throttler.get_status()
        }

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down memory-enhanced orchestrator...")

        # Force cleanup
        self.force_cleanup()

        # Shutdown components
        self.agent_pool.shutdown()
        self.throttler.shutdown()

        logger.info("Orchestrator shutdown complete")

# Main execution function
def orchestrate_with_memory_management(user_prompt: str) -> Dict[str, Any]:
    """Main function to orchestrate with memory management"""
    orchestrator = MemoryEnhancedOrchestrator()

    try:
        # Create orchestration plan
        plan = orchestrator.create_plan(user_prompt)

        # Execute plan
        result = orchestrator.execute_plan(plan)

        # Add status information
        result['status'] = orchestrator.get_orchestration_status()

        return result

    finally:
        # Cleanup
        orchestrator.shutdown()

if __name__ == "__main__":
    # Test the memory-enhanced orchestrator
    test_prompt = "Analyze the security and performance of the current codebase and generate tests"

    print("Memory-Enhanced Orchestrator Test")
    print("=" * 50)
    print(f"Test prompt: {test_prompt}")
    print()

    result = orchestrate_with_memory_management(test_prompt)

    print("Result:")
    print(json.dumps(result, indent=2))