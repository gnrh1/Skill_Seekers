# Performance Profiling Guide

## Overview

The Skill_Seekers profiler provides comprehensive performance analysis for documentation scraping, helping you optimize configurations for speed and memory efficiency.

## Quick Start

### Profile a Configuration

```bash
# Profile with default settings (20 pages)
python3 cli/doc_scraper.py --config configs/react.json --profile

# Profile with more pages for better accuracy
python3 cli/doc_scraper.py --config configs/godot.json --profile --profile-pages 50

# Profile interactively
python3 cli/doc_scraper.py --interactive --profile
```

### Standalone Profiler

```bash
# Use standalone profiler module
python3 cli/scraper_profiler.py configs/react.json 20

# Profile multiple configs
for config in configs/*.json; do
    python3 cli/scraper_profiler.py "$config" 15
done
```

## What Gets Measured

### 1. **Async vs Sync Mode Comparison**
- Pages per second throughput
- Memory usage (peak and average)
- Actual speedup factor (validates "3x faster" claim)
- Optimal worker count (tests 2, 4, and 8 workers)

### 2. **llms.txt Detection Performance**
- Detects if site provides llms.txt
- Measures download speed vs HTML scraping
- Validates "10x faster" performance claim
- Automatic recommendation if available

### 3. **Memory Profiling**
- Peak memory usage during scraping
- Average memory consumption
- Memory savings between modes
- Identifies memory-intensive configs

### 4. **Config-Specific Analysis**
- Rate limiting effectiveness
- Page processing throughput
- Bottleneck identification
- Optimization recommendations

## Sample Output

```
======================================================================
📊 PERFORMANCE BENCHMARK REPORT
======================================================================

Config: react
Base URL: https://react.dev/
Total Pages: 500
llms.txt Available: ✅ Yes
Timestamp: 2024-01-20 15:30:00

----------------------------------------------------------------------
PERFORMANCE COMPARISON
----------------------------------------------------------------------

Mode                 Pages/sec    Memory       Speedup   
----------------------------------------------------------------------
Sync                 12.50        120.5        1.0x (baseline)
Async (4 workers)    38.20        80.3         3.06x
llms.txt             125.00       45.2         10.00x

----------------------------------------------------------------------
RECOMMENDATIONS
----------------------------------------------------------------------

🔥 HIGHLY RECOMMENDED: Use llms.txt (10.0x faster than HTML scraping)
   llms.txt detected at https://react.dev/ - no code changes needed!

⚡ Use async mode with 4 workers (3.1x faster than sync)
   Add to config: "async_mode": true, "workers": 4

💾 Async mode uses 40.2MB less memory (80.3MB vs 120.5MB)

======================================================================
```

## Understanding the Results

### Speedup Factor
- **1.0x** = Baseline (sync mode)
- **2-3x** = Good async performance
- **10x+** = Excellent (llms.txt available)

### Memory Usage
- **< 50MB** = Excellent (llms.txt mode)
- **50-100MB** = Good (async mode)
- **> 100MB** = Consider optimization (sync mode)

### Pages Per Second
- **< 5 pages/sec** = May need rate limit adjustment
- **5-20 pages/sec** = Normal sync performance
- **20-60 pages/sec** = Good async performance
- **100+ pages/sec** = Excellent (llms.txt)

## Optimization Workflow

### Step 1: Baseline Profile
```bash
# Profile with minimal pages first
python3 cli/doc_scraper.py --config configs/myconfig.json --profile --profile-pages 10
```

### Step 2: Analyze Recommendations
The profiler will suggest:
- Whether llms.txt is available (use it if yes!)
- Optimal async worker count
- Rate limit adjustments
- Memory optimization opportunities

### Step 3: Update Configuration
Based on recommendations:

```json
{
  "name": "myproject",
  "base_url": "https://docs.example.com",
  "async_mode": true,        // ← Add if recommended
  "workers": 4,               // ← Use recommended worker count
  "rate_limit": 0.3,          // ← Reduce if throughput is low
  "max_pages": 1000
}
```

### Step 4: Verify Improvement
```bash
# Profile again with updated config
python3 cli/doc_scraper.py --config configs/myconfig.json --profile --profile-pages 20
```

## Advanced Usage

### Programmatic Profiling

```python
from cli.scraper_profiler import ScraperProfiler, profile_config

# Profile a config file
report = profile_config('configs/react.json', max_pages=30)

# Access results programmatically
print(f"Sync speed: {report.sync_result.pages_per_second:.2f} pages/sec")
print(f"Async speed: {report.async_result.pages_per_second:.2f} pages/sec")
print(f"Speedup: {report.async_result.speedup_factor:.2f}x")

# Check recommendations
for rec in report.recommendations:
    print(f"- {rec}")
```

### Custom Profiling

```python
from cli.scraper_profiler import ScraperProfiler

config = {
    'name': 'test',
    'base_url': 'https://example.com',
    'max_pages': 500
}

profiler = ScraperProfiler(config, max_pages=25)

# Profile individual modes
sync_result = profiler.profile_sync_mode()
async_results = profiler.profile_async_mode(worker_counts=[2, 4, 8, 16])
llms_result = profiler.profile_llms_txt()

# Generate custom analysis
best_async = max(async_results, key=lambda r: r.pages_per_second)
print(f"Best async: {best_async.worker_count} workers at {best_async.pages_per_second:.1f} pages/sec")
```

## Output Files

Profiling generates two report files in `output/profiles/`:

### Text Report (`{config_name}_profile.txt`)
Human-readable report with:
- Performance comparison table
- Detailed recommendations
- Speedup calculations
- Memory usage analysis

### JSON Report (`{config_name}_profile.json`)
Machine-readable data with:
- Raw performance metrics
- All test results
- Recommendations list
- Timestamp and metadata

Example:
```json
{
  "config_name": "react",
  "base_url": "https://react.dev/",
  "total_pages": 500,
  "llms_txt_available": true,
  "sync_result": {
    "mode": "sync",
    "duration_seconds": 8.5,
    "pages_scraped": 20,
    "pages_per_second": 2.35,
    "memory_peak_mb": 120.5,
    "worker_count": 1
  },
  "async_result": { ... },
  "recommendations": [ ... ]
}
```

## Performance Tips

### For Large Documentation (1000+ pages)
1. **Always profile first** with 20-50 pages
2. **Enable async mode** with 4-8 workers
3. **Check for llms.txt** (huge speedup if available)
4. **Use checkpointing** for resumable scrapes

### For Rate-Limited Sites
1. **Start conservative** (rate_limit: 1.0)
2. **Profile to find optimal** rate limit
3. **Monitor for 429 errors** (too fast)
4. **Reduce workers** if getting blocked

### For Memory-Constrained Systems
1. **Use async mode** (66% less memory)
2. **Limit workers** to 2-4
3. **Check for llms.txt** (50% less memory)
4. **Split large docs** into smaller configs

## Troubleshooting

### "Pages scraped: 0" in Results
- **Cause**: Config selectors may be incorrect
- **Fix**: Test selectors manually first
- **Tool**: `python3 cli/estimate_pages.py configs/myconfig.json`

### Async Mode Slower Than Sync
- **Cause**: Too many workers for small docs
- **Fix**: Use 2-4 workers for < 200 pages
- **Note**: Async overhead isn't worth it for tiny scrapes

### High Memory Usage
- **Cause**: Large pages or inefficient selectors
- **Fix**: Check selector specificity
- **Alternative**: Use llms.txt if available

### llms.txt Not Detected
- **Cause**: Site doesn't provide llms.txt
- **Check**: Visit `{base_url}/llms.txt` manually
- **Alternatives**: `llms-full.txt`, `llms-small.txt`

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Profile Configs

on:
  pull_request:
    paths:
      - 'configs/**'

jobs:
  profile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
      
      - name: Profile changed configs
        run: |
          source venv/bin/activate
          for config in configs/*.json; do
            python3 cli/doc_scraper.py --config "$config" --profile --profile-pages 15
          done
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: profiling-reports
          path: output/profiles/
```

## API Reference

### ScraperProfiler Class

```python
class ScraperProfiler:
    def __init__(self, config: Dict[str, Any], max_pages: int = 20)
    def profile_sync_mode(self) -> ProfileResult
    def profile_async_mode(self, worker_counts: List[int] = [2, 4, 8]) -> List[ProfileResult]
    def profile_llms_txt(self) -> Optional[ProfileResult]
    def benchmark_full(self) -> ComparisonReport
    def generate_report(self, report: ComparisonReport, output_path: str = None) -> str
    def save_json_report(self, report: ComparisonReport, output_path: str) -> None
```

### ProfileResult Dataclass

```python
@dataclass
class ProfileResult:
    mode: str                      # 'sync', 'async-N', 'llms_txt'
    duration_seconds: float        # Total execution time
    pages_scraped: int            # Number of pages processed
    pages_per_second: float       # Throughput metric
    memory_peak_mb: float         # Peak memory usage
    memory_avg_mb: float          # Average memory usage
    worker_count: int             # Number of workers used
    rate_limit: float             # Rate limit applied
    speedup_factor: Optional[float]  # Compared to baseline
```

### ComparisonReport Dataclass

```python
@dataclass
class ComparisonReport:
    config_name: str
    base_url: str
    total_pages: int
    llms_txt_available: bool
    sync_result: Optional[ProfileResult]
    async_result: Optional[ProfileResult]
    llms_txt_result: Optional[ProfileResult]
    recommendations: List[str]
    timestamp: str
```

## Best Practices

1. **Profile before scaling** - Test with 10-20 pages first
2. **Document findings** - Save reports for reference
3. **Update configs** - Apply recommendations immediately
4. **Re-profile periodically** - Sites change, performance changes
5. **Share insights** - Add profile reports to PRs
6. **Automate profiling** - Integrate with CI/CD for config changes

## FAQ

**Q: How accurate are the profiling results?**
A: Results are measured with actual scraping operations. Use 20+ pages for better accuracy.

**Q: Does profiling consume API quota?**
A: No, profiling uses local scraping without AI enhancement.

**Q: Can I profile without scraping real sites?**
A: No, profiling measures actual HTTP requests to provide accurate metrics.

**Q: How long does profiling take?**
A: Typically 1-3 minutes for 20 pages across all modes.

**Q: Should I profile every config?**
A: Profile new configs and when making significant changes to existing ones.

**Q: Can I profile unified multi-source configs?**
A: Yes, profiling works with documentation, GitHub, and PDF sources.

## Related Tools

- **estimate_pages.py** - Quick page count estimation (no scraping)
- **config_validator.py** - Configuration syntax validation
- **doc_scraper.py** - Main scraping tool with profiling integration

## Support

For issues or questions about profiling:
1. Check existing profile reports in `output/profiles/`
2. Review TROUBLESHOOTING.md for common issues
3. Open an issue with profile output attached
