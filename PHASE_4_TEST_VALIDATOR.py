#!/usr/bin/env python3
"""
Phase 4 Integration Test Validator

Tests:
1. JSON contract parsing from OUTPUT_CONTRACTS.md
2. Droid configuration loading
3. Task delegation syntax validation
4. JSON output schema validation
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class Phase4Validator:
    """Validates Phase 4 integration requirements"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.droids_dir = self.workspace_root / ".factory" / "droids"
        self.output_contracts = self.workspace_root / ".factory" / "OUTPUT_CONTRACTS.md"
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def test_scenario_1_yaml_validation(self) -> bool:
        """Test Scenario 1: YAML & Configuration Validation"""
        print("\n=== TEST SCENARIO 1: YAML & Configuration Validation ===\n")
        
        all_passed = True
        
        # Count droids
        droid_files = list(self.droids_dir.glob("*.md"))
        print(f"✅ Total droid files: {len(droid_files)}")
        if len(droid_files) != 16:
            print(f"❌ Expected 16 droids, found {len(droid_files)}")
            all_passed = False
        
        # Check each droid
        models = []
        json_contracts = 0
        no_anthropic = True
        no_brackets = True
        
        for droid_file in droid_files:
            content = droid_file.read_text()
            
            # Check for gpt-5-codex model
            if "model: gpt-5-codex" in content:
                models.append(True)
            else:
                models.append(False)
                all_passed = False
                print(f"❌ {droid_file.name}: Model not gpt-5-codex")
            
            # Check for JSON contract
            if "REQUIRED OUTPUT CONTRACT" in content:
                json_contracts += 1
            else:
                all_passed = False
                print(f"❌ {droid_file.name}: Missing JSON contract")
            
            # Check for Anthropic tools
            anthropic_tools = ["TodoWrite", "AskUserQuestion", "NotebookEdit", "BashOutput"]
            for tool in anthropic_tools:
                if tool in content:
                    no_anthropic = False
                    all_passed = False
                    print(f"❌ {droid_file.name}: Contains Anthropic tool '{tool}'")
            
            # Check for bracket delimiters in tools
            if re.search(r'tools:\s*\[', content):
                no_brackets = False
                all_passed = False
                print(f"❌ {droid_file.name}: Contains bracket delimiters")
        
        print(f"✅ Models standardized (gpt-5-codex): {len([x for x in models if x])}/16")
        print(f"✅ JSON contracts present: {json_contracts}/16")
        print(f"✅ No Anthropic tools: {no_anthropic}")
        print(f"✅ No bracket delimiters: {no_brackets}")
        
        if all_passed:
            print("\n✅ TEST SCENARIO 1: PASSED")
            self.results["passed"].append("Scenario 1: YAML & Configuration")
        else:
            print("\n❌ TEST SCENARIO 1: FAILED")
            self.results["failed"].append("Scenario 1: YAML & Configuration")
        
        return all_passed
    
    def test_scenario_2_output_contracts(self) -> bool:
        """Test Scenario 2: Output Contract Parsing"""
        print("\n=== TEST SCENARIO 2: Output Contract Parsing ===\n")
        
        if not self.output_contracts.exists():
            print(f"❌ OUTPUT_CONTRACTS.md not found at {self.output_contracts}")
            self.results["failed"].append("Scenario 2: Output Contracts")
            return False
        
        content = self.output_contracts.read_text()
        
        # Extract JSON schemas from markdown
        json_pattern = r'```json\n(.*?)\n```'
        json_blocks = re.findall(json_pattern, content, re.DOTALL)
        
        print(f"✅ Found {len(json_blocks)} JSON contract blocks")
        
        # Validate each JSON block
        valid_json = 0
        for i, json_block in enumerate(json_blocks):
            try:
                parsed = json.loads(json_block)
                valid_json += 1
            except json.JSONDecodeError as e:
                print(f"❌ JSON block {i+1} invalid: {e}")
                self.results["failed"].append(f"Output contract JSON {i+1}")
        
        print(f"✅ Valid JSON schemas: {valid_json}/{len(json_blocks)}")
        
        # Check for critical contract fields
        critical_fields = [
            "droid",
            "timestamp",
            "execution_status",
            "completion_percentage",
            "output"
        ]
        
        universal_envelope_found = all(
            field in content for field in critical_fields
        )
        
        if universal_envelope_found:
            print(f"✅ Universal envelope defined with all critical fields")
        else:
            print(f"❌ Missing universal envelope fields")
        
        all_passed = valid_json == len(json_blocks) and universal_envelope_found
        
        if all_passed:
            print("\n✅ TEST SCENARIO 2: PASSED")
            self.results["passed"].append("Scenario 2: Output Contracts")
        else:
            print("\n❌ TEST SCENARIO 2: FAILED")
            self.results["failed"].append("Scenario 2: Output Contracts")
        
        return all_passed
    
    def test_scenario_3_task_delegation_syntax(self) -> bool:
        """Test Scenario 3: Task Delegation Syntax Validation"""
        print("\n=== TEST SCENARIO 3: Task Delegation Syntax ===\n")
        
        orch_file = self.droids_dir / "intelligence-orchestrator.md"
        if not orch_file.exists():
            print(f"❌ intelligence-orchestrator.md not found")
            self.results["failed"].append("Scenario 3: Task Delegation Syntax")
            return False
        
        content = orch_file.read_text()
        
        # Check for Task delegation syntax documentation
        task_syntax = 'Task: description='
        if task_syntax in content:
            print(f"✅ Task delegation syntax documented")
        else:
            print(f"❌ Task delegation syntax not documented")
            self.results["failed"].append("Scenario 3: Task Delegation Syntax")
            return False
        
        # Check for workflow patterns
        patterns = [
            "Sequential Deep Dive",
            "Parallel Perspectives",
            "Iterative Refinement",
            "Cross-Domain Synthesis"
        ]
        
        patterns_found = 0
        for pattern in patterns:
            if pattern in content:
                patterns_found += 1
                print(f"✅ {pattern} documented")
            else:
                print(f"❌ {pattern} not documented")
        
        # Check for specialist droid routing
        if "specialist" in content.lower() and "routing" in content.lower():
            print(f"✅ Specialist droid routing guide present")
        else:
            print(f"⚠️  Specialist droid routing guide may be incomplete")
            self.results["warnings"].append("Specialist droid routing")
        
        all_passed = (
            task_syntax in content and
            patterns_found == 4
        )
        
        if all_passed:
            print("\n✅ TEST SCENARIO 3: PASSED")
            self.results["passed"].append("Scenario 3: Task Delegation")
        else:
            print("\n❌ TEST SCENARIO 3: FAILED")
            self.results["failed"].append("Scenario 3: Task Delegation")
        
        return all_passed
    
    def test_scenario_4_workflow_patterns(self) -> bool:
        """Test Scenario 4: Workflow Pattern Documentation"""
        print("\n=== TEST SCENARIO 4: Workflow Patterns ===\n")
        
        phase3_doc = self.workspace_root / "PHASE_3_WORKFLOW_COORDINATION.md"
        
        if not phase3_doc.exists():
            print(f"❌ PHASE_3_WORKFLOW_COORDINATION.md not found")
            self.results["failed"].append("Scenario 4: Workflow Patterns")
            return False
        
        content = phase3_doc.read_text()
        
        # Check for workflow patterns
        patterns = {
            "Sequential Deep Dive": ["Phase 1", "Phase 2", "Phase 3"],
            "Parallel Perspectives": ["Parallel", "concurrent"],
            "Iterative Refinement": ["Cycle", "optimization"],
            "Cross-Domain Synthesis": ["cross-domain", "synthesis"]
        }
        
        patterns_found = 0
        for pattern, keywords in patterns.items():
            found = all(kw.lower() in content.lower() for kw in keywords)
            if found:
                patterns_found += 1
                print(f"✅ {pattern} documented")
            else:
                print(f"❌ {pattern} missing keywords: {keywords}")
        
        # Check for examples (accept "Example" or "Example Workflow")
        example_count = content.count("Example") 
        print(f"✅ Examples documented: {example_count}")
        
        all_passed = patterns_found == 4 and example_count > 0
        
        if all_passed:
            print("\n✅ TEST SCENARIO 4: PASSED")
            self.results["passed"].append("Scenario 4: Workflow Patterns")
        else:
            print("\n❌ TEST SCENARIO 4: FAILED")
            self.results["failed"].append("Scenario 4: Workflow Patterns")
        
        return all_passed
    
    def test_scenario_5_json_validation_framework(self) -> bool:
        """Test Scenario 5: JSON Validation Framework"""
        print("\n=== TEST SCENARIO 5: JSON Validation Framework ===\n")
        
        # Check intelligence-orchestrator for validation framework
        orch_file = self.droids_dir / "intelligence-orchestrator.md"
        content = orch_file.read_text()
        
        validation_elements = [
            "Parse JSON",
            "Check required fields",
            "Data quality",
            "validation"
        ]
        
        elements_found = 0
        for element in validation_elements:
            if element.lower() in content.lower():
                elements_found += 1
                print(f"✅ {element} mentioned")
            else:
                print(f"❌ {element} not found")
        
        all_passed = elements_found >= 3
        
        if all_passed:
            print("\n✅ TEST SCENARIO 5: PASSED")
            self.results["passed"].append("Scenario 5: JSON Validation")
        else:
            print("\n❌ TEST SCENARIO 5: FAILED")
            self.results["failed"].append("Scenario 5: JSON Validation")
        
        return all_passed
    
    def generate_summary(self):
        """Generate test summary report"""
        print("\n" + "="*60)
        print("PHASE 4 INTEGRATION TEST SUMMARY")
        print("="*60 + "\n")
        
        print(f"✅ PASSED ({len(self.results['passed'])}):")
        for test in self.results["passed"]:
            print(f"   • {test}")
        
        if self.results["failed"]:
            print(f"\n❌ FAILED ({len(self.results['failed'])}):")
            for test in self.results["failed"]:
                print(f"   • {test}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"   • {warning}")
        
        total = len(self.results["passed"]) + len(self.results["failed"])
        pass_rate = (len(self.results["passed"]) / total * 100) if total > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"OVERALL PASS RATE: {pass_rate:.1f}% ({len(self.results['passed'])}/{total})")
        print(f"{'='*60}\n")
        
        if len(self.results["failed"]) == 0:
            print("🎉 ALL TESTS PASSED - Phase 4 Ready for Production")
        else:
            print("⚠️  Some tests failed - Review failures above")
        
        return len(self.results["failed"]) == 0
    
    def run_all_tests(self) -> bool:
        """Run all Phase 4 tests"""
        print("\n" + "="*60)
        print("PHASE 4 INTEGRATION TESTING - VALIDATOR")
        print("="*60)
        
        results = [
            self.test_scenario_1_yaml_validation(),
            self.test_scenario_2_output_contracts(),
            self.test_scenario_3_task_delegation_syntax(),
            self.test_scenario_4_workflow_patterns(),
            self.test_scenario_5_json_validation_framework()
        ]
        
        self.generate_summary()
        
        return all(results)


if __name__ == "__main__":
    workspace = "/Users/docravikumar/Code/skill-test/Skill_Seekers"
    validator = Phase4Validator(workspace)
    success = validator.run_all_tests()
    exit(0 if success else 1)
