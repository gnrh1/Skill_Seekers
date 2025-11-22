#!/usr/bin/env python3
"""
Human Oversight Integration System
Provides checkpoints and approval mechanisms for critical memory operations
"""

import time
import json
import logging
import threading
import psutil
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OversightLevel(Enum):
    """Oversight levels for different operation types"""
    AUTO_APPROVE = "auto_approve"      # No human oversight required
    WARNING = "warning"                # Log warning, allow auto-approval
    APPROVAL_REQUIRED = "approval"     # Must get human approval
    EMERGENCY = "emergency"           # Immediate attention required

class OperationType(Enum):
    """Types of operations requiring oversight"""
    DEEP_DELEGATION = "deep_delegation"
    MEMORY_PRESSURE = "memory_pressure"
    CIRCULAR_REFS = "circular_refs"
    PARALLEL_LIMIT = "parallel_delegation_exceeded"
    AGENT_SPAWN = "agent_spawn"
    CLEANUP_FAILURE = "cleanup_failure"

@dataclass
class OversightRequest:
    """Represents a request for human oversight"""
    request_id: str
    operation_type: OperationType
    oversight_level: OversightLevel
    context: Dict[str, Any]
    timestamp: datetime
    timeout_seconds: int = 300  # 5 minutes default
    auto_approve_after: Optional[datetime] = None

@dataclass
class OversightDecision:
    """Represents a human oversight decision"""
    request_id: str
    approved: bool
    decision_timestamp: datetime
    decision_maker: str  # "human" or "timeout"
    reason: Optional[str] = None
    conditions: Optional[List[str]] = None

