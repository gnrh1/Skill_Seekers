# Finance-Screener Droid Ecosystem Integration Guide

**Document Type:** Implementation & Integration Blueprint  
**Version:** 2.0.0  
**Date:** November 21, 2025  
**Status:** Complete Droid Army Deployed & Ready for Integration

---

## Quick Start: Using the Droid Ecosystem

### 1. Location of All Droids

```
finance-screener/.factory/droids/
├── README.md                                       # Master roster (this file references it)
├── finance-intelligence-orchestrator.md            # ⭐ MASTER - Start here
├── financial-data-sql-specialist.md                # SQL generation & validation
├── financial-answer-generation-specialist.md       # Citations & formatting
├── tdd-finance-test-engineer.md                    # Testing (existing)
├── sec-filing-ingestion-specialist.md              # Ingestion pipeline (existing)
├── hybrid-rag-query-architect.md                   # Semantic search (existing)
├── guard-and-safety-specialists.md                 # 5 guard droids in one file
└── system-and-safety-specialists.md                # 5 system droids in one file
```

### 2. How to Invoke Any Droid

**From finance-screener project:**

```bash
# Single-line invocation
@finance-intelligence-orchestrator route query: "What is Apple's revenue?"

# Detailed invocation with context
@financial-data-sql-specialist generate SQL query: "Apple revenue last 3 years" with Decimal precision

# Parallel invocation (for guard specialists)
@api-cost-tracker monitor query cost
@data-integrity-auditor validate result precision
@failure-mode-detector check system health
```

### 3. Understanding Droid Artifacts

Every droid writes results to `.factory/memory/{droid-name}-{ISO8601-timestamp}.json`

Example artifact path: `.factory/memory/financial-data-sql-specialist-2025-11-21T16:45:30Z.json`

**What's in an artifact:**

- Complete analysis (no truncation possible - file system, not API response)
- Metadata (timestamp, mental models applied, execution time)
- Recommendations (prioritized, actionable)
- Example execution or test cases

---

## Core Orchestration Patterns

### Pattern 1: SQL Query (Structured Data)

**User:** "What is Apple's revenue?"

**Flow:**

```
User Query
    ↓
@finance-intelligence-orchestrator (classifies as SQL)
    ├─ Routes to: @financial-data-sql-specialist
    │   ├─ Generates: SELECT revenue FROM filings WHERE ticker='AAPL'
    │   ├─ Validates: Decimal type, safe to execute
    │   └─ Returns artifact: SQL ready
    │
    ├─ Routes to: @financial-answer-generation-specialist
    │   ├─ Formats: "Apple's revenue for FY2024 was $391B"
    │   ├─ Adds citations: "Per 10-K filing, Item 8"
    │   └─ Returns artifact: Answer + citations
    │
    └─ Parallel guard specialists:
        ├─ @api-cost-tracker: Log $0.008 spend
        ├─ @data-precision-validator: Verify Decimal maintained
        ├─ @sec-rate-limit-guardian: Check rate limit
        └─ @regression-detector: Compare against baseline

Final Output: Answer + citations + confidence + cost
```

### Pattern 2: Semantic Query (Conceptual)

**User:** "What is Apple's competitive advantage?"

**Flow:**

```
User Query
    ↓
@finance-intelligence-orchestrator (classifies as semantic)
    ├─ Routes to: @hybrid-rag-query-architect
    │   ├─ BM25 search: Keywords from question
    │   ├─ Vector search: Semantic similarity (ChromaDB)
    │   ├─ Fuses results: RRF ranking
    │   └─ Returns artifact: Top-5 relevant chunks
    │
    ├─ Routes to: @financial-answer-generation-specialist
    │   ├─ Synthesizes: Answer from retrieved chunks
    │   ├─ Adds citations: Link to source 10-K sections
    │   └─ Returns artifact: Answer + citations (medium confidence)
    │
    └─ Parallel guard specialists: (same as SQL path)

Final Output: Answer + citations + lower confidence score
```

### Pattern 3: Fallback (Primary Fails)

**Scenario:** SQL specialist times out or errors

```
User Query
    ↓
@finance-intelligence-orchestrator (attempts SQL path)
    ├─ SQL specialist fails (timeout / syntax error)
    │
    ├─ @failure-mode-detector (detects failure)
    │
    ├─ @graceful-degradation-handler (triggers fallback)
    │
    ├─ Routes to: @hybrid-rag-query-architect (semantic fallback)
    │   └─ Returns artifact: Alternative results
    │
    └─ @financial-answer-generation-specialist
        └─ Returns artifact: Answer (confidence: medium, note: "fallback path")

Final Output: User still gets answer (graceful degradation, no service failure)
```

