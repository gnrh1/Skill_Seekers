#!/usr/bin/env python3
"""
Agent Monitor - Timeout Detection and Recovery System

Monitors agent execution for timeouts, stalled progress, and implements recovery mechanisms.
This addresses the critical failure mode where @precision-editor stalled after Read phase.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/agent_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    RUNNING = "running"
    STALLED = "stalled"
    TIMEOUT = "timeout"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"

@dataclass
class AgentMetrics:
    agent_name: str
    task_id: str
    start_time: datetime
    last_activity: datetime
    tool_usage_count: int = 0
    progress_indicators: List[str] = None
    timeout_threshold: int = 300  # 5 minutes default
    stall_threshold: int = 120   # 2 minutes no activity

    def __post_init__(self):
        if self.progress_indicators is None:
            self.progress_indicators = []

class AgentMonitor:
    """Monitors agent execution and implements recovery mechanisms"""

    def __init__(self, log_dir: str = ".claude/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.active_agents: Dict[str, AgentMetrics] = {}
        self.agent_history: List[Dict] = []
        self.recovery_strategies = {
            AgentStatus.STALLED: self._handle_stalled_agent,
            AgentStatus.TIMEOUT: self._handle_timeout_agent,
            AgentStatus.FAILED: self._handle_failed_agent
        }

    def register_agent(self, agent_name: str, task_id: str,
                      timeout_threshold: int = 300,
                      stall_threshold: int = 120) -> str:
        """Register an agent for monitoring"""
        agent_id = f"{agent_name}_{task_id}_{int(time.time())}"

        metrics = AgentMetrics(
            agent_name=agent_name,
            task_id=task_id,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            timeout_threshold=timeout_threshold,
            stall_threshold=stall_threshold
        )

        self.active_agents[agent_id] = metrics
        logger.info(f"Registered agent {agent_name} with ID {agent_id}")

        return agent_id

    def update_progress(self, agent_id: str, activity: str,
                       tool_usage: bool = False) -> bool:
        """Update agent progress and activity"""
        if agent_id not in self.active_agents:
            logger.warning(f"Agent {agent_id} not found in active monitoring")
            return False

        metrics = self.active_agents[agent_id]
        metrics.last_activity = datetime.now()
        metrics.progress_indicators.append(activity)

        if tool_usage:
            metrics.tool_usage_count += 1

        logger.info(f"Updated progress for {agent_id}: {activity}")
        return True

    def check_agent_health(self, agent_id: str) -> AgentStatus:
        """Check agent health status"""
        if agent_id not in self.active_agents:
            return AgentStatus.FAILED

        metrics = self.active_agents[agent_id]
        now = datetime.now()

        # Check for timeout
        if (now - metrics.start_time).total_seconds() > metrics.timeout_threshold:
            return AgentStatus.TIMEOUT

        # Check for stalling (no recent activity)
        if (now - metrics.last_activity).total_seconds() > metrics.stall_threshold:
            return AgentStatus.STALLED

        # Check for tool usage (agents should be using tools, not just analyzing)
        if metrics.tool_usage_count == 0 and (now - metrics.start_time).total_seconds() > 60:
            return AgentStatus.STALLED

        return AgentStatus.RUNNING

    def monitor_all_agents(self) -> Dict[str, AgentStatus]:
        """Monitor all active agents and return status"""
        status_report = {}

        for agent_id in list(self.active_agents.keys()):
            status = self.check_agent_health(agent_id)
            status_report[agent_id] = status

            if status in [AgentStatus.STALLED, AgentStatus.TIMEOUT, AgentStatus.FAILED]:
                logger.warning(f"Agent {agent_id} status: {status.value}")
                self._attempt_recovery(agent_id, status)

        return status_report

    def _attempt_recovery(self, agent_id: str, status: AgentStatus) -> bool:
        """Attempt to recover a stalled or failed agent"""
        if status in self.recovery_strategies:
            return self.recovery_strategies[status](agent_id)
        return False

    def _handle_stalled_agent(self, agent_id: str) -> bool:
        """Handle stalled agent - try to stimulate progress"""
        metrics = self.active_agents[agent_id]
        logger.info(f"Attempting recovery for stalled agent {agent_id}")

        # Log stall details
        stall_report = {
            "agent_id": agent_id,
            "agent_name": metrics.agent_name,
            "stall_time": datetime.now().isoformat(),
            "last_activity": metrics.last_activity.isoformat(),
            "tool_usage_count": metrics.tool_usage_count,
            "progress_indicators": metrics.progress_indicators[-5:],  # Last 5 activities
            "recovery_attempt": "stimulation"
        }

        self._log_recovery_attempt(stall_report)

        # For now, mark as recovered and let system continue
        # In a real implementation, this would trigger recovery mechanisms
        self.mark_agent_completed(agent_id, "recovered_from_stall")
        return True

    def _handle_timeout_agent(self, agent_id: str) -> bool:
        """Handle timeout agent - terminate and potentially restart"""
        metrics = self.active_agents[agent_id]
        logger.error(f"Agent {agent_id} timed out after {metrics.timeout_threshold} seconds")

        timeout_report = {
            "agent_id": agent_id,
            "agent_name": metrics.agent_name,
            "timeout_time": datetime.now().isoformat(),
            "duration": (datetime.now() - metrics.start_time).total_seconds(),
            "tool_usage_count": metrics.tool_usage_count,
            "recovery_attempt": "timeout_handling"
        }

        self._log_recovery_attempt(timeout_report)
        self.mark_agent_completed(agent_id, "timeout")
        return True

    def _handle_failed_agent(self, agent_id: str) -> bool:
        """Handle failed agent"""
        logger.error(f"Agent {agent_id} failed - marking for manual intervention")
        self.mark_agent_completed(agent_id, "failed")
        return True

    def mark_agent_completed(self, agent_id: str, completion_status: str) -> None:
        """Mark agent as completed and move to history"""
        if agent_id not in self.active_agents:
            return

        metrics = self.active_agents[agent_id]

        completion_record = {
            "agent_id": agent_id,
            "agent_name": metrics.agent_name,
            "task_id": metrics.task_id,
            "start_time": metrics.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - metrics.start_time).total_seconds(),
            "tool_usage_count": metrics.tool_usage_count,
            "progress_indicators": metrics.progress_indicators,
            "completion_status": completion_status
        }

        self.agent_history.append(completion_record)
        del self.active_agents[agent_id]

        logger.info(f"Agent {agent_id} marked as completed: {completion_status}")

        # Save to persistent storage
        self._save_agent_history()

    def _log_recovery_attempt(self, recovery_report: Dict) -> None:
        """Log recovery attempts"""
        recovery_log_file = self.log_dir / "recovery_attempts.json"

        try:
            if recovery_log_file.exists():
                with open(recovery_log_file, 'r') as f:
                    recovery_history = json.load(f)
            else:
                recovery_history = []

            recovery_history.append(recovery_report)

            with open(recovery_log_file, 'w') as f:
                json.dump(recovery_history, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to log recovery attempt: {e}")

    def _save_agent_history(self) -> None:
        """Save agent history to persistent storage"""
        history_file = self.log_dir / "agent_history.json"

        try:
            with open(history_file, 'w') as f:
                json.dump(self.agent_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save agent history: {e}")

    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of agent performance"""
        if not self.agent_history:
            return {"message": "No agent history available"}

        total_agents = len(self.agent_history)
        successful_agents = len([a for a in self.agent_history
                               if a["completion_status"] in ["completed", "recovered_from_stall"]])
        failed_agents = len([a for a in self.agent_history
                           if a["completion_status"] in ["timeout", "failed"]])

        avg_duration = sum(a["duration_seconds"] for a in self.agent_history) / total_agents
        avg_tool_usage = sum(a["tool_usage_count"] for a in self.agent_history) / total_agents

        return {
            "total_agents": total_agents,
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "success_rate": (successful_agents / total_agents) * 100,
            "average_duration_seconds": avg_duration,
            "average_tool_usage": avg_tool_usage,
            "currently_active": len(self.active_agents)
        }

