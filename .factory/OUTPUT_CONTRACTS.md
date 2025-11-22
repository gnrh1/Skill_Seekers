# Factory Droid Output Contracts (Phase 2)

Structured JSON output schemas for all 16 Factory Droids. These contracts enable deterministic parsing, validation, and orchestration of droid outputs.

---

## Universal Envelope (Required for All Droids)

All droids MUST return output wrapped in this envelope:

```json
{
  "droid": "droid-name",
  "timestamp": "2024-11-21T10:00:00Z",
  "execution_status": "completed",
  "completion_percentage": 100,
  "output": {}
}
```

**Note**:

- `execution_status` can be: "completed", "in-progress", "blocked", or "error"
- `completion_percentage` is an integer from 0 to 100
- `output` contains droid-specific structured data (see specialist droid contracts below)

````

---

## Specialist Droid Output Contracts

### 1. scraper-expert

**Purpose**: Web scraping, documentation extraction, conflict detection
**Key Output**: Scraped data metrics, conflict detection results, performance metrics

```json
{
  "summary": "One-line scraping outcome",
  "scraping_results": {
    "total_pages_scraped": 0,
    "files_created": ["paths"],
    "files_modified": ["paths"],
    "data_quality": {
      "avg_content_length": 0,
      "language_distribution": {},
      "selector_accuracy_percent": 0
    }
  },
  "conflicts_detected": [
    {
      "type": "missing_in_docs, missing_in_code, or signature_mismatch",
      "feature": "name",
      "severity": "high, medium, or low",
      "resolution": "recommended fix"
    }
  ],
  "performance": {
    "execution_seconds": 0,
    "pages_per_second": 0,
    "memory_mb": 0
  },
  "next_steps": ["action1", "action2"]
}
```

---

### 2. test-engineer

**Purpose**: Test generation, maintenance, coverage optimization
**Key Output**: Test metrics, coverage analysis, test suite changes

```json
{
  "summary": "One-line test suite outcome",
  "test_metrics": {
    "total_tests": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "coverage_percent": 0,
    "new_tests_added": 0,
    "tests_modified": 0
  },
  "test_suites_modified": [
    {
      "suite_name": "test_scraper_features.py",
      "changes_made": "description",
      "test_count_change": 0,
      "coverage_impact": 0
    }
  ],
  "coverage_by_module": {
    "cli.doc_scraper": 85,
    "cli.conflict_detector": 90
  },
  "failing_tests": [
    {
      "test_name": "test_name",
      "failure_reason": "reason",
      "suggested_fix": "fix description"
    }
  ],
  "performance_tests": {
    "slowest_tests": ["test_name: 2.5s"],
    "recommendations": ["Run with pytest-benchmark", "Add performance fixtures"]
  }
}
```

---

### 3. code-analyzer

**Purpose**: Code quality analysis, complexity metrics, pattern detection
**Key Output**: Complexity scores, design patterns, refactoring recommendations

```json
{
  "summary": "One-line code quality assessment",
  "complexity_analysis": {
    "files_analyzed": 0,
    "avg_cyclomatic_complexity": 0,
    "avg_cognitive_complexity": 0,
    "maintainability_index": 0
  },
  "metrics_by_file": [
    {
      "file": "cli/doc_scraper.py",
      "lines_of_code": 0,
      "cyclomatic_complexity": 0,
      "cognitive_complexity": 0,
      "maintainability_index": 0,
      "technical_debt_estimate_hours": 0
    }
  ],
  "design_patterns_found": [
    {
      "pattern": "Factory Pattern",
      "location": "cli.doc_scraper:DocToSkillConverter",
      "implementation_quality": "good or fair or poor"
    }
  ],
  "anti_patterns_detected": [
    {
      "anti_pattern": "God Object",
      "location": "file:class",
      "severity": "high or medium or low",
      "refactoring_recommendation": "description"
    }
  ],
  "refactoring_recommendations": [
    {
      "recommendation": "Extract method",
      "file": "file_path",
      "priority": "high or medium or low",
      "estimated_effort_hours": 0,
      "expected_impact": "description"
    }
  ],
  "dependency_analysis": {
    "high_coupling_modules": ["module1", "module2"],
    "low_cohesion_classes": ["class1"],
    "circular_dependencies": []
  }
}
```

