#!/usr/bin/env python3
"""
Progress Monitor - Comprehensive Agent Progress Tracking System

Provides real-time monitoring of agent progress with intermediate checkpoints,
progress indicators, and comprehensive status reporting. This addresses the need
for better visibility into agent execution and early detection of stalled agents.
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.claude/logs/progress_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProgressStatus(Enum):
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    STALLED = "stalled"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CheckpointType(Enum):
    START = "start"
    MILESTONE = "milestone"
    TOOL_USAGE = "tool_usage"
    VALIDATION = "validation"
    COMPLETION = "completion"
    ERROR = "error"

@dataclass
class Checkpoint:
    checkpoint_id: str
    checkpoint_type: CheckpointType
    timestamp: datetime
    description: str
    tool_used: Optional[str] = None
    tool_output: Optional[str] = None
    progress_percentage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentProgress:
    agent_name: str
    task_id: str
    start_time: datetime
    status: ProgressStatus
    checkpoints: List[Checkpoint]
    current_progress: float = 0.0
    last_activity: datetime = None
    estimated_completion: Optional[datetime] = None
    tools_used: List[str] = None
    error_count: int = 0
    warning_count: int = 0

    def __post_init__(self):
        if self.checkpoints is None:
            self.checkpoints = []
        if self.tools_used is None:
            self.tools_used = []
        if self.last_activity is None:
            self.last_activity = self.start_time

class ProgressMonitor:
    """Comprehensive progress monitoring system for agents"""

    def __init__(self, config_dir: str = ".claude/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.active_progress: Dict[str, AgentProgress] = {}
        self.progress_history: List[AgentProgress] = []
        self.checkpoints: Dict[str, List[Checkpoint]] = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.callbacks: Dict[str, List[Callable]] = {
            "stall_detected": [],
            "timeout_detected": [],
            "milestone_reached": [],
            "agent_completed": [],
            "error_detected": []
        }
        self.load_configuration()

    def load_configuration(self):
        """Load monitoring configuration"""
        config_file = self.config_dir / "progress_monitor_config.json"

        default_config = {
            "monitoring": {
                "enabled": True,
                "check_interval_seconds": 30,
                "stall_threshold_seconds": 120,
                "timeout_threshold_seconds": 600,
                "progress_update_frequency": 10
            },
            "agent_expectations": {
                "precision-editor": {
                    "expected_tools": ["read_file", "grep_search", "edit_file", "bash"],
                    "min_checkpoints": 4,
                    "estimated_duration_minutes": 10,
                    "critical_checkpoints": ["conflict_analysis", "resolution_start", "validation"]
                },
                "security-analyst": {
                    "expected_tools": ["read_file", "grep_search", "bash"],
                    "min_checkpoints": 3,
                    "estimated_duration_minutes": 15,
                    "critical_checkpoints": ["vulnerability_scan", "fix_application", "validation"]
                },
                "test-generator": {
                    "expected_tools": ["read_file", "write_file", "bash"],
                    "min_checkpoints": 5,
                    "estimated_duration_minutes": 12,
                    "critical_checkpoints": ["test_analysis", "test_creation", "test_execution"]
                },
                "performance-auditor": {
                    "expected_tools": ["read_file", "bash", "grep_search"],
                    "min_checkpoints": 4,
                    "estimated_duration_minutes": 8,
                    "critical_checkpoints": ["analysis_start", "measurements", "recommendations"]
                }
            },
            "alerts": {
                "stall_alert": True,
                "timeout_alert": True,
                "progress_alert": True,
                "error_alert": True,
                "completion_alert": True
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
            logger.error(f"Failed to load configuration: {e}")
            self.config = default_config

    def start_monitoring(self, agent_name: str, task_id: str,
                        estimated_duration_minutes: Optional[int] = None) -> str:
        """Start monitoring an agent"""
        progress_id = f"{agent_name}_{task_id}_{int(time.time())}"

        # Get agent expectations
        agent_config = self.config.get("agent_expectations", {}).get(agent_name, {})
        if estimated_duration_minutes is None:
            estimated_duration_minutes = agent_config.get("estimated_duration_minutes", 10)

        progress = AgentProgress(
            agent_name=agent_name,
            task_id=task_id,
            start_time=datetime.now(),
            status=ProgressStatus.INITIALIZING,
            checkpoints=[],
            estimated_completion=datetime.now() + timedelta(minutes=estimated_duration_minutes)
        )

        self.active_progress[progress_id] = progress
        self.checkpoints[progress_id] = []

        # Add start checkpoint
        self.add_checkpoint(
            progress_id=progress_id,
            checkpoint_type=CheckpointType.START,
            description=f"Started monitoring {agent_name}",
            progress_percentage=0.0
        )

        logger.info(f"Started monitoring {agent_name} with progress ID: {progress_id}")

        # Start monitoring thread if not already running
        if not self.monitoring_active:
            self._start_monitoring_thread()

        return progress_id

    def add_checkpoint(self, progress_id: str, checkpoint_type: CheckpointType,
                       description: str, tool_used: Optional[str] = None,
                       tool_output: Optional[str] = None,
                       progress_percentage: Optional[float] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """Add a progress checkpoint"""
        if progress_id not in self.active_progress:
            logger.warning(f"Progress ID {progress_id} not found")
            return

        checkpoint = Checkpoint(
            checkpoint_id=f"{progress_id}_{len(self.checkpoints[progress_id])}",
            checkpoint_type=checkpoint_type,
            timestamp=datetime.now(),
            description=description,
            tool_used=tool_used,
            tool_output=tool_output,
            progress_percentage=progress_percentage,
            metadata=metadata
        )

        # Update progress
        progress = self.active_progress[progress_id]
        progress.checkpoints.append(checkpoint)
        progress.last_activity = datetime.now()

        if tool_used:
            progress.tools_used.append(tool_used)

        if progress_percentage is not None:
            progress.current_progress = max(progress.current_progress, progress_percentage)

        # Update status based on checkpoint type
        if checkpoint_type == CheckpointType.START:
            progress.status = ProgressStatus.IN_PROGRESS
        elif checkpoint_type == CheckpointType.MILESTONE:
            progress.status = ProgressStatus.IN_PROGRESS
        elif checkpoint_type == CheckpointType.COMPLETION:
            progress.status = ProgressStatus.COMPLETED
        elif checkpoint_type == CheckpointType.ERROR:
            progress.status = ProgressStatus.FAILED
            progress.error_count += 1

        # Add to checkpoints list
        self.checkpoints[progress_id].append(checkpoint)

        # Trigger callbacks
        self._trigger_callbacks(checkpoint_type, progress_id, checkpoint)

        logger.info(f"Added checkpoint for {progress_id}: {description}")

    def record_tool_usage(self, progress_id: str, tool_name: str,
                         tool_output: Optional[str] = None,
                         description: Optional[str] = None):
        """Record tool usage as a checkpoint"""
        if description is None:
            description = f"Used {tool_name}"

        self.add_checkpoint(
            progress_id=progress_id,
            checkpoint_type=CheckpointType.TOOL_USAGE,
            description=description,
            tool_used=tool_name,
            tool_output=tool_output
        )

    def update_progress(self, progress_id: str, progress_percentage: float,
                       description: Optional[str] = None):
        """Update progress percentage"""
        if description is None:
            description = f"Progress updated to {progress_percentage}%"

        self.add_checkpoint(
            progress_id=progress_id,
            checkpoint_type=CheckpointType.MILESTONE,
            description=description,
            progress_percentage=progress_percentage
        )

    def complete_monitoring(self, progress_id: str, success: bool = True,
                           final_description: Optional[str] = None):
        """Complete monitoring for an agent"""
        if progress_id not in self.active_progress:
            logger.warning(f"Progress ID {progress_id} not found for completion")
            return

        progress = self.active_progress[progress_id]

        if final_description is None:
            final_description = "Task completed successfully" if success else "Task failed"

        # Add completion checkpoint
        self.add_checkpoint(
            progress_id=progress_id,
            checkpoint_type=CheckpointType.COMPLETION if success else CheckpointType.ERROR,
            description=final_description,
            progress_percentage=100.0 if success else progress.current_progress
        )

        # Move to history
        self.progress_history.append(progress)
        del self.active_progress[progress_id]

        logger.info(f"Completed monitoring for {progress_id}: {final_description}")

        # Save history
        self._save_progress_history()

    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Started background monitoring thread")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        check_interval = self.config.get("monitoring", {}).get("check_interval_seconds", 30)

        while self.monitoring_active:
            try:
                self._check_all_progress()
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)

    def _check_all_progress(self):
        """Check all active progress for issues"""
        stall_threshold = self.config.get("monitoring", {}).get("stall_threshold_seconds", 120)
        timeout_threshold = self.config.get("monitoring", {}).get("timeout_threshold_seconds", 600)

        current_time = datetime.now()

        for progress_id, progress in list(self.active_progress.items()):
            time_since_activity = (current_time - progress.last_activity).total_seconds()
            time_since_start = (current_time - progress.start_time).total_seconds()

            # Check for timeout
            if time_since_start > timeout_threshold:
                self._handle_timeout(progress_id)
                continue

            # Check for stalling
            if time_since_activity > stall_threshold:
                self._handle_stall(progress_id)

            # Check if critical checkpoints are missed
            self._check_critical_checkpoints(progress_id)

    def _handle_stall(self, progress_id: str):
        """Handle stalled agent"""
        progress = self.active_progress[progress_id]
        progress.status = ProgressStatus.STALLED

        # Add stall checkpoint
        self.add_checkpoint(
            progress_id=progress_id,
            checkpoint_type=CheckpointType.ERROR,
            description=f"Agent stalled - no activity for {self.config.get('monitoring', {}).get('stall_threshold_seconds', 120)} seconds"
        )

        logger.warning(f"Agent {progress_id} detected as stalled")
        self._trigger_callbacks("stall_detected", progress_id, progress)

    def _handle_timeout(self, progress_id: str):
        """Handle timed out agent"""
        progress = self.active_progress[progress_id]
        progress.status = ProgressStatus.FAILED

        # Add timeout checkpoint
        self.add_checkpoint(
            progress_id=progress_id,
            checkpoint_type=CheckpointType.ERROR,
            description=f"Agent timed out after {self.config.get('monitoring', {}).get('timeout_threshold_seconds', 600)} seconds"
        )

        logger.error(f"Agent {progress_id} timed out")
        self._trigger_callbacks("timeout_detected", progress_id, progress)

    def _check_critical_checkpoints(self, progress_id: str):
        """Check if critical checkpoints are missed"""
        progress = self.active_progress[progress_id]
        agent_config = self.config.get("agent_expectations", {}).get(progress.agent_name, {})
        critical_checkpoints = agent_config.get("critical_checkpoints", [])

        # This is a simplified check - in practice, you'd track specific expected checkpoints
        if len(progress.checkpoints) < agent_config.get("min_checkpoints", 3):
            time_elapsed = (datetime.now() - progress.start_time).total_seconds()
            expected_time = agent_config.get("estimated_duration_minutes", 10) * 60

            if time_elapsed > expected_time * 0.7 and len(progress.checkpoints) < expected_time / 60:
                logger.warning(f"Agent {progress_id} may be missing critical checkpoints")

    def _trigger_callbacks(self, event_type: str, progress_id: str, data: Any):
        """Trigger registered callbacks"""
        # Map checkpoint types to callback events
        event_mapping = {
            CheckpointType.MILESTONE: "milestone_reached",
            CheckpointType.ERROR: "error_detected",
            CheckpointType.COMPLETION: "agent_completed"
        }

        if isinstance(event_type, CheckpointType):
            callback_type = event_mapping.get(event_type)
        else:
            callback_type = event_type

        if callback_type in self.callbacks:
            for callback in self.callbacks[callback_type]:
                try:
                    callback(progress_id, data)
                except Exception as e:
                    logger.error(f"Error in callback {callback_type}: {e}")

    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for events"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

    def get_progress_summary(self, progress_id: str) -> Optional[Dict[str, Any]]:
        """Get progress summary for an agent"""
        if progress_id not in self.active_progress:
            return None

        progress = self.active_progress[progress_id]

        # Calculate progress rate
        if progress.checkpoints:
            time_elapsed = (datetime.now() - progress.start_time).total_seconds()
            checkpoint_rate = len(progress.checkpoints) / (time_elapsed / 60)  # checkpoints per minute
        else:
            checkpoint_rate = 0

        return {
            "progress_id": progress_id,
            "agent_name": progress.agent_name,
            "task_id": progress.task_id,
            "status": progress.status.value,
            "current_progress": progress.current_progress,
            "start_time": progress.start_time.isoformat(),
            "last_activity": progress.last_activity.isoformat(),
            "estimated_completion": progress.estimated_completion.isoformat() if progress.estimated_completion else None,
            "checkpoints_count": len(progress.checkpoints),
            "tools_used": progress.tools_used,
            "error_count": progress.error_count,
            "warning_count": progress.warning_count,
            "checkpoint_rate": checkpoint_rate,
            "time_elapsed_minutes": (datetime.now() - progress.start_time).total_seconds() / 60
        }

    def get_all_progress_summaries(self) -> Dict[str, Any]:
        """Get summaries for all active agents"""
        summaries = {}
        for progress_id in self.active_progress:
            summaries[progress_id] = self.get_progress_summary(progress_id)

        return {
            "active_agents": summaries,
            "total_active": len(self.active_progress),
            "monitoring_active": self.monitoring_active,
            "system_health": self._get_system_health()
        }

    def _get_system_health(self) -> str:
        """Get overall system health"""
        if not self.active_progress:
            return "no_active_agents"

        stalled_count = len([p for p in self.active_progress.values() if p.status == ProgressStatus.STALLED])
        failed_count = len([p for p in self.active_progress.values() if p.status == ProgressStatus.FAILED])
        total_count = len(self.active_progress)

        if failed_count > 0:
            return "critical"
        elif stalled_count > 0:
            return "degraded"
        else:
            return "healthy"

    def _save_progress_history(self):
        """Save progress history to file"""
        history_file = Path(".claude/logs/progress_history.json")

        try:
            history_data = []
            for progress in self.progress_history[-100:]:  # Keep last 100 entries
                history_data.append({
                    "agent_name": progress.agent_name,
                    "task_id": progress.task_id,
                    "start_time": progress.start_time.isoformat(),
                    "status": progress.status.value,
                    "final_progress": progress.current_progress,
                    "checkpoints_count": len(progress.checkpoints),
                    "tools_used": progress.tools_used,
                    "error_count": progress.error_count
                })

            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress history: {e}")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped background monitoring")

def main():
    """Main execution for testing progress monitor"""
    monitor = ProgressMonitor()

    print("Progress Monitor initialized")
    print(f"Configuration loaded with {len(monitor.config.get('agent_expectations', {}))} agent expectations")

    # Example usage
    progress_id = monitor.start_monitoring("test-agent", "example-task")

    # Simulate progress
    monitor.record_tool_usage(progress_id, "read_file", "File loaded successfully")
    monitor.update_progress(progress_id, 25.0, "Analysis phase completed")
    monitor.record_tool_usage(progress_id, "edit_file", "Changes applied")
    monitor.update_progress(progress_id, 75.0, "Editing phase completed")
    monitor.record_tool_usage(progress_id, "bash", "Validation passed")

    # Get summary
    summary = monitor.get_progress_summary(progress_id)
    print(f"\nProgress Summary:")
    print(f"Status: {summary['status']}")
    print(f"Progress: {summary['current_progress']}%")
    print(f"Checkpoints: {summary['checkpoints_count']}")
    print(f"Tools Used: {summary['tools_used']}")

    # Complete monitoring
    monitor.complete_monitoring(progress_id, True, "Task completed successfully")

    # Get all summaries
    all_summaries = monitor.get_all_progress_summaries()
    print(f"\nSystem Health: {all_summaries['system_health']}")
    print(f"Active Agents: {all_summaries['total_active']}")

    monitor.stop_monitoring()

if __name__ == "__main__":
    main()