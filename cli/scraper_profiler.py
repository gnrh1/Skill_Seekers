#!/usr/bin/env python3
"""
Performance profiling and benchmarking for doc_scraper.

This module provides comprehensive performance analysis for the Skill_Seekers
documentation scraper, including:
- Async vs sync mode benchmarking
- llms.txt vs HTML scraping comparison
- Memory usage profiling
- Config-specific performance analysis
- Worker count optimization recommendations

Usage:
    from cli.scraper_profiler import ScraperProfiler
    
    profiler = ScraperProfiler(config)
    results = profiler.profile_scraping()
    profiler.generate_report(results)
"""

import time
import tracemalloc
import asyncio
import psutil
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ProfileResult:
    """Container for profiling results."""
    mode: str  # 'sync', 'async', 'llms_txt'
    duration_seconds: float
    pages_scraped: int
    pages_per_second: float
    memory_peak_mb: float
    memory_avg_mb: float
    worker_count: int
    rate_limit: float
    speedup_factor: Optional[float] = None  # compared to baseline
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ComparisonReport:
    """Container for comparison analysis."""
    config_name: str
    base_url: str
    total_pages: int
    llms_txt_available: bool
    sync_result: Optional[ProfileResult]
    async_result: Optional[ProfileResult]
    llms_txt_result: Optional[ProfileResult]
    recommendations: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert None to dict for JSON
        for key in ['sync_result', 'async_result', 'llms_txt_result']:
            if data[key] is None:
                data[key] = {}
        return data