---

### 4. test-generator

**Purpose**: Comprehensive test generation, T.E.S.T. methodology
**Key Output**: Generated tests, coverage targets, CI/CD integration

```json
{
  "summary": "One-line test generation outcome",
  "tests_generated": {
    "unit_tests": 0,
    "integration_tests": 0,
    "performance_tests": 0,
    "security_tests": 0,
    "total_new_tests": 0
  },
  "generated_test_files": [
    {
      "file": "test_file_path",
      "test_count": 0,
      "test_types": ["unit", "integration"],
      "coverage_focus": "method/class names covered"
    }
  ],
  "test_methodology": {
    "methodology": "T.E.S.T.",
    "test_coverage_target_percent": 90,
    "current_coverage_percent": 0,
    "coverage_gap": 0
  },
  "ci_cd_integration": {
    "github_actions_workflow": "generated or updated or not_needed",
    "test_parallelization": "enabled or disabled",
    "estimated_ci_runtime_seconds": 0
  },
  "test_quality_metrics": {
    "avg_assertions_per_test": 0,
    "mocking_coverage_percent": 0,
    "fixture_reusability_score": 0
  },
  "failing_test_scenarios": [
    {
      "scenario": "description",
      "test_case": "test_name",
      "root_cause": "cause",
      "mitigation": "fix"
    }
  ]
}
```

---

### 5. architectural-critic

**Purpose**: System architecture analysis, phase boundary detection
**Key Output**: Architectural assessment, phase transitions, improvement strategies

```json
{
  "summary": "One-line architectural assessment",
  "architectural_state": {
    "system_phase": "monolithic or modular or microservices or distributed",
    "phase_transition_risk": "high or medium or low",
    "architectural_health_score": 0
  },
  "complexity_analysis": {
    "system_size_kloc": 0,
    "module_count": 0,
    "coupling_metric": 0,
    "cohesion_metric": 0,
    "architecture_pattern": "layered or hexagonal or microservices"
  },
  "phase_boundaries_detected": [
    {
      "boundary": "description",
      "current_position": "position in system",
      "transition_threshold": "when crossing this threshold",
      "warning_signs": ["sign1", "sign2"],
      "mitigation": "description"
    }
  ],
  "structural_patterns": [
    {
      "pattern": "pattern name",
      "location": "system area",
      "implementation_quality": "good or fair or poor",
      "impact": "positive or negative or neutral"
    }
  ],
  "architectural_debt": [
    {
      "debt_item": "description",
      "impact_area": "performance or maintainability or scalability",
      "estimated_refactoring_effort_hours": 0,
      "priority": "high or medium or low"
    }
  ],
  "improvement_strategies": [
    {
      "strategy": "description",
      "target_phase": "target architecture state",
      "implementation_phases": ["phase1", "phase2"],
      "estimated_total_effort_hours": 0,
      "success_criteria": ["metric1", "metric2"]
    }
  ]
}
```

---

### 6. performance-auditor

**Purpose**: Performance profiling, bottleneck identification, optimization ROI
**Key Output**: Performance metrics, bottleneck analysis, optimization recommendations

```json
{
  "summary": "One-line performance assessment",
  "performance_baseline": {
    "execution_time_seconds": 0,
    "memory_peak_mb": 0,
    "cpu_utilization_percent": 0,
    "io_operations": 0
  },
  "bottleneck_analysis": [
    {
      "bottleneck": "description",
      "location": "file:function",
      "impact_percent": 0,
      "severity": "high or medium or low",
      "optimization_approach": "description"
    }
  ],
  "memory_analysis": {
    "peak_usage_mb": 0,
    "memory_leaks_detected": ["leak1"],
    "inefficient_allocations": ["allocation1"],
    "optimization_potential_mb": 0
  },
  "algorithm_analysis": [
    {
      "function": "function_name",
      "current_complexity": "O(n^2)",
      "optimal_complexity": "O(n)",
      "estimated_speedup": "10x",
      "refactoring_effort_hours": 0
    }
  ],
  "optimization_recommendations": [
    {
      "optimization": "description",
      "estimated_impact_percent": 0,
      "implementation_effort_hours": 0,
      "roi_metric": "10x speedup for 5 hours work",
      "priority": "high or medium or low"
    }
  ],
  "profiling_data": {
    "cpu_profile_file": "path/to/profile.prof",
    "memory_profile_file": "path/to/memory.prof",
    "io_metrics": {}
  }
}
```

