#!/usr/bin/env python3
"""
Robust Agent Creation Pipeline
Bulletproof system for creating agents with atomic operations, validation, and error handling.
Addresses critical engineering failures in the original /create-agent implementation.
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, UTC

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/agent_creation.log'),
        logging.StreamHandler()
    ]
)
llogger = logging.getLogger(__name__)

# Official Anthropic Tool Mapping (Phase 1-4 complete toolkit)
OFFICIAL_TOOL_MAPPING = {
    # Core file operations
    "read_file": "Read",
    "write_file": "Write",
    "edit_file": "Edit",
    "grep_search": "Grep",
    "search_files": "Glob",
    "bash": "Bash",
    "task": "Task",
    "list_dir": "Read",  # Map to Read as alternative
    
    # Phase 1: Universal workflow tracking
    "todo_write": "TodoWrite",
    "todowrite": "TodoWrite",
    
    # Phase 2: External intelligence
    "web_fetch": "WebFetch",
    "webfetch": "WebFetch",
    "web_search": "WebSearch",
    "websearch": "WebSearch",
    
    # Phase 3: Human feedback loop
    "ask_user_question": "AskUserQuestion",
    "askuserquestion": "AskUserQuestion",
    
    # Phase 4: Specialized tools
    "notebook_edit": "NotebookEdit",
    "notebookedit": "NotebookEdit",
    "bash_output": "BashOutput",
    "bashoutput": "BashOutput",
    "kill_shell": "KillShell",
    "killshell": "KillShell"
}

# Official Anthropic YAML fields (strict compliance)
OFFICIAL_YAML_FIELDS = ['name', 'description', 'model', 'tools']

# Valid tool names (lowercase for validation)
VALID_TOOL_NAMES = list(OFFICIAL_TOOL_MAPPING.keys())

# Capitalized tool names for YAML output
CAPITALIZED_TOOLS = list(set(OFFICIAL_TOOL_MAPPING.values()))

@dataclass
class AgentCreationRequest:
    """Atomic agent creation request with validation."""
    name: str
    agent_type: str
    description: str
    model: str
    tools: list
    delegates: list
    tags: list
    framework: str
    content: str
    target_directory: str = ".claude/agents"

@dataclass
class CreationResult:
    """Result of agent creation with complete status tracking."""
    success: bool
    agent_path: Optional[str] = None
    error_message: Optional[str] = None
    creation_time: Optional[datetime] = None
    content_hash: Optional[str] = None
    validation_errors: list = None

class AgentValidationError(Exception):
    """Specific error for agent validation failures."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for {field}: {message}")

class AgentCreationError(Exception):
    """Specific error for agent creation failures."""
    def __init__(self, phase: str, details: str, recoverable: bool = False):
        self.phase = phase
        self.details = details
        self.recoverable = recoverable
        super().__init__(f"Agent creation failed in {phase}: {details}")

def standardize_tools(tools: list) -> list:
    """
    Convert tool names to official Anthropic capitalized format.
    Supports both lowercase and mixed-case input.
    
    Args:
        tools: List of tool names (any case)
    
    Returns:
        List of properly capitalized tool names
    
    Examples:
        ['read_file', 'write_file'] -> ['Read', 'Write']
        ['Read', 'write_file', 'BASH'] -> ['Read', 'Write', 'Bash']
    """
    standardized = []
    for tool in tools:
        # Normalize to lowercase with underscores
        normalized = tool.lower().replace('-', '_')
        # Map to official capitalized name
        if normalized in OFFICIAL_TOOL_MAPPING:
            standardized.append(OFFICIAL_TOOL_MAPPING[normalized])
        else:
            # If not in mapping, try to capitalize properly
            # Check if already in capitalized form
            if tool in CAPITALIZED_TOOLS:
                standardized.append(tool)
            else:
                # Default: title case
                standardized.append(tool.title())
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for tool in standardized:
        if tool not in seen:
            seen.add(tool)
            result.append(tool)
    
    return result

