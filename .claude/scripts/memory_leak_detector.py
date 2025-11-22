#!/usr/bin/env python3
"""
Memory Leak Detection and Analysis Tool
Identifies specific sources of memory leaks in the Skill Seekers ecosystem
"""

import gc
import os
import sys
import time
import psutil
import json
import traceback
import threading
import weakref
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess

class MemoryLeakDetector:
    """Comprehensive memory leak detection system"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.snapshots = []
        self.object_counts = {}
        self.leak_sources = {}
        self.test_results = {}

    def get_memory_snapshot(self, label: str) -> Dict[str, Any]:
        """Capture detailed memory snapshot"""
        try:
            # Process memory
            memory_info = self.process.memory_info()
            memory_full = self.process.memory_full_info()

            # System memory
            system_memory = psutil.virtual_memory()

            # Garbage collection stats
            gc_stats = gc.get_stats() if hasattr(gc, 'get_stats') else []

            # Object counts by type
            object_counts = {}
            for obj_type in [list, dict, tuple, set, str, int, float, bytes, bytearray]:
                count = 0
                try:
                    # Count objects of each type safely
                    count = len([obj for obj in gc.get_objects() if type(obj) is obj_type])
                except (TypeError, RuntimeError):
                    pass
                object_counts[obj_type.__name__] = count

            snapshot = {
                'timestamp': time.time(),
                'label': label,
                'process_memory': {
                    'rss_mb': memory_info.rss / (1024 * 1024),
                    'vms_mb': memory_info.vms / (1024 * 1024),
                    'shared_mb': getattr(memory_full, 'shared', 0) / (1024 * 1024),
                    'text_mb': getattr(memory_full, 'text', 0) / (1024 * 1024),
                    'lib_mb': getattr(memory_full, 'lib', 0) / (1024 * 1024),
                    'data_mb': getattr(memory_full, 'data', 0) / (1024 * 1024),
                    'uss_mb': getattr(memory_full, 'uss', 0) / (1024 * 1024),
                },
                'system_memory': {
                    'available_mb': system_memory.available / (1024 * 1024),
                    'used_mb': system_memory.used / (1024 * 1024),
                    'percent': system_memory.percent,
                },
                'gc_stats': gc_stats,
                'object_counts': object_counts,
                'total_objects': len(gc.get_objects()) if hasattr(gc, 'get_objects') else 0
            }

            self.snapshots.append(snapshot)
            return snapshot

        except Exception as e:
            return {
                'timestamp': time.time(),
                'label': label,
                'error': str(e)
            }

    def test_recursive_delegation_leak(self) -> Dict[str, Any]:
        """Test 1: Recursive agent delegation memory leak"""
        print("\n🔍 Testing Recursive Delegation Memory Leak...")

        initial_snapshot = self.get_memory_snapshot("recursive_test_start")

        try:
            # Simulate recursive agent delegation pattern
            leak_objects = []
            call_stack_depths = []

            def simulate_agent_delegation(depth: int, max_depth: int):
                """Simulate recursive agent delegation that could cause leaks"""
                if depth > max_depth:
                    return []

                # Simulate agent context creation
                agent_context = {
                    'depth': depth,
                    'task_id': f"task_{depth}_{time.time()}",
                    'subtasks': [],
                    'data': ['x'] * (100 * (depth + 1)),  # Increasing data size
                    'callbacks': []
                }

                # Create circular references (common leak pattern)
                if depth > 0:
                    agent_context['parent_context'] = f"context_{depth-1}"

                # Recursive delegation
                for i in range(2):  # 2 sub-tasks per level
                    subtask = simulate_agent_delegation(depth + 1, max_depth)
                    agent_context['subtasks'].append(subtask)

                    # Create callback closure that holds reference
                    def create_callback(task_data, closure_depth=depth):
                        def callback():
                            return f"completed_{closure_depth}_{task_data}"
                        return callback

                    callback = create_callback(agent_context['task_id'])
                    agent_context['callbacks'].append(callback)

                leak_objects.append(agent_context)
                return agent_context

            # Execute recursive delegation with increasing depths
            print("  • Creating recursive delegation patterns...")
            for iteration in range(20):
                depth = min(5 + iteration // 4, 15)  # Gradually increase depth

                delegation_tree = simulate_agent_delegation(0, depth)
                call_stack_depths.append(depth)

                # Measure memory after each iteration
                if iteration % 5 == 0:
                    current_snapshot = self.get_memory_snapshot(f"recursive_iteration_{iteration}")
                    memory_growth = current_snapshot['process_memory']['rss_mb'] - initial_snapshot['process_memory']['rss_mb']
                    print(f"    Iteration {iteration} (depth {depth}): Memory growth: {memory_growth:.1f}MB")

            # Force cleanup
            print("  • Forcing cleanup of delegation objects...")
            leak_objects.clear()
            del call_stack_depths

            # Multiple GC passes to ensure cleanup
            for i in range(3):
                collected = gc.collect()
                print(f"    GC pass {i+1}: {collected} objects collected")
                time.sleep(0.1)

            final_snapshot = self.get_memory_snapshot("recursive_test_end")

            # Calculate leak metrics
            initial_memory = initial_snapshot['process_memory']['rss_mb']
            final_memory = final_snapshot['process_memory']['rss_mb']
            memory_leaked = final_memory - initial_memory

            # Calculate object retention rates
            initial_objects = initial_snapshot.get('total_objects', 0)
            final_objects = final_snapshot.get('total_objects', 0)
            object_retention_rate = (final_objects - initial_objects) / max(1, initial_objects)

            return {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_leaked_mb': memory_leaked,
                'initial_objects': initial_objects,
                'final_objects': final_objects,
                'object_retention_rate': object_retention_rate,
                'max_depth_reached': max(call_stack_depths) if call_stack_depths else 0,
                'delegations_created': len(leak_objects),
                'leak_detected': memory_leaked > 50,  # 50MB threshold
                'gc_passes_required': 3,
                'cleanup_effectiveness': max(0, 1 - (memory_leaked / max(1, initial_memory)))
            }

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'leak_detected': True  # Conservative approach
            }

    def test_web_scraping_leak(self) -> Dict[str, Any]:
        """Test 2: Web scraping memory leak"""
        print("\n🕷️ Testing Web Scraping Memory Leak...")

        initial_snapshot = self.get_memory_snapshot("scraping_test_start")

        try:
            # Simulate the web scraping pattern from doc_scraper.py
            visited_urls = set()
            pending_urls = []
            scraped_data = []

            def simulate_scrape_page(url: str, depth: int):
                """Simulate the scrape_page method pattern"""
                if url in visited_urls or depth > 10:
                    return None

                visited_urls.add(url)

                # Simulate page data extraction
                page_data = {
                    'url': url,
                    'title': f"Page {url}",
                    'content': ['x'] * 1000,  # Simulate content
                    'links': [],
                    'images': [],
                    'scripts': []
                }

                # Generate links (recursive pattern)
                for i in range(5):  # 5 links per page
                    link_url = f"{url}/page{i}"
                    page_data['links'].append(link_url)

                    # Recursively scrape linked pages
                    if depth < 3:  # Limit depth for testing
                        sub_page = simulate_scrape_page(link_url, depth + 1)
                        if sub_page:
                            page_data['links'].append(sub_page)

                scraped_data.append(page_data)
                return page_data

            print("  • Simulating recursive web scraping...")
            # Simulate scraping multiple sites
            for site_id in range(10):
                base_url = f"https://site{site_id}.com"
                pending_urls.append(base_url)

                # Start recursive scraping
                simulate_scrape_page(base_url, 0)

                # Check memory growth
                if site_id % 3 == 2:
                    current_snapshot = self.get_memory_snapshot(f"scraping_site_{site_id}")
                    memory_growth = current_snapshot['process_memory']['rss_mb'] - initial_snapshot['process_memory']['rss_mb']
                    print(f"    Site {site_id}: Memory growth: {memory_growth:.1f}MB")

            print("  • Cleaning up scraping structures...")
            # Clear main data structures
            visited_urls.clear()
            pending_urls.clear()
            scraped_data.clear()

            # Force garbage collection
            for i in range(3):
                collected = gc.collect()
                print(f"    GC pass {i+1}: {collected} objects collected")
                time.sleep(0.1)

            final_snapshot = self.get_memory_snapshot("scraping_test_end")

            # Calculate metrics
            initial_memory = initial_snapshot['process_memory']['rss_mb']
            final_memory = final_snapshot['process_memory']['rss_mb']
            memory_leaked = final_memory - initial_memory

            return {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_leaked_mb': memory_leaked,
                'pages_scraped': len(scraped_data),
                'urls_visited': len(visited_urls),
                'leak_detected': memory_leaked > 30,  # 30MB threshold for scraping
                'cleanup_effectiveness': max(0, 1 - (memory_leaked / max(1, initial_memory)))
            }

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'leak_detected': True
            }

    def test_resource_monitor_leak(self) -> Dict[str, Any]:
        """Test 3: Resource monitoring system memory leak"""
        print("\n📊 Testing Resource Monitor Memory Leak...")

        initial_snapshot = self.get_memory_snapshot("resource_monitor_test_start")

        try:
            # Import and test resource monitoring components
            sys.path.insert(0, '/Users/docravikumar/Code/skill-test/Skill_Seekers/.claude/scripts')

            try:
                from resource_monitor import get_resource_monitor, register_agent, update_agent_status
                from memory_protection_hook import extract_agent_type, check_memory_before_task
            except ImportError as e:
                print(f"    Warning: Could not import resource modules: {e}")
                return {'error': f'Import error: {e}', 'leak_detected': False}

            # Get resource monitor instance
            monitor = get_resource_monitor()

            # Simulate agent registration and monitoring cycles
            print("  • Simulating agent registration cycles...")
            agent_ids = []

            for cycle in range(50):
                # Register multiple agents
                for i in range(5):
                    agent_id = f"test_agent_{cycle}_{i}"
                    agent_type = f"test_type_{i % 3}"

                    register_agent(agent_id, agent_type)
                    agent_ids.append(agent_id)

                # Update status for some agents
                for i in range(0, len(agent_ids), 3):
                    if i < len(agent_ids):
                        update_agent_status(agent_ids[i], 'active')

                # Check memory usage
                if cycle % 10 == 0:
                    current_snapshot = self.get_memory_snapshot(f"resource_monitor_cycle_{cycle}")
                    memory_growth = current_snapshot['process_memory']['rss_mb'] - initial_snapshot['process_memory']['rss_mb']
                    print(f"    Cycle {cycle}: Memory growth: {memory_growth:.1f}MB, Agents: {len(agent_ids)}")

            print("  • Testing resource monitor cleanup...")
            # Test cleanup functionality
            monitor.cleanup_completed_agents()

            # Force cleanup
            agent_ids.clear()

            # Multiple GC passes
            for i in range(3):
                collected = gc.collect()
                print(f"    GC pass {i+1}: {collected} objects collected")
                time.sleep(0.1)

            final_snapshot = self.get_memory_snapshot("resource_monitor_test_end")

            # Calculate metrics
            initial_memory = initial_snapshot['process_memory']['rss_mb']
            final_memory = final_snapshot['process_memory']['rss_mb']
            memory_leaked = final_memory - initial_memory

            return {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_leaked_mb': memory_leaked,
                'agents_registered': len(agent_ids),
                'cleanup_cycles': 50,
                'leak_detected': memory_leaked > 20,  # 20MB threshold
                'cleanup_effectiveness': max(0, 1 - (memory_leaked / max(1, initial_memory)))
            }

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'leak_detected': True
            }

    def test_circular_reference_leak(self) -> Dict[str, Any]:
        """Test 4: Circular reference memory leak"""
        print("\n🔗 Testing Circular Reference Memory Leak...")

        initial_snapshot = self.get_memory_snapshot("circular_ref_test_start")

        try:
            # Create complex circular reference patterns
            circular_objects = []
            weak_refs = []

            class CircularNode:
                def __init__(self, value, node_id):
                    self.value = value
                    self.node_id = node_id
                    self.parent = None
                    self.children = []
                    self.siblings = []
                    self.data = ['x'] * 100

                def add_child(self, child):
                    child.parent = self
                    self.children.append(child)

                def add_sibling(self, sibling):
                    self.siblings.append(sibling)
                    sibling.siblings.append(self)  # Circular sibling reference

            print("  • Creating complex circular reference structures...")
            for forest_id in range(10):
                # Create tree structures with circular references
                root_nodes = []

                for tree_id in range(5):
                    root = CircularNode(f"forest_{forest_id}_tree_{tree_id}", forest_id * 100 + tree_id)
                    root_nodes.append(root)

                    # Build tree with circular references
                    def build_tree(node, depth, max_depth):
                        if depth >= max_depth:
                            return

                        for i in range(3):  # 3 children per node
                            child = CircularNode(f"{node.value}_child_{i}", node.node_id * 10 + i)
                            node.add_child(child)

                            # Add siblings with circular references
                            if i > 0:
                                prev_child = node.children[i-1]
                                child.add_sibling(prev_child)

                            # Recurse
                            build_tree(child, depth + 1, max_depth)

                    build_tree(root, 0, 4)  # 4 levels deep

                # Create cross-tree circular references
                for i in range(len(root_nodes) - 1):
                    root_nodes[i].siblings.append(root_nodes[i + 1])
                    root_nodes[i + 1].siblings.append(root_nodes[i])

                circular_objects.extend(root_nodes)

                # Create weak references to track cleanup
                for node in root_nodes:
                    weak_refs.append(weakref.ref(node))
                    for child in node.children:
                        weak_refs.append(weakref.ref(child))

            print("  • Measuring memory before cleanup...")
            pre_cleanup_snapshot = self.get_memory_snapshot("circular_ref_before_cleanup")

            # Delete all references
            circular_objects.clear()

            print("  • Forcing garbage collection...")
            # Multiple GC passes to break circular references
            surviving_objects = []
            for i in range(5):
                collected = gc.collect()
                surviving = sum(1 for ref in weak_refs if ref() is not None)
                surviving_objects.append(surviving)
                print(f"    GC pass {i+1}: {collected} objects collected, {surviving} objects still referenced")
                time.sleep(0.1)

            final_snapshot = self.get_memory_snapshot("circular_ref_test_end")

            # Calculate metrics
            initial_memory = initial_snapshot['process_memory']['rss_mb']
            final_memory = final_snapshot['process_memory']['rss_mb']
            pre_cleanup_memory = pre_cleanup_snapshot['process_memory']['rss_mb']

            memory_leaked = final_memory - initial_memory
            peak_memory = pre_cleanup_memory - initial_memory
            cleanup_efficiency = (peak_memory - memory_leaked) / max(1, peak_memory)

            return {
                'initial_memory_mb': initial_memory,
                'peak_memory_mb': pre_cleanup_memory,
                'final_memory_mb': final_memory,
                'memory_leaked_mb': memory_leaked,
                'peak_memory_growth_mb': peak_memory,
                'cleanup_efficiency': cleanup_efficiency,
                'total_circular_objects': len(weak_refs),
                'gc_passes': 5,
                'surviving_objects_by_pass': surviving_objects,
                'circular_ref_leak_detected': surviving_objects[-1] > 0,
                'leak_detected': memory_leaked > 40  # 40MB threshold
            }

        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'leak_detected': True
            }

    def run_comprehensive_leak_detection(self) -> Dict[str, Any]:
        """Run all leak detection tests"""
        print("🔍 MEMORY LEAK DETECTION COMPREHENSIVE ANALYSIS")
        print("=" * 60)

        start_time = time.time()
        initial_snapshot = self.get_memory_snapshot("analysis_start")

        test_results = {}

        try:
            # Test 1: Recursive delegation leak
            test_results['recursive_delegation'] = self.test_recursive_delegation_leak()

            # Test 2: Web scraping leak
            test_results['web_scraping'] = self.test_web_scraping_leak()

            # Test 3: Resource monitor leak
            test_results['resource_monitor'] = self.test_resource_monitor_leak()

            # Test 4: Circular reference leak
            test_results['circular_references'] = self.test_circular_reference_leak()

        except Exception as e:
            print(f"\n❌ Critical error in leak detection: {e}")
            test_results['critical_error'] = str(e)

        end_time = time.time()
        final_snapshot = self.get_memory_snapshot("analysis_end")

        # Generate comprehensive report
        self.generate_leak_report(
            initial_snapshot,
            final_snapshot,
            test_results,
            end_time - start_time
        )

        return test_results

    def generate_leak_report(self, start_snapshot, end_snapshot, test_results, total_time):
        """Generate comprehensive leak detection report"""
        print("\n" + "=" * 60)
        print("🔍 MEMORY LEAK DETECTION REPORT")
        print("=" * 60)

        print(f"⏱️  Total Analysis Time: {total_time:.2f} seconds")
        print(f"📊 Start Memory: {start_snapshot.get('process_memory', {}).get('rss_mb', 0):.1f}MB")
        print(f"📊 End Memory: {end_snapshot.get('process_memory', {}).get('rss_mb', 0):.1f}MB")
        print(f"📊 Total Growth: {end_snapshot.get('process_memory', {}).get('rss_mb', 0) - start_snapshot.get('process_memory', {}).get('rss_mb', 0):.1f}MB")

        total_leaks_detected = 0
        critical_leaks = []

        for test_name, result in test_results.items():
            if 'error' in result:
                print(f"\n❌ {test_name.upper()}: ERROR - {result['error']}")
                continue

            print(f"\n🔍 {test_name.upper().replace('_', ' ')}:")

            if 'memory_leaked_mb' in result:
                leaked = result['memory_leaked_mb']
                leak_detected = result.get('leak_detected', False)

                print(f"   • Memory Leaked: {leaked:.1f}MB")
                print(f"   • Leak Detected: {'🚨 YES' if leak_detected else '✅ NO'}")

                if leak_detected:
                    total_leaks_detected += 1
                    if leaked > 100:  # Critical threshold
                        critical_leaks.append((test_name, leaked))
                        print(f"   • Status: 🔴 CRITICAL - Major leak detected!")
                    elif leaked > 50:
                        print(f"   • Status: 🟠 WARNING - Significant leak detected")
                    else:
                        print(f"   • Status: 🟡 MINOR - Minor leak detected")
                else:
                    print(f"   • Status: 🟢 CLEAN - No significant leak")

                # Show additional metrics
                if 'cleanup_effectiveness' in result:
                    effectiveness = result['cleanup_effectiveness']
                    print(f"   • Cleanup Effectiveness: {effectiveness:.1%}")

                if 'object_retention_rate' in result:
                    retention = result['object_retention_rate']
                    print(f"   • Object Retention Rate: {retention:.1%}")

            # Test-specific metrics
            if test_name == 'recursive_delegation':
                if 'max_depth_reached' in result:
                    print(f"   • Max Recursion Depth: {result['max_depth_reached']}")
                if 'delegations_created' in result:
                    print(f"   • Delegations Created: {result['delegations_created']:,}")

            elif test_name == 'web_scraping':
                if 'pages_scraped' in result:
                    print(f"   • Pages Scraped: {result['pages_scraped']:,}")
                if 'urls_visited' in result:
                    print(f"   • URLs Visited: {result['urls_visited']:,}")

            elif test_name == 'resource_monitor':
                if 'agents_registered' in result:
                    print(f"   • Agents Registered: {result['agents_registered']:,}")

            elif test_name == 'circular_references':
                if 'circular_ref_leak_detected' in result:
                    circ_leak = result['circular_ref_leak_detected']
                    print(f"   • Circular References Surviving: {'🚨 YES' if circ_leak else '✅ NO'}")
                if 'total_circular_objects' in result:
                    print(f"   • Total Circular Objects: {result['total_circular_objects']:,}")

        # Overall assessment
        print(f"\n" + "=" * 60)
        print("🎯 OVERALL LEAK ANALYSIS:")

        if critical_leaks:
            print(f"🔴 CRITICAL: {len(critical_leaks)} critical memory leaks detected:")
            for test_name, leaked in critical_leaks:
                print(f"   • {test_name}: {leaked:.1f}MB leaked")

        if total_leaks_detected == 0:
            print("✅ EXCELLENT: No memory leaks detected")
        elif total_leaks_detected <= 2:
            print("🟡 ACCEPTABLE: Minor memory issues detected")
        else:
            print("🔴 CONCERNING: Multiple memory leaks detected")

        # Save detailed results
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_time_seconds': total_time,
            'start_memory': start_snapshot,
            'end_memory': end_snapshot,
            'test_results': test_results,
            'total_leaks_detected': total_leaks_detected,
            'critical_leaks': critical_leaks,
            'memory_snapshots': self.snapshots
        }

        report_path = '/tmp/memory_leak_detection_report.json'
        try:
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"\n📁 Detailed report saved to: {report_path}")
        except Exception as e:
            print(f"\n⚠️  Could not save detailed report: {e}")

        print("=" * 60)

def main():
    """Main execution function"""
    os.chdir('/Users/docravikumar/Code/skill-test/Skill_Seekers')

    # Create and run leak detector
    detector = MemoryLeakDetector()
    results = detector.run_comprehensive_leak_detection()

    return results

if __name__ == "__main__":
    main()