#!/usr/bin/env python3
"""
TDD Tests for Index Codebase
Tests codebase indexing and symbol extraction
"""

import sys
import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from io import StringIO

# Add cli directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'cli'))

from index_codebase import detect_language, should_skip_dir, iter_source_files, summarize_symbols, make_markdown


class TestLanguageDetection(unittest.TestCase):
    """Test language detection functionality"""

    def test_detect_python_language(self):
        """RED: Test Python file detection"""
        self.assertEqual(detect_language('test.py'), 'Python')
        self.assertEqual(detect_language('src/module.py'), 'Python')
        self.assertEqual(detect_language('/path/to/file.py'), 'Python')

    def test_detect_javascript_language(self):
        """RED: Test JavaScript file detection"""
        self.assertEqual(detect_language('app.js'), 'JavaScript')
        self.assertEqual(detect_language('script.js'), 'JavaScript')
        self.assertEqual(detect_language('component.jsx'), 'JavaScript')

    def test_detect_typescript_language(self):
        """RED: Test TypeScript file detection"""
        self.assertEqual(detect_language('types.ts'), 'TypeScript')
        self.assertEqual(detect_language('interface.tsx'), 'TypeScript')

    def test_detect_cpp_language(self):
        """RED: Test C++ file detection"""
        self.assertEqual(detect_language('header.hpp'), 'C++')
        self.assertEqual(detect_language('source.cpp'), 'C++')
        self.assertEqual(detect_language('implementation.cxx'), 'C++')

    def test_detect_c_language(self):
        """RED: Test C file detection"""
        self.assertEqual(detect_language('source.c'), 'C')
        self.assertEqual(detect_language('main.c'), 'C')

    def test_detect_unknown_language(self):
        """RED: Test unknown file extension"""
        self.assertIsNone(detect_language('unknown.xyz'))
        self.assertIsNone(detect_language('file'))
        self.assertIsNone(detect_language('no_extension'))

    def test_detect_language_case_insensitive(self):
        """RED: Test language detection is case insensitive"""
        self.assertEqual(detect_language('TEST.PY'), 'python')
        self.assertEqual(detect_language('APP.JS'), 'javascript')
        self.assertEqual(detect_language('HEADER.HPP'), 'cpp')


class TestDirectorySkipping(unittest.TestCase):
    """Test directory skipping logic"""

    def test_skip_git_directory(self):
        """RED: Test .git directory is skipped"""
        self.assertTrue(should_skip_dir('.git'))
        self.assertTrue(should_skip_dir('subdir/.git'))

    def test_skip_cache_directories(self):
        """RED: Test cache directories are skipped"""
        self.assertTrue(should_skip_dir('__pycache__'))
        self.assertTrue(should_skip_dir('.pytest_cache'))
        self.assertTrue(should_skip_dir('.mypy_cache'))

    def test_skip_venv_directory(self):
        """RED: Test venv directory is skipped"""
        self.assertTrue(should_skip_dir('.venv'))
        self.assertTrue(should_skip_dir('venv'))

    def test_skip_node_modules(self):
        """RED: Test node_modules directory is skipped"""
        self.assertTrue(should_skip_dir('node_modules'))

    def test_not_skip_normal_directories(self):
        """RED: Test normal directories are not skipped"""
        self.assertFalse(should_skip_dir('src'))
        self.assertFalse(should_skip_dir('tests'))
        self.assertFalse(should_skip_dir('docs'))
        self.assertFalse(should_skip_dir('lib'))

    def test_not_skip_hidden_dirs(self):
        """RED: Test some hidden directories are not skipped"""
        self.assertFalse(should_skip_dir('.config'))
        self.assertFalse(should_skip_dir('.vscode'))


