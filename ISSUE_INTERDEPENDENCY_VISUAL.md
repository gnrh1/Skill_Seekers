# Three Issues: Interdependency & Second-Order Effects (Visual Summary)

## Issue Dependency Chain

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ISSUE 2: TOOL COMPLIANCE (Hard Blocker)                      │
│  ════════════════════════════════════════                      │
│  Current: 16 droids use Claude tools (Write, Bash, WebFetch)  │
│  Required: All droids must use Factory tools only             │
│  Impact: If not fixed, Factory Bridge integration fails       │
│  Timeline: 5-9 hours                                           │
│                                                                 │
│  ✓ Without this: Nothing else works                           │
│  ✓ Hard dependency for Issues 1 & 3                           │
│  ✓ Must complete FIRST                                        │
│                                                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────┐
         │ Tools Compliant?  │
         │    (Issue 2)      │
         └─────────┬─────────┘
                   │
           ┌───────┴────────────────────────────────────────────┐
           │                                                    │
           ▼                                                    │
┌─────────────────────────────────────────────────────────────┐│
│                                                             ││
│  ISSUE 3: STRUCTURED OUTPUTS (Enabler)                     ││
│  ═════════════════════════════════════                      ││
│  Current: Droids return prose; no output contract           ││
│  Required: Droids return JSON with defined schema           ││
│  Impact: intelligence-orchestrator cannot parse findings    ││
│  Timeline: 4-5 hours (parallel with Issue 2)                ││
│                                                             ││
│  ✓ Depends on: Issue 2 (tool names must be correct)        ││
│  ✓ Enables: Issue 1 (orchestrator parsing logic)           ││
│  ✓ Must complete BEFORE Issue 1 implementation             ││
│                                                             ││
└────────────────────┬────────────────────────────────────────┘│
                     │                                          │
                     ▼                                          │
         ┌───────────────────┐                                 │
         │ Outputs Structured?                                 │
         │    (Issue 3)      │                                 │
         └─────────┬─────────┘                                 │
                   │                                           │
           ┌───────┴───────────────────────────────────────────┤
           │                                                   │
           ▼                                                   │
┌─────────────────────────────────────────────────────────────┐│
│                                                             ││
│  ISSUE 1: WORKFLOW COORDINATION (Capstone)                 ││
│  ══════════════════════════════════════════                ││
│  Current: Strategies described in prose; no execution logic││
│  Required: Scripted delegation + output capture + synthesis││
│  Impact: intelligence-orchestrator can auto-coordinate     ││
│  Timeline: 3-4 hours (final, depends on 2 & 3)            ││
│                                                             ││
│  ✓ Depends on: Issue 2 (compliant tools) + Issue 3 (JSON) ││
│  ✓ Brings it all together: automation without guidance     ││
│  ✓ Must complete LAST                                      ││
│                                                             ││
└────────────────────┬────────────────────────────────────────┘│
                     │                                          │
                     ▼                                          │
         ┌───────────────────┐                                 │
         │ Workflow Complete?                                  │
         │    (Issue 1)      │                                 │
         └─────────┬─────────┘                                 │
                   │                                           │
                   └───────────────────────────────────────────┘
                           │
                           ▼
                  ✅ Full automation enabled
```

---

## Second-Order Effects: The Cascading Consequences

```
┌─────────────────────────────────────────┐
│ Issue 2: Fix Tool Compliance            │
│ (Write, Bash, WebFetch → Factory tools) │
└────────┬────────────────────────────────┘
         │
         ├─→ SOE 1: Removing TodoWrite breaks planning
         │   └─→ Requires: Replace with narrative planning in droid prompts
         │       └─→ Impact: Droids must structure planning as text steps
         │
         ├─→ SOE 2: Removing AskUserQuestion removes user interaction
         │   └─→ Requires: intelligence-orchestrator provides complete context
         │       └─→ Impact: Orchestrator must analyze task complexity upfront
         │
         ├─→ SOE 3: Write → Create/Edit requires context analysis
         │   └─→ Requires: Manual analysis of each droid's Write usage
         │       └─→ Impact: High-risk changes; must test each droid
         │
         └─→ SOE 4: Bash → Execute requires command semantics clarification
             └─→ Requires: Update all Bash examples to Execute syntax
                 └─→ Impact: Droid capability unchanged but syntax changes

┌─────────────────────────────────────────┐
│ Issue 3: Add Structured Outputs         │
│ (Prose → JSON with defined schema)      │
└────────┬────────────────────────────────┘
         │
         ├─→ SOE 5: JSON schema limits specialist flexibility
         │   └─→ Requires: Add "additional_findings" field to schema
         │       └─→ Impact: Specialists can add unforeseen insights
         │
         ├─→ SOE 6: JSON parsing can fail silently
         │   └─→ Requires: Graceful fallback to text parsing
         │       └─→ Impact: intelligence-orchestrator adds error handling
         │
         ├─→ SOE 7: Defining output format reveals finding inconsistencies
         │   └─→ Requires: Standardize how different specialists report results
         │       └─→ Impact: Each specialist prompt updated with example JSON
         │
         └─→ SOE 8: JSON validation adds latency to parsing
             └─→ Requires: Schema validation in orchestrator
                 └─→ Impact: Orchestrator adds schema validation before synthesis

