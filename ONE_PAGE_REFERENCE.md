# ONE-PAGE REFERENCE: 3 Issues × 4 Mental Models × 12 Second-Order Effects

## THE 3 ISSUES

| Issue                              | What's Wrong                                             | Fix Required                                                  | Blocker?        | Timeline |
| ---------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------- | --------------- | -------- |
| **Issue 2: Tool Compliance**       | 16 droids use Claude tools (Write, Bash, WebFetch, etc.) | Use Factory tools only (Create/Edit, Execute, FetchUrl, etc.) | **HARD**        | 5-9 hrs  |
| **Issue 3: Structured Outputs**    | Droids return prose; can't be parsed                     | Return JSON with defined schema                               | Enables Issue 1 | 4-5 hrs  |
| **Issue 1: Workflow Coordination** | Automation described, not implemented                    | Scripted delegation + parsing + synthesis                     | Capstone        | 3-4 hrs  |

---

## 4 MENTAL MODELS: The Analysis

### 1️⃣ FIRST PRINCIPLES: "What's the core problem?"

- Issue 2: How to make droids Factory-native only?
- Issue 3: How to communicate structured findings?
- Issue 1: How to automate without manual guidance?

### 2️⃣ INVERSION: "What breaks if we don't fix?"

- Issue 2 unfixed → Factory Bridge rejects tools → orchestrator can't invoke droids
- Issue 3 unfixed → Unparseable output → orchestrator synthesis impossible
- Issue 1 unfixed → Manual coordination required each time

### 3️⃣ SYSTEMS THINKING: "How do they interact?"

```
Issue 2 (Tools)
  ↓ enables ↓
Issue 3 (Outputs)
  ↓ enables ↓
Issue 1 (Coordination)
```

**Insight**: Fixing out of order = rework. Must be sequential.

### 4️⃣ DEPENDENCY ANALYSIS: "What must exist first?"

| Dependency                        | Hard/Soft | Issue |
| --------------------------------- | --------- | ----- |
| droid_tools.md as source of truth | HARD      | 2     |
| Factory tools available           | HARD      | 2     |
| Output format standard            | SOFT      | 3     |
| Integration template              | SOFT      | 1     |

---

## 🔗 THE DEPENDENCY CHAIN

```
┌─────────────────────────────────────┐
│ Issue 2: Tool Compliance (5-9 hrs) │
│ FIX FIRST: Hard blocker            │
└─────────────┬───────────────────────┘
              │
              ↓ enables
┌─────────────────────────────────────┐
│ Issue 3: Structured Outputs (4-5) │
│ FIX SECOND: Enables Issue 1        │
└─────────────┬───────────────────────┘
              │
              ↓ enables
┌─────────────────────────────────────┐
│ Issue 1: Workflow Coordination (3-4)│
│ FIX THIRD: Brings it all together  │
└─────────────────────────────────────┘
```

---

## ⚠️ 12 SECOND-ORDER EFFECTS (The Tricky Parts)

### From Issue 2 (Tool Compliance)

| Effect                                    | Cause                                 | Mitigation                                     |
| ----------------------------------------- | ------------------------------------- | ---------------------------------------------- |
| TodoWrite removal breaks planning         | No Factory equivalent                 | Replace with narrative steps in prompts        |
| AskUserQuestion removal breaks automation | Factory has no equivalent             | Orchestrator provides complete context upfront |
| Write → Create/Edit is context-dependent  | Some Write = create, some = append    | Analyze each droid; determine intent manually  |
| Tool examples become outdated             | Names change; examples show old names | Update all examples throughout droid prompts   |

### From Issue 3 (Structured Outputs)

| Effect                              | Cause                                    | Mitigation                                |
| ----------------------------------- | ---------------------------------------- | ----------------------------------------- |
| JSON schema limits flexibility      | Fixed format can't handle new findings   | Add "additional_findings" field to schema |
| JSON parsing fails silently         | Bad format returns no error              | Add graceful fallback + error logging     |
| Output format reveals inconsistency | Different specialists report differently | Standardize format before Issue 2 fix     |
| Validation adds latency             | Schema checking takes time               | Optimize parsing logic; cache results     |

### From Issue 1 (Workflow Coordination)

| Effect                            | Cause                                      | Mitigation                                     |
| --------------------------------- | ------------------------------------------ | ---------------------------------------------- |
| Requires file output location     | Integration summaries must go somewhere    | Define: `.factory/analysis_results/{task_id}/` |
| Assumes all specialists available | Any specialist failure breaks workflow     | Handle failures; provide partial analysis      |
| Decision tree can conflict        | Multiple specialists apply to same task    | Define priority: severity > impact > effort    |
| Synthesis needs complex logic     | Identifying conflicts/dependencies is hard | Add cross-domain synthesis algorithm           |

