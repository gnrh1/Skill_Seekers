# IMMEDIATE ACTION: Issue 2 - Tool Compliance Fixes (Hard Blocker)

**Start Here**: This is the foundation. Must be completed first before Issue 3 & 1.

---

## Issue 2 Summary

**Problem**: 16 droids use Claude-native tools; Factory Bridge only supports Factory tools  
**Impact**: HIGH - Factory Bridge integration fails if tools non-compliant  
**Timeline**: 5-9 hours  
**Priority**: CRITICAL - Blocker for Issues 1 & 3

---

## Tool Compliance Reference

### Factory-Compliant Tools (Source: droid_tools.md)

✅ `Read`, `LS`, `Grep`, `Glob`, `Create`, `Edit`, `MultiEdit`, `ApplyPatch`  
✅ `Execute`, `Kill Process`, `Pipe Process Input`  
✅ `WebSearch`, `FetchUrl`, `Task`, `mcp`

### Non-Compliant Tools Found in Droids

❌ `Write` (10 droids)  
❌ `Bash` (7 droids)  
❌ `WebFetch` (5 droids)  
❌ `TodoWrite` (10 droids)  
❌ `AskUserQuestion` (2 droids)  
❌ `BashOutput` (1 droid)  
❌ `KillShell` (1 droid)  
❌ `NotebookEdit` (1 droid)

---

## Droid-by-Droid Fix Actions

### 1. scraper-expert.md

**Current tools**: Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch, TodoWrite  
**Action**: Remove TodoWrite  
**Effort**: 5 minutes

```diff
- tools: Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch, TodoWrite
+ tools: Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch
```

### 2. intelligence-orchestrator.md

**Current tools**: Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch, TodoWrite  
**Action**: Remove TodoWrite  
**Effort**: 5 minutes

```diff
- tools: Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch, TodoWrite
+ tools: Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch
```

### 3. referee-agent-csp.md

**Current tools**: Read, Write, Bash, Task, Glob, Grep, TodoWrite  
**Actions**:

1. Remove: TodoWrite
2. Replace: Write → Create (or Edit, analyze usage first)
3. Replace: Bash → Execute
   **Effort**: 15 minutes

```diff
- tools: Read, Write, Bash, Task, Glob, Grep, TodoWrite
+ tools: Read, Create, Execute, Task, Glob, Grep
```

**Also update tool examples in prompt**:

```diff
- Bash: python3 script.py
+ Execute: python3 script.py

- Write: output.txt
+ Create: output.txt (or Edit if appending)
```

### 4. test-generator.md

**Current tools**: Read, Write, Grep, Glob, Bash, Task, TodoWrite, WebFetch, AskUserQuestion, NotebookEdit  
**Actions**:

1. Remove: TodoWrite, AskUserQuestion, NotebookEdit
2. Replace: Write → Create (test files are new)
3. Replace: Bash → Execute
4. Replace: WebFetch → FetchUrl
   **Effort**: 20 minutes

```diff
- tools: Read, Write, Grep, Glob, Bash, Task, TodoWrite, WebFetch, AskUserQuestion, NotebookEdit
+ tools: Read, Create, Grep, Glob, Execute, Task, FetchUrl
```

**Add to prompt** (explaining removals):

```markdown
## Tool Availability Note

The following Claude Code tools are not available in Factory Droid environment:

- **AskUserQuestion**: Provide complete context in your analysis task description upfront
- **TodoWrite**: Track progress through narrative step-by-step planning
- **NotebookEdit**: Notebook editing not supported; use text files instead

These limitations require you to:

1. Receive complete task context (no clarifying questions)
2. Provide step-by-step planning as narrative text
3. Return test outputs as code files, not notebooks
```

### 5. code-analyzer.md

**Current tools**: Read, Write, Grep, Glob, Bash, TodoWrite, WebFetch  
**Actions**:

1. Remove: TodoWrite
2. Replace: Write → Create (analysis reports are new)
3. Replace: Bash → Execute
4. Replace: WebFetch → FetchUrl
   **Effort**: 15 minutes