┌─────────────────────────────────────────┐
│ Issue 1: Add Workflow Coordination      │
│ (Prose → Scripted delegation pattern)   │
└────────┬────────────────────────────────┘
         │
         ├─→ SOE 9: Workflow coordination requires file output
         │   └─→ Requires: Define location for integration summaries
         │       └─→ Impact: Creates new directory: .factory/analysis_results/
         │
         ├─→ SOE 10: Scripted delegation assumes all specialists available
         │   └─→ Requires: Fallback if specialist droid fails
         │       └─→ Impact: Orchestrator degrades gracefully (partial analysis)
         │
         ├─→ SOE 11: Decision tree for specialist selection can conflict
         │   └─→ Requires: Define priority when multiple specialists apply
         │       └─→ Impact: Orchestrator makes principled decisions
         │
         └─→ SOE 12: Integration summary requires cross-domain synthesis
             └─→ Requires: Orchestrator identifies conflicts and dependencies
                 └─→ Impact: Adds complexity to synthesis logic
```

---

## Critical Interaction: Tool Compliance ← → Output Contracts

```
┌──────────────────────────────┐
│  Tool Compliance (Issue 2)   │
│  ════════════════════════    │
│  If Write → Create/Edit      │
│  If Bash → Execute           │
│  If WebFetch → FetchUrl      │
└────────────┬─────────────────┘
             │
             ├─ ENABLES ─→ Can droids create output files? (Issue 3)
             │             YES if Write → Create is correct
             │             NO if Write → Edit (append, not create)
             │
             └─ AFFECTS ─→ How should droids save structured output?
                           JSON file (Create) or stdout?
                           Depends on tool choice!

┌──────────────────────────────────────┐
│  Structured Outputs (Issue 3)        │
│  ════════════════════════════════    │
│  If droid outputs JSON to file       │
│    → Requires: Create or Edit tool   │
│  If droid outputs JSON to stdout     │
│    → Requires: No file tools needed  │
│                                      │
│  **Decision**: Define standard first!│
└──────────────────────────────────────┘

**Interdependency**: Tool choice (Issue 2) directly affects how specialists
deliver output (Issue 3). Must decide: file-based or stdout-based JSON?
```

---

## Risk Cascade: What Breaks If You Don't Fix in Sequence?

### Scenario A: Fix Issue 1 Without Fixing Issue 2

```
intelligence-orchestrator (new workflow section added)
  ↓ tries to invoke code-analyzer
    ↓ code-analyzer uses Write tool (not Factory-compliant)
      ↓ Factory Bridge rejects Write → ERROR
  ↓ RESULT: Workflow breaks; cannot invoke specialists
```

**Consequence**: Months of work on Issue 1 blocked by unfixed Issue 2

### Scenario B: Fix Issue 1 Without Fixing Issue 3

```
intelligence-orchestrator (new workflow section added)
  ↓ invokes code-analyzer
    ↓ code-analyzer returns prose findings (no JSON)
  ↓ orchestrator tries to parse JSON → FAILS
  ↓ RESULT: Orchestrator cannot parse findings; synthesis impossible
```

**Consequence**: Workflow coordination doesn't actually work

### Scenario C: Fix All Three Out of Sequence

```
Fix Issue 1 → Issue 3 → Issue 2:
  - Issue 1 describes parsing logic (but no JSON from specialists yet)
  - Issue 3 defines JSON but tools non-compliant
  - Issue 2 fixes tools (but orchestrator already documented wrong parsing)
  - RESULT: Multiple iterations needed; coordination fragile

Fix Issue 2 → Issue 1 → Issue 3:
  - Issue 2 fixes tools (good foundation)
  - Issue 1 adds orchestrator logic (but no JSON contract yet)
  - Issue 3 defines JSON (now must update Issue 1 orchestrator)
  - RESULT: Issue 1 re-done after Issue 3; wasted work

Fix Issue 2 → Issue 3 → Issue 1 (RECOMMENDED):
  - Issue 2 fixes tools (foundation solid)
  - Issue 3 defines JSON contract (specialists know format)
  - Issue 1 adds orchestrator (can rely on fixed tools + JSON format)
  - RESULT: Linear dependencies; each step builds on previous
