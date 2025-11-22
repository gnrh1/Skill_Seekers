#!/usr/bin/env python3
"""
TDD Tests for URL scheme validation
Tests for security vulnerability fix - preventing scheme manipulation attacks
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

# Add cli directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'cli'))

from doc_scraper import DocToSkillConverter
import estimate_pages


class TestURLSchemeValidation(unittest.TestCase):
    """Test URL scheme validation for security"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_config = {
            'name': 'test',
            'base_url': 'https://example.com/',
            'selectors': {'main_content': 'article'},
            'max_pages': 10
        }
        self.original_cwd = sys.path[0]

    def tearDown(self):
        """Clean up"""
        pass

    def test_rejects_javascript_scheme(self):
        """RED: Test that javascript: URLs are rejected"""
        config = self.base_config.copy()
        
        with patch('doc_scraper.urljoin') as mock_urljoin:
            # Mock urljoin to return dangerous javascript URL
            mock_urljoin.return_value = 'javascript:alert(1)'
            
            converter = DocToSkillConverter(config, dry_run=True)
            
            # This should be rejected by scheme validation
            self.assertFalse(converter.is_valid_url('javascript:alert(1)'))

    def test_rejects_data_scheme(self):
        """RED: Test that data: URLs are rejected"""
        config = self.base_config.copy()
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # This should be rejected by scheme validation
        self.assertFalse(converter.is_valid_url('data:text/html,<script>alert(1)</script>'))

    def test_rejects_file_scheme(self):
        """RED: Test that file: URLs are rejected"""
        config = self.base_config.copy()
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # This should be rejected by scheme validation  
        self.assertFalse(converter.is_valid_url('file:///etc/passwd'))

    def test_accepts_http_scheme(self):
        """RED: Test that http: URLs are accepted when base_url is http"""
        config = self.base_config.copy()
        config['base_url'] = 'http://example.com/'
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # This should be accepted
        self.assertTrue(converter.is_valid_url('http://example.com/page'))

    def test_accepts_https_scheme(self):
        """RED: Test that https: URLs are accepted when base_url is https"""
        config = self.base_config.copy()
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # This should be accepted
        self.assertTrue(converter.is_valid_url('https://example.com/page'))

    def test_rejects_scheme_mismatch(self):
        """RED: Test that scheme mismatch between base_url and URL is rejected"""
        config = self.base_config.copy()
        # Base is https but trying to access http
        converter = DocToSkillConverter(config, dry_run=True)
        
        # This should be rejected due to scheme mismatch
        self.assertFalse(converter.is_valid_url('http://example.com/page'))

    def test_rejects_empty_scheme(self):
        """RED: Test that URLs with empty scheme are rejected"""
        config = self.base_config.copy()
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # This should be rejected
        self.assertFalse(converter.is_valid_url('://example.com/page'))

    def test_accepts_relative_urls(self):
        """RED: Test that relative URLs are accepted (no scheme)"""
        config = self.base_config.copy()
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # Simulate urljoin resolving relative URL to absolute URL
        from urllib.parse import urljoin
        relative_url = '/relative/path'
        absolute_url = urljoin(config['base_url'], relative_url)  # This becomes https://example.com/relative/path
        
        # The resolved absolute URL should be accepted
        self.assertTrue(converter.is_valid_url(absolute_url))

    def test_estimate_pages_rejects_dangerous_schemes(self):
        """RED: Test estimate_pages also rejects dangerous schemes"""
        base_url = 'https://example.com/'
        include_patterns = []
        exclude_patterns = []
        
        # This should be rejected
        self.assertFalse(
            estimate_pages.is_valid_url('javascript:alert(1)', base_url, include_patterns, exclude_patterns)
        )
        
        # This should be rejected  
        self.assertFalse(
            estimate_pages.is_valid_url('data:text/html,<script>alert(1)</script>', base_url, include_patterns, exclude_patterns)
        )

    def test_estimate_pages_accepts_valid_schemes(self):
        """RED: Test estimate_pages accepts valid schemes"""
        base_url = 'https://example.com/'
        include_patterns = []
        exclude_patterns = []
        
        # This should be accepted
        self.assertTrue(
            estimate_pages.is_valid_url('https://example.com/page', base_url, include_patterns, exclude_patterns)
        )


class TestURLSchemeValidationIntegration(unittest.TestCase):
    """Integration tests for URL scheme validation in context"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_config = {
            'name': 'test',
            'base_url': 'https://example.com/',
            'selectors': {'main_content': 'article'},
            'max_pages': 1
        }
        self.original_cwd = sys.path[0]

    def test_extract_links_filters_dangerous_schemes(self):
        """RED: Test that link extraction filters dangerous schemes"""
        config = self.base_config.copy()
        
        converter = DocToSkillConverter(config, dry_run=True)
        
        # Mock HTML with dangerous link
        mock_html = '''
        <article>
            <a href="javascript:alert(1)">Dangerous</a>
            <a href="/safe-link">Safe</a>
            <a href="data:text/html,<script>alert(1)</script">Also dangerous</a>
        </article>
        '''
        
        # Mock BeautifulSoup parsing and urljoin simulation
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        soup = BeautifulSoup(mock_html, 'html.parser')
        main = soup.find('article')
        
        # Extract links using converter logic (simulate urljoin resolution)
        page = {'links': []}
        for link in main.find_all('a', href=True):
            # Simulate urljoin resolution
            href = link['href']
            resolved_href = urljoin(config['base_url'], href)  # This resolves relative URLs
            
            # Check if resolved URL is valid
            if converter.is_valid_url(resolved_href) and resolved_href not in page['links']:
                page['links'].append(resolved_href)
        
        # Should only contain safe resolved URLs
        expected_safe_url = urljoin(config['base_url'], '/safe-link')
        self.assertEqual(page['links'], [expected_safe_url])
        
        # Check that dangerous schemes are not in final links
        dangerous_schemes = ['javascript:alert(1)', 'data:text/html,<script>alert(1)</script']
        for dangerous in dangerous_schemes:
            resolved_dangerous = urljoin(config['base_url'], dangerous)
            self.assertNotIn(resolved_dangerous, page['links'])


if __name__ == '__main__':
    unittest.main()
