#!/usr/bin/env python3
"""
TDD Tests for Merge Sources
Tests rule-based and Claude-enhanced merging of multi-source data
"""

import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from dataclasses import asdict

# Add cli directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'cli'))

from merge_sources import RuleBasedMerger, ClaudeEnhancedMerger, merge_sources
from conflict_detector import Conflict


class TestRuleBasedMerger(unittest.TestCase):
    """Test RuleBasedMerger class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.docs_data = {
            'pages': {
                'https://docs.example.com/api': {
                    'title': 'API Reference',
                    'content': '''def create_user(name: str, email: str) -> User: pass'''
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
                                    {'name': 'email', 'type': 'str'}
                                ],
                                'return_type': 'User',
                                'docstring': 'Create user.'
                            }
                        ]
                    }
                ]
            }
        }
        
        self.conflicts = []
        self.merger = RuleBasedMerger(self.docs_data, self.github_data, self.conflicts)

    def test_init_stores_data_correctly(self):
        """RED: Test RuleBasedMerger initialization stores data"""
        self.assertEqual(self.merger.docs_data, self.docs_data)
        self.assertEqual(self.merger.github_data, self.github_data)
        self.assertEqual(self.merger.conflicts, self.conflicts)

    def test_merge_all_returns_dict(self):
        """RED: Test merge_all returns structured dictionary"""
        result = self.merger.merge_all()
        
        self.assertIsInstance(result, dict)
        self.assertIn('apis', result)
        self.assertIn('metadata', result)

    def test_merge_all_includes_apis(self):
        """RED: Test merge_all includes API entries"""
        result = self.merger.merge_all()
        
        apis = result['apis']
        self.assertIsInstance(apis, dict)
        
        # Should include create_user from both sources
        self.assertIn('create_user', apis)
        create_user_result = apis['create_user']
        self.assertIn('merged_info', create_user_result)

    def test_merge_all_includes_metadata(self):
        """RED: Test merge_all includes metadata"""
        result = self.merger.merge_all()
        
        metadata = result['metadata']
        self.assertIsInstance(metadata, dict)
        self.assertIn('merge_mode', metadata)
        self.assertIn('sources', metadata)
        self.assertIn('conflict_count', metadata)

    def test_merge_all_handles_conflicts(self):
        """RED: Test merge_all handles conflicts correctly"""
        # Add conflict
        test_conflict = Conflict(
            type='signature_mismatch',
            severity='low',
            api_name='test_api',
            difference='Test conflict'
        )
        merger_with_conflict = RuleBasedMerger(
            self.docs_data, self.github_data, [test_conflict]
        )
        
        result = merger_with_conflict.merge_all()
        
        metadata = result['metadata']
        self.assertEqual(metadata['conflict_count'], 1)

    def test_merge_single_api(self):
        """RED: Test _merge_single_api merges single API correctly"""
        result = self.merger._merge_single_api('create_user')
        
        self.assertIsInstance(result, dict)
        self.assertIn('api_name', result)
        self.assertIn('merged_info', result)
        self.assertIn('sources', result)

    def test_merge_single_api_with_conflict(self):
        """RED: Test _merge_single_api handles conflicts"""
        # Add conflict for create_user
        test_conflict = Conflict(
            type='signature_mismatch',
            severity='low',
            api_name='create_user',
            difference='Parameter mismatch'
        )
        merger_with_conflict = RuleBasedMerger(
            self.docs_data, self.github_data, [test_conflict]
        )
        
        result = merger_with_conflict._merge_single_api('create_user')
        
        merged_info = result['merged_info']
        self.assertIn('conflict', merged_info)
        self.assertEqual(merged_info['conflict']['api_name'], 'create_user')

    def test_merge_single_api_docs_only(self):
        """RED: Test _merge_single_api handles docs-only API"""
        docs_only_data = {
            'pages': {
                'https://docs.example.com/api': {
                    'title': 'API Reference',
                    'content': '''def docs_only_api() -> Result: pass'''
                }
            }
        }
        
        merger_docs_only = RuleBasedMerger(docs_only_data, {}, [])
        result = merger_docs_only._merge_single_api('docs_only_api')
        
        merged_info = result['merged_info']
        self.assertIn('docs_only', merged_info)
        self.assertTrue(merged_info['docs_only'])

    def test_merge_single_api_code_only(self):
        """RED: Test _merge_single_api handles code-only API"""
        code_only_data = {
            'code_analysis': {
                'depth': 'surface',
                'files': [
                    {
                        'file': 'src/api.py',
                        'functions': [
                            {
                                'name': 'code_only_api',
                                'parameters': [],
                                'return_type': 'Result'
                            }
                        ]
                    }
                ]
            }
        }
        
        merger_code_only = RuleBasedMerger({}, code_only_data, [])
        result = merger_code_only._merge_single_api('code_only_api')
        
        merged_info = result['merged_info']
        self.assertIn('undocumented', merged_info)
        self.assertTrue(merged_info['undocumented'])

    def test_create_merged_signature(self):
        """RED: Test _create_merged_signature creates proper signature"""
        code_info = {
            'parameters': [
                {'name': 'param1', 'type': 'str'},
                {'name': 'param2', 'type': 'int', 'default': '0'}
            ],
            'return_type': 'Result'
        }
        docs_info = {
            'return_type': 'Result'
        }
        
        signature = self.merger._create_merged_signature(code_info, docs_info)
        
        # Should include both parameters
        self.assertIn('param1', signature)
        self.assertIn('param2', signature)
        self.assertIn('default', signature)  # Default value preserved
        self.assertIn('-> Result', signature)  # Return type included

    def test_empty_data_handling(self):
        """RED: Test merger handles empty data gracefully"""
        empty_merger = RuleBasedMerger({}, {}, [])
        result = empty_merger.merge_all()
        
        self.assertIsInstance(result, dict)
        self.assertIn('apis', result)
        self.assertIn('metadata', result)
        self.assertEqual(len(result['apis']), 0)


class TestClaudeEnhancedMerger(unittest.TestCase):
    """Test ClaudeEnhancedMerger class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.docs_data = {'pages': {}}
        self.github_data = {'code_analysis': {'depth': 'surface', 'files': []}}
        self.conflicts = []
        self.merger = ClaudeEnhancedMerger(self.docs_data, self.github_data, self.conflicts)

    def test_init_stores_data_correctly(self):
        """RED: Test ClaudeEnhancedMerger initialization stores data"""
        self.assertEqual(self.merger.docs_data, self.docs_data)
        self.assertEqual(self.merger.github_data, self.github_data)
        self.assertEqual(self.merger.conflicts, self.conflicts)

    def test_merge_all_returns_dict(self):
        """RED: Test merge_all returns structured dictionary"""
        with patch.object(self.merger, '_launch_claude_merge') as mock_launch, \
             patch.object(self.merger, '_read_merged_results') as mock_read:
            
            mock_launch.return_value = None
            mock_read.return_value = {'merged': 'data'}
            
            result = self.merger.merge_all()
            
            self.assertIsInstance(result, dict)
            self.assertIn('merged', result)

    def test_create_workspace(self):
        """RED: Test _create_workspace creates temporary directory"""
        workspace = self.merger._create_workspace()
        
        self.assertIsInstance(workspace, str)
        self.assertTrue(Path(workspace).exists())
        self.assertTrue(workspace.startswith(tempfile.gettempdir()))

    def test_count_by_field(self):
        """RED: Test _count_by_field counts occurrences correctly"""
        test_data = {
            'files': [
                {'type': 'function', 'name': 'func1'},
                {'type': 'class', 'name': 'Class1'},
                {'type': 'function', 'name': 'func2'}
            ]
        }
        
        counts = self.merger._count_by_field('type')
        
        self.assertEqual(counts.get('function', 0), 2)
        self.assertEqual(counts.get('class', 0), 1)

    def test_launch_claude_merge(self):
        """RED: Test _launch_claude_merge calls Claude Code"""
        workspace = '/tmp/test_workspace'
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            self.merger._launch_claude_merge(workspace)
            
            # Should call subprocess.run with appropriate arguments
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0]
            
            # Check that claude command is called
            cmd = call_args[0]
            self.assertTrue(any('claude' in str(arg) for arg in cmd))

    def test_launch_claude_merge_handles_error(self):
        """RED: Test _launch_claude_merge handles subprocess errors"""
        workspace = '/tmp/test_workspace'
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, 'claude')
            
            with self.assertRaises(Exception):
                self.merger._launch_claude_merge(workspace)

    def test_read_merged_results(self):
        """RED: Test _read_merged_results reads merged data from workspace"""
        workspace = '/tmp/test_workspace'
        merged_data = {'apis': {'test': 'data'}}
        
        with patch('builtins.open', mock_open(read_data=json.dumps(merged_data))):
            with patch('json.load') as mock_load:
                mock_load.return_value = merged_data
                
                result = self.merger._read_merged_results(workspace)
                
                self.assertEqual(result, merged_data)

    def test_read_merged_results_handles_missing_file(self):
        """RED: Test _read_merged_results handles missing file gracefully"""
        workspace = '/tmp/nonexistent_workspace'
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = self.merger._read_merged_results(workspace)
            
            # Should return empty dict or handle gracefully
            self.assertIsInstance(result, dict)


