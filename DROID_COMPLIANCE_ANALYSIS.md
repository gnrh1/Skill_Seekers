# Droid Compliance & Workflow Coordination Analysis

## Multi-Modal Adjudication of 3 Interrelated Issues

**Date**: November 21, 2025  
**Scope**: intelligence-orchestrator, tool compliance, structured outputs  
**Mental Models Applied**: First Principles, Inversion, Systems Thinking, Second-Order Effects

---

## ISSUE INVENTORY

### Issue 1: Workflow Coordination Missing

- **Current State**: intelligence-orchestrator.md has _documentation_ of strategies but no _executable_ delegation framework
- **Gap**: No standardized way to capture specialist outputs and synthesize integration summaries
- **Status**: Documented but not formalized as scripted pattern

### Issue 2: Tool Compliance Violations

- **Current State**: Multiple droids use Claude-native tools instead of Factory-compliant tools
- **Non-Compliant Tools Found** (across 16 droids):
  - `Write` (Claude) → Factory equivalent: `Create` or `Edit`
  - `WebFetch` (Claude) → Factory equivalent: `FetchUrl`
  - `AskUserQuestion` (Claude) → Factory has no equivalent (requires removal or redesign)
  - `TodoWrite` (Claude) → Factory equivalent: Planning primitive (no direct tool)
  - `Glob` (Listed in Factory, but listed in some droids as valid)
  - `BashOutput`, `KillShell` (Non-standard, not in droid_tools.md glossary)
  - `NotebookEdit` (Claude-specific, no Factory equivalent)

### Issue 3: Structured Output Contracts Missing

- **Current State**: Droids provide prose recommendations but no machine-readable output format
- **Gap**: intelligence-orchestrator cannot programmatically parse and synthesize specialist findings
- **Consequence**: Manual labor required to extract insights; fails "without extra guidance" requirement

---

## MENTAL MODEL 1: FIRST PRINCIPLES

**Question: What is the fundamental problem each issue represents?**

### Issue 1 Fundamental Problem

"How do we make multi-domain coordination _automatic_ without requiring manual guidance on each invocation?"

**Root Cause**: Coordination is described in prose (strategies) but not mechanized. When intelligence-orchestrator delegates, it has no _executable specification_ for how to capture, parse, and synthesize outputs.

**First Principles Solution**:

- Define explicit delegation contract (what to ask, what format to expect)
- Define output parsing rule (how to extract structured data)
- Define synthesis rule (how to combine findings)

### Issue 2 Fundamental Problem

"How do we ensure droids use only Factory-native capabilities, not Claude-native ones?"

**Root Cause**: Droids were created by mapping Claude Code agent tools directly. Factory tools are a _subset_ of Claude tools with different names and different semantics.

**First Principles Solution**:

- Accept that some Claude tools have NO Factory equivalent (e.g., `AskUserQuestion`)
- For tools with equivalents, rename them standardly
- For tools without equivalents, either remove or redesign the capability

### Issue 3 Fundamental Problem

"How do specialists communicate structured findings instead of prose?"

**Root Cause**: No output contract. Droids write recommendations in natural language; intelligence-orchestrator reads prose and manually synthesizes.

**First Principles Solution**:

- Define structured output format (JSON/YAML)
- Add to droid prompts: "Return findings as structured data"
- Intelligence-orchestrator: parse, merge, synthesize

---

## MENTAL MODEL 2: INVERSION (What Could Go Wrong?)

### Failure Mode 1: Workflow Coordination Breaks

**Inversion**: What if intelligence-orchestrator cannot reliably parse specialist outputs?

| Scenario                                            | Consequence                                          | Likelihood                  |
| --------------------------------------------------- | ---------------------------------------------------- | --------------------------- |
| Specialist returns prose instead of structured data | Orchestrator can't programmatically extract findings | HIGH if no output contract  |
| Specialist tool fails mid-analysis                  | No partial output captured                           | MEDIUM if no error handling |
| Multiple specialists return conflicting findings    | Orchestrator can't prioritize or reconcile           | HIGH if no decision rule    |

**Mitigation**:

- Enforce structured output via task description
- Add fallback: if structured output fails, parse prose (graceful degradation)
- Define conflict resolution rule in intelligence-orchestrator

### Failure Mode 2: Tool Compliance Creates Model Incompatibility

**Inversion**: What if a droid lists `Write` in its tools but Factory only has `Edit` and `Create`?