---

## Integration with finance-screener Python Code

### 1. Simple Query Integration

**File:** `skill_seeker_mcp/finance_tools/query.py`

```python
"""Execute financial query using droid ecosystem."""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

async def query_financial_data(user_query: str) -> Dict[str, Any]:
    """Execute financial query using droid orchestrator."""

    # Step 1: Delegate to master orchestrator
    orchestration_task = {
        "description": f"Process financial query: {user_query}",
        "subagent_type": "finance-intelligence-orchestrator"
    }

    # Step 2: Execute task via framework (returns minimal response with artifact path)
    result = await delegate_task(orchestration_task)

    # Step 3: Read complete artifact from filesystem
    artifact_path = result["artifact_path"]  # .factory/memory/finance-intelligence-orchestrator-*.json
    artifact = read_json(artifact_path)

    # Step 4: Extract key fields
    answer = artifact["synthesis"]["final_answer"]
    confidence = artifact["execution_summary"]["confidence"]
    citations = artifact.get("citations", [])
    specialists_used = len(artifact.get("specialist_delegations", []))

    # Step 5: Return to user
    return {
        "status": "success",
        "answer": answer,
        "confidence": confidence,
        "citations": citations,
        "metadata": {
            "query": user_query,
            "specialists_used": specialists_used,
            "execution_time_ms": artifact["execution_summary"]["total_time_ms"],
            "estimated_cost": artifact["execution_summary"].get("total_cost", 0)
        }
    }

# Usage
if __name__ == "__main__":
    result = asyncio.run(query_financial_data("What is Apple's revenue trend?"))
    print(json.dumps(result, indent=2))
```

### 2. Advanced: Access Individual Specialist Artifacts

**Pattern:** Read specialist outputs directly

```python
def analyze_query_execution(orchestrator_artifact_path: str) -> Dict[str, Any]:
    """Analyze how orchestrator routed and executed query."""

    # Read orchestrator artifact
    orch_artifact = read_json(orchestrator_artifact_path)

    # Extract specialist delegations
    delegations = orch_artifact["specialist_delegations"]

    # Analysis result
    analysis = {
        "query": orch_artifact["user_query"],
        "specialists": []
    }

    # For each specialist that was called
    for delegation in delegations:
        specialist_name = delegation["specialist"]
        specialist_artifact_path = delegation["artifact_path"]
        execution_time = delegation["execution_time_ms"]

        # Read specialist's artifact
        specialist_artifact = read_json(specialist_artifact_path)

        # Extract key info
        analysis["specialists"].append({
            "name": specialist_name,
            "status": specialist_artifact.get("status", "unknown"),
            "execution_time_ms": execution_time,
            "key_findings": specialist_artifact.get("key_findings", []),
            "recommendations": specialist_artifact.get("recommendations", [])
        })

    return analysis
```

### 3. Testing Pattern: Mock Droids

**File:** `tests/test_droid_integration.py`

```python
"""Test finance-screener integration with droid ecosystem."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
from pathlib import Path
from skill_seeker_mcp.finance_tools.query import query_financial_data

@pytest.fixture
def mock_orchestrator_artifact():
    """Mock orchestrator artifact (success case)."""
    return {
        "droid": "finance-intelligence-orchestrator",
        "timestamp": "2025-11-21T16:45:00Z",
        "user_query": "What is Apple's revenue?",
        "synthesis": {
            "final_answer": "Apple's revenue for FY2024 was $391.04 billion"
        },
        "execution_summary": {
            "confidence": "very_high",
            "total_time_ms": 4290,
            "specialists_used": 3,
            "total_cost": 0.008
        },
        "specialist_delegations": [
            {
                "specialist": "financial-data-sql-specialist",
                "artifact_path": ".factory/memory/financial-data-sql-specialist-2025-11-21T16:45:30Z.json",
                "execution_time_ms": 1250
            }
        ]
    }

@pytest.mark.asyncio
async def test_query_financial_data_success(mock_orchestrator_artifact, tmp_path):
    """Test successful query execution through droid ecosystem."""

    # Create mock artifact file
    artifact_path = tmp_path / "finance-intelligence-orchestrator-2025-11-21T16:45:00Z.json"
    artifact_path.write_text(json.dumps(mock_orchestrator_artifact))

    # Mock the task delegation function to return artifact path
    with patch("query.delegate_task") as mock_delegate:
        mock_execute.return_value = {
            "artifact_path": str(artifact_path),
            "status": "completed"
        }

        # Mock read_json
        with patch("query.read_json") as mock_read:
            mock_read.return_value = mock_orchestrator_artifact

            # Execute query
            result = await query_financial_data("What is Apple's revenue?")

            # Verify result
            assert result["status"] == "success"
            assert "Apple's revenue for FY2024 was $391.04 billion" in result["answer"]
            assert result["confidence"] == "very_high"
            assert result["metadata"]["execution_time_ms"] == 4290
```

