#!/usr/bin/env python3
"""
Circuit Breaker System - Skip Failed Agents and Continue

Implements circuit breaker patterns to handle agent failures gracefully.
When an agent fails or times out, the system can continue with remaining tasks
instead of completely blocking the workflow.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/circuit_breaker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, skip this agent
    HALF_OPEN = "half_open"  # Testing if agent recovered

class AgentPriority(Enum):
    CRITICAL = "critical"    # Cannot skip (e.g., security fixes)
    HIGH = "high"           # Try backup agent first
    MEDIUM = "medium"       # Skip with manual intervention planned
    LOW = "low"            # Skip and continue

@dataclass
class AgentConfig:
    name: str
    priority: AgentPriority
    timeout_seconds: int
    retry_attempts: int
    backup_agents: List[str]
    can_skip: bool
    manual_intervention_required: bool = False

@dataclass
class CircuitBreakerState:
    agent_name: str
    state: CircuitState
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    retry_count: int = 0
    total_attempts: int = 0
    next_attempt_time: Optional[datetime] = None

class CircuitBreaker:
    """Circuit breaker for agent failure handling"""

    def __init__(self, config_dir: str = ".claude/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.circuits: Dict[str, CircuitBreakerState] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.failure_history: List[Dict] = []
        self.load_agent_configs()

    def load_agent_configs(self):
        """Load agent configurations"""
        config_file = self.config_dir / "circuit_breaker_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    for agent_data in config_data.get("agents", []):
                        config = AgentConfig(
                            name=agent_data["name"],
                            priority=AgentPriority(agent_data["priority"]),
                            timeout_seconds=agent_data["timeout_seconds"],
                            retry_attempts=agent_data["retry_attempts"],
                            backup_agents=agent_data["backup_agents"],
                            can_skip=agent_data["can_skip"],
                            manual_intervention_required=agent_data.get("manual_intervention_required", False)
                        )
                        self.agent_configs[config.name] = config
            except Exception as e:
                logger.error(f"Failed to load agent configs: {e}")
                self.create_default_configs()
        else:
            self.create_default_configs()

    def create_default_configs(self):
        """Create default agent configurations"""
        default_configs = [
            AgentConfig(
                name="precision-editor",
                priority=AgentPriority.HIGH,
                timeout_seconds=180,
                retry_attempts=2,
                backup_agents=["code-analyzer", "architectural-critic"],
                can_skip=True,
                manual_intervention_required=True  # Conflict resolution needs human oversight
            ),
            AgentConfig(
                name="security-analyst",
                priority=AgentPriority.CRITICAL,
                timeout_seconds=600,
                retry_attempts=3,
                backup_agents=[],
                can_skip=False  # Security fixes cannot be skipped
            ),
            AgentConfig(
                name="test-generator",
                priority=AgentPriority.MEDIUM,
                timeout_seconds=420,
                retry_attempts=2,
                backup_agents=["code-analyzer"],
                can_skip=True
            ),
            AgentConfig(
                name="performance-auditor",
                priority=AgentPriority.MEDIUM,
                timeout_seconds=480,
                retry_attempts=2,
                backup_agents=["code-analyzer"],
                can_skip=True
            ),
            AgentConfig(
                name="architectural-critic",
                priority=AgentPriority.MEDIUM,
                timeout_seconds=300,
                retry_attempts=2,
                backup_agents=["code-analyzer"],
                can_skip=True
            ),
            AgentConfig(
                name="cognitive-resonator",
                priority=AgentPriority.LOW,
                timeout_seconds=240,
                retry_attempts=1,
                backup_agents=[],
                can_skip=True
            ),
            AgentConfig(
                name="referee-agent-csp",
                priority=AgentPriority.HIGH,
                timeout_seconds=300,
                retry_attempts=2,
                backup_agents=["orchestrator-agent"],
                can_skip=False  # Synthesis is critical
            )
        ]

        for config in default_configs:
            self.agent_configs[config.name] = config

        # Save default configurations
        self.save_agent_configs()

    def save_agent_configs(self):
        """Save agent configurations to file"""
        config_data = {
            "agents": [
                {
                    "name": config.name,
                    "priority": config.priority.value,
                    "timeout_seconds": config.timeout_seconds,
                    "retry_attempts": config.retry_attempts,
                    "backup_agents": config.backup_agents,
                    "can_skip": config.can_skip,
                    "manual_intervention_required": config.manual_intervention_required
                }
                for config in self.agent_configs.values()
            ]
        }

        config_file = self.config_dir / "circuit_breaker_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save agent configs: {e}")

    def get_circuit(self, agent_name: str) -> CircuitBreakerState:
        """Get or create circuit breaker state for agent"""
        if agent_name not in self.circuits:
            self.circuits[agent_name] = CircuitBreakerState(
                agent_name=agent_name,
                state=CircuitState.CLOSED
            )
        return self.circuits[agent_name]

    def can_execute_agent(self, agent_name: str) -> tuple[bool, str]:
        """Check if agent can execute and return reason"""
        circuit = self.get_circuit(agent_name)
        config = self.agent_configs.get(agent_name)

        if not config:
            return False, f"Agent {agent_name} not configured"

        # Check circuit state
        if circuit.state == CircuitState.OPEN:
            # Check if circuit should be half-open
            if (circuit.next_attempt_time and
                datetime.now() >= circuit.next_attempt_time):
                circuit.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit for {agent_name} moved to HALF_OPEN")
                return True, "Circuit half-open - testing recovery"
            else:
                return False, f"Circuit open - {circuit.failure_count} failures"

        return True, "Circuit closed - agent can execute"

    def record_agent_success(self, agent_name: str):
        """Record successful agent execution"""
        circuit = self.get_circuit(agent_name)
        circuit.last_success_time = datetime.now()
        circuit.failure_count = 0
        circuit.retry_count = 0
        circuit.state = CircuitState.CLOSED

        logger.info(f"Recorded success for agent {agent_name}")

    def record_agent_failure(self, agent_name: str, failure_reason: str):
        """Record agent failure and update circuit state"""
        circuit = self.get_circuit(agent_name)
        config = self.agent_configs.get(agent_name)

        circuit.failure_count += 1
        circuit.last_failure_time = datetime.now()
        circuit.total_attempts += 1

        # Record failure
        failure_record = {
            "agent_name": agent_name,
            "failure_time": circuit.last_failure_time.isoformat(),
            "failure_reason": failure_reason,
            "failure_count": circuit.failure_count,
            "circuit_state": circuit.state.value
        }
        self.failure_history.append(failure_record)

        # Check if circuit should open
        if config and circuit.failure_count >= config.retry_attempts:
            circuit.state = CircuitState.OPEN
            # Set next attempt time (exponential backoff)
            backoff_seconds = min(300, 30 * (2 ** circuit.failure_count))
            circuit.next_attempt_time = datetime.now() + timedelta(seconds=backoff_seconds)

            logger.warning(f"Circuit opened for agent {agent_name} after {circuit.failure_count} failures")
            logger.info(f"Next attempt allowed at {circuit.next_attempt_time}")

        logger.warning(f"Recorded failure for agent {agent_name}: {failure_reason}")

    def get_backup_agent(self, failed_agent: str) -> Optional[str]:
        """Get backup agent for failed agent"""
        config = self.agent_configs.get(failed_agent)
        if not config or not config.backup_agents:
            return None

        # Find first available backup agent
        for backup_name in config.backup_agents:
            can_execute, reason = self.can_execute_agent(backup_name)
            if can_execute:
                logger.info(f"Using backup agent {backup_name} for failed agent {failed_agent}")
                return backup_name

        return None

    def should_skip_agent(self, agent_name: str) -> tuple[bool, str, Optional[str]]:
        """Determine if agent should be skipped and provide backup"""
        config = self.agent_configs.get(agent_name)
        if not config:
            return False, "Agent not configured", None

        can_execute, reason = self.can_execute_agent(agent_name)

        if can_execute:
            return False, "Agent can execute", None

        # Agent cannot execute, check if we can skip
        if not config.can_skip:
            return False, f"Agent cannot be skipped (priority: {config.priority.value})", None

        # Try to find backup agent
        backup_agent = self.get_backup_agent(agent_name)
        if backup_agent:
            return False, f"Using backup agent: {backup_agent}", backup_agent

        # No backup available, check if we can skip
        if config.manual_intervention_required:
            return True, f"Agent skipped - requires manual intervention", None

        return True, f"Agent skipped - priority: {config.priority.value}", None

    def get_workflow_plan(self, required_agents: List[str]) -> Dict[str, Any]:
        """Get execution plan for workflow with circuit breaker logic"""
        plan = {
            "original_agents": required_agents.copy(),
            "execution_plan": [],
            "skipped_agents": [],
            "backup_agents_used": [],
            "manual_intervention_required": [],
            "critical_failures": []
        }

        for agent_name in required_agents:
            config = self.agent_configs.get(agent_name)
            if not config:
                plan["skipped_agents"].append({
                    "agent": agent_name,
                    "reason": "Agent not configured"
                })
                continue

            should_skip, reason, backup = self.should_skip_agent(agent_name)

            if should_skip:
                plan["skipped_agents"].append({
                    "agent": agent_name,
                    "reason": reason
                })
                if config.manual_intervention_required:
                    plan["manual_intervention_required"].append(agent_name)
                if config.priority == AgentPriority.CRITICAL:
                    plan["critical_failures"].append(agent_name)
            elif backup:
                plan["execution_plan"].append(backup)
                plan["backup_agents_used"].append({
                    "original": agent_name,
                    "backup": backup,
                    "reason": reason
                })
            else:
                plan["execution_plan"].append(agent_name)

        # Determine if workflow can proceed
        plan["can_proceed"] = len(plan["critical_failures"]) == 0
        plan["requires_manual_intervention"] = len(plan["manual_intervention_required"]) > 0

        return plan

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        total_circuits = len(self.circuits)
        open_circuits = len([c for c in self.circuits.values() if c.state == CircuitState.OPEN])
        closed_circuits = len([c for c in self.circuits.values() if c.state == CircuitState.CLOSED])
        half_open_circuits = len([c for c in self.circuits.values() if c.state == CircuitState.HALF_OPEN])

        recent_failures = [f for f in self.failure_history
                          if datetime.fromisoformat(f["failure_time"]) > datetime.now() - timedelta(hours=1)]

        return {
            "total_agents": total_circuits,
            "circuits_open": open_circuits,
            "circuits_closed": closed_circuits,
            "circuits_half_open": half_open_circuits,
            "recent_failures_count": len(recent_failures),
            "total_failure_history": len(self.failure_history),
            "system_health": "healthy" if open_circuits == 0 else "degraded" if open_circuits < total_circuits / 2 else "critical"
        }

def main():
    """Main execution for testing circuit breaker"""
    breaker = CircuitBreaker()

    print("Circuit Breaker System initialized")
    print(f"Loaded {len(breaker.agent_configs)} agent configurations")

    # Test workflow planning
    required_agents = ["precision-editor", "security-analyst", "test-generator", "performance-auditor"]
    plan = breaker.get_workflow_plan(required_agents)

    print("\nWorkflow Execution Plan:")
    print(f"Original agents: {plan['original_agents']}")
    print(f"Execution plan: {plan['execution_plan']}")
    print(f"Skipped agents: {[s['agent'] for s in plan['skipped_agents']]}")
    print(f"Can proceed: {plan['can_proceed']}")
    print(f"Requires manual intervention: {plan['requires_manual_intervention']}")

    # Test system health
    health = breaker.get_system_health()
    print(f"\nSystem Health: {health['system_health']}")
    print(f"Open circuits: {health['circuits_open']}/{health['total_agents']}")

if __name__ == "__main__":
    main()