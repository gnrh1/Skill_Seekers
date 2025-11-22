# Create-Agent Command Compliance Fix Plan

## 🚨 Critical Compliance Issues Identified

Based on comprehensive evaluation of the `/create-agent` command, several critical compliance gaps with official Anthropic specifications have been identified that prevent generation of robust, valid agents.

---

## Issue 1: Tool Name Capitalization Mismatch

### Problem
The current system generates lowercase tool names but official Anthropic specification requires **capitalized tool names**.

**Current State (Non-Compliant):**
```python
# Generated in robust_agent_creator.py
["read_file", "write_file", "edit_file", "grep_search", "search_files", "bash", "task"]
```

**Required State (Compliant):**
```python
["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Task"]
```

### Impact
- Generated agents immediately fail Anthropic validation
- Inconsistent tool naming across agent files
- Validation errors prevent agent registration

### Root Cause
Missing systematic mapping between display names and internal tool identifiers.

---

## Issue 2: Non-Compliant YAML Field Generation

### Problem
The system generates extra YAML fields beyond the 4 official Anthropic fields.

**Current State (Non-Compliant):**
```yaml
---
name: custom-agent
description: Agent description
model: sonnet
tools: read_file, write_file, edit_file
framework: react                    # ❌ NON-COMPLIANT
methodology: T.E.S.T.             # ❌ NON-COMPLIANT
specialization: testing            # ❌ NON-COMPLIANT
capabilities: ["unit", "integration"] # ❌ NON-COMPLIANT
---
```

**Required State (Compliant):**
```yaml
---
name: custom-agent
description: Agent description
model: sonnet
tools: Read, Write, Edit, Grep, Glob, Bash, Task
---
```

### Impact
- Violates strict Anthropic agent specification
- Generated agents are rejected by validation systems
- Creates incompatible agent files

---

## Issue 3: Missing Tool Name Standardization

### Problem
No systematic validation or mapping exists to ensure consistent tool name usage.

### Current Inconsistencies
- Test suite generates lowercase names
- Agent files have mixed case
- No validation during agent creation
- Manual corrections required for compliance

---

## 🔧 Comprehensive Remediation Plan

### Phase 1: Critical Tool Name Standardization

**Objective**: Fix immediate validation failures by ensuring consistent tool naming.

#### Task 1.1: Create Definitive Tool Mapping
```python
# Add to robust_agent_creator.py
TOOL_NAME_MAPPING = {
    "read_file": "Read",
    "write_file": "Write",
    "edit_file": "Edit",
    "grep_search": "Grep",
    "search_files": "Glob",
    "bash": "Bash",
    "task": "Task"
}

def standardize_tool_names(tools):
    """Convert display names to official capitalized names."""
    return [TOOL_NAME_MAPPING.get(tool, tool.title()) for tool in tools]
```

#### Task 1.2: Update Agent Creation Logic
```python
# In robust_agent_creator.py
def create_agent_with_standardized_tools(config):
    """Create agent with properly capitalized tool names."""
    standardized_tools = standardize_tool_names(config['tools'])

    yaml_content = f"""---
name: {config['name']}
description: {config['description']}
model: {config['model']}
tools: {', '.join(standardized_tools)}
---

# Agent content follows...
"""
    return yaml_content
```

#### Task 1.3: Fix Existing Agent Files
- Scan all `.claude/agents/*.md` files
- Identify lowercase tool names in YAML frontmatter
- Convert to capitalized versions
- Validate updated compliance

#### Task 1.4: Update Test Suite
- Modify test generation to use standardized tool names
- Add validation tests for tool name compliance
- Ensure all generated agents use correct capitalization

---

### Phase 2: YAML Compliance Enforcement

**Objective**: Restrict YAML generation to official Anthropic specification only.

#### Task 2.1: Restrict to Official Fields
```python
# Define allowed fields constant
OFFICIAL_YAML_FIELDS = ['name', 'description', 'model', 'tools']

def validate_yaml_fields(yaml_dict):
    """Ensure YAML contains only official fields."""
    for field in yaml_dict.keys():
        if field not in OFFICIAL_YAML_FIELDS:
            raise ValueError(f"Non-compliant field '{field}'. Only {OFFICIAL_YAML_FIELDS} allowed")
    return yaml_dict
```

#### Task 2.2: Remove Non-Compliant Field Generation
- Remove `framework`, `methodology`, `specialization`, `capabilities` field generation
- Update agent templates to use only official fields
- Delete non-compliant field generation logic

