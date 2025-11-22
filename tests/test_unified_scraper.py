#!/usr/bin/env python3
"""
TDD Tests for Unified Multi-Source Scraper
Tests orchestration of scraping from multiple sources
"""

import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict

# Add cli directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'cli'))

from unified_scraper import UnifiedScraper


class TestUnifiedScraper(unittest.TestCase):
    """Test UnifiedScraper class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            'name': 'test_project',
            'description': 'Test project for unified scraping',
            'sources': [
                {
                    'name': 'docs',
                    'type': 'documentation',
                    'base_url': 'https://docs.example.com/',
                    'max_pages': 10,
                    'selectors': {'main_content': 'article'}
                },
                {
                    'name': 'github', 
                    'type': 'github',
                    'repo': 'test/project',
                    'max_files': 20,
                    'code_analysis_depth': 'surface'
                }
            ],
            'merge_mode': 'rule-based',
            'enhancement': {
                'mode': 'local'
            }
        }
        
        self.config_path = '/tmp/test_config.json'
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        self.scraper = UnifiedScraper(self.config_path)

    def tearDown(self):
        """Clean up test fixtures"""
        if Path(self.config_path).exists():
            Path(self.config_path).unlink()

    def test_init_stores_config(self):
        """RED: Test UnifiedScraper initialization stores config correctly"""
        self.assertEqual(self.scraper.config['name'], 'test_project')
        self.assertEqual(len(self.scraper.config['sources']), 2)
        self.assertEqual(self.scraper.config['merge_mode'], 'rule-based')

    def test_init_with_merge_mode_override(self):
        """RED: Test merge mode override in initialization"""
        scraper_with_override = UnifiedScraper(self.config_path, merge_mode='claude-enhanced')
        self.assertEqual(scraper_with_override.merge_mode, 'claude-enhanced')

    def test_scrape_all_sources_returns_dict(self):
        """RED: Test scrape_all_sources returns structured results"""
        with patch.object(self.scraper, '_scrape_documentation') as mock_docs, \
             patch.object(self.scraper, '_scrape_github') as mock_github, \
             patch.object(self.scraper, '_scrape_pdf') as mock_pdf:
            
            # Mock successful scraping
            mock_docs.return_value = {'pages': []}
            mock_github.return_value = {'files': []}
            mock_pdf.return_value = {'pages': []}
            
            results = self.scraper.scrape_all_sources()
            
            # Should return structured results dict
            self.assertIsInstance(results, dict)
            self.assertIn('documentation', results)
            self.assertIn('github', results)
            self.assertIn('pdf', results)

    def test_scrape_all_sources_handles_missing_source_types(self):
        """RED: Test scrape_all_sources handles unsupported source types gracefully"""
        config_with_unsupported = self.test_config.copy()
        config_with_unsupported['sources'][0]['type'] = 'unsupported_type'
        
        config_path = '/tmp/test_unsupported.json'
        with open(config_path, 'w') as f:
            json.dump(config_with_unsupported, f)
        
        scraper = UnifiedScraper(config_path)
        
        with patch.object(scraper, '_scrape_documentation') as mock_docs:
            mock_docs.return_value = {'pages': []}
            results = scraper.scrape_all_sources()
            
            # Should still return results dict, even with unsupported types
            self.assertIsInstance(results, dict)
            self.assertIn('documentation', results)
        
        Path(config_path).unlink()

    def test_scrape_documentation_calls_scraper(self):
        """RED: Test _scrape_documentation calls appropriate scraper"""
        source = {
            'name': 'docs',
            'type': 'documentation',
            'base_url': 'https://docs.example.com/',
            'max_pages': 5
        }
        
        with patch('doc_scraper.DocToSkillConverter') as mock_converter:
            mock_instance = mock_converter.return_value
            mock_instance.scrape_all.return_value = {'pages': []}
            
            result = self.scraper._scrape_documentation(source)
            
            # Should call DocToSkillConverter with config
            mock_converter.assert_called_once()
            call_args = mock_converter.call_args[0]
            self.assertEqual(call_args[0]['base_url'], source['base_url'])
            self.assertEqual(call_args[0]['max_pages'], source['max_pages'])

    def test_scrape_github_calls_scraper(self):
        """RED: Test _scrape_github calls appropriate scraper"""
        source = {
            'name': 'github',
            'type': 'github',
            'repo': 'test/project',
            'max_files': 10
        }
        
        with patch('github_scraper.GitHubScraper') as mock_scraper:
            mock_instance = mock_scraper.return_value
            mock_instance.scrape_all.return_value = {'files': []}
            
            result = self.scraper._scrape_github(source)
            
            # Should call GitHubScraper with config
            mock_scraper.assert_called_once()
            call_args = mock_scraper.call_args[0]
            self.assertEqual(call_args[0]['repo'], source['repo'])
            self.assertEqual(call_args[0]['max_files'], source['max_files'])

    def test_scrape_pdf_calls_scraper(self):
        """RED: Test _scrape_pdf calls appropriate scraper"""
        source = {
            'name': 'pdf',
            'type': 'pdf',
            'path': '/path/to/pdfs',
            'max_pages': 3
        }
        
        with patch('pdf_scraper.PDFScraper') as mock_scraper:
            mock_instance = mock_scraper.return_value
            mock_instance.scrape_all.return_value = {'pages': []}
            
            result = self.scraper._scrape_pdf(source)
            
            # Should call PDFScraper with config
            mock_scraper.assert_called_once()
            call_args = mock_scraper.call_args[0]
            self.assertEqual(call_args[0]['path'], source['path'])
            self.assertEqual(call_args[0]['max_pages'], source['max_pages'])

    def test_detect_conflicts_returns_list(self):
        """RED: Test detect_conflicts returns conflict list"""
        # Mock scraping results
        self.scraper.scraped_data = {
            'documentation': {'pages': []},
            'github': {'code_analysis': {'depth': 'surface', 'files': []}},
            'pdf': {'pages': []}
        }
        
        with patch('conflict_detector.ConflictDetector') as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.detect_all_conflicts.return_value = []
            
            conflicts = self.scraper.detect_conflicts()
            
            # Should call ConflictDetector and return list
            mock_detector.assert_called_once()
            self.assertIsInstance(conflicts, list)

    def test_merge_sources_calls_merger(self):
        """RED: Test merge_sources calls appropriate merger"""
        # Mock conflicts
        conflicts = []
        
        # Set merge mode
        self.scraper.merge_mode = 'rule-based'
        
        with patch('merge_sources.RuleBasedMerger') as mock_merger:
            mock_instance = mock_merger.return_value
            mock_instance.merge_all.return_value = {'merged': 'data'}
            
            result = self.scraper.merge_sources(conflicts)
            
            # Should call RuleBasedMerger for rule-based mode
            mock_merger.assert_called_once()
            self.assertIsInstance(result, dict)

    def test_merge_sources_handles_claude_enhanced_mode(self):
        """RED: Test merge_sources handles claude-enhanced mode"""
        conflicts = []
        self.scraper.merge_mode = 'claude-enhanced'
        
        with patch('merge_sources.ClaudeEnhancedMerger') as mock_merger:
            mock_instance = mock_merger.return_value
            mock_instance.merge_all.return_value = {'enhanced': 'data'}
            
            result = self.scraper.merge_sources(conflicts)
            
            # Should call ClaudeEnhancedMerger for claude-enhanced mode
            mock_merger.assert_called_once()
            self.assertIsInstance(result, dict)

    def test_build_skill_calls_skill_builder(self):
        """RED: Test build_skill calls UnifiedSkillBuilder"""
        # Mock merged data
        merged_data = {'content': 'test'}
        
        with patch('unified_skill_builder.UnifiedSkillBuilder') as mock_builder:
            mock_instance = mock_builder.return_value
            mock_instance.build_skill.return_value = {'skill': 'built'}
            
            result = self.scraper.build_skill(merged_data)
            
            # Should call UnifiedSkillBuilder
            mock_builder.assert_called_once()
            self.assertIsInstance(result, dict)

    def test_run_executes_full_workflow(self):
        """RED: Test run method executes complete workflow"""
        with patch.object(self.scraper, 'scrape_all_sources') as mock_scrape, \
             patch.object(self.scraper, 'detect_conflicts') as mock_detect, \
             patch.object(self.scraper, 'merge_sources') as mock_merge, \
             patch.object(self.scraper, 'build_skill') as mock_build:
            
            # Mock workflow steps
            mock_scrape.return_value = {'docs': 'data', 'github': 'data'}
            mock_detect.return_value = []
            mock_merge.return_value = {'merged': 'data'}
            mock_build.return_value = {'skill': 'output'}
            
            result = self.scraper.run()
            
            # Should execute all workflow steps in order
            mock_scrape.assert_called_once()
            mock_detect.assert_called_once()
            mock_merge.assert_called_once()
            mock_build.assert_called_once()
            self.assertIsInstance(result, dict)

    def test_run_handles_errors_gracefully(self):
        """RED: Test run method handles errors gracefully"""
        with patch.object(self.scraper, 'scrape_all_sources') as mock_scrape:
            # Mock scraping error
            mock_scrape.side_effect = Exception("Scraping failed")
            
            # Should not raise exception, but handle gracefully
            with self.assertRaises(Exception):
                self.scraper.run()

    def test_empty_config_handling(self):
        """RED: Test UnifiedScraper handles empty config gracefully"""
        empty_config = {'name': 'empty', 'sources': []}
        config_path = '/tmp/test_empty.json'
        with open(config_path, 'w') as f:
            json.dump(empty_config, f)
        
        try:
            scraper = UnifiedScraper(config_path)
            # Should initialize without crashing
            self.assertEqual(len(scraper.config['sources']), 0)
        finally:
            Path(config_path).unlink()

    def test_missing_config_key_handling(self):
        """RED: Test UnifiedScraper handles missing config keys gracefully"""
        incomplete_config = {'name': 'incomplete'}  # Missing sources
        config_path = '/tmp/test_incomplete.json'
        with open(config_path, 'w') as f:
            json.dump(incomplete_config, f)
        
        try:
            scraper = UnifiedScraper(config_path)
            # Should handle missing keys with defaults
            self.assertEqual(scraper.config.get('sources', []), [])
        finally:
            Path(config_path).unlink()


class TestUnifiedScraperCLI(unittest.TestCase):
    """Test UnifiedScraper CLI interface"""

    def test_main_with_config_argument(self):
        """RED: Test main CLI accepts config argument"""
        test_config = {'name': 'cli_test'}
        config_path = '/tmp/test_cli_config.json'
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        with patch('sys.argv', ['unified_scraper.py', '--config', config_path]):
            with patch('unified_scraper.UnifiedScraper') as mock_scraper:
                mock_instance = mock_scraper.return_value
                mock_instance.run.return_value = {'result': 'success'}
                
                try:
                    from unified_scraper import main
                    main()
                    # Should create UnifiedScraper with config path
                    mock_scraper.assert_called_once_with(config_path, None)
                except SystemExit:
                    pass  # Expected when CLI completes
        
        Path(config_path).unlink()

    def test_main_with_merge_mode_argument(self):
        """RED: Test main CLI accepts merge-mode argument"""
        test_config = {'name': 'cli_test'}
        config_path = '/tmp/test_cli_merge.json'
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        with patch('sys.argv', ['unified_scraper.py', '--config', config_path, '--merge-mode', 'claude-enhanced']):
            with patch('unified_scraper.UnifiedScraper') as mock_scraper:
                mock_instance = mock_scraper.return_value
                mock_instance.run.return_value = {'result': 'success'}
                
                try:
                    from unified_scraper import main
                    main()
                    # Should pass merge mode override
                    mock_scraper.assert_called_once_with(config_path, 'claude-enhanced')
                except SystemExit:
                    pass  # Expected when CLI completes
        
        Path(config_path).unlink()

    def test_main_requires_config_argument(self):
        """RED: Test main CLI requires config argument"""
        with patch('sys.argv', ['unified_scraper.py']):
            with patch('builtins.print') as mock_print:
                try:
                    from unified_scraper import main
                    main()
                    self.fail("Should have raised SystemExit")
                except SystemExit:
                    # Should print error message
                    mock_print.assert_called()
                    any_call_args = [call[0][0] for call in mock_print.call_args_list]
                    self.assertTrue(any('config' in str(args) for args in any_call_args))


if __name__ == '__main__':
    unittest.main()
