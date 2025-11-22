---
name: validate-droids
description: Comprehensive validation of Factory Droid configuration, YAML syntax, and structure. Checks AGENTS.md, .droid.yaml, droids, commands, and memory files.
parameters:
  - name: fix
    type: boolean
    default: false
    description: Automatically fix common issues (not yet implemented)
  - name: verbose
    type: boolean
    default: false
    description: Show detailed validation output with per-file results
---

# /validate-droids: Factory Droid Validation System

Validates Factory Droid configuration (AGENTS.md, .droid.yaml, droids/*.md, commands/*.md, memory/*.md).

## Purpose

Ensures Factory Droid configuration files are well-formed, syntactically correct, and follow best practices. Adapted from Claude Code's `/check-hook` command for the Factory Droid platform.

## Validation Checks

### 1. Root Configuration Validation
- ✅ **AGENTS.md**: YAML frontmatter syntax and required fields (name, description)
- ✅ **.droid.yaml**: YAML structure and dictionary format
- ✅ **Field Validation**: Minimum length requirements (name >= 3 chars, description >= 20 chars)

### 2. Factory Structure Validation
- ✅ **.factory/ directory**: Presence check
- ✅ **Subdirectories**: droids/, commands/, memory/, scripts/
- ✅ **Critical vs Optional**: Identifies missing critical directories

### 3. Droid Validation
- ✅ **YAML Frontmatter**: Syntax validation in all droids/*.md files
- ✅ **Required Fields**: name, description, model (optional), tools (optional)
- ✅ **Content Length**: Minimum 100 characters excluding frontmatter
- ✅ **Recommended Sections**: Commands, Specialization, Standards (informational only)

### 4. Command Validation
- ✅ **YAML Frontmatter**: Syntax validation in all commands/*.md files
- ✅ **Required Fields**: name, description
- ✅ **Parameters**: Checks for parameter definitions (recommended for commands)
- ✅ **Content Structure**: Validates markdown structure

### 5. Memory File Validation
- ✅ **Markdown Format**: Basic markdown validation
- ✅ **Content Length**: Minimum 50 characters
- ✅ **Readability**: Ensures files contain substantial content

## Common Issues Detected

### Critical Issues (❌)
- Missing YAML frontmatter (files must start with `---`)
- Malformed YAML syntax (indentation, colons, quotes)
- Missing required fields (name, description)
- Invalid field types (name must be string, etc.)
- Unreadable files (permissions, encoding)

### Warnings (⚠️)
- Very short content (< 100 chars for droids, < 50 chars for memory)
- Short descriptions (< 20 characters)
- Missing recommended sections (Commands, Specialization)
- Missing optional directories (scripts/, docs/)
- Missing optional files (AGENTS.md, .droid.yaml)

### Informational (ℹ️)
- Missing parameters in commands (may be intentional)
- Missing optional frontmatter fields (model, tools, delegates_to)
- Recommended structure improvements

## Usage

### Quick Validation
```bash
# Validate all Factory Droid configuration
/validate-droids

# Expected output:
# 🔍 Factory Droid Validation Report
# ==================================
# 
# 📋 Validating root configuration...
# ✅ Root configuration valid
# 📂 Checking .factory/ structure...
# ✅ .factory/ structure present (4/4 directories)
# 🤖 Validating droids...
#   ✅ 4/4 droids valid
# ⚡ Validating commands...
#   ✅ 2/2 commands valid
# 🧠 Validating memory files...
#   ✅ 2/2 memory files valid
# 
# Overall Health: 🟢 Excellent (100%)
```

### Verbose Output
```bash
# Show detailed per-file validation
/validate-droids --verbose

# Additional output includes:
# - Per-file YAML frontmatter validation
# - Content structure details
# - Missing optional sections
# - Field value validation
```

### With Automatic Fixes (Future)
```bash
# Apply automatic fixes to common issues
/validate-droids --fix

# Note: --fix is not yet implemented
# Manual fixes required for detected issues
```

## Validation Scoring

The validation system calculates an overall health score (0-100%):

| Component | Weight | Criteria |
|-----------|--------|----------|
| **Root Configuration** | 25% | AGENTS.md + .droid.yaml validity |
| **Factory Structure** | 15% | .factory/ directory presence |
| **Droids** | 30% | Percentage of valid droids/*.md files |
| **Commands** | 15% | Percentage of valid commands/*.md files |
| **Memory** | 15% | Percentage of valid memory/*.md files |

### Health Status

- 🟢 **Excellent (95-100%)**: All components valid, production-ready
- 🟡 **Good (80-94%)**: Minor issues, generally safe
- 🟠 **Fair (60-79%)**: Several issues need attention
- 🔴 **Poor (0-59%)**: Critical issues require immediate fixes

## Example Output

### All Valid Configuration

```
🔍 Factory Droid Validation Report
==================================

📋 Validating root configuration...
✅ Root configuration valid
📂 Checking .factory/ structure...
✅ .factory/ structure present (4/4 directories)
🤖 Validating droids...
  ✅ 4/4 droids valid
⚡ Validating commands...
  ✅ 2/2 commands valid
🧠 Validating memory files...
  ✅ 2/2 memory files valid

Root Configuration: ✅
Factory Structure: ✅
Droids: ✅ 4/4 valid
Commands: ✅ 2/2 valid
Memory: ✅ 2/2 valid

Overall Health: 🟢 Excellent (100%)
```

### With Issues Detected

```
🔍 Factory Droid Validation Report
==================================

📋 Validating root configuration...
✅ Root configuration valid
📂 Checking .factory/ structure...
✅ .factory/ structure present (4/4 directories)
🤖 Validating droids...
  ⚠️ 3/4 droids valid
⚡ Validating commands...
  ✅ 2/2 commands valid
🧠 Validating memory files...
  ✅ 2/2 memory files valid

Root Configuration: ✅
Factory Structure: ✅
Droids: ⚠️ 3/4 valid
Commands: ✅ 2/2 valid
Memory: ✅ 2/2 valid

Overall Health: 🟡 Good (87%)

🚨 Issues found:
  ❌ Critical: scraper-expert.md: YAML syntax error: mapping values are not allowed here
  ⚠️ Warning: test-engineer.md: 'description' should be >= 20 chars

💡 Suggestions:
  - Fix invalid droid files (check YAML frontmatter)
```

## Script Location

The validation script is located at:
```
.factory/scripts/validate_droids.py
```

**Requirements:**
- Python 3.10+
- PyYAML library (`pip install pyyaml`)

## Direct Script Execution

You can also run the validation script directly:

```bash
# From project root
python3 .factory/scripts/validate_droids.py

# With verbose output
python3 .factory/scripts/validate_droids.py --verbose

# From any directory
python3 .factory/scripts/validate_droids.py --project-dir /path/to/project

# Exit codes
# 0 = Health score >= 80% (success)
# 1 = Health score < 80% (issues found)
```

## Integration with Workflows

### Pre-Commit Hook (Optional)

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Validate Factory Droid configuration before commit

python3 .factory/scripts/validate_droids.py
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "❌ Factory Droid validation failed"
    echo "💡 Run: /validate-droids --verbose"
    exit 1
fi

exit 0
```

### CI/CD Integration

Add to GitHub Actions workflow:
```yaml
- name: Validate Factory Droids
  run: |
    pip install pyyaml
    python3 .factory/scripts/validate_droids.py --verbose
```

## Comparison with /check-hook

This command is adapted from Claude Code's `/check-hook` but simplified for Factory Droid:

| Feature | /check-hook (Claude Code) | /validate-droids (Factory) |
|---------|--------------------------|----------------------------|
| **Target** | .claude/settings.json hooks | .factory/ configuration |
| **YAML Validation** | JSON syntax | YAML frontmatter |
| **Hook Testing** | Executes hooks with sample data | N/A (no hooks) |
| **Registry Validation** | agent_registry.json | N/A (no registry) |
| **Environment Check** | Python venv + dependencies | PyYAML only |
| **Fix Capability** | Automatic quote/permission fixes | Not yet implemented |
| **Lines of Code** | 571 lines | 420 lines |

## Troubleshooting

### "No module named 'yaml'"

**Issue:** PyYAML not installed

**Fix:**
```bash
pip install pyyaml
```

### "YAML syntax error"

**Issue:** Malformed YAML frontmatter

**Common causes:**
- Missing closing `---` after frontmatter
- Incorrect indentation (use spaces, not tabs)
- Unquoted strings with special characters
- Missing colons after keys

**Fix:** Review YAML syntax in the reported file

### "Missing required fields"

**Issue:** Frontmatter missing `name` or `description`

**Fix:** Add required fields to YAML frontmatter:
```yaml
---
name: my-droid
description: A detailed description of what this droid does (min 20 chars)
---
```

### Permission Errors

**Issue:** Cannot read configuration files

**Fix:**
```bash
chmod 644 .factory/droids/*.md
chmod 644 .factory/commands/*.md
chmod 644 .factory/memory/*.md
```

## Best Practices

1. **Run validation before commits** to catch issues early
2. **Use verbose mode** when debugging specific issues
3. **Maintain minimum description length** (>= 20 chars) for clarity
4. **Include recommended sections** in droids (Commands, Specialization)
5. **Test after changes** to ensure configuration remains valid

## Future Enhancements

The `--fix` flag will support automatic fixes for:
- Common YAML syntax errors (quote escaping, indentation)
- Missing frontmatter boilerplate
- Standardized markdown formatting
- Field value normalization

## See Also

- **AGENTS.md** - Root-level agent configuration
- **.droid.yaml** - Project behavior customization
- **validate_execution.py** - Security validation for commands
- **FACTORY_SETUP_COMPLETE.md** - Factory configuration documentation