#### Task 2.3: Add Pre-Compliance Validation
```python
def validate_agent_before_creation(config):
    """Validate agent configuration before file creation."""
    required_fields = ['name', 'description', 'model', 'tools']

    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")

    # Validate tool names
    standardized_tools = standardize_tool_names(config['tools'])

    # Validate model
    if config['model'] not in ['opus', 'sonnet']:
        raise ValueError(f"Invalid model: {config['model']}. Use 'opus' or 'sonnet'")

    return {
        'name': config['name'],
        'description': config['description'],
        'model': config['model'],
        'tools': standardized_tools
    }
```

---

### Phase 3: Integration with Tool Enhancement Analysis

**Objective**: Ensure create-agent produces agents ready for the CTO's recommended tool enhancements.

#### Task 3.1: Incorporate CTO's Tool Recommendations
Based on the CTO's analysis, implement recommended base tool sets:

```python
BASE_TOOL_SET = ['Read', 'Write', 'Grep', 'Bash', 'Task']  # All agents get this
ENHANCED_TOOLS = {
    'analysis': ['Glob', 'WebFetch'],
    'interaction': ['AskUserQuestion'],
    'performance': ['BashOutput', 'KillShell'],
    'testing': ['NotebookEdit'],
    'workflow': ['TodoWrite']
}
```

#### Task 3.2: Smart Tool Recommendation
```python
def recommend_tools_for_agent_type(agent_type, description):
    """Recommend tools based on agent type and description analysis."""
    tools = BASE_TOOL_SET.copy()

    # Analysis patterns for tool recommendation
    if any(keyword in description.lower() for keyword in ['analyze', 'audit', 'review']):
        tools.extend(ENHANCED_TOOLS['analysis'])

    if any(keyword in description.lower() for keyword in ['user', 'feedback', 'collaborate']):
        tools.extend(ENHANCED_TOOLS['interaction'])

    if any(keyword in description.lower() for keyword in ['performance', 'optimize', 'profiling']):
        tools.extend(ENHANCED_TOOLS['performance'])

    if any(keyword in description.lower() for keyword in ['test', 'testing', 'coverage']):
        tools.extend(ENHANCED_TOOLS['testing'])

    # Add TodoWrite to all agents per CTO recommendation
    tools.append('TodoWrite')

    return sorted(list(set(tools)))  # Remove duplicates, sort alphabetically
```

#### Task 3.3: Enhanced Agent Creation Workflow
```python
def create_enhanced_agent(config):
    """Create agent with CTO-recommended tool sets."""
    # Validate base configuration
    base_config = validate_agent_before_creation(config)

    # Recommend additional tools based on analysis
    recommended_tools = recommend_tools_for_agent_type(
        config.get('type', ''),
        base_config['description']
    )

    # Merge with user-specified tools
    final_tools = sorted(list(set(
        base_config['tools'] + recommended_tools
    )))

    # Create final compliant agent
    enhanced_config = {
        **base_config,
        'tools': final_tools
    }

    return enhanced_config
```

---

### Phase 4: Enhanced Validation & Testing

#### Task 4.1: YAML Compliance Validator
```python
import yaml
from pathlib import Path

class AgentYAMLValidator:
    """Comprehensive YAML compliance validator for agents."""

    OFFICIAL_FIELDS = {'name', 'description', 'model', 'tools'}
    VALID_MODELS = {'opus', 'sonnet'}
    VALID_TOOLS = {
        'Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash', 'Task',
        'TodoWrite', 'WebFetch', 'WebSearch', 'AskUserQuestion',
        'NotebookEdit', 'BashOutput', 'KillShell'
    }

    def validate_agent_file(self, file_path: Path):
        """Validate agent file for compliance."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract YAML frontmatter
            if not content.startswith('---'):
                raise ValueError("Agent file must start with YAML frontmatter")

            parts = content.split('---', 2)
            if len(parts) < 2:
                raise ValueError("Agent file missing YAML frontmatter separator")

            yaml_content = parts[1].strip()
            yaml_dict = yaml.safe_load(yaml_content)

            return self.validate_yaml_structure(yaml_dict)

        except Exception as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")

    def validate_yaml_structure(self, yaml_dict):
        """Validate YAML dictionary compliance."""
        errors = []

        # Check for required fields
        required_fields = ['name', 'description', 'model', 'tools']
        for field in required_fields:
            if field not in yaml_dict:
                errors.append(f"Missing required field: {field}")

        # Check for prohibited fields
        for field in yaml_dict:
            if field not in self.OFFICIAL_FIELDS:
                errors.append(f"Non-compliant field: {field}. Only {self.OFFICIAL_FIELDS} allowed")

        # Validate model
        if 'model' in yaml_dict and yaml_dict['model'] not in self.VALID_MODELS:
            errors.append(f"Invalid model: {yaml_dict['model']}. Use {self.VALID_MODELS}")

        # Validate tools
        if 'tools' in yaml_dict:
            tools = yaml_dict['tools']
            if isinstance(tools, str):
                tools = [t.strip() for t in tools.split(',')]

            for tool in tools:
                if tool not in self.VALID_TOOLS:
                    errors.append(f"Invalid tool: {tool}. Use one of {self.VALID_TOOLS}")

        if errors:
            raise ValueError("YAML validation errors:\n" + "\n".join(f"- {error}" for error in errors))

        return {
            'status': 'compliant',
            'score': 100,
            'warnings': []
        }
```

