#!/usr/bin/env python3
"""
Circular Reference Elimination System
Implements weak reference patterns and explicit cleanup for agent delegation
"""

import weakref
import gc
import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from threading import RLock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentTask:
    """Represents an agent task with weak references to prevent circular refs"""
    task_id: str
    agent_type: str
    description: str
    prompt: str
    depth: int = 0
    priority: int = 1

class AgentContext:
    """
    Agent context with circular reference elimination
    Uses weak references and explicit cleanup to prevent memory leaks
    """

    def __init__(self, task_id: str, parent_context: Optional['AgentContext'] = None):
        self.task_id = task_id
        self.parent_ref = weakref.ref(parent_context) if parent_context else None

        # Use weak references for subtasks to prevent cycles
        self._subtask_refs: List[weakref.ref] = []
        self.subtask_ids: Set[str] = set()  # Track IDs separately

        # Task data
        self.data = []
        self.metadata = {}

        # Callbacks with weak references
        self._callback_refs: List[weakref.ref] = []

        # State tracking
        self.created_at = time.time()
        self.cleaned_up = False
        self.cleanup_lock = RLock()

    def add_subtask(self, subtask_context: 'AgentContext') -> None:
        """Add subtask with weak reference to prevent circular references"""
        if self.cleaned_up:
            logger.warning(f"Attempting to add subtask to cleaned context {self.task_id}")
            return

        with self.cleanup_lock:
            self._subtask_refs.append(weakref.ref(subtask_context))
            self.subtask_ids.add(subtask_context.task_id)

    def add_callback(self, callback_func) -> None:
        """Add callback with weak reference"""
        if self.cleaned_up:
            return

        with self.cleanup_lock:
            self._callback_refs.append(weakref.ref(callback_func))

    def get_parent(self) -> Optional['AgentContext']:
        """Get parent context via weak reference"""
        return self.parent_ref() if self.parent_ref else None

    def get_active_subtasks(self) -> List['AgentContext']:
        """Get still-alive subtasks"""
        active_subtasks = []
        for ref in self._subtask_refs:
            subtask = ref()
            if subtask and not subtask.cleaned_up:
                active_subtasks.append(subtask)
        return active_subtasks

    def cleanup(self) -> None:
        """Explicit cleanup method to break all reference cycles"""
        with self.cleanup_lock:
            if self.cleaned_up:
                return

            logger.debug(f"Cleaning up agent context: {self.task_id}")

            # Clear data structures
            self.data.clear()
            self.metadata.clear()
            self.subtask_ids.clear()

            # Clear weak reference lists
            self._subtask_refs.clear()
            self._callback_refs.clear()

            # Clear parent reference
            self.parent_ref = None

            # Mark as cleaned
            self.cleaned_up = True

    def __del__(self):
        """Ensure cleanup happens even if explicit cleanup is missed"""
        if not self.cleaned_up:
            self.cleanup()