---

## Droid Decision Tree: When to Use Which Droid

```
Query arrives
    │
    ├─ Is this about financials? (revenue, EPS, growth, ratios)
    │  ├─ YES (structured query like "revenue 2022-2024")
    │  │  └─ Use @financial-data-sql-specialist
    │  │
    │  └─ NO (conceptual like "strategy", "competitive advantage")
    │     └─ Use @hybrid-rag-query-architect
    │
    ├─ Background: ALWAYS include
    │  ├─ @financial-answer-generation-specialist (format + cite)
    │  ├─ @api-cost-tracker (monitor spend)
    │  ├─ @data-precision-validator (verify Decimal)
    │  └─ @failure-mode-detector (early warning)
    │
    ├─ If something fails
    │  ├─ @graceful-degradation-handler (fallback)
    │  └─ @regression-detector (compare baseline)
    │
    └─ Conditional specialists
       ├─ If data validation needed: @data-integrity-auditor
       ├─ If rate limiting concern: @sec-rate-limit-guardian
       ├─ If edge cases likely: @edge-case-hunter
       └─ If sync issues suspected: @duckdb-chromadb-sync-validator
```

---

## Configuration: Set Up .factory/memory for Artifacts

### 1. Create Memory Directory

```bash
cd finance-screener
mkdir -p .factory/memory
```

### 2. Add .gitignore

**File:** `.factory/memory/.gitignore`

```
# Ignore all runtime artifact files
*.json

# Except for examples (if you want to commit)
!example-artifact.json
!.gitignore
```

### 3. Verify Setup

```bash
# Should show only .gitignore
ls -la .factory/memory/

# When droids run, should create timestamped files
# .factory/memory/finance-intelligence-orchestrator-2025-11-21T16:45:00Z.json
# .factory/memory/financial-data-sql-specialist-2025-11-21T16:45:30Z.json
# etc.
```

---

## Monitoring Droid Ecosystem Health

### 1. Check Recent Artifacts

```bash
# Show 10 most recent artifacts
ls -lt .factory/memory/*.json | head -10

# Show artifacts from today
find .factory/memory -name "*-2025-11-21T*.json" | sort
```

### 2. Analyze Artifact Statistics

```python
"""Check droid ecosystem health."""

import json
from pathlib import Path
from datetime import datetime

def analyze_artifacts(memory_dir: Path = Path(".factory/memory")):
    """Analyze recent droid execution statistics."""

    # Find all artifacts from today
    today = datetime.now().strftime("%Y-%m-%d")
    artifacts = list(memory_dir.glob(f"*-{today}T*.json"))

    # Aggregate statistics
    stats = {
        "total_artifacts": len(artifacts),
        "by_droid": {},
        "total_cost": 0,
        "total_time_ms": 0,
        "success_rate": 0
    }

    for artifact_path in artifacts:
        artifact = json.loads(artifact_path.read_text())
        droid_name = artifact.get("droid", "unknown")

        # Track by droid
        if droid_name not in stats["by_droid"]:
            stats["by_droid"][droid_name] = {"count": 0, "total_cost": 0}

        stats["by_droid"][droid_name]["count"] += 1

        # Aggregate costs
        if "cost_summary" in artifact:
            cost = artifact["cost_summary"].get("total_cost", 0)
            stats["total_cost"] += cost
            stats["by_droid"][droid_name]["total_cost"] += cost

    return stats

# Usage
stats = analyze_artifacts()
print(f"Total queries today: {stats['total_artifacts']}")
print(f"Total spend: ${stats['total_cost']:.3f}")
print(f"By droid: {json.dumps(stats['by_droid'], indent=2)}")
```

### 3. Cleanup Old Artifacts (Manual)

```bash
# Delete artifacts older than 7 days
find .factory/memory -name "*.json" -mtime +7 -delete

# Or keep only last 100 artifacts per droid
# (implement cleanup script as needed)
```

---

## Troubleshooting Common Issues

### Issue 1: Droid Artifact Not Created

**Symptom:** Task returns success but artifact_path file doesn't exist

**Root Cause:** Droid crashed before writing artifact (or wrong path)

