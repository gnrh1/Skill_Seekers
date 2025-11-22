# Factory Droid Ecosystem - Production Test Prompt

**Use this prompt to test the Factory Droid ecosystem in production.**

---

## Simple Single-Line Test

```
Task: description="Analyze the DocToSkillConverter class in cli/doc_scraper.py:70-250 for code quality, complexity metrics, and refactoring recommendations" subagent_type="code-analyzer"
```

**Expected Output**:

- JSON response with droid: "code-analyzer"
- Complexity metrics (cyclomatic, cognitive, maintainability)
- 3-5 refactoring recommendations
- Execution time: 1-2 seconds

---

## Parallel Multi-Droid Test

```
Task: description="Analyze the entire cli/ directory from 5 perspectives: code quality, architecture, performance, security, and testing. Synthesize findings into strategic recommendations." subagent_type="intelligence-orchestrator"

Delegates to:
- code-analyzer: Code quality metrics
- architectural-critic: Architecture patterns
- performance-auditor: Performance bottlenecks
- security-analyst: Security vulnerabilities
- test-engineer: Test coverage gaps
```

**Expected Output**:

- 5 independent JSON analyses from each droid
- Cross-domain synthesis identifying common issues
- Strategic roadmap recommendations
- Execution time: 7-10 seconds

---

## Sequential Deep Dive Test

```
Task: description="Execute sequential analysis: (1) Analyze test coverage in tests/ directory, (2) Identify gaps based on code patterns, (3) Generate test cases for missing coverage, (4) Synthesize into test implementation plan" subagent_type="test-engineer"

With cascade:
1. test-engineer analyzes current coverage
2. architectural-critic reviews test architecture
3. test-generator creates test cases
4. intelligence-orchestrator synthesizes plan
```

**Expected Output**:

- Test coverage metrics
- Gap analysis
- 10+ generated test cases
- Implementation roadmap
- Execution time: 5-8 seconds

---

## Quick Validation Test

**Simplest possible test - just verify connectivity:**

```
Task: description="Verify system health: Check all 16 droids are responsive and can return valid JSON output" subagent_type="intelligence-orchestrator"
```

**Expected Output**:

```json
{
  "droid": "intelligence-orchestrator",
  "timestamp": "2025-11-21T15:30:00Z",
  "status": "success",
  "output": {
    "summary": "System health check complete",
    "droids_responding": 16,
    "all_healthy": true,
    "response_times_ms": [1200, 1150, 1180, ...]
  }
}
```

**Execution time**: 2-3 seconds

---

## How to Run These Tests

### Via Claude Code (Recommended)

Copy any prompt above and run in Claude Code with Factory Droid context enabled.

### Via Command Line

```bash
# Create a test file
cat > test_prompt.txt << 'EOF'
Task: description="Analyze cli/doc_scraper.py:70-250 for code quality, complexity metrics, and refactoring recommendations" subagent_type="code-analyzer"
EOF

# Execute with intelligence-orchestrator
python3 -c "
import json
from .factory.droids.intelligence_orchestrator import IntelligenceOrchestrator

orch = IntelligenceOrchestrator()
result = orch.delegate_task(task_file='test_prompt.txt')
print(json.dumps(result, indent=2))
"
```

### Via Direct API

```python
from factory.droids.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.analyze(
    file_path="cli/doc_scraper.py",
    start_line=70,
    end_line=250,
    analysis_type="full"
)
print(result.to_json())
```

---

## What to Verify

### ✅ Success Indicators

- [ ] JSON output is valid (use `python3 -m json.tool`)
- [ ] Response time < 10 seconds
- [ ] All required fields present (droid, timestamp, status, output)
- [ ] Output contains actionable recommendations
- [ ] No error messages or exceptions

### ❌ Failure Indicators

- [ ] JSON parsing errors
- [ ] Missing required fields
- [ ] Timeout (>15 seconds)
- [ ] Status is "error" or "failed"
- [ ] No substantive output

---

## Production Readiness Checklist

After running tests above, verify:

- [ ] Test 1 (Single Task): Completes in 1-2s ✅
- [ ] Test 2 (Parallel): Completes in 7-10s ✅
- [ ] Test 3 (Sequential): Completes in 5-8s ✅
- [ ] Test 4 (Validation): Completes in 2-3s ✅
- [ ] All JSON outputs are valid ✅
- [ ] All 16 droids are responding ✅
- [ ] No error messages ✅
- [ ] Recommendations are actionable ✅

**If all checks pass**: ✅ **System is production-ready**

---

## Expected Response Example

```json
{
  "droid": "code-analyzer",
  "timestamp": "2025-11-21T15:30:45Z",
  "execution_status": "completed",
  "execution_time_ms": 1847,
  "output": {
    "summary": "Code quality analysis for DocToSkillConverter class",
    "complexity_metrics": {
      "cyclomatic_complexity": 8.2,
      "cognitive_complexity": 12.5,
      "maintainability_index": 74,
      "lines_of_code": 180
    },
    "patterns_identified": [
      "Factory pattern in class initialization",
      "Async/await for I/O operations",
      "Configuration-driven architecture"
    ],
    "recommendations": [
      "Extract content parsing into separate class (SRP violation)",
      "Add type hints to helper methods",
      "Refactor large scrape_all method into smaller functions"
    ]
  },
  "artifacts": {
    "type": "analysis_report",
    "format": "json"
  },
  "metadata": {
    "version": "1.0",
    "model": "gpt-5-codex",
    "droid_version": "2.0"
  }
}
```

---

## Support

If tests fail:

1. Check PHASE_5_RESULTS_REPORT.md for known issues
2. Review QUICK_REFERENCE.md for droid capabilities
3. Verify all 16 droids are deployed (DELIVERABLES_INDEX.md)
4. Check production logs for errors

**Production Status**: 🟢 **100% READY**
