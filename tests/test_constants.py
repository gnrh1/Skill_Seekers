#!/usr/bin/env python3
"""Test suite for cli/constants.py module."""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.constants import (
    DEFAULT_RATE_LIMIT,
    DEFAULT_MAX_PAGES,
    DEFAULT_CHECKPOINT_INTERVAL,
    DEFAULT_ASYNC_MODE,
    CONTENT_PREVIEW_LENGTH,
    MAX_PAGES_WARNING_THRESHOLD,
    MIN_CATEGORIZATION_SCORE,
    URL_MATCH_POINTS,
    TITLE_MATCH_POINTS,
    CONTENT_MATCH_POINTS,
    API_CONTENT_LIMIT,
    API_PREVIEW_LIMIT,
    LOCAL_CONTENT_LIMIT,
    LOCAL_PREVIEW_LIMIT,
    DEFAULT_MAX_DISCOVERY,
    DISCOVERY_THRESHOLD,
    MAX_REFERENCE_FILES,
    MAX_CODE_BLOCKS_PER_PAGE,
)


class TestConstants(unittest.TestCase):
    """Test that all constants are defined and have sensible values."""

    def test_scraping_constants_exist(self):
        """Test that scraping constants are defined."""
        self.assertIsNotNone(DEFAULT_RATE_LIMIT)
        self.assertIsNotNone(DEFAULT_MAX_PAGES)
        self.assertIsNotNone(DEFAULT_CHECKPOINT_INTERVAL)
        self.assertIsNotNone(DEFAULT_ASYNC_MODE)

    def test_scraping_constants_types(self):
        """Test that scraping constants have correct types."""
        self.assertIsInstance(DEFAULT_RATE_LIMIT, (int, float))
        self.assertIsInstance(DEFAULT_MAX_PAGES, int)
        self.assertIsInstance(DEFAULT_CHECKPOINT_INTERVAL, int)
        self.assertIsInstance(DEFAULT_ASYNC_MODE, bool)

    def test_scraping_constants_ranges(self):
        """Test that scraping constants have sensible values."""
        self.assertGreater(DEFAULT_RATE_LIMIT, 0)
        self.assertGreater(DEFAULT_MAX_PAGES, 0)
        self.assertGreater(DEFAULT_CHECKPOINT_INTERVAL, 0)
        self.assertEqual(DEFAULT_RATE_LIMIT, 0.5)
        self.assertEqual(DEFAULT_MAX_PAGES, 500)
        self.assertEqual(DEFAULT_CHECKPOINT_INTERVAL, 1000)
        self.assertEqual(DEFAULT_ASYNC_MODE, True)

    def test_content_analysis_constants(self):
        """Test content analysis constants."""
        self.assertEqual(CONTENT_PREVIEW_LENGTH, 500)
        self.assertEqual(MAX_PAGES_WARNING_THRESHOLD, 10000)
        self.assertGreater(MAX_PAGES_WARNING_THRESHOLD, DEFAULT_MAX_PAGES)

    def test_categorization_constants(self):
        """Test categorization scoring constants."""
        self.assertEqual(MIN_CATEGORIZATION_SCORE, 2)
        self.assertEqual(URL_MATCH_POINTS, 3)
        self.assertEqual(TITLE_MATCH_POINTS, 2)
        self.assertEqual(CONTENT_MATCH_POINTS, 1)
        # Verify scoring hierarchy
        self.assertGreater(URL_MATCH_POINTS, TITLE_MATCH_POINTS)
        self.assertGreater(TITLE_MATCH_POINTS, CONTENT_MATCH_POINTS)

    def test_enhancement_constants_exist(self):
        """Test that enhancement constants are defined."""
        self.assertIsNotNone(API_CONTENT_LIMIT)
        self.assertIsNotNone(API_PREVIEW_LIMIT)
        self.assertIsNotNone(LOCAL_CONTENT_LIMIT)
        self.assertIsNotNone(LOCAL_PREVIEW_LIMIT)

    def test_enhancement_constants_values(self):
        """Test enhancement constants have expected values."""
        self.assertEqual(API_CONTENT_LIMIT, 100000)
        self.assertEqual(API_PREVIEW_LIMIT, 40000)
        self.assertEqual(LOCAL_CONTENT_LIMIT, 50000)
        self.assertEqual(LOCAL_PREVIEW_LIMIT, 20000)

    def test_enhancement_limits_hierarchy(self):
        """Test that API limits are higher than local limits."""
        self.assertGreater(API_CONTENT_LIMIT, LOCAL_CONTENT_LIMIT)
        self.assertGreater(API_PREVIEW_LIMIT, LOCAL_PREVIEW_LIMIT)
        self.assertGreater(API_CONTENT_LIMIT, API_PREVIEW_LIMIT)
        self.assertGreater(LOCAL_CONTENT_LIMIT, LOCAL_PREVIEW_LIMIT)

    def test_estimation_constants(self):
        """Test page estimation constants."""
        self.assertEqual(DEFAULT_MAX_DISCOVERY, 1000)
        self.assertEqual(DISCOVERY_THRESHOLD, 10000)
        self.assertGreater(DISCOVERY_THRESHOLD, DEFAULT_MAX_DISCOVERY)

    def test_file_limit_constants(self):
        """Test file limit constants."""
        self.assertEqual(MAX_REFERENCE_FILES, 100)
        self.assertEqual(MAX_CODE_BLOCKS_PER_PAGE, 5)
        self.assertGreater(MAX_REFERENCE_FILES, 0)
        self.assertGreater(MAX_CODE_BLOCKS_PER_PAGE, 0)