**Solution:**

1. Check droid executed: Look for any error messages in orchestrator output
2. Verify path format: Should be `.factory/memory/{droid-name}-{ISO8601-timestamp}.json`
3. Check file permissions: Ensure .factory/memory is writable
4. Manual fallback: Route to next specialist in fallback chain

### Issue 2: Artifact Too Large / Truncated

**Symptom:** JSON parsing fails or fields are missing

**Root Cause:** File-based architecture should prevent this, but verify

**Solution:**

1. Check file size: `ls -lh .factory/memory/file.json` (should be <5 MB)
2. Validate JSON: `python3 -m json.tool .factory/memory/file.json` (should parse)
3. Re-run specialist: Droid should produce complete artifact on retry

### Issue 3: Orchestrator Routes to Wrong Specialist

**Symptom:** SQL query routed to semantic specialist or vice versa

**Root Cause:** Query classification error in orchestrator

**Solution:**

1. Check orchestrator artifact: Review classification logic
2. Provide explicit type hint: "This is a SQL query about revenue"
3. File issue: Orchestrator mental model may need tuning

### Issue 4: High Cost per Query

**Symptom:** API cost tracker shows $0.50+ per query

**Root Cause:** Unnecessary specialist delegation or table extraction

**Solution:**

1. Check artifact: Which specialists were called?
2. Review query: Did it trigger Gemini Vision unnecessarily?
3. Optimize: Route to semantic path (free) instead of SQL (costs)

---

## Mental Model Checklist for Integration

Before deploying droid ecosystem:

- [ ] **First Principles:** Each droid has single responsibility ✓
- [ ] **Second Order Effects:** Cost tracking prevents budget overrun ✓
- [ ] **Systems Thinking:** All 16 droids coordinate through orchestrator ✓
- [ ] **Inversion:** Failure handling and fallbacks implemented ✓
- [ ] **Interdependencies:** DuckDB/ChromaDB sync validated ✓

Before each query:

- [ ] Query routed to appropriate specialist
- [ ] Guard specialists running in parallel
- [ ] Artifact path valid and timestamped
- [ ] Cost tracked and within budget
- [ ] Confidence score honest and justified

---

## Advanced: Custom Droid Development

To add a new specialist droid to the ecosystem:

1. **Create markdown file:** `.factory/droids/{name}.md`
2. **Add YAML front matter:** name, description, model, tools, mental_models
3. **Document specialization:** What does this droid do?
4. **Specify artifact format:** JSON schema expected
5. **Add mental models:** Which 2-3 mental models apply?
6. **Implement protocol:** Write artifacts to `.factory/memory/{name}-{timestamp}.json`
7. **Register with orchestrator:** Add routing logic in intelligence-orchestrator.md
8. **Test integration:** Create test case in tests/test_droid_integration.py

Example: Creating a "Financial Forecasting Specialist"

````markdown
---
name: financial-forecasting-specialist
description: Forecast future financial metrics using historical trends
model: claude-opus
tools: [Read, Execute]
mental_models:
  - second_order_effects: "Forecast accuracy affects user confidence"
  - inversion: "What makes forecasts wrong? Market disruption"
---

# Financial Forecasting Specialist

**ROLE:** Generate financial forecasts (future revenues, earnings) based on historical trends.

## Specialization

- Historical trend analysis
- Time series forecasting (regression, exponential smoothing)
- Scenario analysis (base case, upside, downside)
- Confidence intervals (high, medium, low)

## Protocol Enforcement

**Artifact Path:** `.factory/memory/financial-forecasting-specialist-{ISO8601-timestamp}.json`

**Artifact Content:**

```json
{
  "droid": "financial-forecasting-specialist",
  "timestamp": "2025-11-21T16:45:00Z",
  "forecast": {
    "metric": "Apple revenue",
    "base_case_fy2025": 420000000000,
    "upside_case_fy2025": 480000000000,
    "downside_case_fy2025": 380000000000,
    "confidence": "medium"
  }
}
```
````

```

---

## Next Steps

1. ✅ **Droids deployed:** 16 specialist droids ready
2. ✅ **Orchestrator operational:** Intelligence orchestrator ready to route
3. ✅ **Option C active:** Artifacts in .factory/memory/
4. ⏳ **Integration in progress:** Add orchestrator calls to query.py
5. ⏳ **Testing:** Create test suite for droid integration
6. ⏳ **Monitoring:** Deploy pipeline-monitoring-specialist
7. ⏳ **Optimization:** Tune specialist paths based on real usage

---

**Finance-screener droid ecosystem is ready for integration!**

```
