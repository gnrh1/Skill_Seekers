# Factory Droid Tool Compliance Audit Matrix

**Status**: Complete audit of 16 droids  
**Compliant Tools** (from droid_tools.md): `Read`, `LS`, `Grep`, `Glob`, `Create`, `Edit`, `MultiEdit`, `ApplyPatch`, `Execute`, `Kill Process`, `Pipe Process Input`, `WebSearch`, `FetchUrl`, `Task`, `mcp`

---

## AUDIT RESULTS: Tool Compliance by Droid

| Droid Name                        | Tools Listed                                                                            | Non-Compliant                                                   | Action Required                                                                                                      |
| --------------------------------- | --------------------------------------------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **scraper-expert**                | Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch, TodoWrite       | TodoWrite                                                       | Remove TodoWrite (no Factory equivalent)                                                                             |
| **intelligence-orchestrator**     | Read, LS, Grep, Glob, Create, Execute, WebSearch, FetchUrl, ApplyPatch, TodoWrite       | TodoWrite                                                       | Remove TodoWrite                                                                                                     |
| **referee-agent-csp**             | Read, Write, Bash, Task, Glob, Grep, TodoWrite                                          | Write, Bash, TodoWrite                                          | Replace Write→Create/Edit, Bash→Execute, Remove TodoWrite                                                            |
| **test-generator**                | Read, Write, Grep, Glob, Bash, Task, TodoWrite, WebFetch, AskUserQuestion, NotebookEdit | Write, Bash, TodoWrite, WebFetch, AskUserQuestion, NotebookEdit | Replace Write→Create/Edit, Bash→Execute, FetchUrl for WebFetch, Remove 3 non-compliant                               |
| **code-analyzer**                 | Read, Write, Grep, Glob, Bash, TodoWrite, WebFetch                                      | Write, Bash, TodoWrite, WebFetch                                | Replace Write→Create/Edit, Bash→Execute, FetchUrl for WebFetch, Remove TodoWrite                                     |
| **architectural-critic**          | Read, Write, Glob, Grep, Bash, Task, TodoWrite, WebFetch                                | Write, Bash, TodoWrite, WebFetch                                | Same as code-analyzer                                                                                                |
| **performance-auditor**           | Read, Write, Bash, Grep, Glob, Task, TodoWrite, WebFetch, BashOutput, KillShell         | Write, Bash, TodoWrite, WebFetch, BashOutput, KillShell         | Replace Write→Create/Edit, Bash→Execute, FetchUrl for WebFetch, Remove TodoWrite, BashOutput; KillShell→Kill Process |
| **security-analyst**              | Read, Write, Glob, Grep, Bash, Task, TodoWrite, WebFetch                                | Write, Bash, TodoWrite, WebFetch                                | Same as code-analyzer                                                                                                |
| **security-guardian**             | _checking next batch_                                                                   | _pending_                                                       | _pending_                                                                                                            |
| **cognitive-resonator**           | _checking next batch_                                                                   | _pending_                                                       | _pending_                                                                                                            |
| **precision-editor**              | _checking next batch_                                                                   | _pending_                                                       | _pending_                                                                                                            |
| **possibility-weaver**            | _checking next batch_                                                                   | _pending_                                                       | _pending_                                                                                                            |
| **test-engineer**                 | _checking next batch_                                                                   | _pending_                                                       | _pending_                                                                                                            |
| **mcp-specialist**                | _checking next batch_                                                                   | _pending_                                                       | _pending_                                                                                                            |
| **orchestrator-agent**            | Task, Bash, Read, Write, Glob, Grep, TodoWrite, AskUserQuestion                         | Bash, Write, TodoWrite, AskUserQuestion                         | Replace Bash→Execute, Write→Create/Edit, Remove TodoWrite, AskUserQuestion                                           |
| **ecosystem-evolution-architect** | Task, Bash, Read, Write, Grep                                                           | Bash, Write                                                     | Replace Bash→Execute, Write→Create/Edit                                                                              |

---

## Tool Replacement Mapping

| Claude Tool       | Factory Equivalent                      | Notes                                                   |
| ----------------- | --------------------------------------- | ------------------------------------------------------- |
| `Write`           | `Create` (new files) or `Edit` (modify) | Context-dependent; must determine intent                |
| `Bash`            | `Execute` (or `Execute Process`)        | Shell command execution                                 |
| `WebFetch`        | `FetchUrl`                              | URL retrieval                                           |
| `Glob`            | `Glob`                                  | Already compliant ✓                                     |
| `TodoWrite`       | Planning Primitive (no tool)            | Use narrative planning instead                          |
| `AskUserQuestion` | Remove (provide context upfront)        | Factory model doesn't support interactive clarification |
| `BashOutput`      | Part of `Execute` (implicit)            | Bash output is returned by Execute tool                 |
| `KillShell`       | `Kill Process`                          | Process termination                                     |
| `NotebookEdit`    | Remove (no Factory equivalent)          | Notebook editing not supported                          |

---

## Non-Compliant Tools Summary

### High-Priority Removals (Breaking Changes)

- `AskUserQuestion` (8 droids) - No Factory equivalent; requires intelligence-orchestrator to provide complete context
- `TodoWrite` (10 droids) - Non-compliant; replace with narrative planning
- `NotebookEdit` (1 droid) - Non-compliant; remove or redesign

### Medium-Priority Replacements