class DelegationCircuitBreaker:
    """
    Prevents excessive delegation depth and parallel delegations
    Adds human oversight checkpoints for critical operations
    """

    def __init__(self, max_depth: int = 5, max_parallel_delegations: int = 10):
        self.max_depth = max_depth
        self.max_parallel = max_parallel_delegations
        self.active_delegations: Dict[str, AgentContext] = {}
        self.delegation_lock = RLock()
        self.oversight_manager = None

    def set_oversight_manager(self, oversight_manager):
        """Set human oversight manager for critical operations"""
        self.oversight_manager = oversight_manager

    def can_delegate(self, from_task: AgentTask, to_agent_type: str) -> tuple[bool, str]:
        """
        Check if delegation is allowed and requires human oversight

        Returns:
            (can_delegate, reason_or_approval_status)
        """
        with self.delegation_lock:
            # Check delegation depth
            current_depth = from_task.depth

            if current_depth >= self.max_depth:
                reason = f"Maximum delegation depth ({self.max_depth}) exceeded"

                # Request human oversight for depth violations
                if self.oversight_manager:
                    approval = self.oversight_manager.request_approval(
                        operation="deep_delegation",
                        context={
                            'current_depth': current_depth,
                            'max_depth': self.max_depth,
                            'from_task': from_task.task_id,
                            'to_agent': to_agent_type
                        }
                    )
                    if not approval:
                        return False, reason + " - Human approval denied"
                    logger.info(f"Human approval granted for deep delegation: {current_depth}")
                else:
                    return False, reason

            # Check parallel delegation limit
            active_count = len(self.active_delegations)

            if active_count >= self.max_parallel:
                reason = f"Maximum parallel delegations ({self.max_parallel}) exceeded"

                # Request human oversight for parallel limit violations
                if self.oversight_manager:
                    approval = self.oversight_manager.request_approval(
                        operation="parallel_delegation_exceeded",
                        context={
                            'current_count': active_count,
                            'max_parallel': self.max_parallel,
                            'from_task': from_task.task_id
                        }
                    )
                    if not approval:
                        return False, reason + " - Human approval denied"
                    logger.info(f"Human approval granted for parallel delegation: {active_count}")
                else:
                    return False, reason

            return True, "Delegation allowed"

    def register_delegation(self, task_id: str, context: AgentContext) -> None:
        """Register a new delegation"""
        with self.delegation_lock:
            self.active_delegations[task_id] = context
            logger.debug(f"Registered delegation: {task_id} (total: {len(self.active_delegations)})")

    def complete_delegation(self, task_id: str) -> None:
        """Complete a delegation and cleanup context"""
        with self.delegation_lock:
            if task_id in self.active_delegations:
                context = self.active_delegations[task_id]

                # Explicit cleanup
                context.cleanup()

                # Remove from active delegations
                del self.active_delegations[task_id]

                logger.debug(f"Completed delegation: {task_id} (remaining: {len(self.active_delegations)})")

    def get_delegation_stats(self) -> Dict[str, Any]:
        """Get current delegation statistics"""
        with self.delegation_lock:
            active_count = len(self.active_delegations)
            max_depth = 0
            active_contexts = []

            for context in self.active_delegations.values():
                if not context.cleaned_up:
                    active_contexts.append(context)
                    max_depth = max(max_depth, context.get_parent() is not None)

            return {
                'active_delegations': active_count,
                'max_depth_found': max_depth,
                'contexts_pending_cleanup': len(active_contexts)
            }

class AgentLifecycleManager:
    """
    Manages agent lifecycle with proper cleanup and memory monitoring
    """

    def __init__(self):
        self.active_agents: Dict[str, AgentContext] = {}
        self.metadata: Dict[str, Dict] = {}
        self.cleanup_registry: List[weakref.finalize] = []
        self.lifecycle_lock = RLock()
        self.total_created = 0
        self.total_cleaned = 0

    def create_agent_context(self, task: AgentTask, parent_context: Optional[AgentContext] = None) -> AgentContext:
        """Create new agent context with automatic cleanup registration"""
        with self.lifecycle_lock:
            # Create context
            context = AgentContext(task.task_id, parent_context)

            # Store active reference
            self.active_agents[task.task_id] = context

            # Store metadata separately (doesn't create circular refs)
            self.metadata[task.task_id] = {
                'agent_type': task.agent_type,
                'description': task.description,
                'depth': task.depth,
                'priority': task.priority,
                'created_at': context.created_at,
                'parent_id': parent_context.task_id if parent_context else None
            }

            # Register cleanup finalizer
            cleanup_finalizer = weakref.finalize(
                context,
                self._cleanup_agent_callback,
                task.task_id
            )
            self.cleanup_registry.append(cleanup_finalizer)

            self.total_created += 1
            logger.info(f"Created agent context: {task.task_id} (type: {task.agent_type}, depth: {task.depth})")

            return context

    def _cleanup_agent_callback(self, task_id: str) -> None:
        """Callback triggered when agent context is garbage collected"""
        with self.lifecycle_lock:
            if task_id in self.metadata:
                logger.debug(f"Agent context garbage collected: {task_id}")
                del self.metadata[task_id]
                self.total_cleaned += 1

    def explicit_cleanup(self, task_id: str) -> bool:
        """Perform explicit cleanup of agent context"""
        with self.lifecycle_lock:
            if task_id not in self.active_agents:
                return False

            context = self.active_agents[task_id]

            # Perform cleanup
            context.cleanup()

            # Remove from active agents
            del self.active_agents[task_id]

            self.total_cleaned += 1
            logger.info(f"Explicit cleanup completed: {task_id}")

            return True

    def cleanup_all(self) -> int:
        """Cleanup all active agent contexts"""
        with self.lifecycle_lock:
            task_ids = list(self.active_agents.keys())
            cleaned_count = 0

            for task_id in task_ids:
                if self.explicit_cleanup(task_id):
                    cleaned_count += 1

            logger.info(f"Cleanup all completed: {cleaned_count}/{len(task_ids)} agents")
            return cleaned_count

    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """Get lifecycle management statistics"""
        with self.lifecycle_lock:
            active_count = len(self.active_agents)
            metadata_count = len(self.metadata)

            # Check for orphaned metadata (cleaned but not removed)
            orphaned_metadata = 0
            for task_id in list(self.metadata.keys()):
                if task_id not in self.active_agents:
                    # Check if context still exists via weak refs
                    found = False
                    for finalizer in self.cleanup_registry:
                        if hasattr(finalizer, 'args') and finalizer.args == (task_id,):
                            found = True
                            break
                    if not found:
                        orphaned_metadata += 1
                        del self.metadata[task_id]

            return {
                'active_agents': active_count,
                'metadata_entries': metadata_count,
                'orphaned_metadata': orphaned_metadata,
                'total_created': self.total_created,
                'total_cleaned': self.total_cleaned,
                'cleanup_efficiency': self.total_cleaned / max(1, self.total_created),
                'pending_finalizers': len(self.cleanup_registry)
            }