---

### 7. security-analyst

**Purpose**: Security vulnerability analysis, code security assessment
**Key Output**: Vulnerability report, security metrics, remediation guidance

```json
{
  "summary": "One-line security assessment",
  "vulnerability_scan": {
    "vulnerabilities_found": 0,
    "critical_count": 0,
    "high_count": 0,
    "medium_count": 0,
    "low_count": 0
  },
  "vulnerabilities": [
    {
      "id": "CVE-2024-XXXXX or internal-id",
      "type": "sql_injection or xss or path_traversal or secret_leak",
      "location": "file:line",
      "severity": "critical or high or medium or low",
      "description": "vulnerability description",
      "proof_of_concept": "code snippet",
      "remediation": "fix description",
      "remediation_priority": 1
    }
  ],
  "dependency_vulnerabilities": [
    {
      "package": "package_name",
      "current_version": "1.0.0",
      "vulnerable_versions": "<=1.2.3",
      "fixed_version": "1.2.4",
      "cve": "CVE-2024-XXXXX",
      "severity": "high"
    }
  ],
  "security_best_practices": [
    {
      "practice": "description",
      "current_implementation": "status",
      "recommended_action": "action",
      "effort_hours": 0
    }
  ],
  "secrets_found": [
    {
      "type": "api_key or password or token",
      "location": "file:line",
      "severity": "critical",
      "remediation": "rotate immediately"
    }
  ],
  "security_score": 0
}
```

---

### 8. intelligence-orchestrator

**Purpose**: Multi-domain analysis coordination, strategic synthesis
**Key Output**: Cross-domain insights, strategic recommendations, implementation plan

```json
{
  "summary": "One-line strategic outcome",
  "analysis_domains": [
    {
      "domain": "agent-intelligence or workflow-efficiency or architectural-coherence",
      "files_analyzed": ["file1", "file2"],
      "key_findings": "summary",
      "priority": "high or medium or low"
    }
  ],
  "cross_domain_patterns": [
    {
      "pattern": "description",
      "domains_affected": ["domain1", "domain2"],
      "impact": "strategic impact description"
    }
  ],
  "identified_conflicts": [
    {
      "conflict": "description",
      "domains": ["domain1", "domain2"],
      "resolution": "resolution approach"
    }
  ],
  "strategic_recommendations": [
    {
      "recommendation": "specific actionable recommendation",
      "priority": "high or medium or low",
      "estimated_impact": "outcome and metrics improvement",
      "dependencies": ["prerequisite1"],
      "success_criteria": ["metric1"]
    }
  ],
  "implementation_plan": {
    "phase_1_immediate": ["action1", "action2"],
    "phase_2_medium_term": ["action1"],
    "phase_3_long_term": ["action1"],
    "total_effort_hours": 0,
    "resource_requirements": "description"
  },
  "risks": [
    {
      "risk": "description",
      "severity": "high or medium or low",
      "mitigation": "strategy"
    }
  ]
}
```

---

### 9. cognitive-resonator

**Purpose**: Code harmony analysis, cognitive flow optimization
**Key Output**: Cognitive metrics, harmony assessment, DX recommendations

```json
{
  "summary": "One-line cognitive assessment",
  "cognitive_load_analysis": {
    "avg_cognitive_load_score": 0,
    "high_load_functions": ["function1"],
    "cognitive_complexity_hotspots": ["area1"]
  },
  "mental_model_alignment": {
    "alignment_score": 0,
    "pattern_consistency": "consistent or inconsistent",
    "learning_curve_estimate_hours": 0
  },
  "code_harmony_assessment": [
    {
      "area": "naming conventions",
      "harmony_score": 0,
      "issues": ["issue1"],
      "recommendations": ["recommendation1"]
    }
  ],
  "developer_experience_metrics": {
    "code_readability_score": 0,
    "pattern_predictability": 0,
    "onboarding_difficulty": "easy or medium or hard"
  },
  "optimization_recommendations": [
    {
      "recommendation": "description",
      "impact_area": "readability or predictability or maintainability",
      "effort_hours": 0,
      "expected_learning_curve_reduction_hours": 0
    }
  ]
}
```

