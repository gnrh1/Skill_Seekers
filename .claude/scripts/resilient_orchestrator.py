#!/usr/bin/env python3
"""
Resilient Orchestrator - Integrated Agent Recovery and Monitoring System

Integrates timeout detection, circuit breakers, backup deployment, and progress monitoring
to create a resilient agent orchestration system that can handle failures gracefully.
This addresses the core architectural issues identified in the multi-model analysis.
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

# Import our resilience components
from agent_monitor import AgentMonitor, AgentStatus
from circuit_breaker import CircuitBreaker, AgentPriority
from backup_agent_deployer import BackupAgentDeployer, DeploymentStatus
from progress_monitor import ProgressMonitor, ProgressStatus, CheckpointType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [ResilientOrchestrator] %(message)s',
    handlers=[
        logging.FileHandler('../logs/resilient_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentTask:
    """Represents a task assigned to an agent"""
    def __init__(self, task_id: str, agent_name: str, task_description: str,
                 priority: str = "medium", critical_path: bool = False,
                 context: Optional[Dict] = None):
        self.task_id = task_id
        self.agent_name = agent_name
        self.task_description = task_description
        self.priority = priority
        self.critical_path = critical_path
        self.context = context or {}
        self.assigned_agent = agent_name
        self.backup_deployed = False
        self.completion_time: Optional[datetime] = None
        self.result_summary: Optional[str] = None
        self.failure_reason: Optional[str] = None

class ResilientOrchestrator:
    """Integrated resilient agent orchestration system"""

    def __init__(self, config_dir: str = ".claude/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        # Initialize all components
        self.agent_monitor = AgentMonitor()
        self.circuit_breaker = CircuitBreaker()
        self.backup_deployer = BackupAgentDeployer()
        self.progress_monitor = ProgressMonitor()

        # Orchestrator state
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_history: List[AgentTask] = []
        self.workflow_queue: List[AgentTask] = []
        self.orchestration_active = False

        # Statistics
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "backup_deployments": 0,
            "circuit_breaks": 0,
            "timeout_recoveries": 0
        }

        # Register callbacks
        self._register_callbacks()

        # Load configuration
        self.load_configuration()

    def load_configuration(self):
        """Load orchestrator configuration"""
        config_file = self.config_dir / "resilient_orchestrator_config.json"

        default_config = {
            "orchestration": {
                "max_concurrent_tasks": 5,
                "task_timeout_minutes": 30,
                "backup_deployment_threshold": 0.7,  # Deploy backup after 70% of time elapsed
                "auto_retry_enabled": True,
                "max_retry_attempts": 2
            },
            "agent_mappings": {
                "precision-editor": {
                    "backup_priority": 1,
                    "critical_path": True,
                    "expected_duration_minutes": 10
                },
                "security-analyst": {
                    "backup_priority": 1,
                    "critical_path": True,
                    "expected_duration_minutes": 15
                },
                "test-generator": {
                    "backup_priority": 2,
                    "critical_path": False,
                    "expected_duration_minutes": 12
                },
                "performance-auditor": {
                    "backup_priority": 2,
                    "critical_path": False,
                    "expected_duration_minutes": 8
                }
            },
            "resilience_strategies": {
                "timeout_handling": "deploy_backup",
                "stall_handling": "stimulate_then_backup",
                "circuit_break_handling": "skip_with_manual_intervention",
                "critical_task_handling": "retry_with_different_agent"
            }
        }

        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to load orchestrator configuration: {e}")
            self.config = default_config

    def _register_callbacks(self):
        """Register callbacks between components"""
        # Progress monitor callbacks
        self.progress_monitor.register_callback("stall_detected", self._handle_stall_detected)
        self.progress_monitor.register_callback("timeout_detected", self._handle_timeout_detected)
        self.progress_monitor.register_callback("error_detected", self._handle_error_detected)
        self.progress_monitor.register_callback("agent_completed", self._handle_agent_completed)

    def submit_task(self, agent_name: str, task_description: str,
                   priority: str = "medium", critical_path: bool = False,
                   context: Optional[Dict] = None) -> str:
        """Submit a task for resilient execution"""
        task_id = f"{agent_name}_{int(time.time())}"

        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            task_description=task_description,
            priority=priority,
            critical_path=critical_path,
            context=context
        )

        # Check if agent can execute
        can_execute, reason = self.circuit_breaker.can_execute_agent(agent_name)

        if not can_execute:
            logger.warning(f"Agent {agent_name} cannot execute: {reason}")

            # Try to find backup
            backup_agent = self.circuit_breaker.get_backup_agent(agent_name)
            if backup_agent:
                logger.info(f"Using backup agent {backup_agent} for task {task_id}")
                task.assigned_agent = backup_agent
            else:
                # Check if we can skip
                should_skip, skip_reason, _ = self.circuit_breaker.should_skip_agent(agent_name)
                if should_skip:
                    logger.error(f"Task {task_id} skipped: {skip_reason}")
                    task.failure_reason = skip_reason
                    self.task_history.append(task)
                    return task_id

        # Add to queue
        self.workflow_queue.append(task)
        self.stats["total_tasks"] += 1

        logger.info(f"Submitted task {task_id} for agent {task.assigned_agent}")

        # Start orchestration if not active
        if not self.orchestration_active:
            self._start_orchestration()

        return task_id

    def _start_orchestration(self):
        """Start the orchestration loop"""
        if self.orchestration_active:
            return

        self.orchestration_active = True
        orchestration_thread = threading.Thread(target=self._orchestration_loop, daemon=True)
        orchestration_thread.start()
        logger.info("Started resilient orchestration loop")

    def _orchestration_loop(self):
        """Main orchestration loop"""
        max_concurrent = self.config.get("orchestration", {}).get("max_concurrent_tasks", 5)

        while self.orchestration_active or self.workflow_queue:
            try:
                # Process queue
                while (self.workflow_queue and
                       len(self.active_tasks) < max_concurrent):
                    task = self.workflow_queue.pop(0)
                    self._execute_task(task)

                # Check for recovery opportunities
                self._check_recovery_opportunities()

                # Clean up completed tasks
                self._cleanup_completed_tasks()

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                time.sleep(10)

    def _execute_task(self, task: AgentTask):
        """Execute a task with full resilience monitoring"""
        logger.info(f"Executing task {task.task_id} with agent {task.assigned_agent}")

        # Add to active tasks
        self.active_tasks[task.task_id] = task

        # Start all monitoring systems
        agent_monitor_id = self.agent_monitor.register_agent(
            agent_name=task.assigned_agent,
            task_id=task.task_id,
            timeout_threshold=self.config.get("orchestration", {}).get("task_timeout_minutes", 30) * 60
        )

        progress_id = self.progress_monitor.start_monitoring(
            agent_name=task.assigned_agent,
            task_id=task.task_id,
            estimated_duration_minutes=self.config.get("agent_mappings", {}).get(task.agent_name, {}).get("expected_duration_minutes", 10)
        )

        # Store monitoring IDs
        task.context.update({
            "agent_monitor_id": agent_monitor_id,
            "progress_id": progress_id
        })

        # In a real implementation, this would trigger the actual agent execution
        # For now, we'll simulate it with progress updates
        self._simulate_task_execution(task)

    def _simulate_task_execution(self, task: AgentTask):
        """Simulate task execution with progress updates"""
        def simulation_worker():
            try:
                progress_id = task.context["progress_id"]
                agent_monitor_id = task.context["agent_monitor_id"]

                # Simulate work with checkpoints
                self.progress_monitor.record_tool_usage(
                    progress_id, "read_file",
                    f"Started {task.task_description}"
                )
                self.progress_monitor.update_progress(progress_id, 20.0, "Analysis phase")

                # Simulate some work
                time.sleep(2)

                self.progress_monitor.record_tool_usage(
                    progress_id, "grep_search",
                    "Found relevant code sections"
                )
                self.progress_monitor.update_progress(progress_id, 50.0, "Processing phase")

                # Simulate more work
                time.sleep(3)

                self.progress_monitor.record_tool_usage(
                    progress_id, "edit_file",
                    "Applied changes successfully"
                )
                self.progress_monitor.update_progress(progress_id, 80.0, "Implementation phase")

                # Final validation
                time.sleep(2)

                self.progress_monitor.record_tool_usage(
                    progress_id, "bash",
                    "Validation completed successfully"
                )
                self.progress_monitor.update_progress(progress_id, 100.0, "Task completed")

                # Mark as completed
                task.completion_time = datetime.now()
                task.result_summary = f"Task completed successfully by {task.assigned_agent}"

                # Update monitoring systems
                self.agent_monitor.mark_agent_completed(agent_monitor_id, "completed")
                self.progress_monitor.complete_monitoring(progress_id, True, task.result_summary)

                # Record success
                self.circuit_breaker.record_agent_success(task.assigned_agent)
                self.stats["successful_tasks"] += 1

                logger.info(f"Task {task.task_id} completed successfully")

            except Exception as e:
                # Handle simulation errors
                task.failure_reason = str(e)
                self._handle_task_failure(task)

        # Run simulation in background thread
        simulation_thread = threading.Thread(target=simulation_worker, daemon=True)
        simulation_thread.start()

    def _handle_stall_detected(self, progress_id: str, data: Any):
        """Handle stalled agent detection"""
        logger.warning(f"Stall detected for progress {progress_id}")

        # Find corresponding task
        task = self._find_task_by_progress_id(progress_id)
        if not task:
            return

        # Check resilience strategy
        strategy = self.config.get("resilience_strategies", {}).get("stall_handling", "stimulate_then_backup")

        if strategy == "deploy_backup":
            self._deploy_backup_for_task(task)
        elif strategy == "stimulate_then_backup":
            # Try to stimulate first (in real implementation)
            logger.info(f"Attempting to stimulate stalled agent {task.assigned_agent}")
            # Deploy backup if stimulation doesn't work
            threading.Timer(30, lambda: self._deploy_backup_for_task(task)).start()

    def _handle_timeout_detected(self, progress_id: str, data: Any):
        """Handle timeout detection"""
        logger.error(f"Timeout detected for progress {progress_id}")

        task = self._find_task_by_progress_id(progress_id)
        if not task:
            return

        self.stats["timeout_recoveries"] += 1
        strategy = self.config.get("resilience_strategies", {}).get("timeout_handling", "deploy_backup")

        if strategy == "deploy_backup":
            self._deploy_backup_for_task(task)

    def _handle_error_detected(self, progress_id: str, data: Any):
        """Handle error detection"""
        logger.warning(f"Error detected for progress {progress_id}")

        task = self._find_task_by_progress_id(progress_id)
        if not task:
            return

        # Check if we should deploy backup
        if task.critical_path and not task.backup_deployed:
            self._deploy_backup_for_task(task)

    def _handle_agent_completed(self, progress_id: str, data: Any):
        """Handle agent completion"""
        logger.info(f"Agent completed for progress {progress_id}")

        task = self._find_task_by_progress_id(progress_id)
        if task:
            logger.info(f"Task {task.task_id} completed successfully")

    def _deploy_backup_for_task(self, task: AgentTask):
        """Deploy backup agent for a task"""
        if task.backup_deployed:
            logger.warning(f"Backup already deployed for task {task.task_id}")
            return

        logger.info(f"Deploying backup agent for task {task.task_id}")

        # Deploy backup
        backup_task_id = self.backup_deployer.deploy_backup_agent(
            failed_agent=task.agent_name,
            task_description=task.task_description,
            task_criticality="high" if task.critical_path else "medium",
            context=task.context
        )

        if backup_task_id:
            task.backup_deployed = True
            self.stats["backup_deployments"] += 1

            # In real implementation, would monitor backup deployment
            # For now, we'll just complete the backup after a delay
            threading.Timer(10, lambda: self._complete_backup_deployment(backup_task_id, task)).start()

    def _complete_backup_deployment(self, backup_task_id: str, original_task: AgentTask):
        """Complete backup deployment"""
        success = True  # Simulate success
        result = f"Backup agent completed task for {original_task.agent_name}"

        self.backup_deployer.complete_deployment(
            backup_task_id, success, result_summary=result
        )

        if success:
            original_task.completion_time = datetime.now()
            original_task.result_summary = result
            original_task.assigned_agent += " (backup)"
            self.stats["successful_tasks"] += 1
        else:
            self._handle_task_failure(original_task)

    def _handle_task_failure(self, task: AgentTask):
        """Handle task failure"""
        logger.error(f"Task {task.task_id} failed: {task.failure_reason}")

        # Record failure in circuit breaker
        self.circuit_breaker.record_agent_failure(task.agent_name, task.failure_reason or "Unknown error")

        # Update statistics
        self.stats["failed_tasks"] += 1

        # Move to history
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        self.task_history.append(task)

    def _find_task_by_progress_id(self, progress_id: str) -> Optional[AgentTask]:
        """Find task by progress ID"""
        for task in self.active_tasks.values():
            if task.context.get("progress_id") == progress_id:
                return task
        return None

    def _check_recovery_opportunities(self):
        """Check for opportunities to recover failed tasks"""
        # This would implement intelligent retry logic
        pass

    def _cleanup_completed_tasks(self):
        """Clean up completed tasks"""
        completed_tasks = [
            task_id for task_id, task in self.active_tasks.items()
            if task.completion_time is not None or task.failure_reason is not None
        ]

        for task_id in completed_tasks:
            task = self.active_tasks[task_id]
            self.task_history.append(task)
            del self.active_tasks[task_id]

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        return {
            "active_tasks": {
                task_id: {
                    "agent": task.assigned_agent,
                    "description": task.task_description,
                    "priority": task.priority,
                    "critical_path": task.critical_path,
                    "backup_deployed": task.backup_deployed,
                    "start_time": task.context.get("start_time", "Unknown")
                }
                for task_id, task in self.active_tasks.items()
            },
            "queue_length": len(self.workflow_queue),
            "statistics": self.stats.copy(),
            "system_health": {
                "agent_monitor": self.agent_monitor.get_agent_summary(),
                "circuit_breaker": self.circuit_breaker.get_system_health(),
                "backup_deployer": self.backup_deployer.get_deployment_statistics(),
                "progress_monitor": self.progress_monitor.get_all_progress_summaries()
            },
            "orchestration_active": self.orchestration_active
        }

    def stop_orchestration(self):
        """Stop orchestration gracefully"""
        logger.info("Stopping resilient orchestration")
        self.orchestration_active = False

        # Stop all monitoring components
        self.progress_monitor.stop_monitoring()

def main():
    """Main execution for testing resilient orchestrator"""
    orchestrator = ResilientOrchestrator()

    print("Resilient Orchestrator initialized")
    print("All resilience components integrated:")
    print("- Agent Monitor (timeout detection)")
    print("- Circuit Breaker (failure handling)")
    print("- Backup Deployer (redundancy)")
    print("- Progress Monitor (tracking)")

    # Submit some test tasks
    tasks = [
        ("precision-editor", "Resolve merge conflicts in CLAUDE.md", "high", True),
        ("security-analyst", "Scan for CVE vulnerabilities", "high", True),
        ("test-generator", "Create compatibility tests", "medium", False),
        ("performance-auditor", "Analyze performance impact", "medium", False)
    ]

    submitted_tasks = []
    for agent, description, priority, critical in tasks:
        task_id = orchestrator.submit_task(agent, description, priority, critical)
        submitted_tasks.append(task_id)
        print(f"Submitted task: {task_id}")

    # Monitor for a while
    print("\nMonitoring task execution...")
    for i in range(20):
        status = orchestrator.get_workflow_status()
        print(f"\n=== Status Update {i+1}/20 ===")
        print(f"Active tasks: {len(status['active_tasks'])}")
        print(f"Queue length: {status['queue_length']}")
        print(f"Statistics: {status['statistics']}")

        if status['queue_length'] == 0 and len(status['active_tasks']) == 0:
            print("All tasks completed!")
            break

        time.sleep(3)

    # Final status
    final_status = orchestrator.get_workflow_status()
    print(f"\n=== Final Status ===")
    print(f"Total tasks: {final_status['statistics']['total_tasks']}")
    print(f"Successful: {final_status['statistics']['successful_tasks']}")
    print(f"Failed: {final_status['statistics']['failed_tasks']}")
    print(f"Backup deployments: {final_status['statistics']['backup_deployments']}")

    orchestrator.stop_orchestration()
    print("\nResilient orchestration test completed")

if __name__ == "__main__":
    main()