class RobustAgentCreator:
    """
    Bulletproof agent creation system with atomic operations and comprehensive validation.
    Addresses every engineering failure identified in the meta-analysis.
    """

    def __init__(self):
        self.agents_dir = Path(".claude/agents")
        self.registry_path = Path(".claude/skills/agent-scaffolding-toolkit/assets/agent_registry.json")
        self.logs_dir = Path(".claude/logs")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist with proper permissions."""
        try:
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            self.logs_dir.mkdir(parents=True, exist_ok=True)

            # Verify write permissions
            test_file = self.agents_dir / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()

            logger.info("Directory structure and permissions verified")
        except Exception as e:
            raise AgentCreationError("initialization", f"Directory setup failed: {e}")

    def validate_agent_request(self, request: AgentCreationRequest) -> None:
        """Comprehensive input validation - Layer 1 validation."""
        logger.info(f"Starting validation for agent: {request.name}")

        # Name validation
        if not request.name or not request.name.strip():
            raise AgentValidationError("name", "Agent name cannot be empty")

        if not request.name.replace("-", "").replace("_", "").isalnum():
            raise AgentValidationError("name", "Agent name must contain only alphanumeric characters, hyphens, and underscores")

        # Check for existing agent
        agent_path = self.agents_dir / f"{request.name}.md"
        if agent_path.exists():
            raise AgentValidationError("name", f"Agent '{request.name}' already exists at {agent_path}")

        # Content validation
        if not request.content or len(request.content.strip()) < 100:
            raise AgentValidationError("content", "Agent content must be at least 100 characters")

        # Required sections validation
        required_sections = ["# ", "## Agent Identity", "## Core Purpose", "## Integration with Existing Agent Ecosystem"]
        missing_sections = [section for section in required_sections if section not in request.content]
        if missing_sections:
            raise AgentValidationError("content", f"Missing required sections: {missing_sections}")

        # Tool validation
        valid_tools = VALID_TOOL_NAMES + CAPITALIZED_TOOLS  # Accept both formats
        invalid_tools = [tool for tool in request.tools if tool not in valid_tools]
        if invalid_tools:
            raise AgentValidationError("tools", f"Invalid tools: {invalid_tools}. Valid tools: {CAPITALIZED_TOOLS}")

        logger.info("Input validation passed")

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash for content verification."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def normalize_content_for_hash(self, content: str) -> str:
        """Normalize content by removing timestamps for consistent hashing."""
        lines = content.split('\n')
        normalized_lines = []

        for line in lines:
            # Remove timestamp lines from frontmatter
            if 'created:' in line and 'T' in line and 'Z' in line:
                # Replace with placeholder for consistent hashing
                line = line[:line.find(':') + 1] + ' TIMESTAMP_PLACEHOLDER'
            normalized_lines.append(line)

        return '\n'.join(normalized_lines)

    def create_agent_file(self, request: AgentCreationRequest) -> Tuple[str, str]:
        """Atomically create agent file with proper permissions - Layer 2 persistence."""
        logger.info(f"Creating agent file: {request.name}")

        try:
            agent_path = self.agents_dir / f"{request.name}.md"

            # Add frontmatter if not present
            if not request.content.startswith('---'):
                # Standardize tools to official capitalized format
                standardized_tools = standardize_tools(request.tools)
                
                # Generate compliant YAML frontmatter (4 fields only per Anthropic spec)
                frontmatter = f"""---
name: {request.name}
description: {request.description}
model: {request.model}
tools: {', '.join(standardized_tools)}
---