| Scenario                                                         | Consequence                       | Likelihood |
| ---------------------------------------------------------------- | --------------------------------- | ---------- |
| Factory Bridge tries to invoke `Write`                           | Tool invocation fails             | HIGH       |
| Droid asks user "Which tool did you mean?"                       | Breaks automation model           | HIGH       |
| Droid uses wrong tool (`Edit` instead of `Create` for new files) | Creates wrong files or overwrites | MEDIUM     |

**Mitigation**:

- Audit all droids: replace non-compliant tool names
- Add validation script: check droid YAML against droid_tools.md glossary
- For tools without equivalents (e.g., `AskUserQuestion`), remove from tool list and redesign prompt

### Failure Mode 3: Missing Output Contracts Cascade

**Inversion**: What if test-generator returns test code but intelligence-orchestrator expects JSON?

| Scenario                                              | Consequence                         | Likelihood |
| ----------------------------------------------------- | ----------------------------------- | ---------- |
| intelligence-orchestrator tries to parse code as JSON | JSON decode error                   | HIGH       |
| Orchestrator ignores test-generator findings          | Incomplete analysis                 | HIGH       |
| Manual workaround added (parse prose)                 | Adds complexity, defeats automation | MEDIUM     |

**Mitigation**:

- Define output contract BEFORE adding specialists
- Test contract: have specialist provide sample output
- intelligence-orchestrator: validate output format before parsing

---

## MENTAL MODEL 3: SYSTEMS THINKING

**Question: How do the 3 issues interact as a system?**

### Current System State (Broken Feedback Loop)

```
intelligence-orchestrator (wants structured outputs)
    ↓ (sends vague task descriptions)
    ├─ code-analyzer (uses non-compliant tools: Write, WebFetch, TodoWrite)
    │    ↓ (returns prose findings)
    ├─ performance-auditor (uses non-compliant tools: Write, Bash, BashOutput)
    │    ↓ (returns prose findings)
    └─ test-generator (uses non-compliant tools: Write, Glob, NotebookEdit)
         ↓ (returns prose findings)

    ↓ (tries to synthesize)
    ❌ BLOCKED: No parsing rule
    ↓ (falls back to manual review)
    ❌ Result: Defeats "without extra guidance" requirement
```

**Second-Order Effects**:

1. **Tool Violations Don't Fail Immediately**: Droids might work in Claude Code but fail in Factory Bridge (hidden until deployment)
2. **Output Format Inconsistency Accumulates**: Each droid returns findings differently; orchestrator needs custom parser for each
3. **Workflow Coordination Incomplete**: intelligence-orchestrator can't form stable feedback loops; new specialists break integration
4. **Dependency Chain**: Fixing workflow coordination requires fixing output contracts, which requires fixing tool compliance

### Desired System State (Stable Feedback Loop)

```
intelligence-orchestrator (scripted delegation)
    ↓ (sends structured task with output contract)
    ├─ code-analyzer (uses only Factory tools: Read, Edit, Bash, Grep)
    │    ↓ (returns JSON: {findings, recommendations, priority})
    ├─ performance-auditor (uses only Factory tools: Read, Bash, Grep)
    │    ↓ (returns JSON: {bottlenecks, metrics, roi})
    └─ test-generator (uses only Factory tools: Read, Create, Execute)
         ↓ (returns JSON: {test_plan, coverage, strategy})

    ↓ (parses structured outputs)
    ✅ SUCCESS: JSON parsing succeeds
    ↓ (synthesizes findings)
    ✅ SUCCESS: Integration summary generated automatically
    ↓ (can loop: capture feedback, refine droids)
    ✅ STABLE: Workflow coordination works end-to-end
```

**Systems Insight**: The three issues form a **causal chain**:

- Tool compliance violations → Factory Bridge failures → orchestrator can't invoke droids reliably
- Structured outputs missing → orchestrator can't parse findings → synthesis requires manual work
- Workflow coordination undefined → orchestrator doesn't know when to invoke which droids → no feedback loop

**Implication**: Fixing in reverse order (3 → 2 → 1) vs. forward order (1 → 2 → 3) has different risks:

- **Forward** (1 → 2 → 3): Define workflow coordination first, then discover tool/output gaps as you try to implement it
- **Reverse** (3 → 2 → 1): Fix tool compliance first (hard requirement), then add output contracts, then integrate into workflow

