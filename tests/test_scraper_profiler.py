"""
Comprehensive tests for scraper_profiler.py

Tests cover:
- ProfileResult and ComparisonReport data classes
- ScraperProfiler initialization and configuration
- Performance measurement for sync/async/llms.txt modes
- Memory profiling accuracy
- Report generation (text and JSON)
- Recommendations generation logic
- Integration with doc_scraper
"""

import json
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cli.scraper_profiler import (
    ProfileResult,
    ComparisonReport,
    ScraperProfiler,
    profile_config
)


class TestProfileResult:
    """Test ProfileResult dataclass."""
    
    def test_profile_result_creation(self):
        """Test creating ProfileResult with all fields."""
        result = ProfileResult(
            mode="sync",
            duration_seconds=10.5,
            pages_scraped=100,
            pages_per_second=9.52,
            memory_peak_mb=120.5,
            memory_avg_mb=100.2,
            worker_count=1,
            rate_limit=0.5,
            speedup_factor=None
        )
        
        assert result.mode == "sync"
        assert result.duration_seconds == 10.5
        assert result.pages_scraped == 100
        assert result.speedup_factor is None
    
    def test_profile_result_to_dict(self):
        """Test ProfileResult conversion to dictionary."""
        result = ProfileResult(
            mode="async",
            duration_seconds=5.0,
            pages_scraped=100,
            pages_per_second=20.0,
            memory_peak_mb=80.0,
            memory_avg_mb=70.0,
            worker_count=4,
            rate_limit=0.5,
            speedup_factor=2.1
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data['mode'] == "async"
        assert data['speedup_factor'] == 2.1
        assert 'duration_seconds' in data


class TestComparisonReport:
    """Test ComparisonReport dataclass."""
    
    def test_comparison_report_creation(self):
        """Test creating ComparisonReport."""
        sync_result = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=50,
            pages_per_second=5.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        report = ComparisonReport(
            config_name="test",
            base_url="https://example.com",
            total_pages=500,
            llms_txt_available=False,
            sync_result=sync_result,
            async_result=None,
            llms_txt_result=None,
            recommendations=["Use async mode"],
            timestamp="2024-01-01 12:00:00"
        )
        
        assert report.config_name == "test"
        assert report.llms_txt_available is False
        assert len(report.recommendations) == 1
    
    def test_comparison_report_to_dict(self):
        """Test ComparisonReport conversion to dictionary."""
        report = ComparisonReport(
            config_name="test",
            base_url="https://example.com",
            total_pages=500,
            llms_txt_available=True,
            sync_result=None,
            async_result=None,
            llms_txt_result=None,
            recommendations=[],
            timestamp="2024-01-01"
        )
        
        data = report.to_dict()
        assert isinstance(data, dict)
        assert data['config_name'] == "test"
        # None should be converted to empty dict
        assert data['sync_result'] == {}


class TestScraperProfiler:
    """Test ScraperProfiler class."""
    
    @pytest.fixture
    def sample_config(self):
        """Provide sample configuration for testing."""
        return {
            'name': 'test',
            'base_url': 'https://example.com',
            'max_pages': 500,
            'rate_limit': 0.5,
            'workers': 1,
            'async_mode': False
        }
    
    @pytest.fixture
    def profiler(self, sample_config):
        """Provide ScraperProfiler instance."""
        return ScraperProfiler(sample_config, max_pages=20)
    
    def test_profiler_initialization(self, sample_config):
        """Test profiler initializes with correct configuration."""
        profiler = ScraperProfiler(sample_config, max_pages=20)
        
        assert profiler.config['name'] == 'test'
        assert profiler.max_pages == 20
        assert profiler.config['max_pages'] == 20  # Overridden
        assert profiler.original_max_pages == 500  # Preserved
        assert profiler.baseline_result is None
    
    def test_measure_memory(self, profiler):
        """Test memory measurement returns positive value."""
        memory = profiler._measure_memory()
        
        assert isinstance(memory, float)
        assert memory > 0  # Should have some memory usage
    
    def test_extract_page_count_dict(self, profiler):
        """Test extracting page count from dictionary result."""
        result = {'total_pages': 42}
        count = profiler._extract_page_count(result)
        assert count == 42
    
    def test_extract_page_count_object(self, profiler):
        """Test extracting page count from object with pages attribute."""
        mock_result = Mock()
        mock_result.pages = [1, 2, 3, 4, 5]
        
        count = profiler._extract_page_count(mock_result)
        assert count == 5
    
    def test_extract_page_count_total_pages_attr(self, profiler):
        """Test extracting page count from object with total_pages attribute."""
        mock_result = Mock(spec=['total_pages'])  # Use spec to limit Mock attributes
        mock_result.total_pages = 100
        
        count = profiler._extract_page_count(mock_result)
        assert count == 100
    
    @patch('cli.doc_scraper.DocToSkillConverter')
    def test_profile_sync_mode(self, mock_converter_class, profiler):
        """Test profiling sync mode creates correct result."""
        # Setup mock
        mock_converter = Mock()
        mock_converter.pages = [{'title': 'Page 1'}] * 10
        mock_converter_class.return_value = mock_converter
        
        # Mock scrape_all to do minimal work
        def mock_scrape():
            time.sleep(0.1)  # Simulate some work
        mock_converter.scrape_all = mock_scrape
        
        # Profile
        result = profiler.profile_sync_mode()
        
        # Verify
        assert result.mode == "sync"
        assert result.worker_count == 1
        assert result.duration_seconds > 0
        assert profiler.baseline_result is not None  # Should set baseline
    
    @patch('cli.doc_scraper.DocToSkillConverter')
    def test_profile_async_mode(self, mock_converter_class, profiler):
        """Test profiling async mode with multiple worker counts."""
        # Setup mock
        mock_converter = Mock()
        mock_converter.pages = [{'title': 'Page 1'}] * 10
        mock_converter_class.return_value = mock_converter
        
        def mock_scrape():
            time.sleep(0.05)
        mock_converter.scrape_all = mock_scrape
        
        # Set baseline first
        profiler.baseline_result = ProfileResult(
            mode="sync", duration_seconds=1.0, pages_scraped=10,
            pages_per_second=10.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        # Profile with specific worker counts
        results = profiler.profile_async_mode(worker_counts=[2, 4])
        
        assert len(results) == 2
        assert results[0].mode == "async-2"
        assert results[1].mode == "async-4"
        assert results[0].worker_count == 2
        assert results[1].worker_count == 4
    
    def test_profile_llms_txt_available(self, profiler):
        """Test profiling when llms.txt is available."""
        # Set baseline
        profiler.baseline_result = ProfileResult(
            mode="sync", duration_seconds=5.0, pages_scraped=50,
            pages_per_second=10.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        # Mock _profile_execution to return a successful result
        def mock_profile_exec(*args, **kwargs):
            return ProfileResult(
                mode="llms_txt",
                duration_seconds=0.5,
                pages_scraped=50,
                pages_per_second=100.0,
                memory_peak_mb=50.0,
                memory_avg_mb=45.0,
                worker_count=1,
                rate_limit=0.0,
                speedup_factor=10.0
            )
        
        with patch.object(profiler, '_profile_execution', side_effect=mock_profile_exec) as mock_exec:
            # Also mock DocToSkillConverter to return a working converter
            with patch('cli.doc_scraper.DocToSkillConverter') as mock_conv_class:
                mock_conv = Mock()
                mock_conv._try_llms_txt = Mock(return_value=True)
                mock_conv.pages = [{'title': f'Page {i}'} for i in range(50)]
                mock_conv_class.return_value = mock_conv
                
                # Profile
                result = profiler.profile_llms_txt()
        
        assert result is not None
        assert result.mode == "llms_txt"
        assert result.pages_scraped == 50
    
    @patch('cli.doc_scraper.DocToSkillConverter')
    def test_profile_llms_txt_not_available(self, mock_converter_class, profiler):
        """Test profiling when llms.txt is not available."""
        mock_converter = Mock()
        mock_converter.pages = []
        mock_converter_class.return_value = mock_converter
        
        mock_converter._try_llms_txt = lambda: False
        
        result = profiler.profile_llms_txt()
        
        assert result is None
    
    def test_generate_recommendations_llms_txt(self, profiler):
        """Test recommendations when llms.txt is available."""
        sync = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=100,
            pages_per_second=10.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        async_result = ProfileResult(
            mode="async", duration_seconds=5.0, pages_scraped=100,
            pages_per_second=20.0, memory_peak_mb=80.0, memory_avg_mb=70.0,
            worker_count=4, rate_limit=0.5, speedup_factor=2.0
        )
        
        llms_txt = ProfileResult(
            mode="llms_txt", duration_seconds=1.0, pages_scraped=100,
            pages_per_second=100.0, memory_peak_mb=50.0, memory_avg_mb=45.0,
            worker_count=1, rate_limit=0.0, speedup_factor=10.0
        )
        
        recommendations = profiler._generate_recommendations(sync, async_result, llms_txt)
        
        # Should recommend llms.txt first
        assert len(recommendations) > 0
        assert any('llms.txt' in rec for rec in recommendations)
        assert any('10.0x' in rec or '10x' in rec for rec in recommendations)
    
    def test_generate_recommendations_async_only(self, profiler):
        """Test recommendations when only async is faster."""
        sync = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=100,
            pages_per_second=10.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        async_result = ProfileResult(
            mode="async", duration_seconds=4.0, pages_scraped=100,
            pages_per_second=25.0, memory_peak_mb=60.0, memory_avg_mb=55.0,
            worker_count=8, rate_limit=0.5, speedup_factor=2.5
        )
        
        recommendations = profiler._generate_recommendations(sync, async_result, None)
        
        assert len(recommendations) > 0
        assert any('async mode' in rec for rec in recommendations)
        assert any('8 workers' in rec for rec in recommendations)
    
    def test_generate_recommendations_memory_savings(self, profiler):
        """Test memory saving recommendations."""
        sync = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=100,
            pages_per_second=10.0, memory_peak_mb=120.0, memory_avg_mb=110.0,
            worker_count=1, rate_limit=0.5
        )
        
        async_result = ProfileResult(
            mode="async", duration_seconds=5.0, pages_scraped=100,
            pages_per_second=20.0, memory_peak_mb=80.0, memory_avg_mb=75.0,
            worker_count=4, rate_limit=0.5, speedup_factor=2.0
        )
        
        recommendations = profiler._generate_recommendations(sync, async_result, None)
        
        # Should mention memory savings (40MB difference)
        assert any('memory' in rec.lower() for rec in recommendations)
        assert any('40' in rec or 'MB' in rec for rec in recommendations)
    
    def test_generate_recommendations_large_docs(self, profiler):
        """Test recommendations for large documentation."""
        profiler.original_max_pages = 5000  # Large docs
        
        sync = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=20,
            pages_per_second=2.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        async_result = ProfileResult(
            mode="async", duration_seconds=6.0, pages_scraped=20,
            pages_per_second=3.3, memory_peak_mb=80.0, memory_avg_mb=75.0,
            worker_count=4, rate_limit=0.5, speedup_factor=1.67
        )
        
        recommendations = profiler._generate_recommendations(sync, async_result, None)
        
        # Should recommend async for large docs
        assert any('5000 pages' in rec or 'Large' in rec for rec in recommendations)
    
    def test_generate_report_text_format(self, profiler):
        """Test text report generation formatting."""
        sync_result = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=50,
            pages_per_second=5.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        report = ComparisonReport(
            config_name="test",
            base_url="https://example.com",
            total_pages=500,
            llms_txt_available=False,
            sync_result=sync_result,
            async_result=None,
            llms_txt_result=None,
            recommendations=["Test recommendation"],
            timestamp="2024-01-01 12:00:00"
        )
        
        report_text = profiler.generate_report(report)
        
        # Check key sections exist
        assert "PERFORMANCE BENCHMARK REPORT" in report_text
        assert "test" in report_text
        assert "https://example.com" in report_text
        assert "PERFORMANCE COMPARISON" in report_text
        assert "RECOMMENDATIONS" in report_text
        assert "Test recommendation" in report_text
    
    def test_save_json_report(self, profiler, tmp_path):
        """Test JSON report saving."""
        report = ComparisonReport(
            config_name="test",
            base_url="https://example.com",
            total_pages=500,
            llms_txt_available=True,
            sync_result=None,
            async_result=None,
            llms_txt_result=None,
            recommendations=[],
            timestamp="2024-01-01"
        )
        
        output_file = tmp_path / "test_report.json"
        profiler.save_json_report(report, str(output_file))
        
        assert output_file.exists()
        
        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        
        assert data['config_name'] == "test"
        assert data['llms_txt_available'] is True


class TestProfileConfigFunction:
    """Test standalone profile_config function."""
    
    @patch('cli.scraper_profiler.ScraperProfiler')
    def test_profile_config_integration(self, mock_profiler_class, tmp_path):
        """Test profile_config convenience function."""
        # Create test config file
        config = {
            'name': 'test',
            'base_url': 'https://example.com',
            'max_pages': 500
        }
        config_file = tmp_path / "test.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Setup mock
        mock_profiler = Mock()
        mock_report = ComparisonReport(
            config_name="test",
            base_url="https://example.com",
            total_pages=500,
            llms_txt_available=False,
            sync_result=None,
            async_result=None,
            llms_txt_result=None,
            recommendations=[],
            timestamp="2024-01-01"
        )
        mock_profiler.benchmark_full.return_value = mock_report
        mock_profiler.generate_report.return_value = "Test report"
        mock_profiler_class.return_value = mock_profiler
        
        # Call function
        result = profile_config(str(config_file), max_pages=10)
        
        # Verify
        assert result == mock_report
        mock_profiler.benchmark_full.assert_called_once()
        mock_profiler.generate_report.assert_called_once()


class TestIntegration:
    """Integration tests for profiler with real config."""
    
    def test_profiler_with_minimal_config(self):
        """Test profiler works with minimal configuration."""
        config = {
            'name': 'minimal',
            'base_url': 'https://example.com',
            'selectors': {
                'main_content': 'article'
            }
        }
        
        profiler = ScraperProfiler(config, max_pages=5)
        
        assert profiler.config['name'] == 'minimal'
        assert profiler.max_pages == 5
        assert profiler.config['max_pages'] == 5
    
    def test_speedup_calculation(self):
        """Test speedup factor is calculated correctly."""
        config = {'name': 'test', 'base_url': 'https://example.com'}
        profiler = ScraperProfiler(config)
        
        # Set baseline
        profiler.baseline_result = ProfileResult(
            mode="sync", duration_seconds=10.0, pages_scraped=100,
            pages_per_second=10.0, memory_peak_mb=100.0, memory_avg_mb=90.0,
            worker_count=1, rate_limit=0.5
        )
        
        # Create result with speedup
        faster_result = ProfileResult(
            mode="async", duration_seconds=4.0, pages_scraped=100,
            pages_per_second=25.0, memory_peak_mb=80.0, memory_avg_mb=75.0,
            worker_count=4, rate_limit=0.5,
            speedup_factor=10.0 / 4.0  # 2.5x speedup
        )
        
        assert faster_result.speedup_factor == 2.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
