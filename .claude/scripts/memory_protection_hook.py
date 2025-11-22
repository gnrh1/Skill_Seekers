#!/usr/bin/env python3
"""
Memory Protection Hook for Task Tool
Intercepts Task tool calls and enforces memory limits before agent spawn
Logs agent type for full traceability
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Configure logging
log_dir = os.path.join(os.path.dirname(script_dir), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'memory_protection_hook.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_agent_type():
    """Extract agent/subagent type from Task tool call parameters"""
    agent_type = "unknown"
    
    # Try to get from environment variables (Claude Code passes tool params here)
    if 'CLAUDE_TOOL_PARAMS' in os.environ:
        try:
            params = json.loads(os.environ['CLAUDE_TOOL_PARAMS'])
            agent_type = params.get('subagent_type', 'unknown')
        except (json.JSONDecodeError, AttributeError):
            pass
    
    # Try to get from stdin (alternative method)
    if agent_type == "unknown" and not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read()
            if stdin_data:
                params = json.loads(stdin_data)
                agent_type = params.get('subagent_type', 'unknown')
        except (json.JSONDecodeError, ValueError):
            pass
    
    # Try to get from sys.argv
    if agent_type == "unknown":
        for arg in sys.argv[1:]:
            if 'subagent_type' in arg or 'agent_type' in arg:
                try:
                    # Handle formats like: key=value or {"key": "value"}
                    if '=' in arg:
                        parts = arg.split('=')
                        if len(parts) == 2:
                            agent_type = parts[1].strip('"\'')
                    elif '{' in arg:
                        parsed = json.loads(arg)
                        agent_type = parsed.get('subagent_type', parsed.get('agent_type', 'unknown'))
                except (json.JSONDecodeError, ValueError, IndexError):
                    pass
    
    return agent_type

def check_memory_before_task():
    """Check if system has resources for new Task tool call"""
    try:
        from resource_monitor import check_resources_before_agent_spawn, register_agent
        
        # Extract agent type for traceability
        agent_type = extract_agent_type()
        
        # Check resources
        resources_ok, msg = check_resources_before_agent_spawn()
        
        timestamp = datetime.now().isoformat()
        
        if not resources_ok:
            logger.warning(f"[{timestamp}] Task blocked for @{agent_type}: {msg}")
            print(json.dumps({
                "allowed": False,
                "reason": msg,
                "agent_type": agent_type,
                "timestamp": timestamp
            }))
            sys.exit(1)  # Block the tool call
        
        # Register this agent spawn
        agent_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        register_agent(agent_id, agent_type)
        
        logger.info(f"[{timestamp}] Task allowed for @{agent_type}: {msg} (Agent ID: {agent_id})")
        print(json.dumps({
            "allowed": True,
            "reason": msg,
            "agent_type": agent_type,
            "agent_id": agent_id,
            "timestamp": timestamp
        }))
        sys.exit(0)  # Allow the tool call
        
    except ImportError as e:
        logger.error(f"Failed to import resource_monitor: {e}")
        # Allow by default if monitoring system unavailable
        agent_type = extract_agent_type()
        print(json.dumps({
            "allowed": True,
            "reason": "Memory monitoring unavailable - allowing by default",
            "agent_type": agent_type,
            "error": str(e)
        }))
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error checking resources: {e}")
        # Allow by default on error to avoid blocking all agents
        agent_type = extract_agent_type()
        print(json.dumps({
            "allowed": True,
            "reason": "Error checking resources - allowing by default",
            "agent_type": agent_type,
            "error": str(e)
        }))
        sys.exit(0)

if __name__ == "__main__":
    check_memory_before_task()