---

## ✅ EXECUTION ROADMAP: 12-18 Hours Total

### PHASE 1: Tool Compliance (5-9 hours)

```
Batch 1: Remove non-compliant (TodoWrite, AskUserQuestion, etc.)      30 min
Batch 2: Simple replacements (Bash→Execute, WebFetch→FetchUrl, etc.) 30 min
Batch 3: Context-dependent replacements (Write→Create/Edit analysis) 2-3 hrs
Validation & Factory Bridge testing                                    1 hr
TOTAL: 5-9 hours
```

**Outcome**: Solid foundation; Factory Bridge can invoke all droids

### PHASE 2: Structured Outputs (4-5 hours)

```
Define JSON schema for 6 specialists                  1 hr
Add output contracts to droid prompts                 1 hr
Create example outputs                                1 hr
Test specialist output capture                        1-2 hrs
TOTAL: 4-5 hours
```

**Outcome**: Specialists output structured data; ready for parsing

### PHASE 3: Workflow Coordination (3-4 hours)

```
Add Workflow Coordination section to orchestrator     1 hr
Implement specialist selection decision tree         30 min
Implement parsing + synthesis logic                   1 hr
End-to-end testing                                    1 hr
TOTAL: 3-4 hours
```

**Outcome**: Full automation; no manual guidance needed

### PHASE 4: Validation (1-2 hours)

```
Integration testing with all specialists             1 hr
Failure scenario testing                             30 min
Final documentation                                  30 min
TOTAL: 1-2 hours
```

---

## 🚨 CRITICAL SUCCESS FACTORS

| Factor                       | Why It Matters             | How to Ensure                       |
| ---------------------------- | -------------------------- | ----------------------------------- |
| **Don't skip order**         | Wrong order = rework       | Fix Issue 2 → 3 → 1 (not any other) |
| **Don't ignore SOE**         | Cascades affect next phase | Review 12 effects; plan mitigations |
| **Don't underestimate**      | 12-18 hrs is realistic     | Don't try to do it in 2 hours       |
| **Test with Factory Bridge** | Tools fail in FB not Code  | Test each droid after changes       |

---

## 📋 QUICK START CHECKLIST

### This Week

- [ ] Read ANALYSIS_COMPLETE_SUMMARY.md (5 min overview)
- [ ] Read ISSUE_2_ACTION_ITEMS.md (execution plan)
- [ ] Backup droids: `cp -r .factory/droids .factory/droids.backup`
- [ ] Start Phase 1, Batch 1 (remove non-compliant tools)

### Next Week

- [ ] Batch 2 & 3 (tool replacements + testing)
- [ ] Phase 2 (output contracts)
- [ ] Phase 3 (workflow coordination)
- [ ] Phase 4 (validation)

---

## 📊 SUCCESS METRICS

| Issue       | Success Criteria                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| **Issue 2** | ✅ All 16 droids use Factory tools only ✅ Factory Bridge can invoke droids ✅ Each tested with sample task |
| **Issue 3** | ✅ All 6 specialists return JSON ✅ Orchestrator parses 100% ✅ Graceful fallback works                     |
| **Issue 1** | ✅ Auto-coordinates without guidance ✅ Integration summaries generated ✅ End-to-end tested                |

---

## 🔗 DOCUMENT MAP

| Document                        | Read For                | Time       |
| ------------------------------- | ----------------------- | ---------- |
| ANALYSIS_COMPLETE_SUMMARY.md    | Quick overview          | 5 min      |
| **ISSUE_2_ACTION_ITEMS.md**     | **Immediate execution** | **20 min** |
| DROID_COMPLIANCE_ANALYSIS.md    | Deep analysis           | 30 min     |
| ISSUE_INTERDEPENDENCY_VISUAL.md | Visual understanding    | 10 min     |
| DROID_TOOL_COMPLIANCE_AUDIT.md  | Audit reference         | 5 min      |
| DROID_ANALYSIS_INDEX.md         | Navigation guide        | 5 min      |

---

## 🎯 THE BOTTOM LINE

✅ **3 issues form a causal chain** - Fix in sequence: 2 → 3 → 1  
✅ **Identified 12 second-order effects** - Each has mitigation  
✅ **Clear execution roadmap** - 12-18 hours across 2 weeks  
✅ **Success criteria defined** - Know when you're done

**Next Step**: Open ISSUE_2_ACTION_ITEMS.md and start Phase 1.

You've got this! 🚀
