# Skill_Seekers Tech Stack

## Core Dependencies (Required)

**Python Runtime:**
- Python 3.10+ (REQUIRED minimum version)
- Rationale: Type hints, match/case, async improvements

**HTTP & Web Scraping:**
- requests 2.32.5 - Synchronous HTTP client
- beautifulsoup4 4.14.2 - HTML parsing and CSS selectors
- aiohttp (optional) - Async HTTP client for async scraping mode

**Testing:**
- pytest 8.4.2 - Test framework (299 tests, 100% pass rate)
- pytest-asyncio - Async test support
- pytest-cov - Coverage reporting

## Optional Features

**API Enhancement:**
- anthropic - Anthropic Claude API for SKILL.md enhancement
- Cost: ~$0.15-0.30 per skill enhancement
- Alternative: Local enhancement using Claude Code Max (free)

**GitHub Repository Scraping:**
- PyGithub 2.5.0 - GitHub API client
- Enables: Code analysis, issues, releases, repo metadata
- Requires: GITHUB_TOKEN for higher rate limits

**PDF Extraction:**
- PyMuPDF 1.24.14 - PDF text and table extraction
- Pillow 11.0.0 - Image processing
- pytesseract 0.3.13 - OCR for scanned PDFs (requires tesseract binary)

**MCP Integration:**
- mcp==1.18.0 - Model Context Protocol for Claude Code
- starlette - ASGI web framework
- uvicorn - ASGI server
- httpx - Async HTTP client for MCP

## Development Tools

**Virtual Environment:**
- venv (standard library) - Isolated Python environment
- MANDATORY for all development work
- Location: `venv/` in project root

**Package Management:**
- pip - Package installer
- requirements.txt - Dependency specification
- pip freeze - Dependency snapshot

**Version Control:**
- git 2.51.2+ - Version control
- Branch: development (default)
- Remote: GitHub

## Architecture Decisions

### Single-File Scraper Design
**File:** `cli/doc_scraper.py` (line 70: DocToSkillConverter class)

**Rationale:**
- Scraping logic is tightly coupled (URL validation → fetch → parse → categorize)
- Simpler to maintain than distributed modules
- Clear execution flow: scrape_all() → build_skill()
- Easy to add features without cross-file dependencies

**Trade-off:** Single file is large (~1000 lines), but organized into clear methods

### Async-First for I/O
**Performance:**
- Sync mode: ~18 pages/sec, 120 MB memory
- Async mode: ~55 pages/sec, 40 MB memory
- **Result:** 3x faster, 66% less memory

**Implementation:**
- Uses aiohttp for async HTTP
- Connection pooling (reuses TCP connections)
- Concurrent scraping with asyncio.gather()

**When to Use:**
- Async: 200+ pages (network latency dominates)
- Sync: < 200 pages (simpler, overhead not worth it)

### llms.txt Prioritized Over HTML
**Detection Order:**
1. `{base_url}/llms-full.txt` (complete documentation)
2. `{base_url}/llms.txt` (standard version)
3. `{base_url}/llms-small.txt` (quick reference)
4. Fall back to HTML scraping

**Benefits:**
- 10x faster (5 seconds vs 20-60 seconds)
- More reliable (maintained by docs authors)
- Better quality (pre-formatted for LLMs)
- No rate limiting issues (single file download)

**Example:** Hono framework at https://hono.dev/llms-full.txt

### Virtual Environment Mandatory
**Why:**
- Prevents system Python pollution
- Ensures consistent dependency versions across team
- Allows Python 3.10+ requirement without breaking system
- Isolates testing environment (pytest, mock libraries)

**Enforcement:**
- Pre-commit hooks check for venv activation
- AGENTS.md lists venv activation as first command
- .droid.yaml includes venv check in workflow

## Dependency Management

### Core vs Optional
**Core dependencies** (required for basic functionality):
- Installed by default: `pip install requests beautifulsoup4 pytest`
- Total: 3 packages + dependencies

**Optional dependencies** (feature-specific):
- API enhancement: `pip install anthropic`
- GitHub scraping: `pip install PyGithub`
- PDF extraction: `pip install PyMuPDF`
- OCR support: `pip install pytesseract Pillow`
- MCP server: `pip install mcp starlette uvicorn`

### Update Policy
**Minor versions:** Allowed automatically (2.32.x → 2.33.x)
**Major versions:** Require review and testing (2.x → 3.x)
**Rationale:** Balance between security updates and stability

### Security Scanning
**Tools:**
- pip-audit - Scan for known vulnerabilities
- Safety - Check against safety database
- Dependabot - Automated dependency updates (GitHub)

## Performance Characteristics

### Scraping Performance

| Mode | Pages/sec | Memory | Workers | Use Case |
|------|-----------|--------|---------|----------|
| Sync | ~18 | 120 MB | 1 | < 200 pages |
| Async | ~55 | 40 MB | 4-8 | 200+ pages |

### Processing Time

| Task | Duration | Notes |
|------|----------|-------|
| Page estimation | 1-3 min | Non-destructive, validates URLs |
| Documentation scraping | 15-45 min | Depends on size and mode |
| GitHub analysis | 5-10 min | Depends on repo size |
| PDF extraction | 2-15 min | Varies by PDF size and complexity |
| Skill building | 1-3 min | Fast, from cached data |
| Enhancement (local) | 30-60 sec | Uses Claude Code Max |
| Enhancement (API) | 20-40 sec | Uses Anthropic API |
| Packaging | 5-10 sec | Creates .zip file |

### Memory Limits

**Typical usage:**
- Small docs (< 200 pages): 50-80 MB
- Medium docs (200-1000 pages): 80-150 MB
- Large docs (1000-10000 pages): 150-500 MB

**Optimization:**
- Use async mode for 66% memory reduction
- Process in batches for massive docs (> 10K pages)
- Clear page cache between batches if needed

## Version History

**Current:** v2.0.0
- Multi-source scraping (docs + GitHub + PDF)
- Conflict detection (4 types)
- Unified scraper architecture

**Previous:**
- v1.2.0: PDF support with OCR
- v1.1.0: GitHub repository scraping
- v1.0.0: HTML documentation scraping

## External Services

### Anthropic API (Optional)
**Purpose:** AI-powered SKILL.md enhancement

**Authentication:** API key via ANTHROPIC_API_KEY environment variable

**Rate Limits:**
- Tier 1: 50 requests/minute
- Tier 2: 1000 requests/minute
- Typical usage: 1-2 requests per skill enhancement

**Cost:** ~$0.15-0.30 per skill enhancement (Claude Sonnet 3.5)

### GitHub API (Optional)
**Purpose:** Repository analysis, issues, releases

**Authentication:** GITHUB_TOKEN environment variable (optional but recommended)

**Rate Limits:**
- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour
- Typical usage: 10-50 requests per repo scrape

## Platform Support

**Primary:** macOS, Linux
**Secondary:** Windows (with WSL recommended)

**Known Issues:**
- Windows: File path handling differences (use pathlib)
- Windows: Virtual environment activation syntax different
- All platforms: Tesseract binary required for OCR (separate install)

## See Also

- **CLAUDE.md:** Technical architecture deep dive
- **requirements.txt:** Exact dependency versions
- **setup_mcp.sh:** MCP server installation
- **ASYNC_SUPPORT.md:** Async scraping guide