"""
                content_with_frontmatter = frontmatter + request.content
            else:
                content_with_frontmatter = request.content

            # Generate hash of normalized content (without timestamps)
            content_hash = self.generate_content_hash(self.normalize_content_for_hash(content_with_frontmatter))

            # Atomic write operation
            temp_path = agent_path.with_suffix('.tmp')
            temp_path.write_text(content_with_frontmatter, encoding='utf-8')

            # Verify write operation
            if not temp_path.exists():
                raise AgentCreationError("persistence", f"Temporary file creation failed: {temp_path}")

            written_content = temp_path.read_text(encoding='utf-8')
            if len(written_content) != len(content_with_frontmatter):
                raise AgentCreationError("persistence", "File content mismatch after write")

            # Atomic move
            temp_path.rename(agent_path)

            # Verify final file
            if not agent_path.exists():
                raise AgentCreationError("persistence", f"Final agent file not found: {agent_path}")

            logger.info(f"Agent file created successfully: {agent_path}")
            return str(agent_path), content_hash

        except Exception as e:
            # Cleanup on failure
            temp_path = self.agents_dir / f"{request.name}.tmp"
            if temp_path.exists():
                temp_path.unlink()
            raise AgentCreationError("persistence", f"File creation failed: {e}")

    def verify_agent_creation(self, agent_path: str, expected_hash: str) -> None:
        """Comprehensive verification of created agent - Layer 3 validation."""
        logger.info(f"Verifying agent creation: {agent_path}")

        try:
            path_obj = Path(agent_path)

            # Existence verification
            if not path_obj.exists():
                raise AgentCreationError("verification", f"Agent file does not exist: {agent_path}")

            # Content verification
            content = path_obj.read_text(encoding='utf-8')
            if not content.strip():
                raise AgentCreationError("verification", "Agent file is empty")

            # Hash verification (using normalized content)
            actual_hash = self.generate_content_hash(self.normalize_content_for_hash(content))
            if actual_hash != expected_hash:
                raise AgentCreationError("verification",
                    f"Content hash mismatch. Expected: {expected_hash[:16]}..., Got: {actual_hash[:16]}...")

            # Structure verification
            required_patterns = ["# ", "## ", "### ", "```", "**"]
            missing_patterns = [pattern for pattern in required_patterns if pattern not in content]
            if missing_patterns:
                raise AgentCreationError("verification", f"Missing structural patterns: {missing_patterns}")

            # YAML frontmatter verification
            if content.startswith('---'):
                frontmatter_end = content.find('---', 3)
                if frontmatter_end == -1:
                    raise AgentCreationError("verification", "Invalid YAML frontmatter structure")

                frontmatter = content[3:frontmatter_end].strip()
                required_fields = ["name", "description", "model"]
                for field in required_fields:
                    if f"{field}:" not in frontmatter:
                        raise AgentCreationError("verification", f"Missing frontmatter field: {field}")

            logger.info("Agent creation verification passed")

        except Exception as e:
            raise AgentCreationError("verification", f"Verification failed: {e}")

    def update_agent_registry(self, request: AgentCreationRequest) -> None:
        """Update agent registry with new agent - Layer 4 system validation."""
        logger.info("Updating agent registry")

        try:
            # Load existing registry
            if self.registry_path.exists():
                registry = json.loads(self.registry_path.read_text(encoding='utf-8'))
                # Ensure registry has required structure
                if "agents" not in registry:
                    registry["agents"] = []
                if not isinstance(registry["agents"], list):
                    # Convert dict format to list format
                    if isinstance(registry["agents"], dict):
                        registry["agents"] = [registry["agents"][name] for name in registry["agents"]]
                    else:
                        registry["agents"] = []
            else:
                registry = {
                    "version": "1.0",
                    "generated_at": datetime.now(UTC).isoformat(),
                    "agents": []
                }

            # Create new agent entry matching registry format
            agent_info = {
                "name": request.name,
                "file_path": os.path.abspath(f".claude/agents/{request.name}.md"),
                "type": request.agent_type,
                "description": request.description,
                "tools": request.tools,
                "delegates_to": request.delegates,
                "updated_at": datetime.now(UTC).isoformat(),
                "created_at": datetime.now(UTC).isoformat(),
                "version": "1.0",
                "usage_stats": {
                    "invocation_count": 0,
                    "success_rate": 1.0
                }
            }

            # Add new agent to registry list
            registry["agents"].append(agent_info)
            registry["generated_at"] = datetime.now(UTC).isoformat()

            # Atomic registry update
            temp_registry = self.registry_path.with_suffix('.tmp')
            temp_registry.write_text(json.dumps(registry, indent=2), encoding='utf-8')
            temp_registry.rename(self.registry_path)

            logger.info("Agent registry updated successfully")

        except Exception as e:
            raise AgentCreationError("registry_update", f"Registry update failed: {e}")

    def create_agent(self, request: AgentCreationRequest) -> CreationResult:
        """
        Complete atomic agent creation pipeline with comprehensive validation.
        This method fixes ALL engineering failures identified in the meta-analysis.
        """
        creation_start_time = datetime.now(UTC)
        logger.info(f"Starting atomic agent creation for: {request.name}")

        try:
            # Phase 1: Input Validation (Layer 1)
            self.validate_agent_request(request)

            # Phase 2: Atomic File Creation (Layer 2)
            agent_path, content_hash = self.create_agent_file(request)

            # Phase 3: Comprehensive Verification (Layer 3)
            self.verify_agent_creation(agent_path, content_hash)

            # Phase 4: System Integration (Layer 4)
            self.update_agent_registry(request)

            # Success
            creation_time = datetime.now(UTC)
            duration = (creation_time - creation_start_time).total_seconds()

            logger.info(f"Agent '{request.name}' created successfully in {duration:.2f}s")

            return CreationResult(
                success=True,
                agent_path=agent_path,
                creation_time=creation_time,
                content_hash=content_hash,
                validation_errors=[]
            )

        except (AgentValidationError, AgentCreationError) as e:
            # Comprehensive error handling with cleanup
            logger.error(f"Agent creation failed: {e}")

            # Cleanup partial operations
            try:
                agent_file = self.agents_dir / f"{request.name}.md"
                if agent_file.exists():
                    agent_file.unlink()

                temp_file = self.agents_dir / f"{request.name}.tmp"
                if temp_file.exists():
                    temp_file.unlink()

            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")

            return CreationResult(
                success=False,
                error_message=str(e),
                creation_time=datetime.now(UTC),
                validation_errors=[str(e)]
            )

        except Exception as e:
            # Catch-all for unexpected failures
            logger.error(f"Unexpected agent creation failure: {e}")

            return CreationResult(
                success=False,
                error_message=f"Unexpected error: {e}",
                creation_time=datetime.now(UTC),
                validation_errors=[f"System error: {e}"]
            )

def main():
    """CLI interface for robust agent creation."""
    if len(sys.argv) < 2:
        print("Usage: python3 robust_agent_creator.py <agent_config.json>")
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        request = AgentCreationRequest(**config)
        creator = RobustAgentCreator()
        result = creator.create_agent(request)

        if result.success:
            print(f"✅ Agent created successfully!")
            print(f"📍 Location: {result.agent_path}")
            print(f"⏰ Created: {result.creation_time}")
            print(f"🔐 Hash: {result.content_hash[:16]}...")
        else:
            print(f"❌ Agent creation failed!")
            print(f"🚫 Error: {result.error_message}")
            for error in result.validation_errors or []:
                print(f"   • {error}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()