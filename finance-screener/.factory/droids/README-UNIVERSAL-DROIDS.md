# Universal Droids - Finance-Screener Adaptation

## Summary

Successfully adapted 6 universal routine droids from root repository for financial-screener ecosystem. All droids:
- ✅ Customized for financial-domain specific analysis
- ✅ Removed Task tool (no inter-droid delegation, only with orchestrator)
- ✅ Consistent model: `custom:GLM-4.6-[Z.AI-Coding-Plan]-0`
- ✅ Option C artifact protocol (file-based, no response size limits)
- ✅ No external dependencies on root droids

## Adapted Droids

### 1. code-analyzer-finance.md
**Purpose:** Deep code quality analysis for financial-screener
**Focus Areas:**
- SQL generation quality (query complexity, JOIN efficiency, parameter binding)
- RAG pipeline complexity (embedding quality, retrieval latency, reranking)
- Data validation robustness (decimal precision, NULL handling, edge cases)
- API integration reliability (error handling, retry logic, rate limiting)
- Coupling analysis (SQL↔DB, RAG↔retriever, API↔pipeline)

**Key Metrics:**
- Cyclomatic complexity of SQL generation
- Decimal precision handling (float vs Decimal)
- Query latency benchmarks
- Validation edge case coverage

**Output:** `.factory/memory/code-analyzer-finance-{ISO8601-timestamp}.json`
**Tools:** Read, Create, Grep, Glob, Execute, FetchUrl (no Task)

### 2. test-generator-finance.md
**Purpose:** Comprehensive test generation using T.E.S.T. methodology
**Test Categories:**
- SQL generation (18 tests): correctness, SQL injection, performance
- RAG retrieval (15 tests): embedding quality, latency, fallback strategies
- Data validation (16 tests): edge cases, precision, extreme values
- SEC API (10 tests): rate limiting, error recovery, consistency
- Pipeline integration (8 tests): end-to-end workflows

**Key Scenarios:**
- Zero/negative stock prices
- Extreme price movements (>50% daily)
- Currency symbol parsing
- Stock split adjustments
- Missing/corrupted data

**Output:** `.factory/memory/test-generator-finance-{ISO8601-timestamp}.json`
**Tools:** Read, Create, Grep, Glob, Execute, FetchUrl (no Task)

### 3. architectural-critic-finance.md
**Purpose:** Detect architectural phase boundaries before system breakdown
**Analysis Areas:**
- Phase boundary detection (when architecture approaches limits)
- Bottleneck identification (SQL, RAG, API, validation)
- Coupling risk analysis (interdependencies)
- Scaling recommendations (sharding, partitioning, caching)
- Trade-off analysis (consistency vs speed, memory vs latency)

**Phase Boundaries:**
- Database: 120GB current, 500GB phase limit (sharding needed)
- RAG vectors: 50K chunks, latency 380ms (p95 500ms limit)
- SEC API: 65% rate limit utilization (90% unsustainable)
- SQL generation: 150 q/s (500 q/s phase limit)

**Output:** `.factory/memory/architectural-critic-finance-{ISO8601-timestamp}.json`
**Tools:** Read, Create, Glob, Grep, Execute, FetchUrl (no Task)

### 4. performance-auditor-finance.md
**Purpose:** Systematic performance optimization with ROI calculations
**Profiling Focus:**
- SQL generation latency (target: <50ms)
- RAG retrieval p95 latency (target: <500ms)
- Database query execution (target: <300ms aggregations)
- SEC API response time (including network)
- Validation overhead (target: <50ms for 500 rules)

**Optimization Framework (P.E.R.F.):**
- **P**rofile: Measure current performance per component
- **E**xamine: Identify bottlenecks with root cause analysis
- **R**ecommend: Prioritize by ROI (latency × usage / effort)
- **F**ollow-up: Re-profile after optimization

**Output:** `.factory/memory/performance-auditor-finance-{ISO8601-timestamp}.json`
**Tools:** Read, Create, Execute, Grep, Glob, FetchUrl (no Task)

### 5. security-analyst-finance.md
**Purpose:** Practical security analysis without requiring deep security expertise
**Analysis Categories:**
- SQL injection prevention (parameter binding, prepared statements)
- Authentication/authorization (CIK validation, user isolation)
- Financial data protection (encryption, PII handling, audit logging)
- SEC API security (credential protection, rate limit bypass prevention)
- Dependency security (CVE scanning, license compliance)

**Vulnerability Severity Levels:**
- Critical: Exploitable immediately (0-day risk)
- High: Serious exposure (API keys, database passwords)
- Medium: Significant risk (weak authentication, unvalidated input)
- Low: Minor issues (dependency updates, cleanup)