---

### 10. possibility-weaver

**Purpose**: Creative problem-solving, design space expansion
**Key Output**: Novel perspectives, constraint analysis, alternative solutions

```json
{
  "summary": "One-line creative breakthrough",
  "problem_analysis": {
    "current_solution_limitations": ["limitation1"],
    "constraint_analysis": ["constraint1"],
    "local_optima_indicators": ["indicator1"]
  },
  "novel_perspectives": [
    {
      "perspective": "description",
      "domain_shift": "from X thinking to Y thinking",
      "applicability": "high or medium or low",
      "implementation_feasibility": "easy or medium or hard"
    }
  ],
  "constraint_innovations": [
    {
      "constraint": "current constraint",
      "beneficial_reframe": "new perspective",
      "solution_space_expansion": "how it expands options"
    }
  ],
  "alternative_solutions": [
    {
      "solution": "description",
      "advantages": ["advantage1"],
      "disadvantages": ["disadvantage1"],
      "compatibility_with_current": "high or medium or low"
    }
  ],
  "creative_recommendations": [
    {
      "recommendation": "specific creative solution",
      "novelty_score": 0,
      "implementation_effort_hours": 0,
      "expected_impact": "description"
    }
  ]
}
```

---

### 11. precision-editor

**Purpose**: Surgical code modifications, targeted improvements
**Key Output**: Code changes applied, modification details, verification results

```json
{
  "summary": "One-line modification outcome",
  "modifications_applied": {
    "files_modified": 0,
    "lines_added": 0,
    "lines_removed": 0,
    "lines_unchanged": 0
  },
  "detailed_changes": [
    {
      "file": "file_path",
      "change_type": "refactor or bugfix or feature or optimization",
      "location": "line range or method name",
      "change_description": "what changed and why",
      "risk_level": "low or medium or high"
    }
  ],
  "impact_analysis": {
    "affected_tests": ["test1", "test2"],
    "api_compatibility": "breaking or compatible",
    "performance_impact": "improvement or neutral or regression",
    "side_effects": ["side_effect1"]
  },
  "verification": {
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "manual_verification_needed": false,
    "verification_checklist": ["check1"]
  },
  "rollback_plan": {
    "rollback_procedure": "steps to undo changes",
    "estimated_rollback_time_minutes": 0
  }
}
```

---

### 12. referee-agent-csp

**Purpose**: Deterministic outcome evaluation, parallel agent synthesis
**Key Output**: Evaluation metrics, selected outcome, synthesis rationale

```json
{
  "summary": "One-line synthesis outcome",
  "evaluation_criteria": {
    "success_metrics": ["metric1", "metric2"],
    "weighting": { "metric1": 0.6, "metric2": 0.4 }
  },
  "evaluated_outcomes": [
    {
      "outcome_id": "outcome1_from_agent1",
      "source_agent": "agent_name",
      "metric_scores": { "metric1": 85, "metric2": 92 },
      "overall_score": 88.2,
      "strengths": ["strength1"],
      "weaknesses": ["weakness1"]
    }
  ],
  "selected_outcome": {
    "id": "selected_outcome_id",
    "source_agent": "winning_agent_name",
    "selection_rationale": "why this outcome was selected",
    "confidence_percent": 95,
    "alternative_outcomes_considered": ["outcome2", "outcome3"]
  },
  "synthesis_notes": "Additional context on the synthesis decision",
  "implementation_guidance": ["step1", "step2"]
}
```

---

### 13. mcp-specialist

**Purpose**: MCP protocol integration, tool definition management
**Key Output**: Tool definitions, schema updates, integration status