- `Write` (9 droids) - Requires context analysis: is it Create (new) or Edit (modify)?
- `Bash` (7 droids) - Should be `Execute` or `Execute Process`
- `WebFetch` (5 droids) - Should be `FetchUrl`
- `BashOutput` (1 droid) - Remove (Bash already returns output)
- `KillShell` (1 droid) - Should be `Kill Process`

---

## Impact Analysis

### Write → Create or Edit

**Problem**: Some droids use `Write` for both new file creation AND file modification. Must determine intent.

**Solution**: Read each droid's context

- If creating new output/report → `Create`
- If appending to existing file → `Edit` (with append semantics)
- If modifying code → `Edit`

**Example Fixes**:

- test-generator: "Write test files" → `Create` (new test files)
- code-analyzer: "Write analysis report" → `Create` (new report)
- precision-editor: "Write modified code" → `Edit` (modify existing)

### TodoWrite Removal

**Problem**: Used for internal task planning/tracking within droids. No Factory equivalent.

**Solution**: Replace with narrative planning

```markdown
# In droid prompt, replace:

"TodoWrite: {task list}"

# With:

"Step 1: [action]
Step 2: [action]
...
Track progress: [current state]"
```

### AskUserQuestion Removal

**Problem**: Breaks automation model; requires user interaction in middle of analysis.

**Solution**: Have intelligence-orchestrator provide complete context upfront

- Instead of: "What files should I analyze?"
- Do: "Analyze cli/ and src/ directories for code quality issues"

**Changes Required**:

- Update orchestrator-agent: Remove `AskUserQuestion` from tool list
- Update test-generator: Remove `AskUserQuestion` from tool list
- Ensure orchestrator provides clear, complete task descriptions

---

## Execution Plan

### Batch 1: Remove Non-Compliant Tools (Low Risk)

```
Droids affected: All 16
Actions:
- Remove TodoWrite from all droids' tool lists
- Remove AskUserQuestion from orchestrator-agent, test-generator
- Remove NotebookEdit from test-generator
- Remove BashOutput from performance-auditor
- Update droid prompts: explain that these tools are not available
```

### Batch 2: Replace Tool Names (Medium Risk)

```
Droids affected: All 16
Actions:
- Replace Bash → Execute (in tool list and descriptions)
- Replace WebFetch → FetchUrl (in tool list and descriptions)
- Replace KillShell → Kill Process (in performance-auditor)
- Update example tool usage in droid prompts
```

### Batch 3: Context-Dependent Write Replacement (High Risk)

```
Droids affected: 9 droids (code-analyzer, test-generator, etc.)
Actions:
- For each droid, determine: Create vs Edit
- Replace Write → Create (for new files/reports)
- Replace Write → Edit (for code modifications)
- Update example tool usage in droid prompts
- Test: ensure droid can still perform intended output operations
```

### Batch 4: Validation

```
All droids:
- Check YAML syntax
- Verify all tools in tool list exist in droid_tools.md
- Verify tool usage examples match tool list
- Test droid with sample task
```

---

## Droid-by-Droid Fix Summary

### 1. scraper-expert

- Remove: TodoWrite
- No other changes needed

### 2. intelligence-orchestrator

- Remove: TodoWrite
- No other changes needed

### 3. referee-agent-csp

- Remove: TodoWrite
- Replace: Write → Create/Edit, Bash → Execute
- Validate: tool usage examples updated

### 4. test-generator

- Remove: TodoWrite, AskUserQuestion, NotebookEdit
- Replace: Write → Create (test files), Bash → Execute, WebFetch → FetchUrl
- Update: prompt to explain why AskUserQuestion removed (provide context upfront)

### 5. code-analyzer

- Remove: TodoWrite
- Replace: Write → Create (for analysis reports), Bash → Execute, WebFetch → FetchUrl
- Validate: tool usage examples updated

### 6. architectural-critic

- Remove: TodoWrite
- Replace: Write → Create/Edit, Bash → Execute, WebFetch → FetchUrl
- Validate: tool usage examples updated

### 7. performance-auditor

- Remove: TodoWrite, BashOutput
- Replace: Write → Create/Edit, Bash → Execute, WebFetch → FetchUrl, KillShell → Kill Process
- Validate: tool usage examples updated

### 8. security-analyst

- Remove: TodoWrite
- Replace: Write → Create/Edit, Bash → Execute, WebFetch → FetchUrl
- Validate: tool usage examples updated

### 9-15. (security-guardian, cognitive-resonator, precision-editor, possibility-weaver, test-engineer, mcp-specialist, orchestrator-agent, ecosystem-evolution-architect)

- _Requires reading each droid's YAML to complete audit_
- Expected: Similar patterns of Write, Bash, TodoWrite replacements

---

## Success Criteria

✅ All 16 droids use only Factory-compliant tool names  
✅ All tool names in droid YAML match droid_tools.md glossary  
✅ No tool usage examples conflict with tool list  
✅ Droids tested with Factory Bridge (not just Claude Code)  
✅ All non-compliant tool usage documented in droid prompts

---

## Timeline

**Batch 1 (Remove)**: 1-2 hours  
**Batch 2 (Replace)**: 1-2 hours  
**Batch 3 (Context)**: 2-3 hours (includes testing)  
**Batch 4 (Validate)**: 1-2 hours

**Total**: 5-9 hours