```diff
- tools: Read, Write, Grep, Glob, Bash, TodoWrite, WebFetch
+ tools: Read, Create, Grep, Glob, Execute, FetchUrl
```

### 6. architectural-critic.md

**Current tools**: Read, Write, Glob, Grep, Bash, Task, TodoWrite, WebFetch  
**Actions**:

1. Remove: TodoWrite
2. Replace: Write → Create or Edit (depends on usage)
3. Replace: Bash → Execute
4. Replace: WebFetch → FetchUrl
   **Effort**: 15 minutes

```diff
- tools: Read, Write, Glob, Grep, Bash, Task, TodoWrite, WebFetch
+ tools: Read, Edit, Glob, Grep, Execute, Task, FetchUrl
```

### 7. performance-auditor.md

**Current tools**: Read, Write, Bash, Grep, Glob, Task, TodoWrite, WebFetch, BashOutput, KillShell  
**Actions**:

1. Remove: TodoWrite, BashOutput
2. Replace: Write → Create or Edit
3. Replace: Bash → Execute
4. Replace: WebFetch → FetchUrl
5. Replace: KillShell → Kill Process
   **Effort**: 20 minutes

```diff
- tools: Read, Write, Bash, Grep, Glob, Task, TodoWrite, WebFetch, BashOutput, KillShell
+ tools: Read, Create, Execute, Grep, Glob, Task, FetchUrl, Kill Process
```

### 8. security-analyst.md

**Current tools**: Read, Write, Glob, Grep, Bash, Task, TodoWrite, WebFetch  
**Actions**:

1. Remove: TodoWrite
2. Replace: Write → Create or Edit
3. Replace: Bash → Execute
4. Replace: WebFetch → FetchUrl
   **Effort**: 15 minutes

```diff
- tools: Read, Write, Glob, Grep, Bash, Task, TodoWrite, WebFetch
+ tools: Read, Create, Glob, Grep, Execute, Task, FetchUrl
```

### 9. orchestrator-agent.md

**Current tools**: Task, Bash, Read, Write, Glob, Grep, TodoWrite, AskUserQuestion  
**Actions**:

1. Remove: TodoWrite, AskUserQuestion
2. Replace: Bash → Execute
3. Replace: Write → Create or Edit
   **Effort**: 15 minutes

```diff
- tools: Task, Bash, Read, Write, Glob, Grep, TodoWrite, AskUserQuestion
+ tools: Task, Execute, Read, Create, Glob, Grep
```

**Update prompt** to explain AskUserQuestion removal.

### 10. ecosystem-evolution-architect.md

**Current tools**: Task, Bash, Read, Write, Grep  
**Actions**:

1. Replace: Bash → Execute
2. Replace: Write → Create or Edit
   **Effort**: 10 minutes

```diff
- tools: Task, Bash, Read, Write, Grep
+ tools: Task, Execute, Read, Create, Grep
```

### 11-16. (Remaining Droids)

_Requires reading each droid's YAML to provide exact fixes_

Expected pattern:

- Remove: TodoWrite (if present)
- Remove: AskUserQuestion (if present)
- Replace: Write → Create/Edit
- Replace: Bash → Execute
- Replace: WebFetch → FetchUrl
- Replace: KillShell → Kill Process
- Remove: BashOutput, NotebookEdit (if present)

---

## Implementation Steps

### Step 1: Read Each Droid (30 minutes)

For each of 16 droids:

```bash
cat .factory/droids/[name].md | head -10
```

Capture tools list and any Claude-specific tool usage in examples.

### Step 2: Apply Batch 1 - Remove Non-Compliant Tools (30 minutes)

```bash
# For all droids, remove these if present:
# TodoWrite, AskUserQuestion, NotebookEdit, BashOutput
```

Use `sed` or manual edits.

### Step 3: Apply Batch 2 - Simple Replacements (30 minutes)

```bash
# Replace all instances of:
# Bash → Execute
# WebFetch → FetchUrl
# KillShell → Kill Process
```

Use `sed -i` for bulk replacements:

```bash
sed -i 's/Bash/Execute/g' .factory/droids/*.md
sed -i 's/WebFetch/FetchUrl/g' .factory/droids/*.md
sed -i 's/KillShell/Kill Process/g' .factory/droids/*.md
```

### Step 4: Apply Batch 3 - Context-Dependent Write Replacements (2-3 hours)

For each droid, read and understand Write usage:

1. Is it creating new files? → Replace with `Create`
2. Is it appending? → Replace with `Edit`
3. Is it modifying code? → Replace with `Edit`

Manual review required; no bulk sed.

### Step 5: Update Tool Examples in Prompts (1-2 hours)

Find all examples in droid prompts that use removed/replaced tools.
Update examples to use Factory tools.

Example:

```markdown
# Before

Bash: python3 -m pytest tests/

# After

Execute: python3 -m pytest tests/
```

### Step 6: Validation (30 minutes)

```bash
# For each droid, verify YAML syntax:
grep -E "^tools:" .factory/droids/*.md

# Check that all listed tools exist in droid_tools.md glossary
```

### Step 7: Factory Bridge Testing (1 hour)

Test each droid with Factory Bridge (not just Claude Code):

```bash
droid test-generator --task "Generate tests for src/main.py"
```

Verify no tool invocation failures.

---

## Tool-by-Tool Replacement Guide

### Write → Create or Edit (Context-Dependent)

**Use Create when**:

- Generating a new file (analysis report, test suite, new code)
- Output file doesn't exist yet
- Writing to a fresh output file

**Use Edit when**:

- Modifying existing code
- Appending to a file
- Updating existing documentation

**Decision Rule**: Read the droid's description of what it does with "Write"

- If "Write test file" → Create
- If "Write analysis report" → Create
- If "Write modified code" → Edit
- If "Append to log" → Edit

### Bash → Execute

**Direct replacement**; no context needed.

- Bash command → Execute command
- Same semantics; different name

### WebFetch → FetchUrl

**Direct replacement**; no context needed.

- WebFetch URL → FetchUrl URL
- Same semantics; different name

---

## Testing Checklist

After completing fixes for each droid:

- [ ] YAML syntax valid (no parsing errors)
- [ ] All tools in tool list exist in droid_tools.md
- [ ] Tool examples in prompt use listed tools
- [ ] No Claude-specific tool names remain
- [ ] Droid tested with Factory Bridge
- [ ] Output files created in expected location
- [ ] No tool invocation failures

---

## Rollback Plan

If a droid breaks after changes:

1. Check YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('.factory/droids/[name].md'))"`
2. If YAML error: Fix syntax error
3. If tool error: Verify tool name against droid_tools.md
4. If example error: Update example to use correct tool
5. If test failure: Revert changes and debug

---

## Success Criteria

✅ All 16 droids have valid YAML  
✅ No Claude-specific tools remain in any droid  
✅ All tools in tool lists exist in droid_tools.md glossary  
✅ Tool examples in prompts use listed tools  
✅ Each droid tested with Factory Bridge  
✅ No tool invocation failures

---

## Time Estimate

| Activity                                  | Time          |
| ----------------------------------------- | ------------- |
| Read all droids & audit (Step 1)          | 30 min        |
| Batch 1 - Remove non-compliant (Step 2)   | 30 min        |
| Batch 2 - Simple replacements (Step 3)    | 30 min        |
| Batch 3 - Write context analysis (Step 4) | 2-3 hrs       |
| Update tool examples (Step 5)             | 1-2 hrs       |
| Validation (Step 6)                       | 30 min        |
| Factory Bridge testing (Step 7)           | 1 hr          |
| **TOTAL**                                 | **5-9 hours** |

---

## Ready to Start?

1. Backup current droids: `cp -r .factory/droids .factory/droids.backup`
2. Start with Batch 1 & 2 (1 hour of safe changes)
3. Test immediately in Factory Bridge
4. Then proceed to Batch 3 (requires analysis)

**Once complete**, you'll have a solid foundation for Issue 3 (Structured Outputs) and Issue 1 (Workflow Coordination).