**Recommendation**: **Reverse order is safer** (3 ← 2 ← 1) because it validates prerequisites before building on them.

---

## MENTAL MODEL 4: DEPENDENCY ANALYSIS

**Question: What must exist for each issue to be solved?**

### Dependency Graph: Tool Compliance (Issue 2)

```
droid_tools.md (source of truth)
    ↓ provides: Factory tool glossary
    ↓
Must Have: Tool name mapping (Claude → Factory)
    ├─ Write → Create OR Edit (depends on context)
    ├─ WebFetch → FetchUrl
    ├─ Bash → Execute Process
    ├─ Glob → Glob (already compliant)
    ├─ TodoWrite → ??? (no equivalent; requires removal)
    ├─ AskUserQuestion → ??? (no equivalent; requires removal)
    ├─ BashOutput → ??? (custom; not in glossary)
    ├─ KillShell → Kill Process (probably intended)
    └─ NotebookEdit → ??? (no Factory equivalent; remove)

    ↓
Must Do: Update all droids' tool lists
    ├─ Audit: which droids list which tools
    ├─ Replace: Claude tool names with Factory equivalents
    ├─ Remove: tools without Factory equivalents
    └─ Validate: droid YAML against droid_tools.md

    ↓
Result: All droids use only Factory-native tools
```

**Hard Dependency**: droid_tools.md must be **source of truth**. All droids validate against it.

### Dependency Graph: Structured Outputs (Issue 3)

```
Output Format Standard (must define)
    ├─ code-analyzer → JSON: {findings: [...], recommendations: [...], priority: "high|medium|low"}
    ├─ performance-auditor → JSON: {bottlenecks: [...], metrics: {...}, roi: number}
    ├─ test-generator → JSON: {test_plan: string, coverage: number, strategy: string}
    ├─ architectural-critic → JSON: {patterns: [...], boundaries: [...], transitions: [...]}
    ├─ security-analyst → JSON: {vulnerabilities: [...], severity: [...], fixes: [...]}
    └─ cognitive-resonator → JSON: {coherence_score: number, patterns: [...], alignment: [...]}

    ↓
Must Exist: Droid prompts explicitly require structured output
    ├─ code-analyzer: "DELIVERABLE: Return findings as JSON..."
    ├─ performance-auditor: "DELIVERABLE: Return bottlenecks as JSON..."
    └─ test-generator: "DELIVERABLE: Return test plan as JSON..."

    ↓
Must Exist: intelligence-orchestrator parsing function
    ├─ Read output files
    ├─ Parse JSON from each specialist
    ├─ Validate schema
    ├─ Merge into unified structure
    └─ Generate integration summary

    ↓
Result: intelligence-orchestrator can programmatically process findings
```

**Hard Dependency**: Output format standard must be **defined first**, then added to each droid.

### Dependency Graph: Workflow Coordination (Issue 1)

```
Workflow Coordination Section (requires Issue 2 & 3 resolved)
    ↓ depends on: Tool compliance (Issue 2) ✓
    ↓ depends on: Structured output contracts (Issue 3) ✓

    ├─ Specialist Delegation Framework (when to invoke which droid)
    ├─ Structured Output Capture (how to parse specialist results)
    ├─ Integration Summary Template (how to synthesize findings)
    └─ Decision Tree (which specialists for which tasks)

    ↓
Result: intelligence-orchestrator.md contains scripted pattern
    ├─ Phase 1: Define scope (which specialists, what analysis)
    ├─ Phase 2: Delegate with output contracts (invoke droids)
    ├─ Phase 3: Parse and synthesize (generate integration summary)
    └─ Every invocation follows same pattern (no extra guidance needed)
```

**Soft Dependency**: Issue 1 can be _documented_ before Issue 2 & 3 are fixed, but it won't _work_ until they're fixed.

**VERDICT**:

- **Hard blocker**: Issue 2 (tool compliance) must be fixed first
- **Soft blocker**: Issue 3 (output contracts) should be designed in parallel, fixed before Issue 1
- **Enabler**: Issue 1 (workflow coordination) can be documented in parallel but implemented last

---

## SECOND-ORDER EFFECTS (The Tricky Parts)

### Second-Order Effect 1: Removing `TodoWrite` Breaks Planning

- **First Order**: `TodoWrite` is not Factory-compliant → remove it
- **Second Order**: Droids use `TodoWrite` to track their internal planning (multi-step analysis)
- **Consequence**: If removed, droids lose planning capability
- **Mitigation**: Replace with "Planning Primitive" (documented in droid_tools.md as non-tool approach)