```json
{
  "summary": "One-line MCP integration outcome",
  "mcp_tools": [
    {
      "tool_name": "tool_name",
      "description": "what the tool does",
      "input_schema": {},
      "output_schema": {},
      "status": "implemented or updated or removed"
    }
  ],
  "integration_status": {
    "tools_total": 0,
    "tools_active": 0,
    "integration_completeness_percent": 0
  },
  "schema_validations": [
    {
      "schema_name": "name",
      "validation_result": "valid or invalid",
      "errors": ["error1"],
      "warnings": ["warning1"]
    }
  ],
  "protocol_compliance": {
    "mcp_version": "1.0",
    "compliance_level": "full or partial or non-compliant",
    "issues": ["issue1"]
  },
  "performance_metrics": {
    "avg_tool_latency_ms": 0,
    "throughput_requests_per_second": 0
  }
}
```

---

### 14. ecosystem-evolution-architect

**Purpose**: Multi-agent system monitoring, phase transition management
**Key Output**: System health assessment, evolution recommendations, roadmap

```json
{
  "summary": "One-line ecosystem health assessment",
  "system_health": {
    "overall_health_score": 0,
    "agent_count": 0,
    "active_agents": 0,
    "system_phase": "growth or optimization or maturity or decline"
  },
  "agent_performance": [
    {
      "agent_name": "agent_name",
      "specialization_effectiveness": 0,
      "workload_distribution": "balanced or overloaded or underutilized",
      "quality_score": 0,
      "reliability_percent": 0
    }
  ],
  "phase_transition_analysis": {
    "current_phase": "current_phase_name",
    "transition_indicators": ["indicator1"],
    "estimated_transition_point": "timeline",
    "preparation_needed": ["preparation1"]
  },
  "bottlenecks_and_constraints": [
    {
      "bottleneck": "description",
      "impact": "system_area",
      "severity": "high or medium or low",
      "resolution_strategy": "description"
    }
  ],
  "evolution_recommendations": [
    {
      "recommendation": "description",
      "target_phase": "desired_state",
      "timeline_months": 0,
      "resource_requirements": "description",
      "success_metrics": ["metric1"]
    }
  ],
  "sustainability_roadmap": {
    "next_3_months": ["action1"],
    "next_6_months": ["action1"],
    "next_12_months": ["action1"],
    "long_term_vision": "description"
  }
}
```

---

### 15. security-guardian

**Purpose**: Proactive secret detection, security enforcement
**Key Output**: Security scan results, threat assessment, remediation guidance

```json
{
  "summary": "One-line security scan outcome",
  "secret_detection": {
    "secrets_found": 0,
    "api_keys_found": 0,
    "passwords_found": 0,
    "tokens_found": 0,
    "other_secrets_found": 0
  },
  "detected_secrets": [
    {
      "type": "api_key or password or token or private_key",
      "location": "file:line",
      "exposure_risk": "critical or high or medium",
      "recommended_action": "action description",
      "action_urgency": "immediate or 24_hours or this_week"
    }
  ],
  "unsafe_patterns": [
    {
      "pattern": "description",
      "location": "file:line",
      "risk": "description",
      "remediation": "fix description"
    }
  ],
  "security_boundaries": {
    "enforcement_status": "enforced or warning or alert",
    "violations": ["violation1"]
  },
  "remediation_summary": {
    "immediate_actions_required": ["action1"],
    "recommended_practices": ["practice1"],
    "timeline_summary": "description"
  },
  "validation": {
    "re_scan_after_fixes": "recommended or not_needed",
    "automation_recommendations": ["automation1"]
  }
}
```

---

## Implementation Notes

1. **All droids must return valid JSON** in the envelope format
2. **Completion artifacts prove successful execution** - absence of JSON = failure
3. **Intelligence-orchestrator parses all outputs** to drive orchestration
4. **Schema validation happens automatically** during orchestration
5. **Optional fields can be null** if not applicable
6. **Custom fields allowed** for droid-specific additions (prefix with `_custom_`)

---

## Version History

 or  Version  or  Date  or  Changes                                     or
 or  -------  or  ----  or  ------------------------------------------  or
 or  1.0      or  2024  or  Initial contract definitions for 15 droids  or

---

**Last Updated**: 2024
**Maintainer**: Factory Droid System
**Status**: Active - Phase 2 Implementation
````