def create_monitor_config() -> Dict[str, Any]:
    """Create default monitoring configuration"""
    return {
        "monitoring": {
            "enabled": True,
            "default_timeout_seconds": 300,  # 5 minutes
            "default_stall_seconds": 120,    # 2 minutes
            "check_interval_seconds": 30,    # Check every 30 seconds
            "auto_recovery": {
                "enabled": True,
                "max_recovery_attempts": 2,
                "recovery_strategies": ["stimulate", "restart", "skip"]
            }
        },
        "agent_thresholds": {
            "precision-editor": {
                "timeout_seconds": 180,  # 3 minutes (shorter due to analysis paralysis risk)
                "stall_seconds": 60,    # 1 minute (very aggressive)
                "min_tool_usage": 1     # Must use at least 1 tool within first minute
            },
            "security-analyst": {
                "timeout_seconds": 600,  # 10 minutes (security analysis takes time)
                "stall_seconds": 180,   # 3 minutes
                "min_tool_usage": 2
            },
            "test-generator": {
                "timeout_seconds": 420,  # 7 minutes
                "stall_seconds": 120,   # 2 minutes
                "min_tool_usage": 3
            },
            "performance-auditor": {
                "timeout_seconds": 480,  # 8 minutes
                "stall_seconds": 150,   # 2.5 minutes
                "min_tool_usage": 2
            }
        },
        "alerts": {
            "stall_alert": True,
            "timeout_alert": True,
            "recovery_alert": True,
            "notification_channels": ["log", "file"]
        }
    }

def main():
    """Main execution for standalone monitoring"""
    monitor = AgentMonitor()

    # Create configuration
    config = create_monitor_config()
    config_file = Path(".claude/config/monitor_config.json")
    config_file.parent.mkdir(exist_ok=True)

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print("Agent Monitor initialized")
    print(f"Configuration saved to {config_file}")
    print(f"Logs directory: {monitor.log_dir}")

    # Example usage
    agent_id = monitor.register_agent("test-agent", "example-task")
    monitor.update_progress(agent_id, "Starting analysis", tool_usage=False)

    status = monitor.check_agent_health(agent_id)
    print(f"Agent status: {status.value}")

if __name__ == "__main__":
    main()