**Output:** `.factory/memory/security-analyst-finance-{ISO8601-timestamp}.json`
**Tools:** Read, Create, Glob, Grep, Execute, FetchUrl (no Task)

### 6. security-guardian-finance.md
**Purpose:** Prevent secret leaks and enforce security boundaries
**Detection Patterns:**
- API keys: `sk-`, `ghp_`, `Bearer`, `api.?key`
- Passwords: `password`, `passwd`, `pwd`, `pass=`
- Database: `DATABASE_URL`, `db_password`
- AWS: `AWS_ACCESS_KEY`, `AWS_SECRET`
- Google: `google_api_key`, `GOOGLE_APPLICATION_CREDENTIALS`

**Boundary Enforcement:**
- ❌ Never in source code: SEC API key, database password, AWS credentials
- ✅ Always environment variables: Secrets moved to `.env`, `os.getenv()`, Kubernetes secrets
- ✅ Git history: No secrets in commits (past or present)
- ✅ Config files: `.gitignore` configured, `.env.example` provided

**Output:** `.factory/memory/security-guardian-finance-{ISO8601-timestamp}.json`
**Tools:** Read, LS, Grep, Glob, Create, Edit, Execute, FetchUrl (no Task)

## Collaboration with Orchestrator

### When to Invoke Each Droid

**Code Quality Issues:**
```
finance-intelligence-orchestrator routes to:
→ code-analyzer-finance (analyze complexity)
→ performance-auditor-finance (profile bottlenecks)
```

**Testing Needs:**
```
finance-intelligence-orchestrator routes to:
→ test-generator-finance (generate comprehensive tests)
→ code-analyzer-finance (validate test quality)
```

**Architectural Review:**
```
finance-intelligence-orchestrator routes to:
→ architectural-critic-finance (phase boundaries)
→ performance-auditor-finance (bottleneck analysis)
```

**Security Concerns:**
```
finance-intelligence-orchestrator routes to:
→ security-guardian-finance (detect secrets)
→ security-analyst-finance (vulnerability assessment)
```

**Surgical Changes:**
```
finance-intelligence-orchestrator might route to:
→ precision-editor-finance (from main .factory/droids/)
(Note: precision-editor is not finance-specific, use root version for surgical edits)
```

## File Organization

```
finance-screener/.factory/droids/
├── finance-intelligence-orchestrator.md          (Master coordinator - existing)
├── code-analyzer-finance.md                      (Code quality specialist)
├── test-generator-finance.md                     (Test generation specialist)
├── architectural-critic-finance.md               (Architecture evolution specialist)
├── performance-auditor-finance.md                (Performance optimization specialist)
├── security-analyst-finance.md                   (Vulnerability analysis specialist)
├── security-guardian-finance.md                  (Secret detection specialist)
├── [Finance-specific droids: financial-data-sql-specialist, etc.]
└── README-UNIVERSAL-DROIDS.md                    (This file)
```

## Artifact Output Protocol (Option C)

All 6 universal droids follow Option C file-based artifact protocol:

**Step 1: Perform Analysis**
```
code-analyzer-finance reads source files, executes analysis
```

**Step 2: Write Artifact File**
```
.factory/memory/code-analyzer-finance-2025-11-21T16:30:12Z.json
(Complete JSON with all findings - NOT limited by response size)
```

**Step 3: Return Minimal Task Response**
```json
{
  "status": "completed",
  "artifact_path": ".factory/memory/code-analyzer-finance-2025-11-21T16:30:12Z.json",
  "summary": "Brief summary of findings"
}
```

**Step 4: Orchestrator Synthesis**
```
intelligence-orchestrator reads artifact files from .factory/memory/
Synthesizes findings across multiple droids
Writes synthesis to: .factory/memory/intelligence-orchestrator-{timestamp}.json
```

## Model Consistency

All 7 droids (6 universal + 1 orchestrator) use:
```
model: custom:GLM-4.6-[Z.AI-Coding-Plan]-0
```

Unified model provides:
- Consistent analysis quality across all droids
- Predictable performance characteristics
- Single model fine-tuning/training target
- Simplified deployment and versioning

## Tool Configuration

### code-analyzer-finance
```
tools: Read, Create, Grep, Glob, Execute, FetchUrl
(No Task - analysis only, no delegation)
```

### test-generator-finance
```
tools: Read, Create, Grep, Glob, Execute, FetchUrl
(No Task - test generation only, no delegation)
```

### architectural-critic-finance
```
tools: Read, Create, Glob, Grep, Execute, FetchUrl
(No Task - analysis only, no delegation)
```

### performance-auditor-finance
```
tools: Read, Create, Execute, Grep, Glob, FetchUrl
(No Task - profiling only, no delegation)
```

