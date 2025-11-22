# Agent YAML Compliance Issues - Detailed Breakdown

## Summary
Found **4 agents** with YAML compliance issues out of **11 active agents**. The intern correctly fixed most agents but missed these specific malformed field entries.

---

## 🚨 Issue 1: `possibility-weaver.md`

### Problem
**Unsupported Field**: `delegates_to` is not part of the official agent specification.

### What the YAML looked like (BEFORE):
```yaml
---
name: possibility-weaver
description: Creative catalyst agent that introduces novel perspectives and beneficial constraints to break developers out of local optima. Uses constraint innovation and perspective synthesis to expand solution spaces while maintaining core system invariants.
model: sonnet
tools: Read, Write, Grep, Bash, Task
---
delegates_to:                # ❌ MALFORMED - Unsupported field
  - code-analyzer
  - architectural-critic
  - cognitive-resonator
```

### What was fixed (AFTER):
```yaml
---
name: possibility-weaver
description: Creative catalyst agent that introduces novel perspectives and beneficial constraints to break developers out of local optima. Uses constraint innovation and perspective synthesis to expand solution spaces while maintaining core system invariants.
model: sonnet
tools: Read, Write, Grep, Bash, Task
---
```

---

## 🚨 Issue 2: `precision-editor.md`

### Problem 1: Unsupported Field
**Unsupported Field**: `tags` is not part of the official agent specification.

### Problem 2: Malformed Field Entries
**Malformed entries**: Lines starting with `- test-generator` and `tags:` without proper YAML structure.

### What the YAML looked like (BEFORE):
```yaml
---
name: precision-editor
description: Surgical code modification specialist that performs precise, system-aware edits with minimal side effects and maximum architectural integrity. Uses gene-editing precision to make targeted modifications while preserving system coherence and design intent.
model: sonnet
tools: Read, Edit, Write, Grep, Bash, Task
---
  - test-generator            # ❌ MALFORMED - Not a valid YAML field
tags:                         # ❌ MALFORMED - Unsupported field
  - precision
  - surgery
  - modifications
  - system-aware
  - gene-editing
  - architectural-integrity
  - targeted-changes
---
```

### What was fixed (AFTER):
```yaml
---
name: precision-editor
description: Surgical code modification specialist that performs precise, system-aware edits with minimal side effects and maximum architectural integrity. Uses gene-editing precision to make targeted modifications while preserving system coherence and design intent.
model: sonnet
tools: Read, Edit, Write, Grep, Bash, Task
---
```

---

## 🚨 Issue 3: `referee-agent-csp.md`

### Problem: Malformed Field Entries
**Malformed entries**: Lines starting with `-` but not associated with any valid YAML field. These appear to be leftover tag-like entries.

### What the YAML looked like (BEFORE):
```yaml
---
name: referee-agent-csp
description: Convergent Synthesis Primitive for deterministic outcome evaluation and autonomous selection. Performs metric-driven synthesis of multiple parallel agent outputs.
model: opus
tools: Read, Bash, Task, Grep
---
  - parallelization         # ❌ MALFORMED - Not a valid YAML field
  - fidelity                 # ❌ MALFORMED - Not a valid YAML field
  - deterministic            # ❌ MALFORMED - Not a valid YAML field
  - convergent-synthesis     # ❌ MALFORMED - Not a valid YAML field
---
```

### What was fixed (AFTER):
```yaml
---
name: referee-agent-csp
description: Convergent Synthesis Primitive for deterministic outcome evaluation and autonomous selection. Performs metric-driven synthesis of multiple parallel agent outputs.
model: opus
tools: Read, Bash, Task, Grep
---
```

---

## 🚨 Issue 4: `test-generator.md`

### Problem: Malformed Field Entries
**Malformed entries**: Lines starting with `-` but not associated with any valid YAML field. These appear to be leftover tag-like entries.

### What the YAML looked like (BEFORE):
```yaml
---
name: test-generator
description: Comprehensive test generation specialist that creates unit, integration, performance, and security tests with coverage optimization and CI/CD integration. Generates maintainable test suites using the T.E.S.T. methodology for maximum effectiveness and developer productivity.
model: sonnet
tools: Read, Write, Grep, Glob, Bash, Task
---
  - integration-testing      # ❌ MALFORMED - Not a valid YAML field
  - test-coverage           # ❌ MALFORMED - Not a valid YAML field
  - automated-testing       # ❌ MALFORMED - Not a valid YAML field
  - ci-cd                   # ❌ MALFORMED - Not a valid YAML field
---
```

### What was fixed (AFTER):
```yaml
---
name: test-generator
description: Comprehensive test generation specialist that creates unit, integration, performance, and security tests with coverage optimization and CI/CD integration. Generates maintainable test suites using the T.E.S.T. methodology for maximum effectiveness and developer productivity.
model: sonnet
tools: Read, Write, Grep, Glob, Bash, Task
---
```

---

## ✅ Official Agent Specification Requirements

### Valid YAML Fields (Only these are allowed):
- `name`: Agent name (required)
- `description`: Agent description (required)
- `model`: Model identifier (`opus`, `sonnet`) (required)
- `tools`: Comma-separated list of capitalized tool names (required)

### Valid Tool Names (Must be capitalized):
- `Read`
- `Write`
- `Edit`
- `Grep`
- `Glob`
- `Bash`
- `Task`

### Invalid Fields Found:
- `type` ❌
- `tags` ❌
- `delegates_to` ❌
- Unassociated `- item` entries ❌

### Correct Format:
```yaml
---
name: agent-name
description: Agent description here
model: sonnet  # or opus
tools: Read, Write, Grep, Bash, Task  # Comma-separated, capitalized
---
```

---

## 📋 Verification Checklist for Intern

Please have the intern verify:

1. **Remove unsupported fields**: `type`, `tags`, `delegates_to`
2. **Remove unassociated list items**: Lines starting with `-` that aren't under a valid field
3. **Ensure proper YAML structure**: Only the 4 valid fields in the frontmatter
4. **Capitalize tool names**: All tool names must be capitalized
5. **Use comma-separated format**: Tools should be comma-separated, not space-separated

## 🎯 Learning Points

1. **YAML Frontmatter Only**: Only valid agent specification fields should be between the `---` markers
2. **No Tag-like Entries**: Unassociated `- item` lists are invalid YAML in this context
3. **Field Validation**: Always validate against official specification
4. **Complete Verification**: Check all files, not just a sample

The intern did good work on most agents but missed these malformed entries that appear to be leftover from an older format or incomplete migration.