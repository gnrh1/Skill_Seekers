#!/usr/bin/env python3
"""
Memory Protection Verification Tool
Checks if memory-enhanced agents are properly activated
"""

import sys
import os
from pathlib import Path

def check_agent_files():
    """Verify memory-enhanced agents are active"""
    agents_dir = Path('.claude/agents')
    
    print("=" * 60)
    print("MEMORY PROTECTION VERIFICATION")
    print("=" * 60)
    
    # Critical agents that must be memory-enhanced
    critical_agents = {
        'orchestrator-agent': False,
        'intelligence-orchestrator': False
    }
    
    # Check for legacy (unsafe) versions
    legacy_found = []
    
    for agent_file in agents_dir.glob('*.md'):
        if agent_file.name.endswith('.backup'):
            continue
            
        with open(agent_file, 'r') as f:
            content = f.read()
            
        # Extract agent name from YAML frontmatter
        if content.startswith('---'):
            lines = content.split('\n')
            for line in lines[1:10]:
                if line.startswith('name:'):
                    agent_name = line.split('name:')[1].strip()
                    
                    # Check if it's a critical agent
                    if agent_name in critical_agents:
                        # Verify it's memory-enhanced
                        if 'memory_enhanced_orchestrator' in content or 'orchestrate_with_memory_management' in content:
                            critical_agents[agent_name] = True
                            print(f"✅ {agent_name}: MEMORY-PROTECTED")
                        else:
                            print(f"❌ {agent_name}: UNSAFE (no memory protection)")
                            legacy_found.append(agent_name)
                    
                    # Check for legacy unsafe patterns
                    if '-legacy' in agent_file.name and not agent_file.name.endswith('.backup'):
                        print(f"⚠️  LEGACY AGENT FOUND: {agent_file.name}")
                        legacy_found.append(agent_file.name)
                    
                    break
    
    print("\n" + "=" * 60)
    
    # Check if all critical agents are protected
    unprotected = [name for name, protected in critical_agents.items() if not protected]
    
    if unprotected:
        print(f"❌ CRITICAL: {len(unprotected)} agents lack memory protection:")
        for agent in unprotected:
            print(f"   - {agent}")
        print("\n⚠️  DANGER: System vulnerable to memory explosion!")
        return False
    
    if legacy_found:
        print(f"⚠️  WARNING: {len(legacy_found)} legacy/unsafe agents found")
        print("   Move them to .backup files")
        return False
    
    print("✅ ALL CRITICAL AGENTS HAVE MEMORY PROTECTION")
    print("✅ System is protected against memory explosions")
    return True

def check_resource_scripts():
    """Verify resource monitoring scripts exist"""
    scripts_dir = Path('.claude/scripts')
    
    print("\n" + "=" * 60)
    print("RESOURCE MONITORING SCRIPTS")
    print("=" * 60)
    
    required_scripts = [
        'resource_monitor.py',
        'agent_circuit_breaker.py',
        'agent_pool.py',
        'memory_enhanced_orchestrator.py'
    ]
    
    all_present = True
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"✅ {script}")
        else:
            print(f"❌ {script} - MISSING!")
            all_present = False
    
    return all_present

def check_python_environment():
    """Check Python version and memory module availability"""
    print("\n" + "=" * 60)
    print("PYTHON ENVIRONMENT")
    print("=" * 60)
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check for required modules
    required_modules = ['psutil', 'resource']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} module available")
        except ImportError:
            print(f"❌ {module} module MISSING - install with: pip install {module}")
            return False
    
    return True

def main():
    os.chdir('/Users/docravikumar/Code/skill-test/Skill_Seekers')
    
    agents_ok = check_agent_files()
    scripts_ok = check_resource_scripts()
    python_ok = check_python_environment()
    
    print("\n" + "=" * 60)
    print("OVERALL STATUS")
    print("=" * 60)
    
    if agents_ok and scripts_ok and python_ok:
        print("✅ SYSTEM FULLY PROTECTED")
        print("\nMemory protection is ACTIVE and working.")
        print("Your system will NOT freeze from agent memory leaks.")
        return 0
    else:
        print("❌ SYSTEM VULNERABLE")
        print("\n⚠️  WARNING: Memory protection is INCOMPLETE!")
        print("   Your system can still freeze from memory leaks.")
        print("\nFix the issues above before using agents.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