```

---

## The Correct Order: Why 2 → 3 → 1 Works

```
PHASE 1: TOOL COMPLIANCE (Issue 2)
  ├─ Audit all droids
  ├─ Replace non-compliant tools
  ├─ Test with Factory Bridge
  └─ Result: Foundation is solid; all droids use correct tools

PHASE 2: STRUCTURED OUTPUTS (Issue 3)
  ├─ Define JSON schema for each specialist
  ├─ Add to droid prompts: "Return as JSON"
  ├─ Test output format
  └─ Result: Specialists now output structured data

PHASE 3: WORKFLOW COORDINATION (Issue 1)
  ├─ Add Workflow Coordination section to intelligence-orchestrator
  ├─ Implement parsing: specialists output JSON (guaranteed by Phase 2)
  ├─ Implement synthesis: intelligently combine structured findings
  ├─ Test end-to-end
  └─ Result: Full automation; no extra guidance needed

Each phase:
  ✓ Depends on previous phase
  ✓ Adds value incrementally
  ✓ Can be validated independently
  ✓ No rework needed
```

---

## Second-Order Effects You Must Anticipate

| Effect                                          | Cause                                          | Prevention                                                        |
| ----------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------- |
| **Removing TodoWrite breaks droid planning**    | TodoWrite removed; no Planning Primitive       | Replace TodoWrite with narrative step-by-step planning in prompts |
| **Removing AskUserQuestion breaks automation**  | No way for specialists to ask clarifications   | Have orchestrator provide complete context upfront                |
| **Write → Create wrong for append operations**  | Some droids append to files, not create new    | Analyze each Write usage; may need Edit instead                   |
| **JSON parsing fails on malformed output**      | Specialist returns prose instead of JSON       | Add graceful fallback; log parsing errors for debugging           |
| **Specialist tools fail; orchestrator hangs**   | No error handling for tool failures            | Add timeout and fallback to partial analysis                      |
| **Integration summary location undefined**      | No standard path for output files              | Define: `.factory/analysis_results/{task_id}/summary.md`          |
| **Conflict between specialist recommendations** | Multiple specialists recommend different fixes | Define priority rule in orchestrator: severity > impact > effort  |
| **Output schema too rigid**                     | Specialist wants to add unexpected findings    | Add "additional_findings" field to JSON schema                    |

---

## Success Metrics

### Issue 2 (Tool Compliance)

- ✅ All 16 droids use only Factory tools
- ✅ No Claude-native tools remain
- ✅ All droid YAML validates against droid_tools.md
- ✅ Tested with Factory Bridge (not just Claude Code)

### Issue 3 (Structured Outputs)

- ✅ Each specialist returns JSON with defined schema
- ✅ Orchestrator can parse 100% of specialist outputs
- ✅ Fallback text parsing works for unexpected formats
- ✅ Parsing errors logged clearly

### Issue 1 (Workflow Coordination)

- ✅ intelligence-orchestrator.md has Workflow Coordination section
- ✅ Can invoke specialists with structured task descriptions
- ✅ Can capture and parse specialist outputs
- ✅ Can synthesize integration summary automatically
- ✅ "Without extra guidance" requirement met

---

## Implementation Checklist

### Phase 1: Tool Compliance (Hours 1-9)

- [ ] Audit all 16 droids for non-compliant tools
- [ ] Create tool replacement mapping document
- [ ] Batch 1: Remove TodoWrite, AskUserQuestion, NotebookEdit from all droids
- [ ] Batch 2: Replace Bash → Execute, WebFetch → FetchUrl, KillShell → Kill Process
- [ ] Batch 3: Context-analyze Write usage; replace with Create or Edit
- [ ] Validate: All droid YAML against droid_tools.md
- [ ] Test: Run each droid with sample task in Factory Bridge
- [ ] Document: Changes to droid prompts explaining tool availability

### Phase 2: Structured Outputs (Hours 10-15)

- [ ] Define JSON output schema for each specialist droid (6 specialists)
- [ ] Add output contract to each specialist's prompt
- [ ] Create example JSON outputs for documentation
- [ ] Test: Run each specialist; capture and validate JSON output
- [ ] Document: Standard output format in .factory/docs/

### Phase 3: Workflow Coordination (Hours 16-19)

- [ ] Add Workflow Coordination section to intelligence-orchestrator.md
- [ ] Implement specialist selection decision tree
- [ ] Implement output parsing logic (JSON + fallback)
- [ ] Implement integration summary generation
- [ ] Define file output location: `.factory/analysis_results/`
- [ ] End-to-end test: Full multi-specialist analysis workflow
- [ ] Document: Updated intelligence-orchestrator with examples

### Final Validation (Hours 20-21)

- [ ] Run full integration test with all 6 specialists
- [ ] Verify orchestrator can handle specialist failures gracefully
- [ ] Verify output files created in correct location
- [ ] Verify integration summary is complete and accurate
- [ ] Test conflicting recommendations are resolved correctly