#### Task 4.2: End-to-End Testing
```python
def test_agent_creation_pipeline():
    """Test complete agent creation pipeline."""
    test_configs = [
        {
            'name': 'test-security-analyst',
            'description': 'Security analysis specialist',
            'model': 'sonnet',
            'type': 'security'
        },
        {
            'name': 'test-performance-auditor',
            'description': 'Performance optimization specialist',
            'model': 'opus',
            'type': 'performance'
        }
    ]

    results = []

    for config in test_configs:
        try:
            # Test enhanced agent creation
            enhanced_config = create_enhanced_agent(config)

            # Test YAML generation
            yaml_content = generate_agent_yaml(enhanced_config)

            # Test validation
            validator = AgentYAMLValidator()
            validation_result = validator.validate_yaml_structure(enhanced_config)

            results.append({
                'agent': config['name'],
                'status': 'success',
                'tools_count': len(enhanced_config['tools']),
                'validation': validation_result
            })

        except Exception as e:
            results.append({
                'agent': config['name'],
                'status': 'failed',
                'error': str(e),
                'validation': None
            })

    return results
```

---

## 📊 Files to Modify

### Core System Files
1. **`.claude/scripts/robust_agent_creator.py`**
   - Add tool name standardization
   - Implement YAML compliance validation
   - Integrate CTO's tool recommendations
   - Update agent creation workflow

2. **Test Suite Files**
   - Update agent creation tests
   - Add compliance validation tests
   - Remove non-compliant field generation tests
   - Add tool name standardization tests

3. **Agent Templates and Configuration**
   - Update templates to use only official fields
   - Add tool recommendation logic
   - Remove non-compliant field templates

### Potential Cleanup Files
1. **Existing Agent Files** (11 files in `.claude/agents/`)
   - Fix any lowercase tool names in YAML frontmatter
   - Remove any non-compliant fields
   - Validate updated compliance

2. **Test Agent Files**
   - Update test-generated agents to be compliant
   - Remove non-compliant test agents
   - Update test data to use proper tool names

---

## 🎯 Expected Outcomes

### Compliance Metrics (Target: 100%)
- **100%** YAML field compliance (only 4 official fields)
- **100%** tool name capitalization compliance
- **100%** agent generation success rate
- **0** validation failures due to specification violations

### Enhanced Capabilities (Target: CTO Integration)
- Agents generated ready for tool enhancement
- Seamless integration with CTO's 38 tool additions
- Consistent agent file generation across system
- Intelligent tool recommendation based on agent type
- Robust error prevention and validation

### System Quality Improvements
- Pre-creation validation prevents invalid agents
- Comprehensive error reporting for debugging
- Consistent formatting and structure
- Integration testing ensures reliability
- Documentation and validation for maintenance

---

## 🚀 Implementation Timeline

### Week 1: Critical Fixes
- **Phase 1**: Tool name standardization (Critical)
- **Phase 2**: YAML compliance enforcement (Critical)

### Week 2: Integration & Testing
- **Phase 3**: Tool enhancement integration (High)
- **Phase 4**: Enhanced validation & testing (Medium)

### Success Criteria
1. All generated agents pass YAML validation
2. Tool names are consistently capitalized
3. Integration with CTO's tool recommendations works seamlessly
4. End-to-end testing shows 100% success rate
5. System prevents non-compliant agent creation

This plan will transform the `/create-agent` command from a potentially non-compliant agent generator into a robust, specification-compliant system that produces agents ready for the comprehensive tool enhancements recommended by the CTO's analysis.