#!/usr/bin/env python3
"""Validate command execution safety before running.

This script is called by PreToolUse hooks to validate commands
before execution, preventing common security and environment issues.
"""

import sys
import re
import os
from typing import Dict, List

def validate_command(command: str) -> Dict[str, str]:
    """Validate command safety.
    
    Checks for:
    - Secret patterns (API keys, tokens)
    - Python without virtual environment
    - Destructive operations
    - Other dangerous patterns
    
    Args:
        command: The command to validate
        
    Returns:
        Dict with:
            - decision: 'approve', 'block', or 'warn'
            - reason: Explanation of decision
            - suggestion: How to fix if blocked/warned (optional)
    """
    # Check for secret patterns
    secret_result = check_secrets(command)
    if secret_result['decision'] != 'approve':
        return secret_result
    
    # Check for Python without venv
    venv_result = check_virtual_environment(command)
    if venv_result['decision'] != 'approve':
        return venv_result
    
    # Check for destructive operations
    destructive_result = check_destructive_ops(command)
    if destructive_result['decision'] != 'approve':
        return destructive_result
    
    # All checks passed
    return {
        'decision': 'approve',
        'reason': 'Command validated successfully'
    }

def check_secrets(command: str) -> Dict[str, str]:
    """Check for secrets in command.
    
    Blocks commands containing:
    - Anthropic API keys (sk-ant-...)
    - GitHub tokens (ghp_...)
    - Environment variable assignments with secrets
    """
    secret_patterns = [
        (r'sk-ant-[a-zA-Z0-9-]{10,}', 'Anthropic API key'),  # Relaxed length requirement
        (r'ghp_[a-zA-Z0-9]{20,}', 'GitHub personal access token'),  # Relaxed length
        (r'ANTHROPIC_API_KEY\s*=', 'API key environment variable assignment'),
        (r'GITHUB_TOKEN\s*=', 'GitHub token environment variable assignment'),
    ]
    
    for pattern, secret_type in secret_patterns:
        if re.search(pattern, command):
            return {
                'decision': 'block',
                'reason': f'Command contains potential secret: {secret_type}',
                'suggestion': 'Use environment variables instead. Set secrets with: export VAR_NAME=value'
            }
    
    return {'decision': 'approve', 'reason': 'No secrets detected'}

def check_virtual_environment(command: str) -> Dict[str, str]:
    """Check if Python command uses virtual environment.
    
    Warns if:
    - Command uses python/python3
    - Command doesn't reference venv/bin
    - Not already in virtual environment
    """
    # Skip check if already in venv
    if os.getenv('VIRTUAL_ENV'):
        return {'decision': 'approve', 'reason': 'Virtual environment already active'}
    
    # Check for Python commands
    python_patterns = [
        r'\bpython\b',
        r'\bpython3\b',
        r'\bpip\b',
        r'\bpip3\b'
    ]
    
    has_python = any(re.search(pattern, command) for pattern in python_patterns)
    has_venv = 'venv/bin' in command or 'source venv/bin/activate' in command
    
    if has_python and not has_venv:
        return {
            'decision': 'warn',
            'reason': 'Python command without virtual environment activation',
            'suggestion': 'Prefix command with: source venv/bin/activate && '
        }
    
    return {'decision': 'approve', 'reason': 'Virtual environment check passed'}

def check_destructive_ops(command: str) -> Dict[str, str]:
    """Check for destructive operations.
    
    Warns about:
    - Recursive deletes (rm -rf)
    - Force git operations (git push --force)
    - Database drops (DROP TABLE, DROP DATABASE)
    - System modifications (chmod 777, chown)
    """
    destructive_patterns = [
        (r'rm\s+-rf\s+/', 'Recursive delete from root'),
        (r'rm\s+-rf\s+\*', 'Recursive delete with wildcard'),
        (r'git\s+push\s+.*--force', 'Force git push'),
        (r'DROP\s+(TABLE|DATABASE)', 'Database drop operation'),
        (r'chmod\s+777', 'Overly permissive file permissions'),
        (r'sudo\s+rm', 'Sudo remove operation'),
    ]
    
    for pattern, op_type in destructive_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return {
                'decision': 'warn',
                'reason': f'Destructive operation detected: {op_type}',
                'suggestion': 'Confirm this operation is intended and safe'
            }
    
    return {'decision': 'approve', 'reason': 'No destructive operations detected'}

def format_output(result: Dict[str, str]) -> None:
    """Format and print validation result.
    
    Args:
        result: Validation result dict
    """
    decision = result['decision']
    reason = result['reason']
    suggestion = result.get('suggestion')
    
    if decision == 'block':
        print(f"❌ BLOCKED: {reason}", file=sys.stderr)
        if suggestion:
            print(f"💡 Suggestion: {suggestion}", file=sys.stderr)
    elif decision == 'warn':
        print(f"⚠️  WARNING: {reason}", file=sys.stderr)
        if suggestion:
            print(f"💡 Suggestion: {suggestion}", file=sys.stderr)
    # Approve is silent (no output needed)

def main():
    """Main entry point for command validation."""
    # Read command from stdin
    command = sys.stdin.read().strip()
    
    if not command:
        # Empty command, nothing to validate
        sys.exit(0)
    
    # Validate command
    result = validate_command(command)
    
    # Output result
    format_output(result)
    
    # Exit with appropriate code
    if result['decision'] == 'block':
        sys.exit(1)  # Block execution
    elif result['decision'] == 'warn':
        sys.exit(0)  # Allow execution but with warning
    else:
        sys.exit(0)  # Approve execution

if __name__ == '__main__':
    main()