class TestMergeSourcesCLI(unittest.TestCase):
    """Test merge_sources CLI interface"""

    def setUp(self):
        """Set up test fixtures"""
        self.docs_data = {'pages': {}}
        self.github_data = {'files': {}}
        
        self.docs_path = '/tmp/test_docs.json'
        self.github_path = '/tmp/test_github.json'
        
        with open(self.docs_path, 'w') as f:
            json.dump(self.docs_data, f)
        with open(self.github_path, 'w') as f:
            json.dump(self.github_data, f)

    def tearDown(self):
        """Clean up test fixtures"""
        for path in [self.docs_path, self.github_path]:
            if Path(path).exists():
                Path(path).unlink()

    def test_merge_sources_with_rule_based_mode(self):
        """RED: Test CLI with rule-based merge mode"""
        output_path = '/tmp/test_output.json'
        
        with patch('sys.argv', [
            'merge_sources.py',
            '--docs', self.docs_path,
            '--github', self.github_path,
            '--output', output_path,
            '--mode', 'rule-based'
        ]):
            with patch('merge_sources.RuleBasedMerger') as mock_merger:
                mock_instance = mock_merger.return_value
                mock_instance.merge_all.return_value = {'merged': 'data'}
                
                try:
                    from merge_sources import main
                    main()
                    
                    # Should create RuleBasedMerger with data
                    mock_merger.assert_called_once()
                    call_args = mock_merger.call_args[0]
                    self.assertEqual(len(call_args), 3)  # docs_data, github_data, conflicts
                except SystemExit:
                    pass  # Expected when CLI completes

    def test_merge_sources_with_claude_enhanced_mode(self):
        """RED: Test CLI with claude-enhanced merge mode"""
        output_path = '/tmp/test_output.json'
        
        with patch('sys.argv', [
            'merge_sources.py',
            '--docs', self.docs_path,
            '--github', self.github_path,
            '--output', output_path,
            '--mode', 'claude-enhanced'
        ]):
            with patch('merge_sources.ClaudeEnhancedMerger') as mock_merger:
                mock_instance = mock_merger.return_value
                mock_instance.merge_all.return_value = {'enhanced': 'data'}
                
                try:
                    from merge_sources import main
                    main()
                    
                    # Should create ClaudeEnhancedMerger with data
                    mock_merger.assert_called_once()
                except SystemExit:
                    pass  # Expected when CLI completes

    def test_merge_sources_writes_output_file(self):
        """RED: Test CLI writes output file"""
        output_path = '/tmp/test_merge_output.json'
        
        with patch('sys.argv', [
            'merge_sources.py',
            '--docs', self.docs_path,
            '--github', self.github_path,
            '--output', output_path,
            '--mode', 'rule-based'
        ]):
            with patch('merge_sources.RuleBasedMerger') as mock_merger:
                mock_instance = mock_merger.return_value
                mock_instance.merge_all.return_value = {'result': 'success'}
                
                try:
                    from merge_sources import main
                    main()
                    
                    # Should write output file
                    self.assertTrue(Path(output_path).exists())
                    
                    with open(output_path, 'r') as f:
                        output_data = json.load(f)
                        self.assertIn('result', output_data)
                        
                except SystemExit:
                    pass  # Expected when CLI completes
                finally:
                    if Path(output_path).exists():
                        Path(output_path).unlink()


if __name__ == '__main__':
    unittest.main()