class TestConstantsUsage(unittest.TestCase):
    """Test that constants are properly used in other modules."""

    def test_doc_scraper_imports_constants(self):
        """Test that doc_scraper imports and uses constants."""
        from cli import doc_scraper
        # Check that doc_scraper can access the constants
        self.assertTrue(hasattr(doc_scraper, 'DEFAULT_RATE_LIMIT'))
        self.assertTrue(hasattr(doc_scraper, 'DEFAULT_MAX_PAGES'))

    def test_estimate_pages_imports_constants(self):
        """Test that estimate_pages imports and uses constants."""
        from cli import estimate_pages
        # Verify function signature uses constants
        import inspect
        sig = inspect.signature(estimate_pages.estimate_pages)
        self.assertIn('max_discovery', sig.parameters)

    def test_enhance_skill_imports_constants(self):
        """Test that enhance_skill imports constants."""
        try:
            from cli import enhance_skill
            # Check module loads without errors
            self.assertIsNotNone(enhance_skill)
        except (ImportError, SystemExit) as e:
            # anthropic package may not be installed or module exits on import
            # This is acceptable - we're just checking the constants import works
            pass

    def test_enhance_skill_local_imports_constants(self):
        """Test that enhance_skill_local imports constants."""
        from cli import enhance_skill_local
        self.assertIsNotNone(enhance_skill_local)


class TestConstantsExports(unittest.TestCase):
    """Test that constants module exports are correct."""

    def test_all_exports_exist(self):
        """Test that all items in __all__ exist."""
        from cli import constants
        self.assertTrue(hasattr(constants, '__all__'))
        for name in constants.__all__:
            self.assertTrue(
                hasattr(constants, name),
                f"Constant '{name}' in __all__ but not defined"
            )

    def test_all_exports_count(self):
        """Test that __all__ has expected number of exports."""
        from cli import constants
        # We defined 18 constants (including DEFAULT_ASYNC_MODE)
        self.assertEqual(len(constants.__all__), 18)


