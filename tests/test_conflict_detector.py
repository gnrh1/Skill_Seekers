#!/usr/bin/env python3
"""
TDD Tests for Conflict Detector
Tests for multi-source conflict detection between documentation and code
"""

import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add cli directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'cli'))

from conflict_detector import ConflictDetector, Conflict


class TestConflictDetector(unittest.TestCase):
    """Test ConflictDetector class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.docs_data = {
            'pages': {
                'https://docs.example.com/api/user': {
                    'title': 'User API reference',
                    'content': '''
                    def create_user(name: str, email: str) -> User:
                        """Create a new user account."""
                        pass
                    def delete_user(user_id: int) -> bool:
                        """Delete user by ID."""
                        pass
                    '''
                },
                'https://docs.example.com/api/auth': {
                    'title': 'Authentication API',
                    'content': '''
                    def login(username: str, password: str) -> Token:
                        """User login."""
                        pass
                    '''
                }
            }
        }
        
        self.github_data = {
            'code_analysis': {
                'depth': 'surface',
                'files': [
                    {
                        'file': 'src/user.py',
                        'functions': [
                            {
                                'name': 'create_user',
                                'parameters': [
                                    {'name': 'name', 'type': 'str'},
                                    {'name': 'email', 'type': 'str'},
                                    {'name': 'role', 'type': 'str', 'default': 'user'}
                                ],
                                'return_type': 'User',
                                'docstring': 'Create user with role.',
                                'line_number': 1
                            },
                            {
                                'name': 'delete_user',
                                'parameters': [
                                    {'name': 'user_id', 'type': 'int'}
                                ],
                                'return_type': 'bool',
                                'docstring': 'Delete user permanently.',
                                'line_number': 2
                            },
                            {
                                'name': 'get_user',
                                'parameters': [
                                    {'name': 'user_id', 'type': 'int'}
                                ],
                                'return_type': 'User',
                                'docstring': 'Get user by ID.',
                                'line_number': 3
                            }
                        ]
                    },
                    {
                        'file': 'src/auth.py',
                        'functions': [
                            {
                                'name': 'login',
                                'parameters': [
                                    {'name': 'username', 'type': 'str'},
                                    {'name': 'password', 'type': 'str'},
                                    {'name': 'mfa', 'type': 'bool', 'default': False}
                                ],
                                'return_type': 'Token',
                                'docstring': 'Login with optional MFA.',
                                'line_number': 1
                            },
                            {
                                'name': 'logout',
                                'parameters': [
                                    {'name': 'token', 'type': 'str'}
                                ],
                                'return_type': 'bool',
                                'docstring': 'Logout user.',
                                'line_number': 2
                            }
                        ]
                    }
                ]
            }
        }
        
        self.detector = ConflictDetector(self.docs_data, self.github_data)

    def test_init_stores_data_correctly(self):
        """RED: Test ConflictDetector initialization stores data"""
        self.assertEqual(self.detector.docs_data, self.docs_data)
        self.assertEqual(self.detector.github_data, self.github_data)

    def test_extract_docs_apis_parses_functions(self):
        """RED: Test _extract_docs_apis correctly parses function signatures"""
        apis = self.detector._extract_docs_apis()
        
        # Should extract documented APIs
        self.assertIn('create_user', apis)
        self.assertIn('delete_user', apis) 
        self.assertIn('login', apis)
        
        # Check create_user signature
        create_user_info = apis['create_user']
        self.assertEqual(create_user_info['parameters'][0]['name'], 'name')
        self.assertEqual(create_user_info['parameters'][1]['name'], 'email')
        self.assertEqual(create_user_info['return_type'], 'User')  # Check return type parsing

    def test_extract_code_apis_parses_functions(self):
        """RED: Test _extract_code_apis correctly parses code functions"""
        apis = self.detector._extract_code_apis()
        
        # Should extract code APIs
        self.assertIn('create_user', apis)
        self.assertIn('delete_user', apis)
        self.assertIn('get_user', apis)
        self.assertIn('login', apis)
        self.assertIn('logout', apis)
        
        # Check create_user signature from code
        create_user_info = apis['create_user']
        self.assertEqual(create_user_info['parameters'][0]['name'], 'name')
        self.assertEqual(create_user_info['parameters'][1]['name'], 'email')
        self.assertEqual(create_user_info['parameters'][2]['name'], 'role')  # Has default
        self.assertEqual(create_user_info['parameters'][2]['default'], 'user')

    def test_detect_missing_in_docs(self):
        """RED: Test detection of APIs present in code but missing from docs"""
        conflicts = self.detector._find_missing_in_docs()
        
        # Should find get_user and logout (in code but not docs)
        missing_apis = [c.api_name for c in conflicts if c.type == 'missing_in_docs']
        self.assertIn('get_user', missing_apis)
        self.assertIn('logout', missing_apis)
        self.assertEqual(len(missing_apis), 2)
        
        # Check severity
        get_user_conflict = next(c for c in conflicts if c.api_name == 'get_user')
        self.assertEqual(get_user_conflict.severity, 'high')  # Missing documentation is severe

    def test_detect_missing_in_code(self):
        """RED: Test detection of APIs documented but not in code"""
        # Modify docs to include something not in code
        docs_with_extra = {
            'pages': {
                'https://docs.example.com/api/extra': {
                    'title': 'Extra API',
                    'content': 'def update_user(user_id: int, data: dict) -> User: pass'
                }
            }
        }
        detector_with_extra = ConflictDetector(docs_with_extra, self.github_data)
        conflicts = detector_with_extra._find_missing_in_code()
        
        # Should find update_user (in docs but not code)
        missing_apis = [c.api_name for c in conflicts if c.type == 'missing_in_code']
        self.assertIn('update_user', missing_apis)
        self.assertEqual(len(missing_apis), 1)
        
        # Check severity
        update_user_conflict = next(c for c in conflicts if c.api_name == 'update_user')
        self.assertEqual(update_user_conflict.severity, 'medium')

    def test_detect_signature_mismatches(self):
        """RED: Test detection of parameter mismatches between docs and code"""
        conflicts = self.detector._find_signature_mismatches()
        
        # Should find signature mismatch in login (docs has 2 params, code has 3)
        login_conflicts = [c for c in conflicts if c.api_name == 'login']
        self.assertEqual(len(login_conflicts), 1)
        
        login_conflict = login_conflicts[0]
        self.assertEqual(login_conflict.type, 'signature_mismatch')
        self.assertIn('parameter count mismatch', login_conflict.difference)
        self.assertEqual(login_conflict.severity, 'medium')

    def test_detect_all_conflicts_integration(self):
        """RED: Test detect_all_conflicts returns comprehensive conflict list"""
        all_conflicts = self.detector.detect_all_conflicts()
        
        # Should detect multiple conflict types
        conflict_types = set(c.type for c in all_conflicts)
        expected_types = {'missing_in_docs', 'signature_mismatch'}
        self.assertTrue(expected_types.issubset(conflict_types))
        
        # Should have at least 2 conflicts total (based on current test data)
        self.assertGreaterEqual(len(all_conflicts), 2)
        
        # Check severity distribution
        medium_severity = [c for c in all_conflicts if c.severity == 'medium']
        low_severity = [c for c in all_conflicts if c.severity == 'low']
        self.assertGreaterEqual(len(medium_severity), 1)  # missing_in_docs should be medium
        self.assertGreaterEqual(len(low_severity), 1)     # signature_mismatch should be low

    def test_generate_summary_structure(self):
        """RED: Test generate_summary creates proper structure"""
        all_conflicts = self.detector.detect_all_conflicts()
        summary = self.detector.generate_summary(all_conflicts)
        
        # Check summary structure
        self.assertIn('total_conflicts', summary)
        self.assertIn('by_type', summary)
        self.assertIn('by_severity', summary)
        self.assertIn('conflicts', summary)
        
        # Check counts
        self.assertEqual(summary['total_conflicts'], len(all_conflicts))
        self.assertIsInstance(summary['by_type'], dict)
        self.assertIsInstance(summary['by_severity'], dict)

    def test_save_conflicts_writes_json(self):
        """RED: Test save_conflicts writes valid JSON"""
        all_conflicts = self.detector.detect_all_conflicts()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = f"{tmpdir}/conflicts.json"
            self.detector.save_conflicts(all_conflicts, output_path)
            
            # Verify file exists and is valid JSON
            self.assertTrue(Path(output_path).exists())
            
            with open(output_path, 'r') as f:
                saved_data = json.load(f)
                self.assertIn('summary', saved_data)
                self.assertIn('conflicts', saved_data)
                self.assertEqual(len(saved_data['conflicts']), len(all_conflicts))

    def test_empty_data_handling(self):
        """RED: Test conflict detector handles empty data gracefully"""
        empty_detector = ConflictDetector({'pages': []}, {'files': []})
        
        # Should not crash and return empty results
        apis = empty_detector._extract_docs_apis()
        code_apis = empty_detector._extract_code_apis()
        conflicts = empty_detector.detect_all_conflicts()
        
        self.assertEqual(len(apis), 0)
        self.assertEqual(len(code_apis), 0)
        self.assertEqual(len(conflicts), 0)

    def test_malformed_content_handling(self):
        """RED: Test conflict detector handles malformed content gracefully"""
        malformed_docs = {
            'pages': [
                {
                    'url': 'https://docs.example.com/malformed',
                    'content': 'def broken_syntax(  # Missing closing parenthesis'
                }
            ]
        }
        malformed_detector = ConflictDetector(malformed_docs, self.github_data)
        
        # Should not crash, may return empty or partial results
        try:
            apis = malformed_detector._extract_docs_apis()
            # Should handle gracefully (either return empty or partial results)
            self.assertIsInstance(apis, dict)
        except Exception as e:
            self.fail(f"_extract_docs_apis should handle malformed content gracefully: {e}")


class TestConflictDataclass(unittest.TestCase):
    """Test Conflict dataclass functionality"""

    def test_conflict_creation(self):
        """RED: Test Conflict dataclass creation and attributes"""
        conflict = Conflict(
            type='missing_in_docs',
            severity='high',
            api_name='test_api',
            docs_info={'description': 'Test API'},
            code_info={'file': 'test.py'},
            difference='API not documented',
            suggestion='Add documentation'
        )
        
        self.assertEqual(conflict.type, 'missing_in_docs')
        self.assertEqual(conflict.severity, 'high')
        self.assertEqual(conflict.api_name, 'test_api')
        self.assertEqual(conflict.difference, 'API not documented')
        self.assertEqual(conflict.suggestion, 'Add documentation')

    def test_conflict_to_dict_conversion(self):
        """RED: Test Conflict can be converted to dict for JSON serialization"""
        conflict = Conflict(
            type='signature_mismatch',
            severity='medium',
            api_name='test_func',
            difference='Parameter count mismatch'
        )
        
        from dataclasses import asdict
        conflict_dict = asdict(conflict)
        
        self.assertIn('type', conflict_dict)
        self.assertIn('severity', conflict_dict)
        self.assertIn('api_name', conflict_dict)
        self.assertIn('difference', conflict_dict)
        self.assertEqual(conflict_dict['type'], 'signature_mismatch')
        self.assertEqual(conflict_dict['severity'], 'medium')


if __name__ == '__main__':
    unittest.main()