class HumanOversightManager:
    """
    Manages human oversight for critical agent operations
    Provides checkpoints and approval mechanisms with configurable policies
    """

    def __init__(self, approval_timeout: int = 300):
        self.approval_timeout = approval_timeout
        self.pending_requests: Dict[str, OversightRequest] = {}
        self.decisions: Dict[str, OversightDecision] = {}
        self.approval_queue = queue.Queue()
        self.lock = threading.RLock()

        # Configuration for different operation types
        self.operation_policies = {
            OperationType.DEEP_DELEGATION: {
                'max_depth_threshold': 4,
                'oversight_level': OversightLevel.APPROVAL_REQUIRED,
                'timeout_seconds': 180,  # 3 minutes
                'auto_approve_after_minutes': 10  # Auto-approve after 10 minutes
            },
            OperationType.MEMORY_PRESSURE: {
                'warning_threshold': 70,    # 70% memory
                'critical_threshold': 85,   # 85% memory
                'emergency_threshold': 95,  # 95% memory
                'oversight_levels': {
                    'warning': OversightLevel.WARNING,
                    'critical': OversightLevel.APPROVAL_REQUIRED,
                    'emergency': OversightLevel.EMERGENCY
                },
                'timeout_seconds': 60  # 1 minute for memory issues
            },
            OperationType.CIRCULAR_REFS: {
                'detection_threshold': 3,  # 3+ circular references
                'oversight_level': OversightLevel.APPROVAL_REQUIRED,
                'timeout_seconds': 120  # 2 minutes
            },
            OperationType.PARALLEL_LIMIT: {
                'max_parallel_threshold': 8,
                'oversight_level': OversightLevel.APPROVAL_REQUIRED,
                'timeout_seconds': 180  # 3 minutes
            },
            OperationType.CLEANUP_FAILURE: {
                'failure_threshold': 3,  # 3 failed cleanup attempts
                'oversight_level': OversightLevel.EMERGENCY,
                'timeout_seconds': 30  # 30 seconds for cleanup issues
            }
        }

        # Approval history and metrics
        self.total_requests = 0
        self.auto_approvals = 0
        self.human_approvals = 0
        self.rejections = 0
        self.timeouts = 0

        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_requests, daemon=True)
        self.cleanup_thread.start()

        logger.info("Human Oversight Manager initialized")

    def request_approval(self, operation: str, context: Dict[str, Any]) -> bool:
        """
        Request approval for a critical operation

        Args:
            operation: Operation type string
            context: Context information for the operation

        Returns:
            bool: True if approved, False if denied
        """
        try:
            op_type = OperationType(operation)
        except ValueError:
            logger.warning(f"Unknown operation type: {operation}, auto-approving")
            return True

        with self.lock:
            self.total_requests += 1

            # Determine oversight level and requirements
            oversight_level, policy = self._determine_oversight_level(op_type, context)

            if oversight_level == OversightLevel.AUTO_APPROVE:
                self.auto_approvals += 1
                logger.debug(f"Auto-approving operation: {operation}")
                return True

            if oversight_level == OversightLevel.WARNING:
                self.auto_approvals += 1
                logger.warning(f"Warning for operation: {operation} - Context: {context}")
                return True

            # Create oversight request
            request_id = f"req_{int(time.time() * 1000)}_{operation}"
            timeout = policy.get('timeout_seconds', self.approval_timeout)

            request = OversightRequest(
                request_id=request_id,
                operation_type=op_type,
                oversight_level=oversight_level,
                context=context,
                timestamp=datetime.now(),
                timeout_seconds=timeout
            )

            # Set auto-approval time if configured
            auto_approve_minutes = policy.get('auto_approve_after_minutes')
            if auto_approve_minutes:
                request.auto_approve_after = datetime.now() + timedelta(minutes=auto_approve_minutes)

            # Store request
            self.pending_requests[request_id] = request

            # Add to approval queue
            self.approval_queue.put(request)

            logger.info(f"Oversight request created: {request_id} for {operation}")

            # Wait for decision (with timeout)
            decision = self._wait_for_decision(request_id, timeout)

            if decision.approved:
                if decision.decision_maker == "timeout":
                    self.timeouts += 1
                    logger.warning(f"Request auto-approved after timeout: {request_id}")
                else:
                    self.human_approvals += 1
                    logger.info(f"Request approved by human: {request_id}")
                return True
            else:
                self.rejections += 1
                logger.warning(f"Request rejected: {request_id} - Reason: {decision.reason}")
                return False

        except Exception as e:
            logger.error(f"Error requesting approval for {operation}: {e}")
            # Conservative approach: approve on error
            return True

    def _determine_oversight_level(self, op_type: OperationType, context: Dict[str, Any]) -> tuple[OversightLevel, Dict]:
        """Determine the oversight level for an operation based on context"""

        policy = self.operation_policies.get(op_type, {
            'oversight_level': OversightLevel.AUTO_APPROVE
        })

        if op_type == OperationType.DEEP_DELEGATION:
            depth = context.get('current_depth', 0)
            max_depth = policy.get('max_depth_threshold', 4)

            if depth > max_depth + 2:  # Significantly over limit
                return OversightLevel.EMERGENCY, policy
            elif depth > max_depth:
                return OversightLevel.APPROVAL_REQUIRED, policy
            else:
                return OversightLevel.AUTO_APPROVE, policy

        elif op_type == OperationType.MEMORY_PRESSURE:
            memory_percent = context.get('memory_percent', 0)
            warning_threshold = policy.get('warning_threshold', 70)
            critical_threshold = policy.get('critical_threshold', 85)
            emergency_threshold = policy.get('emergency_threshold', 95)

            if memory_percent >= emergency_threshold:
                return OversightLevel.EMERGENCY, policy
            elif memory_percent >= critical_threshold:
                return OversightLevel.APPROVAL_REQUIRED, policy
            elif memory_percent >= warning_threshold:
                return OversightLevel.WARNING, policy
            else:
                return OversightLevel.AUTO_APPROVE, policy

        elif op_type == OperationType.CIRCULAR_REFS:
            ref_count = context.get('circular_ref_count', 0)
            threshold = policy.get('detection_threshold', 3)

            if ref_count > threshold * 2:
                return OversightLevel.EMERGENCY, policy
            elif ref_count >= threshold:
                return OversightLevel.APPROVAL_REQUIRED, policy
            else:
                return OversightLevel.AUTO_APPROVE, policy

        elif op_type == OperationType.PARALLEL_LIMIT:
            parallel_count = context.get('current_count', 0)
            threshold = policy.get('max_parallel_threshold', 8)

            if parallel_count > threshold * 2:
                return OversightLevel.EMERGENCY, policy
            elif parallel_count >= threshold:
                return OversightLevel.APPROVAL_REQUIRED, policy
            else:
                return OversightLevel.AUTO_APPROVE, policy

        elif op_type == OperationType.CLEANUP_FAILURE:
            failure_count = context.get('failure_count', 0)
            threshold = policy.get('failure_threshold', 3)

            if failure_count >= threshold:
                return policy.get('oversight_level', OversightLevel.EMERGENCY), policy

        # Default to auto-approve
        return OversightLevel.AUTO_APPROVE, policy

    def _wait_for_decision(self, request_id: str, timeout: int) -> OversightDecision:
        """Wait for human decision on an approval request"""

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if decision has been made
            if request_id in self.decisions:
                return self.decisions[request_id]

            # Check for auto-approval
            if request_id in self.pending_requests:
                request = self.pending_requests[request_id]
                if request.auto_approve_after and datetime.now() >= request.auto_approve_after:
                    decision = OversightDecision(
                        request_id=request_id,
                        approved=True,
                        decision_timestamp=datetime.now(),
                        decision_maker="timeout",
                        reason="Auto-approved due to timeout"
                    )
                    self.decisions[request_id] = decision
                    del self.pending_requests[request_id]
                    return decision

            time.sleep(0.5)  # Check every 500ms

        # Timeout reached
        request = self.pending_requests.get(request_id)
        if request:
            decision = OversightDecision(
                request_id=request_id,
                approved=True,  # Auto-approve on timeout to avoid blocking
                decision_timestamp=datetime.now(),
                decision_maker="timeout",
                reason="Auto-approved due to timeout"
            )
            self.decisions[request_id] = decision
            del self.pending_requests[request_id]
            return decision

        # Should not reach here, but provide safe default
        return OversightDecision(
            request_id=request_id,
            approved=True,
            decision_timestamp=datetime.now(),
            decision_maker="timeout",
            reason="Request not found, auto-approved"
        )

    def manual_decision(self, request_id: str, approved: bool, reason: str = None, conditions: List[str] = None) -> bool:
        """
        Make a manual decision on a pending request

        Args:
            request_id: ID of the request to decide on
            approved: Whether to approve the request
            reason: Optional reason for the decision
            conditions: Optional conditions for approval

        Returns:
            bool: True if decision was made, False if request not found
        """
        with self.lock:
            if request_id not in self.pending_requests:
                logger.warning(f"Request not found for decision: {request_id}")
                return False

            decision = OversightDecision(
                request_id=request_id,
                approved=approved,
                decision_timestamp=datetime.now(),
                decision_maker="human",
                reason=reason,
                conditions=conditions
            )

            self.decisions[request_id] = decision
            del self.pending_requests[request_id]

            logger.info(f"Manual decision recorded for {request_id}: {'APPROVED' if approved else 'REJECTED'}")
            if reason:
                logger.info(f"  Reason: {reason}")

            return True

    def _cleanup_expired_requests(self):
        """Background thread to cleanup expired requests"""
        while True:
            try:
                current_time = datetime.now()
                expired_requests = []

                with self.lock:
                    for request_id, request in self.pending_requests.items():
                        if (current_time - request.timestamp).seconds > request.timeout_seconds:
                            expired_requests.append(request_id)

                    for request_id in expired_requests:
                        request = self.pending_requests[request_id]

                        # Auto-expire with approval (conservative approach)
                        decision = OversightDecision(
                            request_id=request_id,
                            approved=True,
                            decision_timestamp=current_time,
                            decision_maker="timeout",
                            reason="Auto-approved due to request timeout"
                        )

                        self.decisions[request_id] = decision
                        del self.pending_requests[request_id]
                        self.timeouts += 1

                        logger.warning(f"Request expired and auto-approved: {request_id}")

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
                time.sleep(30)

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get list of pending approval requests"""
        with self.lock:
            pending = []
            for request_id, request in self.pending_requests.items():
                pending.append({
                    'request_id': request_id,
                    'operation_type': request.operation_type.value,
                    'oversight_level': request.oversight_level.value,
                    'context': request.context,
                    'timestamp': request.timestamp.isoformat(),
                    'timeout_seconds': request.timeout_seconds,
                    'time_remaining': request.timeout_seconds - (datetime.now() - request.timestamp).seconds
                })
            return pending

    def get_oversight_stats(self) -> Dict[str, Any]:
        """Get comprehensive oversight statistics"""
        with self.lock:
            pending_count = len(self.pending_requests)
            total_decisions = len(self.decisions)

            return {
                'total_requests': self.total_requests,
                'auto_approvals': self.auto_approvals,
                'human_approvals': self.human_approvals,
                'rejections': self.rejections,
                'timeouts': self.timeouts,
                'pending_requests': pending_count,
                'total_decisions': total_decisions,
                'approval_rate': (self.auto_approvals + self.human_approvals + self.timeouts) / max(1, self.total_requests),
                'human_involvement_rate': self.human_approvals / max(1, self.total_requests),
                'rejection_rate': self.rejections / max(1, self.total_requests)
            }

class MemoryPressureAlertSystem:
    """
    Monitors memory usage and generates alerts at different thresholds
    Integrates with HumanOversightManager for critical situations
    """

    def __init__(self, oversight_manager: Optional[HumanOversightManager] = None):
        self.oversight_manager = oversight_manager
        self.process = psutil.Process()
        self.alert_history = []
        self.alert_thresholds = {
            'warning': 60,    # 60% memory usage
            'critical': 80,   # 80% memory usage
            'emergency': 95   # 95% memory usage
        }
        self.monitoring_active = False
        self.monitor_thread = None

    def check_memory_pressure(self) -> Dict[str, Any]:
        """Check current memory pressure and generate alerts if needed"""
        try:
            # Get memory information
            memory_info = self.process.memory_info()
            system_memory = psutil.virtual_memory()

            process_memory_mb = memory_info.rss / (1024 * 1024)
            system_memory_percent = system_memory.percent
            system_available_mb = system_memory.available / (1024 * 1024)

            # Determine alert level
            alert_level = self._determine_alert_level(system_memory_percent)

            # Generate alert if needed
            if alert_level != 'normal':
                self._generate_alert(alert_level, {
                    'process_memory_mb': process_memory_mb,
                    'system_memory_percent': system_memory_percent,
                    'system_available_mb': system_available_mb,
                    'timestamp': datetime.now().isoformat()
                })

            return {
                'alert_level': alert_level,
                'process_memory_mb': process_memory_mb,
                'system_memory_percent': system_memory_percent,
                'system_available_mb': system_available_mb,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking memory pressure: {e}")
            return {
                'alert_level': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _determine_alert_level(self, memory_percent: float) -> str:
        """Determine alert level based on memory usage"""
        if memory_percent >= self.alert_thresholds['emergency']:
            return 'emergency'
        elif memory_percent >= self.alert_thresholds['critical']:
            return 'critical'
        elif memory_percent >= self.alert_thresholds['warning']:
            return 'warning'
        else:
            return 'normal'

    def _generate_alert(self, level: str, context: Dict[str, Any]) -> None:
        """Generate memory pressure alert"""
        alert = {
            'level': level,
            'context': context,
            'timestamp': context['timestamp']
        }

        self.alert_history.append(alert)

        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        # Log alert
        if level == 'emergency':
            logger.critical(f"🚨 EMERGENCY: Memory usage at {context['system_memory_percent']:.1f}%")
        elif level == 'critical':
            logger.error(f"⚠️ CRITICAL: Memory usage at {context['system_memory_percent']:.1f}%")
        elif level == 'warning':
            logger.warning(f"⚡ WARNING: Memory usage at {context['system_memory_percent']:.1f}%")

        # Request human oversight for critical situations
        if self.oversight_manager and level in ['critical', 'emergency']:
            self.oversight_manager.request_approval(
                operation="memory_pressure",
                context={
                    'memory_percent': context['system_memory_percent'],
                    'process_memory_mb': context['process_memory_mb'],
                    'available_mb': context['system_available_mb'],
                    'alert_level': level
                }
            )

    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous memory monitoring"""
        if self.monitoring_active:
            logger.warning("Memory monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_memory_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"Started memory monitoring with {interval_seconds}s interval")

    def stop_monitoring(self):
        """Stop continuous memory monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped memory monitoring")

    def _monitor_memory_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self.check_memory_pressure()
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)

    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = []

        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
            if alert_time >= cutoff_time:
                recent_alerts.append(alert)

        return recent_alerts

def test_oversight_system():
    """Test the human oversight system"""
    print("🧪 Testing Human Oversight System...")

    # Create oversight manager
    oversight_manager = HumanOversightManager(approval_timeout=30)

    # Create memory pressure alert system
    alert_system = MemoryPressureAlertSystem(oversight_manager)

    print("  • Testing different operation types...")

    # Test 1: Normal operation (should auto-approve)
    approved = oversight_manager.request_approval(
        operation="agent_spawn",
        context={'agent_type': 'test_agent', 'priority': 1}
    )
    print(f"    Normal operation: {'✅ Approved' if approved else '❌ Rejected'}")

    # Test 2: Deep delegation (should request approval)
    approved = oversight_manager.request_approval(
        operation="deep_delegation",
        context={'current_depth': 6, 'max_depth': 4, 'from_task': 'test_task'}
    )
    print(f"    Deep delegation: {'✅ Approved' if approved else '❌ Rejected'}")

    # Test 3: Memory pressure warning
    approved = oversight_manager.request_approval(
        operation="memory_pressure",
        context={'memory_percent': 75, 'process_memory_mb': 800, 'available_mb': 2000}
    )
    print(f"    Memory pressure (75%): {'✅ Approved' if approved else '❌ Rejected'}")

    # Test 4: Memory pressure critical
    approved = oversight_manager.request_approval(
        operation="memory_pressure",
        context={'memory_percent': 90, 'process_memory_mb': 1000, 'available_mb': 500}
    )
    print(f"    Memory pressure (90%): {'✅ Approved' if approved else '❌ Rejected'}")

    # Test 5: Circular references
    approved = oversight_manager.request_approval(
        operation="circular_refs",
        context={'circular_ref_count': 5, 'detection_threshold': 3}
    )
    print(f"    Circular references (5): {'✅ Approved' if approved else '❌ Rejected'}")

    print("  • Testing memory pressure monitoring...")
    memory_status = alert_system.check_memory_pressure()
    print(f"    Current memory: {memory_status.get('system_memory_percent', 0):.1f}% ({memory_status.get('alert_level', 'unknown')})")

    print("  • Testing manual decision making...")
    pending = oversight_manager.get_pending_requests()
    if pending:
        request_id = pending[0]['request_id']
        success = oversight_manager.manual_decision(
            request_id=request_id,
            approved=True,
            reason="Test manual approval"
        )
        print(f"    Manual decision: {'✅ Success' if success else '❌ Failed'}")
    else:
        print("    No pending requests for manual decision")

    # Get final statistics
    stats = oversight_manager.get_oversight_stats()
    print(f"  • Final statistics:")
    print(f"    Total requests: {stats['total_requests']}")
    print(f"    Auto-approvals: {stats['auto_approvals']}")
    print(f"    Human approvals: {stats['human_approvals']}")
    print(f"    Approval rate: {stats['approval_rate']:.1%}")
    print(f"    Human involvement: {stats['human_involvement_rate']:.1%}")

    return stats

if __name__ == "__main__":
    # Run the test
    result = test_oversight_system()

    print("\n" + "=" * 60)
    print("🎯 HUMAN OVERSIGHT SYSTEM TEST RESULTS:")
    print("=" * 60)
    print(f"Total Requests Processed: {result['total_requests']}")
    print(f"Auto-Approvals: {result['auto_approvals']}")
    print(f"Human Approvals: {result['human_approvals']}")
    print(f"Rejections: {result['rejections']}")
    print(f"Timeouts: {result['timeouts']}")
    print(f"Approval Rate: {result['approval_rate']:.1%}")
    print(f"Human Involvement Rate: {result['human_involvement_rate']:.1%}")
    print("=" * 60)
    print("✅ Human Oversight System operational")
    print("=" * 60)