### security-analyst-finance
```
tools: Read, Create, Glob, Grep, Execute, FetchUrl
(No Task - analysis only, no delegation)
```

### security-guardian-finance
```
tools: Read, LS, Grep, Glob, Create, Edit, Execute, FetchUrl
(No Task - boundary enforcement only, no delegation)
```

**Note:** No droid includes `Task` tool. Only `intelligence-orchestrator` delegates using Task tool.

## Key Differences from Root Droids

### 1. Financial Domain Specificity
Root droids are generic; finance versions include:
- SQL generation analysis (security, correctness, performance)
- RAG pipeline optimization (for financial documents)
- SEC API integration concerns
- Financial data precision and validation
- Decimal handling (not float) for monetary values
- Stock split and corporate action handling

### 2. Artifact Protocol Option C
- Specialized for finance-screener Option C file-based protocol
- Artifact paths include `-finance` suffix
- Artifact content includes financial-specific metrics

### 3. No Task Tool
- Root droids may delegate to specialists via Task tool
- Finance versions perform all analysis independently
- Delegation only happens via orchestrator (finance-intelligence-orchestrator)

### 4. Zero External Dependencies
- Each finance droid is self-contained
- No imports from root droid files
- No cross-droid calls (only via orchestrator)
- Can be used independently or via orchestrator

## Integration Points

### With finance-intelligence-orchestrator
```
orchestrator reads .factory/droids/finance-intelligence-orchestrator.md
orchestrator delegates to: (all 6 universal droids above)
orchestrator synthesizes: outputs to .factory/memory/finance-intelligence-orchestrator-{timestamp}.json
```

### With finance-specific droids
These 6 universal droids complement existing finance-specific droids:

| Universal Droid | Complements | Financial-Specific Droid |
|---|---|---|
| code-analyzer-finance | Quality review | financial-data-sql-specialist |
| test-generator-finance | Test coverage | data-precision-validator |
| architectural-critic-finance | Scaling planning | pipeline-monitoring-specialist |
| performance-auditor-finance | Optimization | rag-hybrid-search-architect |
| security-analyst-finance | Vulnerability review | sec-filing-ingestion-specialist |
| security-guardian-finance | Secret prevention | (all droids) |

## Usage Examples

### Scenario 1: Code Review Before Merge
```
finance-intelligence-orchestrator receives: "Review PR #142 before merge"

Routes to:
→ code-analyzer-finance: Analyze code quality, anti-patterns
→ security-guardian-finance: Check for secrets
→ security-analyst-finance: Vulnerability scan
→ test-generator-finance: Verify test coverage

Synthesizes: Overall safety assessment, priority fixes, merge recommendation
```

### Scenario 2: Performance Optimization Sprint
```
finance-intelligence-orchestrator receives: "Optimize query latency"

Routes to:
→ performance-auditor-finance: Profile current latency, identify bottlenecks
→ architectural-critic-finance: Suggest scaling changes
→ code-analyzer-finance: Find optimization opportunities

Synthesizes: Ranked optimizations by ROI, effort estimates, implementation roadmap
```

### Scenario 3: New Feature Testing
```
finance-intelligence-orchestrator receives: "Generate tests for stock split feature"

Routes to:
→ test-generator-finance: Generate comprehensive test suite
→ code-analyzer-finance: Analyze test quality and coverage
→ security-analyst-finance: Identify security test gaps

Synthesizes: Complete test suite, coverage metrics, security validation results
```

## Maintenance Notes

### Updating Financial Domain Knowledge
To update finance-specific analysis:
1. Modify individual `-finance.md` droid file
2. Update relevant sections (e.g., "Financial-Screener Context")
3. Restart orchestrator to pick up changes

### Adding New Universal Droid
To add a new universal droid type:
1. Adapt from root `.factory/droids/`
2. Add `-finance` suffix to name
3. Include financial-domain examples
4. Remove Task tool references
5. Ensure model = `custom:GLM-4.6-[Z.AI-Coding-Plan]-0`
6. Update this README

### Monitoring Droid Health
```
for droid in code-analyzer-finance test-generator-finance ...
  check: .factory/memory/$droid-*.json (latest run)
  verify: timestamp within 24 hours
  validate: JSON structure matches schema
```

## Success Metrics

These 6 universal droids provide value when:
- ✅ Code quality issues detected before production
- ✅ 85%+ test coverage achieved
- ✅ Performance bottlenecks identified and fixed
- ✅ Security vulnerabilities caught before merge
- ✅ Architectural phase boundaries known before scaling issues
- ✅ No secrets committed to repository

---

**Created:** 2025-11-21
**Model Version:** GLM-4.6-[Z.AI-Coding-Plan]-0
**Artifact Protocol:** Option C (File-Based)
**Status:** Production Ready