class ScraperProfiler:
    """Performance profiler for documentation scraper."""
    
    def __init__(self, config: Dict[str, Any], max_pages: int = 20):
        """Initialize profiler with config.
        
        Args:
            config: Scraper configuration dictionary
            max_pages: Maximum pages to scrape during profiling (default: 20)
        """
        self.config = config
        self.max_pages = max_pages
        self.original_max_pages = config.get('max_pages')
        
        # Override max_pages for profiling
        self.config['max_pages'] = max_pages
        
        # Process for memory monitoring
        self.process = psutil.Process()
        
        # Baseline for comparison
        self.baseline_result: Optional[ProfileResult] = None
        
    def _measure_memory(self) -> float:
        """Get current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
        """
        return self.process.memory_info().rss / 1024 / 1024
    
    def _profile_execution(
        self, 
        func, 
        *args, 
        mode: str = "sync",
        worker_count: int = 1,
        **kwargs
    ) -> ProfileResult:
        """Profile a scraping function execution.
        
        Args:
            func: Function to profile
            *args: Positional arguments for function
            mode: Execution mode ('sync', 'async', 'llms_txt')
            worker_count: Number of workers used
            **kwargs: Keyword arguments for function
            
        Returns:
            ProfileResult with timing and memory metrics
        """
        # Start memory tracking
        tracemalloc.start()
        memory_samples = []
        start_memory = self._measure_memory()
        
        # Execute function
        start_time = time.perf_counter()
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error during profiling: {e}")
            tracemalloc.stop()
            raise
        
        end_time = time.perf_counter()
        
        # Memory metrics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_memory = self._measure_memory()
        
        duration = end_time - start_time
        memory_peak = peak / 1024 / 1024  # Convert to MB
        memory_avg = (start_memory + end_memory) / 2
        
        # Extract pages scraped from result
        pages_scraped = self._extract_page_count(result)
        pages_per_second = pages_scraped / duration if duration > 0 else 0
        
        # Calculate speedup
        speedup = None
        if self.baseline_result and self.baseline_result.duration_seconds > 0:
            speedup = self.baseline_result.duration_seconds / duration
        
        return ProfileResult(
            mode=mode,
            duration_seconds=duration,
            pages_scraped=pages_scraped,
            pages_per_second=pages_per_second,
            memory_peak_mb=memory_peak,
            memory_avg_mb=memory_avg,
            worker_count=worker_count,
            rate_limit=self.config.get('rate_limit', 0.5),
            speedup_factor=speedup
        )
    
    def _extract_page_count(self, result: Any) -> int:
        """Extract page count from scraper result.
        
        Args:
            result: Result from scraper execution
            
        Returns:
            Number of pages scraped
        """
        # Handle different return types
        if isinstance(result, dict):
            return result.get('total_pages', 0)
        elif hasattr(result, 'total_pages') and isinstance(getattr(result, 'total_pages', None), int):
            return result.total_pages
        elif hasattr(result, 'pages'):
            try:
                return len(result.pages)
            except TypeError:
                # pages attribute exists but can't get len (e.g., Mock object)
                return 0
        return 0
    
    def profile_sync_mode(self) -> ProfileResult:
        """Profile synchronous scraping mode.
        
        Returns:
            ProfileResult for sync mode
        """
        logger.info("📊 Profiling sync mode...")
        
        from cli.doc_scraper import DocToSkillConverter
        
        # Create config for sync mode
        sync_config = self.config.copy()
        sync_config['async_mode'] = False
        sync_config['workers'] = 1
        
        # Create scraper and profile
        scraper = DocToSkillConverter(sync_config, dry_run=False)
        
        result = self._profile_execution(
            scraper.scrape_all,
            mode="sync",
            worker_count=1
        )
        
        # Set as baseline if first profile
        if self.baseline_result is None:
            self.baseline_result = result
        
        logger.info(f"✅ Sync mode: {result.pages_per_second:.2f} pages/sec, "
                   f"{result.memory_peak_mb:.1f}MB peak memory")
        
        return result
    
    def profile_async_mode(self, worker_counts: List[int] = None) -> List[ProfileResult]:
        """Profile asynchronous scraping mode with different worker counts.
        
        Args:
            worker_counts: List of worker counts to test (default: [2, 4, 8])
            
        Returns:
            List of ProfileResults for each worker count
        """
        if worker_counts is None:
            worker_counts = [2, 4, 8]
        
        results = []
        
        for workers in worker_counts:
            logger.info(f"📊 Profiling async mode with {workers} workers...")
            
            from cli.doc_scraper import DocToSkillConverter
            
            # Create config for async mode
            async_config = self.config.copy()
            async_config['async_mode'] = True
            async_config['workers'] = workers
            
            # Create scraper and profile
            scraper = DocToSkillConverter(async_config, dry_run=False)
            
            result = self._profile_execution(
                scraper.scrape_all,
                mode=f"async-{workers}",
                worker_count=workers
            )
            
            logger.info(f"✅ Async mode ({workers} workers): {result.pages_per_second:.2f} pages/sec, "
                       f"{result.memory_peak_mb:.1f}MB peak memory, "
                       f"{result.speedup_factor:.2f}x speedup" if result.speedup_factor else "")
            
            results.append(result)
        
        return results
    
    def profile_llms_txt(self) -> Optional[ProfileResult]:
        """Profile llms.txt detection and download if available.
        
        Returns:
            ProfileResult for llms.txt mode, or None if not available
        """
        logger.info("📊 Profiling llms.txt detection...")
        
        from cli.doc_scraper import DocToSkillConverter
        
        # Check if llms.txt is available
        scraper = DocToSkillConverter(self.config.copy(), dry_run=False)
        
        result = self._profile_execution(
            scraper._try_llms_txt,
            mode="llms_txt",
            worker_count=1
        )
        
        if result.pages_scraped > 0:
            logger.info(f"✅ llms.txt mode: {result.pages_per_second:.2f} pages/sec, "
                       f"{result.memory_peak_mb:.1f}MB peak memory, "
                       f"{result.speedup_factor:.2f}x speedup" if result.speedup_factor else "")
            return result
        else:
            logger.info("ℹ️  llms.txt not available for this config")
            return None
    
    def benchmark_full(self) -> ComparisonReport:
        """Run full benchmark comparing all modes.
        
        Returns:
            ComparisonReport with all results and recommendations
        """
        logger.info("\n" + "=" * 60)
        logger.info("🚀 STARTING FULL PERFORMANCE BENCHMARK")
        logger.info("=" * 60)
        logger.info(f"Config: {self.config['name']}")
        logger.info(f"Base URL: {self.config['base_url']}")
        logger.info(f"Max pages (profiling): {self.max_pages}")
        logger.info("")
        
        # Profile sync mode (baseline)
        sync_result = self.profile_sync_mode()
        
        # Profile async modes
        async_results = self.profile_async_mode([2, 4, 8])
        best_async = max(async_results, key=lambda r: r.pages_per_second)
        
        # Profile llms.txt if available
        llms_txt_result = self.profile_llms_txt()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sync_result, best_async, llms_txt_result
        )
        
        # Create comparison report
        report = ComparisonReport(
            config_name=self.config['name'],
            base_url=self.config['base_url'],
            total_pages=self.original_max_pages or 500,
            llms_txt_available=llms_txt_result is not None,
            sync_result=sync_result,
            async_result=best_async,
            llms_txt_result=llms_txt_result,
            recommendations=recommendations,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return report
    
    def _generate_recommendations(
        self,
        sync: ProfileResult,
        async_best: ProfileResult,
        llms_txt: Optional[ProfileResult]
    ) -> List[str]:
        """Generate optimization recommendations based on results.
        
        Args:
            sync: Sync mode result
            async_best: Best async mode result
            llms_txt: llms.txt result (if available)
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # llms.txt recommendation
        if llms_txt and llms_txt.speedup_factor:
            speedup = llms_txt.speedup_factor
            recommendations.append(
                f"🔥 HIGHLY RECOMMENDED: Use llms.txt ({speedup:.1f}x faster than HTML scraping)"
            )
            recommendations.append(
                f"   llms.txt detected at {self.config['base_url']} - no code changes needed!"
            )
        
        # Async mode recommendation
        if async_best.speedup_factor and async_best.speedup_factor > 1.5:
            recommendations.append(
                f"⚡ Use async mode with {async_best.worker_count} workers "
                f"({async_best.speedup_factor:.1f}x faster than sync)"
            )
            recommendations.append(
                f"   Add to config: \"async_mode\": true, \"workers\": {async_best.worker_count}"
            )
        
        # Memory optimization
        memory_diff = sync.memory_peak_mb - async_best.memory_peak_mb
        if memory_diff > 20:
            recommendations.append(
                f"💾 Async mode uses {memory_diff:.1f}MB less memory "
                f"({async_best.memory_peak_mb:.1f}MB vs {sync.memory_peak_mb:.1f}MB)"
            )
        
        # Rate limit recommendation
        if sync.pages_per_second < 5:
            recommendations.append(
                f"⏱️  Low throughput detected ({sync.pages_per_second:.1f} pages/sec)"
            )
            recommendations.append(
                f"   Consider reducing rate_limit from {sync.rate_limit}s to 0.3s"
            )
        
        # Large docs recommendation
        if self.original_max_pages and self.original_max_pages > 200:
            recommendations.append(
                f"📚 Large documentation ({self.original_max_pages} pages) - "
                f"async mode strongly recommended"
            )
        
        return recommendations
    
    def generate_report(self, report: ComparisonReport, output_path: Optional[str] = None) -> str:
        """Generate human-readable performance report.
        
        Args:
            report: ComparisonReport to format
            output_path: Optional file path to save report
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("📊 PERFORMANCE BENCHMARK REPORT")
        lines.append("=" * 70)
        lines.append(f"\nConfig: {report.config_name}")
        lines.append(f"Base URL: {report.base_url}")
        lines.append(f"Total Pages: {report.total_pages}")
        lines.append(f"llms.txt Available: {'✅ Yes' if report.llms_txt_available else '❌ No'}")
        lines.append(f"Timestamp: {report.timestamp}")
        
        lines.append("\n" + "-" * 70)
        lines.append("PERFORMANCE COMPARISON")
        lines.append("-" * 70)
        
        # Results table
        lines.append(f"\n{'Mode':<20} {'Pages/sec':<12} {'Memory':<12} {'Speedup':<10}")
        lines.append("-" * 70)
        
        if report.sync_result:
            lines.append(
                f"{'Sync':<20} "
                f"{report.sync_result.pages_per_second:<12.2f} "
                f"{report.sync_result.memory_peak_mb:<12.1f} "
                f"{'1.0x (baseline)':<10}"
            )
        
        if report.async_result:
            speedup_str = f"{report.async_result.speedup_factor:.2f}x" if report.async_result.speedup_factor else "N/A"
            lines.append(
                f"{'Async (' + str(report.async_result.worker_count) + ' workers)':<20} "
                f"{report.async_result.pages_per_second:<12.2f} "
                f"{report.async_result.memory_peak_mb:<12.1f} "
                f"{speedup_str:<10}"
            )
        
        if report.llms_txt_result:
            speedup_str = f"{report.llms_txt_result.speedup_factor:.2f}x" if report.llms_txt_result.speedup_factor else "N/A"
            lines.append(
                f"{'llms.txt':<20} "
                f"{report.llms_txt_result.pages_per_second:<12.2f} "
                f"{report.llms_txt_result.memory_peak_mb:<12.1f} "
                f"{speedup_str:<10}"
            )
        
        # Recommendations
        if report.recommendations:
            lines.append("\n" + "-" * 70)
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 70)
            for rec in report.recommendations:
                lines.append(f"\n{rec}")
        
        lines.append("\n" + "=" * 70)
        
        report_text = "\n".join(lines)
        
        # Save to file if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report_text)
            logger.info(f"\n📝 Report saved to: {output_path}")
        
        return report_text
    
    def save_json_report(self, report: ComparisonReport, output_path: str) -> None:
        """Save report as JSON for programmatic access.
        
        Args:
            report: ComparisonReport to save
            output_path: File path for JSON output
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        logger.info(f"📊 JSON report saved to: {output_path}")


def profile_config(config_path: str, max_pages: int = 20, output_dir: str = "output/profiles") -> ComparisonReport:
    """Convenience function to profile a configuration file.
    
    Args:
        config_path: Path to configuration JSON file
        max_pages: Maximum pages to scrape during profiling
        output_dir: Directory for output reports
        
    Returns:
        ComparisonReport with benchmark results
    """
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    # Create profiler and run benchmark
    profiler = ScraperProfiler(config, max_pages=max_pages)
    report = profiler.benchmark_full()
    
    # Generate reports
    config_name = config['name']
    text_report = profiler.generate_report(
        report, 
        output_path=f"{output_dir}/{config_name}_profile.txt"
    )
    profiler.save_json_report(
        report,
        output_path=f"{output_dir}/{config_name}_profile.json"
    )
    
    # Print to console
    print(text_report)
    
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 cli/scraper_profiler.py <config_path> [max_pages]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    # Profile configuration
    profile_config(config_path, max_pages=max_pages)