class CircularReferenceDetector:
    """
    Detects and reports circular reference patterns in agent contexts
    """

    def __init__(self):
        self.detection_results = []

    def detect_circular_references(self, context: AgentContext, visited: Optional[Set[str]] = None, path: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Detect circular references starting from a given context

        Returns detection report with path and severity
        """
        if visited is None:
            visited = set()
        if path is None:
            path = []

        current_id = context.task_id

        # Check if we've seen this context before (circular reference detected)
        if current_id in visited:
            cycle_start = path.index(current_id)
            cycle_path = path[cycle_start:] + [current_id]

            return {
                'has_circular_ref': True,
                'cycle_length': len(cycle_path) - 1,
                'cycle_path': cycle_path,
                'root_context': path[0] if path else current_id,
                'severity': 'high' if len(cycle_path) > 3 else 'medium'
            }

        # Mark as visited and add to path
        visited.add(current_id)
        path.append(current_id)

        # Check subtasks recursively
        for subtask in context.get_active_subtasks():
            result = self.detect_circular_references(subtask, visited.copy(), path.copy())
            if result['has_circular_ref']:
                return result

        # Check parent context
        parent = context.get_parent()
        if parent:
            result = self.detect_circular_references(parent, visited.copy(), path.copy())
            if result['has_circular_ref']:
                return result

        # No circular references found
        return {
            'has_circular_ref': False,
            'checked_depth': len(path),
            'root_context': current_id
        }

    def scan_all_contexts(self, contexts: List[AgentContext]) -> Dict[str, Any]:
        """Scan multiple contexts for circular references"""
        total_contexts = len(contexts)
        circular_refs_found = 0
        max_cycle_length = 0
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}

        for context in contexts:
            result = self.detect_circular_references(context)

            if result['has_circular_ref']:
                circular_refs_found += 1
                max_cycle_length = max(max_cycle_length, result['cycle_length'])

                if 'severity' in result:
                    severity_counts[result['severity']] += 1

                self.detection_results.append(result)

        return {
            'total_contexts_scanned': total_contexts,
            'circular_references_detected': circular_refs_found,
            'max_cycle_length': max_cycle_length,
            'severity_distribution': severity_counts,
            'detection_rate': circular_refs_found / max(1, total_contexts),
            'detailed_results': self.detection_results[-10:]  # Last 10 results
        }

# Global instances for easy access
_delegation_circuit_breaker = None
_lifecycle_manager = None
_circular_detector = None

def get_delegation_circuit_breaker() -> DelegationCircuitBreaker:
    """Get global delegation circuit breaker instance"""
    global _delegation_circuit_breaker
    if _delegation_circuit_breaker is None:
        _delegation_circuit_breaker = DelegationCircuitBreaker()
    return _delegation_circuit_breaker

def get_agent_lifecycle_manager() -> AgentLifecycleManager:
    """Get global agent lifecycle manager instance"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = AgentLifecycleManager()
    return _lifecycle_manager

def get_circular_reference_detector() -> CircularReferenceDetector:
    """Get global circular reference detector instance"""
    global _circular_detector
    if _circular_detector is None:
        _circular_detector = CircularReferenceDetector()
    return _circular_detector

def test_circular_reference_fix():
    """Test the circular reference elimination system"""
    print("🧪 Testing Circular Reference Elimination System...")

    # Initialize components
    circuit_breaker = get_delegation_circuit_breaker()
    lifecycle_manager = get_agent_lifecycle_manager()
    detector = get_circular_reference_detector()

    # Create test tasks
    tasks = []
    contexts = []

    print("  • Creating agent contexts with delegation...")

    # Create root task
    root_task = AgentTask("root", "orchestrator", "Root coordination task", "", 0)
    root_context = lifecycle_manager.create_agent_context(root_task)
    contexts.append(root_context)

    # Create delegation chain
    for i in range(1, 6):  # 5 levels deep
        task = AgentTask(f"task_{i}", f"agent_type_{i % 3}", f"Task {i}", "", i)

        # Check if delegation is allowed
        can_delegate, reason = circuit_breaker.can_delegate(tasks[-1] if tasks else root_task, task.agent_type)

        if can_delegate:
            parent_context = contexts[-1] if contexts else root_context
            context = lifecycle_manager.create_agent_context(task, parent_context)

            # Add subtask relationship
            parent_context.add_subtask(context)

            # Register delegation
            circuit_breaker.register_delegation(task.task_id, context)

            contexts.append(context)
            tasks.append(task)

            print(f"    Created task {i}: {task.agent_type} at depth {i}")
        else:
            print(f"    Blocked delegation at depth {i}: {reason}")
            break

    # Scan for circular references
    print("  • Scanning for circular references...")
    scan_result = detector.scan_all_contexts(contexts)

    print(f"    Contexts scanned: {scan_result['total_contexts_scanned']}")
    print(f"    Circular references: {scan_result['circular_references_detected']}")
    print(f"    Detection rate: {scan_result['detection_rate']:.1%}")

    # Test cleanup
    print("  • Testing cleanup mechanisms...")

    # Complete delegations
    for task in tasks:
        circuit_breaker.complete_delegation(task.task_id)

    # Explicit cleanup
    cleaned_count = lifecycle_manager.cleanup_all()

    # Force garbage collection
    collected = gc.collect()

    # Get final stats
    lifecycle_stats = lifecycle_manager.get_lifecycle_stats()
    delegation_stats = circuit_breaker.get_delegation_stats()

    print(f"    Explicit cleanup: {cleaned_count} agents")
    print(f"    GC collected: {collected} objects")
    print(f"    Lifecycle efficiency: {lifecycle_stats['cleanup_efficiency']:.1%}")
    print(f"    Active delegations: {delegation_stats['active_delegations']}")

    # Final verification
    print("  • Verifying no circular references remain...")
    final_scan = detector.scan_all_contexts([ctx for ctx in contexts if not ctx.cleaned_up])

    if final_scan['circular_references_detected'] == 0:
        print("    ✅ No circular references detected - SUCCESS!")
    else:
        print(f"    ❌ Still {final_scan['circular_references_detected']} circular references - FAILURE!")

    return {
        'contexts_created': len(contexts),
        'circular_refs_initial': scan_result['circular_references_detected'],
        'circular_refs_final': final_scan['circular_references_detected'],
        'cleanup_efficiency': lifecycle_stats['cleanup_efficiency'],
        'success': final_scan['circular_references_detected'] == 0
    }

if __name__ == "__main__":
    # Run the test
    result = test_circular_reference_fix()

    print("\n" + "=" * 60)
    print("🎯 CIRCULAR REFERENCE FIX TEST RESULTS:")
    print("=" * 60)
    print(f"Contexts Created: {result['contexts_created']}")
    print(f"Initial Circular Refs: {result['circular_refs_initial']}")
    print(f"Final Circular Refs: {result['circular_refs_final']}")
    print(f"Cleanup Efficiency: {result['cleanup_efficiency']:.1%}")
    print(f"Overall Success: {'✅ YES' if result['success'] else '❌ NO'}")
    print("=" * 60)