### Second-Order Effect 2: Removing `AskUserQuestion` Requires Redesign

- **First Order**: `AskUserQuestion` is Claude-specific → no Factory equivalent
- **Second Order**: Some droids (orchestrator-agent, test-generator) use it to ask for clarification
- **Consequence**: Specialist droids can't ask clarifying questions; orchestrator must provide complete context
- **Mitigation**: Update intelligence-orchestrator to provide comprehensive context upfront; remove `AskUserQuestion` from specialists

### Second-Order Effect 3: Structured Outputs Reduce Flexibility

- **First Order**: Define JSON output format → droids must return structured data
- **Second Order**: Droids can't add new insights not in the JSON schema
- **Consequence**: Specialists constrained to predefined output format; may miss important findings
- **Mitigation**: Add "additional_findings" field to JSON schema for unforeseen insights

### Second-Order Effect 4: Output Validation Can Fail Silently

- **First Order**: intelligence-orchestrator validates specialist outputs as JSON
- **Second Order**: If specialist returns malformed JSON, orchestrator discards it (doesn't fail loudly)
- **Consequence**: Missing findings without clear error message
- **Mitigation**: Require intelligence-orchestrator to log parsing failures and attempt text fallback

### Second-Order Effect 5: Tool Compliance Audit Reveals Inconsistency

- **First Order**: Replace `Write` with `Edit` or `Create`
- **Second Order**: Some droids use `Write` to _append_ (neither `Edit` nor `Create` are append operations)
- **Consequence**: Droids can't implement append-to-file patterns
- **Mitigation**: Define append semantics in `Edit` tool documentation; clarify when to use `Create` (new) vs `Edit` (modify)

### Second-Order Effect 6: Workflow Coordination Requires Orchestrator Changes

- **First Order**: Add "Workflow Coordination" section to intelligence-orchestrator
- **Second Order**: intelligence-orchestrator now has mutation tools (Create, Edit, ApplyPatch); it can write integration summaries
- **Consequence**: Integration summaries are generated files, not just printed text
- **Mitigation**: Define file location standard: `.factory/analysis_results/{analysis_id}/integration-summary.md`

---

## IMPLEMENTATION ROADMAP

### Phase 1: Tool Compliance Audit & Fix (Week 1)

**Step 1.1**: Create tool mapping document

```
Tool Mapping (Claude → Factory):
- Write → Edit (modify) OR Create (new)
- WebFetch → FetchUrl
- Bash → Execute Process
- Glob → Glob ✓
- TodoWrite → Remove (use Planning Primitive instead)
- AskUserQuestion → Remove (provide context upfront)
- BashOutput → Remove (Bash tool returns output)
- KillShell → Kill Process
- NotebookEdit → Remove (no Factory equivalent)
```

**Step 1.2**: Audit all 16 droids

```
For each droid:
- Read tools list
- Check against mapping
- Identify replacements
- Document special cases
```

**Step 1.3**: Fix droids (batch replacements)

```
- Replace Write → Edit (where appropriate)
- Replace WebFetch → FetchUrl
- Remove AskUserQuestion, TodoWrite, BashOutput, NotebookEdit
- Update Bash → Execute Process (if needed)
- Update tool descriptions in droid prompts
```

**Step 1.4**: Validate with script

```
Script: check if all droid tools exist in droid_tools.md glossary
Output: Pass/Fail for each droid
```

### Phase 2: Structured Output Contracts (Week 1-2)

**Step 2.1**: Define output format standard

````markdown
# Output Format Standard for Factory Droids

## code-analyzer Output

```json
{
  "domain": "code-analysis",
  "files_analyzed": ["src/file1.py", "src/file2.py"],
  "complexity_metrics": {
    "avg_cyclomatic": 6.2,
    "avg_cognitive": 5.1
  },
  "findings": [
    {
      "type": "high_complexity",
      "location": "src/file1.py:45",
      "severity": "medium"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "Refactor function X",
      "impact": "Reduce complexity by 40%"
    }
  ]
}
```
````

## (Similar structures for all other droids)

````

**Step 2.2**: Add output requirements to each droid prompt
```markdown
# In each droid's "MANDATORY TOOL USAGE REQUIREMENTS" section:

## OUTPUT DELIVERABLE (MANDATORY)

When analysis is complete, you MUST return findings in the following JSON structure:
\`\`\`json
{domain, files_analyzed, findings, recommendations, priority}
\`\`\`

This structured output is required for integration with intelligence-orchestrator.
If structured output is impossible, return as JSON with "parsing_mode": "text" and raw text in "text_findings" field.
````

**Step 2.3**: Test output contracts

```
For each droid:
- Invoke with test task
- Capture output
- Validate JSON schema
- Ensure all required fields present
- Document any parsing failures
```

### Phase 3: Workflow Coordination Section (Week 2)

**Step 3.1**: Add "Workflow Coordination" section to intelligence-orchestrator
(Use the comprehensive pattern defined in earlier analysis)

**Step 3.2**: Define delegation decision tree

```markdown
## Specialist Selection Decision Tree

1. Analyzing code structure/quality? → code-analyzer
2. Evaluating system design/boundaries? → architectural-critic
3. Finding performance issues? → performance-auditor
4. Designing test strategy? → test-generator
5. Reviewing security? → security-analyst
6. Analyzing developer experience? → cognitive-resonator
```

**Step 3.3**: Implement orchestrator parsing logic

````python
def parse_specialist_output(output_text: str) -> Dict:
    """Parse specialist output as JSON with graceful degradation."""
    try:
        # Try to extract JSON from output
        json_match = re.search(r'```json\n(.*?)\n```', output_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
    except json.JSONDecodeError:
        # Fallback: return raw output
        return {"parsing_mode": "text", "raw_output": output_text}
````

**Step 3.4**: Implement integration summary generation

```python
def synthesize_integration_summary(specialist_outputs: Dict[str, Dict]) -> str:
    """Synthesize findings from all specialists."""
    # Merge domain findings
    # Identify cross-domain patterns
    # Detect conflicts and dependencies
    # Generate structured summary
    # Write to .factory/analysis_results/
```

### Phase 4: Validation & Testing (Week 2)

**Step 4.1**: End-to-end test

```
Task: "Analyze src/doc_scraper.py for code quality, performance, testing, and security"

Expected:
1. intelligence-orchestrator invokes all 5 specialists
2. Each specialist returns structured output
3. Orchestrator parses all 5 outputs
4. Integration summary generated
5. Summary includes cross-domain insights
```

**Step 4.2**: Failure scenario testing

```
Scenario 1: One specialist fails → others succeed, partial summary generated
Scenario 2: One specialist returns prose instead of JSON → fallback parsing
Scenario 3: Conflicting recommendations → prioritize by severity/impact
```

**Step 4.3**: Documentation

```
- Update intelligence-orchestrator.md
- Document output format standard in .factory/docs/
- Add examples of specialist outputs
- Create troubleshooting guide
```

---

## RISK ASSESSMENT

| Risk                                          | Severity | Mitigation                            | Timeline |
| --------------------------------------------- | -------- | ------------------------------------- | -------- |
| Tool compliance breaks Factory integration    | HIGH     | Audit early, test in Factory Bridge   | Week 1   |
| Specialist output format incomplete           | MEDIUM   | Define schema first, test outputs     | Week 1-2 |
| Workflow coordination doesn't work end-to-end | MEDIUM   | Full integration test before rollout  | Week 2   |
| Removing tools breaks existing workflows      | MEDIUM   | Search for tool usage, update prompts | Week 1   |
| Output parsing fails on unexpected formats    | LOW      | Graceful fallback to text parsing     | Week 2   |

---

## CONCLUSION

**Optimal Fix Sequence** (addressing all three issues):

1. **Issue 2 First** (Tool Compliance): Hard blocker; Foundation for everything else

   - Audit droids
   - Replace non-compliant tool names
   - Validate against droid_tools.md
   - **Timeline**: 3-4 hours

2. **Issue 3 In Parallel** (Structured Outputs): Enables Issue 1

   - Define output format standard
   - Add to each droid prompt
   - Test output contracts
   - **Timeline**: 4-5 hours

3. **Issue 1 Last** (Workflow Coordination): Brings it all together
   - Add section to intelligence-orchestrator
   - Implement parsing and synthesis logic
   - End-to-end testing
   - **Timeline**: 3-4 hours

**Total Effort**: 10-13 hours across 2 weeks

**Key Success Factor**: Issues are interdependent. Fixing them in reverse order (2 → 3 → 1) ensures each layer is solid before building the next.
