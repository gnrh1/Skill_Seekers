#!/usr/bin/env python3
"""
Factory Droid Validation System

Comprehensive validation of Factory Droid configuration, YAML syntax, and structure.
Adapted from Claude Code's check-hooks.py for Factory Droid platform.
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

try:
    import yaml
except ImportError:
    print("❌ Error: PyYAML not installed")
    print("💡 Install with: pip install pyyaml")
    sys.exit(1)


class DroidValidator:
    """Comprehensive Factory Droid validation system."""

    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.factory_dir = self.project_dir / ".factory"
        self.agents_md = self.project_dir / "AGENTS.md"
        self.droid_yaml = self.project_dir / ".droid.yaml"
        self.issues = []
        self.fixes_applied = []
        self.is_verbose = False

    def validate_all(self, fix: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Run comprehensive droid validation."""
        self.is_verbose = verbose

        print("🔍 Factory Droid Validation Report")
        print("=" * 34)
        print()

        results = {
            'root_config': False,
            'factory_structure': False,
            'droids': {},
            'commands': {},
            'memory': {},
            'overall_score': 0,
            'issues': [],
            'fixes_applied': []
        }

        # 1. Root Configuration Validation
        print("📋 Validating root configuration...")
        results['root_config'] = self._validate_root_config()

        # 2. Factory Directory Structure
        print("📂 Checking .factory/ structure...")
        results['factory_structure'] = self._validate_factory_structure()

        # 3. Droid Validation
        if (self.factory_dir / "droids").exists():
            print("🤖 Validating droids...")
            results['droids'] = self._validate_droids()

        # 4. Command Validation
        if (self.factory_dir / "commands").exists():
            print("⚡ Validating commands...")
            results['commands'] = self._validate_commands()

        # 5. Memory Validation
        if (self.factory_dir / "memory").exists():
            print("🧠 Validating memory files...")
            results['memory'] = self._validate_memory()

        # 6. Apply fixes if requested
        if fix and self.issues:
            print("\n🔨 Applying fixes...")
            self._apply_fixes()
            results['fixes_applied'] = self.fixes_applied

        # 7. Calculate overall score
        results['overall_score'] = self._calculate_score(results)
        results['issues'] = self.issues

        # 8. Generate report
        self._generate_report(results)

        return results

    def _validate_root_config(self) -> bool:
        """Validate AGENTS.md and .droid.yaml."""
        all_valid = True

        # Validate AGENTS.md
        if self.agents_md.exists():
            agents_valid = self._validate_yaml_frontmatter(
                self.agents_md, "AGENTS.md", required_fields=['name', 'description']
            )
            all_valid = all_valid and agents_valid
        else:
            self.issues.append(("⚠️ Warning", "AGENTS.md not found (optional but recommended)"))

        # Validate .droid.yaml
        if self.droid_yaml.exists():
            try:
                with open(self.droid_yaml, 'r') as f:
                    yaml_content = yaml.safe_load(f)
                
                if not isinstance(yaml_content, dict):
                    self.issues.append(("❌ Critical", ".droid.yaml: Must be YAML dictionary"))
                    all_valid = False
                else:
                    if self.is_verbose:
                        print(f"  ✅ .droid.yaml: Valid YAML structure")
            except yaml.YAMLError as e:
                self.issues.append(("❌ Critical", f".droid.yaml: YAML syntax error: {e}"))
                all_valid = False
        else:
            self.issues.append(("⚠️ Warning", ".droid.yaml not found (optional)"))

        if all_valid:
            print("✅ Root configuration valid")
        
        return all_valid

    def _validate_factory_structure(self) -> bool:
        """Validate .factory/ directory structure."""
        if not self.factory_dir.exists():
            self.issues.append(("❌ Critical", ".factory/ directory not found"))
            return False

        expected_dirs = ['droids', 'commands', 'memory', 'scripts']
        found_dirs = []
        missing_dirs = []

        for dir_name in expected_dirs:
            dir_path = self.factory_dir / dir_name
            if dir_path.exists():
                found_dirs.append(dir_name)
                if self.is_verbose:
                    print(f"  ✅ {dir_name}/ exists")
            else:
                missing_dirs.append(dir_name)
                if self.is_verbose:
                    print(f"  ℹ️  {dir_name}/ not found (may be optional)")

        # Only droids/, commands/, or memory/ are critical
        critical_missing = [d for d in missing_dirs if d in ['droids', 'commands', 'memory']]
        
        if critical_missing:
            self.issues.append(("⚠️ Warning", f"Missing directories: {', '.join(critical_missing)}"))
        
        print(f"✅ .factory/ structure present ({len(found_dirs)}/{len(expected_dirs)} directories)")
        return True

    def _validate_droids(self) -> Dict:
        """Validate all droid definition files."""
        droids_dir = self.factory_dir / "droids"
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'details': []
        }

        if not droids_dir.exists():
            return results

        droid_files = list(droids_dir.glob("*.md"))
        results['total'] = len(droid_files)

        for droid_file in droid_files:
            is_valid = self._validate_droid_file(droid_file)
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
            
            results['details'].append({
                'name': droid_file.name,
                'valid': is_valid
            })

        status = "✅" if results['invalid'] == 0 else "⚠️"
        print(f"  {status} {results['valid']}/{results['total']} droids valid")

        return results

    def _validate_droid_file(self, file_path: Path) -> bool:
        """Validate a single droid definition file."""
        # Validate YAML frontmatter
        has_valid_yaml = self._validate_yaml_frontmatter(
            file_path, 
            file_path.name,
            required_fields=['name', 'description']
        )
        
        if not has_valid_yaml:
            return False

        # Validate content structure
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Check for minimum content length (excluding frontmatter)
            content_without_frontmatter = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            
            if len(content_without_frontmatter.strip()) < 100:
                self.issues.append(("⚠️ Warning", f"{file_path.name}: Very short content (< 100 chars)"))
            
            # Check for recommended sections (not required, just recommended)
            recommended_sections = ['Commands', 'Specialization', 'Detection', 'Standards']
            missing_sections = []
            
            for section in recommended_sections:
                if section not in content and section.lower() not in content.lower():
                    missing_sections.append(section)
            
            if missing_sections and self.is_verbose:
                print(f"  ℹ️  {file_path.name}: Missing recommended sections: {', '.join(missing_sections[:2])}")

            return True

        except Exception as e:
            self.issues.append(("❌ Critical", f"{file_path.name}: Content validation error: {e}"))
            return False

    def _validate_commands(self) -> Dict:
        """Validate all command definition files."""
        commands_dir = self.factory_dir / "commands"
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'details': []
        }

        if not commands_dir.exists():
            return results

        command_files = list(commands_dir.glob("*.md"))
        results['total'] = len(command_files)

        for command_file in command_files:
            is_valid = self._validate_command_file(command_file)
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
            
            results['details'].append({
                'name': command_file.name,
                'valid': is_valid
            })

        status = "✅" if results['invalid'] == 0 else "⚠️"
        print(f"  {status} {results['valid']}/{results['total']} commands valid")

        return results

    def _validate_command_file(self, file_path: Path) -> bool:
        """Validate a single command definition file."""
        # Validate YAML frontmatter with parameters
        has_valid_yaml = self._validate_yaml_frontmatter(
            file_path, 
            file_path.name,
            required_fields=['name', 'description']
        )
        
        if not has_valid_yaml:
            return False

        # Check for parameters in frontmatter (recommended for commands)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter_text = frontmatter_match.group(1)
                frontmatter = yaml.safe_load(frontmatter_text)
                
                if 'parameters' not in frontmatter and self.is_verbose:
                    print(f"  ℹ️  {file_path.name}: No parameters defined (may be optional)")

            return True

        except Exception as e:
            self.issues.append(("❌ Critical", f"{file_path.name}: Command validation error: {e}"))
            return False

    def _validate_memory(self) -> Dict:
        """Validate memory files."""
        memory_dir = self.factory_dir / "memory"
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'details': []
        }

        if not memory_dir.exists():
            return results

        memory_files = list(memory_dir.glob("*.md"))
        results['total'] = len(memory_files)

        for memory_file in memory_files:
            is_valid = self._validate_memory_file(memory_file)
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
            
            results['details'].append({
                'name': memory_file.name,
                'valid': is_valid
            })

        status = "✅" if results['invalid'] == 0 else "⚠️"
        print(f"  {status} {results['valid']}/{results['total']} memory files valid")

        return results

    def _validate_memory_file(self, file_path: Path) -> bool:
        """Validate a single memory file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Memory files are just markdown, check for minimum content
            if len(content.strip()) < 50:
                self.issues.append(("⚠️ Warning", f"{file_path.name}: Very short content (< 50 chars)"))
            
            if self.is_verbose:
                print(f"  ✅ {file_path.name}: Valid markdown")

            return True

        except Exception as e:
            self.issues.append(("❌ Critical", f"{file_path.name}: Read error: {e}"))
            return False

    def _validate_yaml_frontmatter(self, file_path: Path, display_name: str, 
                                   required_fields: List[str] = None) -> bool:
        """Validate YAML frontmatter in a markdown file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Check for YAML frontmatter
            if not content.startswith('---'):
                self.issues.append(("❌ Critical", f"{display_name}: Missing YAML frontmatter"))
                return False

            # Extract frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                self.issues.append(("❌ Critical", f"{display_name}: Malformed YAML frontmatter"))
                return False

            frontmatter_text = frontmatter_match.group(1)

            # Parse YAML
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
            except yaml.YAMLError as e:
                self.issues.append(("❌ Critical", f"{display_name}: YAML syntax error: {e}"))
                return False

            if not isinstance(frontmatter, dict):
                self.issues.append(("❌ Critical", f"{display_name}: YAML frontmatter must be a dictionary"))
                return False

            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in frontmatter]
                if missing_fields:
                    self.issues.append(("❌ Critical", 
                        f"{display_name}: Missing required fields: {', '.join(missing_fields)}"))
                    return False

            # Validate field content
            if 'name' in frontmatter:
                name = frontmatter['name']
                if not isinstance(name, str) or len(name) < 3:
                    self.issues.append(("❌ Critical", f"{display_name}: 'name' must be string (min 3 chars)"))
                    return False

            if 'description' in frontmatter:
                desc = frontmatter['description']
                if not isinstance(desc, str) or len(desc) < 20:
                    self.issues.append(("⚠️ Warning", f"{display_name}: 'description' should be >= 20 chars"))

            if self.is_verbose:
                print(f"  ✅ {display_name}: Valid YAML frontmatter")

            return True

        except Exception as e:
            self.issues.append(("❌ Critical", f"{display_name}: Validation error: {e}"))
            return False

    def _apply_fixes(self):
        """Apply automatic fixes to common issues."""
        print("  ℹ️  Automatic fixes not yet implemented")
        print("  💡 Manual fixes required for detected issues")

    def _calculate_score(self, results: Dict) -> int:
        """Calculate overall droid health score."""
        scores = []

        # Root configuration (25%)
        scores.append(25 if results['root_config'] else 0)

        # Factory structure (15%)
        scores.append(15 if results['factory_structure'] else 0)

        # Droids (30%)
        if results['droids'].get('total', 0) > 0:
            droid_pct = results['droids']['valid'] / results['droids']['total']
            scores.append(int(droid_pct * 30))
        else:
            scores.append(30)  # No droids is OK

        # Commands (15%)
        if results['commands'].get('total', 0) > 0:
            cmd_pct = results['commands']['valid'] / results['commands']['total']
            scores.append(int(cmd_pct * 15))
        else:
            scores.append(15)  # No commands is OK

        # Memory (15%)
        if results['memory'].get('total', 0) > 0:
            mem_pct = results['memory']['valid'] / results['memory']['total']
            scores.append(int(mem_pct * 15))
        else:
            scores.append(15)  # No memory files is OK

        return sum(scores)

    def _generate_report(self, results: Dict):
        """Generate a detailed validation report."""
        print()

        # Root config status
        root_status = "✅" if results['root_config'] else "❌"
        print(f"Root Configuration: {root_status}")

        # Factory structure status
        struct_status = "✅" if results['factory_structure'] else "❌"
        print(f"Factory Structure: {struct_status}")

        # Component summaries
        for component in ['droids', 'commands', 'memory']:
            comp_results = results[component]
            if comp_results.get('total', 0) > 0:
                valid = comp_results['valid']
                total = comp_results['total']
                status = "✅" if comp_results['invalid'] == 0 else "⚠️"
                print(f"{component.capitalize()}: {status} {valid}/{total} valid")

        print()

        # Overall health
        score = results['overall_score']
        if score >= 95:
            health_emoji = "🟢"
            health_status = "Excellent"
        elif score >= 80:
            health_emoji = "🟡"
            health_status = "Good"
        elif score >= 60:
            health_emoji = "🟠"
            health_status = "Fair"
        else:
            health_emoji = "🔴"
            health_status = "Poor"

        print(f"Overall Health: {health_emoji} {health_status} ({score}%)")

        # Issues summary
        if results['issues']:
            print()
            print("🚨 Issues found:")
            for severity, issue in results['issues']:
                print(f"  {severity}: {issue}")

        # Fixes applied
        if results['fixes_applied']:
            print()
            print("🔨 Fixes applied:")
            for fix in results['fixes_applied']:
                print(f"  ✅ {fix}")

        # Suggestions
        if score < 100:
            print()
            print("💡 Suggestions:")
            if not results['root_config']:
                print("  - Review AGENTS.md and .droid.yaml for YAML errors")
            if results.get('droids', {}).get('invalid', 0) > 0:
                print("  - Fix invalid droid files (check YAML frontmatter)")
            if results.get('commands', {}).get('invalid', 0) > 0:
                print("  - Fix invalid command files (check parameters definition)")


def main():
    """Main entry point for droid validation."""
    parser = argparse.ArgumentParser(description="Validate Factory Droid configuration")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes (not yet implemented)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--project-dir", help="Project directory (default: current)")

    args = parser.parse_args()

    validator = DroidValidator(args.project_dir)

    results = validator.validate_all(
        fix=args.fix,
        verbose=args.verbose
    )

    # Exit with appropriate code
    if results['overall_score'] >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Issues found


if __name__ == "__main__":
    main()