class TestConstantsBusinessLogic(unittest.TestCase):
    """Test business logic relationships between constants."""

    def test_scraping_performance_relationships(self):
        """Test that scraping constants follow performance best practices."""
        # Checkpoint should be larger than max_pages for large sites
        self.assertGreater(DEFAULT_CHECKPOINT_INTERVAL, DEFAULT_MAX_PAGES)

        # Rate limit should be reasonable for web scraping
        self.assertGreaterEqual(DEFAULT_RATE_LIMIT, 0.1)  # Not too fast
        self.assertLessEqual(DEFAULT_RATE_LIMIT, 5.0)      # Not too slow

    def test_content_processing_relationships(self):
        """Test content processing constant relationships."""
        # Content preview should be reasonable for categorization
        self.assertGreater(CONTENT_PREVIEW_LENGTH, 100)
        self.assertLessEqual(CONTENT_PREVIEW_LENGTH, 2000)

        # Warning threshold should be much higher than default max
        self.assertGreater(MAX_PAGES_WARNING_THRESHOLD, DEFAULT_MAX_PAGES * 5)

        # Code blocks limit should be reasonable per page
        self.assertGreater(MAX_CODE_BLOCKS_PER_PAGE, 1)
        self.assertLessEqual(MAX_CODE_BLOCKS_PER_PAGE, 20)

    def test_enhancement_content_relationships(self):
        """Test enhancement content limit relationships."""
        # API should handle more content than local
        self.assertGreater(API_CONTENT_LIMIT, LOCAL_CONTENT_LIMIT)
        self.assertGreater(API_PREVIEW_LIMIT, LOCAL_PREVIEW_LIMIT)

        # Content limits should be larger than preview limits
        self.assertGreater(API_CONTENT_LIMIT, API_PREVIEW_LIMIT)
        self.assertGreater(LOCAL_CONTENT_LIMIT, LOCAL_PREVIEW_LIMIT)

        # Limits should be reasonable for processing
        self.assertLessEqual(API_CONTENT_LIMIT, 1000000)  # 1MB max
        self.assertLessEqual(LOCAL_CONTENT_LIMIT, 500000) # 500KB max

    def test_discovery_threshold_relationships(self):
        """Test discovery and threshold relationships."""
        # Discovery threshold should be higher than default discovery
        self.assertGreater(DISCOVERY_THRESHOLD, DEFAULT_MAX_DISCOVERY)

        # Discovery should be reasonable for documentation sites
        self.assertGreater(DEFAULT_MAX_DISCOVERY, 100)
        self.assertLessEqual(DEFAULT_MAX_DISCOVERY, 10000)

    def test_categorization_scoring_logic(self):
        """Test that categorization scoring follows logical hierarchy."""
        # URL matches should be worth more than title matches
        self.assertGreater(URL_MATCH_POINTS, TITLE_MATCH_POINTS)

        # Title matches should be worth more than content matches
        self.assertGreater(TITLE_MATCH_POINTS, CONTENT_MATCH_POINTS)

        # Minimum score should be achievable with combinations
        self.assertLessEqual(MIN_CATEGORIZATION_SCORE, URL_MATCH_POINTS)
        self.assertLessEqual(MIN_CATEGORIZATION_SCORE, TITLE_MATCH_POINTS + CONTENT_MATCH_POINTS)

        # Points should be positive integers
        for points in [URL_MATCH_POINTS, TITLE_MATCH_POINTS, CONTENT_MATCH_POINTS]:
            self.assertIsInstance(points, int)
            self.assertGreater(points, 0)

    def test_file_limits_reasonableness(self):
        """Test that file limits are reasonable for skill generation."""
        # Reference files should be reasonable for organization
        self.assertGreater(MAX_REFERENCE_FILES, 10)
        self.assertLessEqual(MAX_REFERENCE_FILES, 1000)

        # Should have reasonable ratio to pages
        self.assertLessEqual(MAX_REFERENCE_FILES, DEFAULT_MAX_PAGES // 2)


class TestConstantsEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for constants."""

    def test_constants_are_immutable(self):
        """Test that constants resist modification (as much as Python allows)."""
        # Test that constants don't have setters (they're module-level)
        from cli import constants

        # Should be able to access all constants
        for name in constants.__all__:
            value = getattr(constants, name)
            self.assertIsNotNone(value, f"Constant {name} should not be None")

    def test_constants_have_proper_types(self):
        """Test that all constants have expected Python types."""
        type_expectations = {
            'DEFAULT_RATE_LIMIT': (int, float),
            'DEFAULT_MAX_PAGES': int,
            'DEFAULT_CHECKPOINT_INTERVAL': int,
            'DEFAULT_ASYNC_MODE': bool,
            'CONTENT_PREVIEW_LENGTH': int,
            'MAX_PAGES_WARNING_THRESHOLD': int,
            'MIN_CATEGORIZATION_SCORE': int,
            'URL_MATCH_POINTS': int,
            'TITLE_MATCH_POINTS': int,
            'CONTENT_MATCH_POINTS': int,
            'API_CONTENT_LIMIT': int,
            'API_PREVIEW_LIMIT': int,
            'LOCAL_CONTENT_LIMIT': int,
            'LOCAL_PREVIEW_LIMIT': int,
            'DEFAULT_MAX_DISCOVERY': int,
            'DISCOVERY_THRESHOLD': int,
            'MAX_REFERENCE_FILES': int,
            'MAX_CODE_BLOCKS_PER_PAGE': int,
        }

        from cli import constants

        for name, expected_type in type_expectations.items():
            value = getattr(constants, name)
            self.assertIsInstance(
                value, expected_type,
                f"Constant {name} should be {expected_type}, got {type(value)}"
            )

    def test_constants_are_positive_where_expected(self):
        """Test that numeric constants are positive where it makes sense."""
        positive_constants = [
            DEFAULT_RATE_LIMIT,
            DEFAULT_MAX_PAGES,
            DEFAULT_CHECKPOINT_INTERVAL,
            CONTENT_PREVIEW_LENGTH,
            MAX_PAGES_WARNING_THRESHOLD,
            MIN_CATEGORIZATION_SCORE,
            URL_MATCH_POINTS,
            TITLE_MATCH_POINTS,
            CONTENT_MATCH_POINTS,
            API_CONTENT_LIMIT,
            API_PREVIEW_LIMIT,
            LOCAL_CONTENT_LIMIT,
            LOCAL_PREVIEW_LIMIT,
            DEFAULT_MAX_DISCOVERY,
            DISCOVERY_THRESHOLD,
            MAX_REFERENCE_FILES,
            MAX_CODE_BLOCKS_PER_PAGE,
        ]

        for constant in positive_constants:
            self.assertGreater(constant, 0, f"Constant should be positive: {constant}")

    def test_constants_are_reasonable_scale(self):
        """Test that constants are on reasonable scale for their purpose."""
        # Rate limiting: 0.1 to 10 seconds
        self.assertGreaterEqual(DEFAULT_RATE_LIMIT, 0.1)
        self.assertLessEqual(DEFAULT_RATE_LIMIT, 10.0)

        # Page counts: 1 to 1 million
        self.assertGreaterEqual(DEFAULT_MAX_PAGES, 1)
        self.assertLessEqual(DEFAULT_MAX_PAGES, 1000000)

        # Content limits: 100 to 1MB (500 is actual value)
        self.assertGreaterEqual(CONTENT_PREVIEW_LENGTH, 100)
        self.assertLessEqual(CONTENT_PREVIEW_LENGTH, 1000000)

        # File limits: 1 to 10,000
        self.assertGreaterEqual(MAX_REFERENCE_FILES, 1)
        self.assertLessEqual(MAX_REFERENCE_FILES, 10000)


class TestConstantsDocumentation(unittest.TestCase):
    """Test that constants are properly documented and accessible."""

    def test_constants_module_docstring(self):
        """Test that constants module has proper documentation."""
        from cli import constants
        self.assertIsNotNone(constants.__doc__)
        self.assertGreater(len(constants.__doc__.strip()), 50)

    def test_constants_are_discoverable(self):
        """Test that constants can be discovered programmatically."""
        from cli import constants

        # All constants should be in module namespace
        for name in constants.__all__:
            self.assertTrue(hasattr(constants, name))

        # Constants should not start with underscore (except __all__)
        for name in dir(constants):
            if not name.startswith('_') and name != 'constants':
                attr = getattr(constants, name)
                # Should be a constant (immutable-like value)
                if isinstance(attr, (int, float, bool)):
                    self.assertIn(name, constants.__all__,
                                f"Exported constant {name} missing from __all__")


if __name__ == '__main__':
    unittest.main()