class TestSourceFileIteration(unittest.TestCase):
    """Test source file iteration functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_root = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_root)

    def test_iter_python_files(self):
        """RED: Test iteration finds Python files"""
        # Create test Python files
        Path(self.test_root, 'test.py').touch()
        Path(self.test_root, 'subdir', 'module.py').mkdir(parents=True)
        Path(self.test_root, 'subdir', 'module.py').touch()

        files = iter_source_files(self.test_root)

        # Should find Python files
        python_files = [f for f in files if f.endswith('.py')]
        self.assertGreaterEqual(len(python_files), 2)

    def test_iter_mixed_language_files(self):
        """RED: Test iteration finds multiple language files"""
        # Create test files in different languages
        Path(self.test_root, 'test.py').touch()
        Path(self.test_root, 'app.js').touch()
        Path(self.test_root, 'header.hpp').touch()

        files = iter_source_files(self.test_root)

        # Should find files from all supported languages
        extensions = set(Path(f).suffix for f in files)
        self.assertIn('.py', extensions)
        self.assertIn('.js', extensions)
        self.assertIn('.hpp', extensions)

    def test_iter_skips_excluded_directories(self):
        """RED: Test iteration skips excluded directories"""
        # Create files in excluded directories
        Path(self.test_root, '.git', 'config.py').mkdir(parents=True)
        Path(self.test_root, '.git', 'config.py').touch()
        Path(self.test_root, '__pycache__', 'module.pyc').mkdir(parents=True)
        Path(self.test_root, '__pycache__', 'module.pyc').touch()
        Path(self.test_root, 'normal.py').touch()

        files = iter_source_files(self.test_root)

        # Should not find files in excluded directories
        git_files = [f for f in files if '.git' in f]
        cache_files = [f for f in files if '__pycache__' in f]
        normal_files = [f for f in files if 'normal.py' in f]

        self.assertEqual(len(git_files), 0)
        self.assertEqual(len(cache_files), 0)
        self.assertGreaterEqual(len(normal_files), 1)

    def test_iter_empty_directory(self):
        """RED: Test iteration handles empty directory"""
        files = iter_source_files(self.test_root)
        self.assertEqual(len(files), 0)

    def test_iter_nonexistent_directory(self):
        """RED: Test iteration handles nonexistent directory"""
        nonexistent = Path(self.test_root, 'nonexistent')
        files = iter_source_files(str(nonexistent))
        self.assertEqual(len(files), 0)


class TestSymbolSummarization(unittest.TestCase):
    """Test symbol summarization functionality"""

    def test_summarize_empty_records(self):
        """RED: Test summarization handles empty records"""
        records = []
        summary = summarize_symbols(records)

        self.assertIn('classes_index', summary)
        self.assertIn('functions_index', summary)
        self.assertEqual(len(summary['classes_index']), 0)
        self.assertEqual(len(summary['functions_index']), 0)

    def test_summarize_classes(self):
        """RED: Test summarization groups classes"""
        records = [
            {
                'type': 'class',
                'name': 'User',
                'file': 'models.py',
                'line_number': 10,
                'base_classes': ['BaseModel']
            },
            {
                'type': 'class',
                'name': 'User',  # Duplicate name, different location
                'file': 'entities.py',
                'line_number': 5,
                'base_classes': []
            },
            {
                'type': 'class',
                'name': 'Product',
                'file': 'models.py',
                'line_number': 50,
                'base_classes': ['BaseModel']
            }
        ]

        summary = summarize_symbols(records)
        classes_index = summary['classes_index']

        # Should group by class name
        self.assertIn('User', classes_index)
        self.assertIn('Product', classes_index)

        # User should have 2 occurrences
        self.assertEqual(len(classes_index['User']), 2)

        # Each entry should have expected fields
        for user_entry in classes_index['User']:
            self.assertIn('file', user_entry)
            self.assertIn('line_number', user_entry)
            self.assertIn('base_classes', user_entry)

    def test_summarize_functions(self):
        """RED: Test summarization groups functions"""
        records = [
            {
                'type': 'function',
                'name': 'create_user',
                'file': 'user.py',
                'line_number': 20,
                'parameters': [{'name': 'name', 'type': 'str'}],
                'return_type': 'User'
            },
            {
                'type': 'function',
                'name': 'create_user',  # Duplicate name
                'file': 'api.py',
                'line_number': 10,
                'parameters': [{'name': 'email', 'type': 'str'}],
                'return_type': 'User'
            },
            {
                'type': 'function',
                'name': 'delete_user',
                'file': 'user.py',
                'line_number': 30,
                'parameters': [],
                'return_type': 'bool'
            }
        ]

        summary = summarize_symbols(records)
        functions_index = summary['functions_index']

        # Should group by function name
        self.assertIn('create_user', functions_index)
        self.assertIn('delete_user', functions_index)

        # create_user should have 2 occurrences
        self.assertEqual(len(functions_index['create_user']), 2)

        # Each entry should have expected fields
        for func_entry in functions_index['create_user']:
            self.assertIn('file', func_entry)
            self.assertIn('line_number', func_entry)

    def test_summarize_mixed_records(self):
        """RED: Test summarization handles mixed record types"""
        records = [
            {'type': 'class', 'name': 'User', 'file': 'models.py'},
            {'type': 'function', 'name': 'create_user', 'file': 'user.py'},
            {'type': 'function', 'name': 'delete_user', 'file': 'user.py'}
        ]

        summary = summarize_symbols(records)

        # Should create both indices
        self.assertIn('classes_index', summary)
        self.assertIn('functions_index', summary)
        self.assertEqual(len(summary['classes_index']), 1)
        self.assertEqual(len(summary['functions_index']), 2)

    def test_summarize_ignores_other_types(self):
        """RED: Test summarization ignores non-class/function records"""
        records = [
            {'type': 'variable', 'name': 'const', 'file': 'config.py'},
            {'type': 'import', 'name': 'module', 'file': 'main.py'},
            {'type': 'class', 'name': 'User', 'file': 'models.py'},
            {'type': 'function', 'name': 'func', 'file': 'utils.py'}
        ]

        summary = summarize_symbols(records)

        # Should only include classes and functions
        self.assertEqual(len(summary['classes_index']), 1)
        self.assertEqual(len(summary['functions_index']), 1)


class TestMarkdownGeneration(unittest.TestCase):
    """Test Markdown generation functionality"""

    def test_make_markdown_basic_structure(self):
        """RED: Test Markdown generation creates basic structure"""
        index = {
            'classes_index': {'TestClass': [{'file': 'test.py', 'line_number': 10}]},
            'functions_index': {'test_func': [{'file': 'test.py', 'line_number': 20}]},
            'metadata': {'total_files': 1, 'total_symbols': 2}
        }

        markdown = make_markdown(index)

        # Should contain title
        self.assertIn('# Code Index', markdown)
        self.assertIn('## Summary', markdown)

        # Should contain sections
        self.assertIn('## Classes', markdown)
        self.assertIn('## Functions', markdown)

        # Should contain symbol names
        self.assertIn('TestClass', markdown)
        self.assertIn('test_func', markdown)

    def test_make_markdown_includes_metadata(self):
        """RED: Test Markdown generation includes metadata"""
        index = {
            'classes_index': {},
            'functions_index': {},
            'metadata': {
                'total_files': 5,
                'total_symbols': 10,
                'languages': ['python', 'javascript']
            }
        }

        markdown = make_markdown(index)

        # Should include summary statistics
        self.assertIn('5 files', markdown)
        self.assertIn('10 symbols', markdown)
        self.assertIn('python', markdown)
        self.assertIn('javascript', markdown)

    def test_make_markdown_groups_by_symbol(self):
        """RED: Test Markdown generation groups by symbol name"""
        index = {
            'classes_index': {
                'User': [
                    {'file': 'models.py', 'line_number': 10},
                    {'file': 'entities.py', 'line_number': 5}
                ]
            },
            'functions_index': {}
        }

        markdown = make_markdown(index)

        # Should group User class occurrences
        self.assertIn('User', markdown)
        self.assertIn('models.py:10', markdown)
        self.assertIn('entities.py:5', markdown)

    def test_make_markdown_handles_empty_index(self):
        """RED: Test Markdown generation handles empty index"""
        index = {
            'classes_index': {},
            'functions_index': {},
            'metadata': {'total_files': 0, 'total_symbols': 0}
        }

        markdown = make_markdown(index)

        # Should still generate valid Markdown
        self.assertIn('# Code Index', markdown)
        self.assertIn('## Summary', markdown)
        self.assertIn('0 files', markdown)
        self.assertIn('0 symbols', markdown)

    def test_make_markdown_escapes_special_chars(self):
        """RED: Test Markdown generation escapes special characters"""
        index = {
            'classes_index': {
                'Test<Class>': [{'file': 'test.py', 'line_number': 10}]
            },
            'functions_index': {}
        }

        markdown = make_markdown(index)

        # Should generate valid Markdown without breaking
        self.assertIn('Test<Class>', markdown)
        self.assertIn('test.py:10', markdown)


if __name__ == '__main__':
    unittest.main()
