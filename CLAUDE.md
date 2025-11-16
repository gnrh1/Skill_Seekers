# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<<<<<<< HEAD
## Project Overview

**Skill Seeker** is a Python-based tool that automatically converts documentation websites, GitHub repositories, and PDFs into Claude AI skills. It transforms scattered documentation into organized, comprehensive skills that can be uploaded to Claude for enhanced AI assistance.
=======
## 🎯 Current Status (November 11, 2025)

**Version:** v2.0.0 (Production Ready - Published on PyPI!)
**Active Development:** Flexible, incremental task-based approach
>>>>>>> upstream/development

**Version:** 2.0.0 (Production Ready)
**Python Requirements:** Python 3.10+
**Key Features:** Multi-source scraping, conflict detection, AI enhancement, MCP integration

<<<<<<< HEAD
## Repository Structure

```
Skill_Seekers/
├── cli/                           # Main CLI tools
│   ├── doc_scraper.py            # Core documentation scraper
│   ├── unified_scraper.py        # Multi-source scraper (NEW v2.0.0)
│   ├── github_scraper.py         # GitHub repository scraper
│   ├── pdf_scraper.py            # PDF extraction tool
│   ├── enhance_skill.py          # AI-powered skill enhancement
│   ├── enhance_skill_local.py    # Local enhancement (no API key)
│   ├── package_skill.py          # Package skills into .zip files
│   ├── upload_skill.py           # Auto-upload to Claude
│   ├── estimate_pages.py         # Quick page count estimation
│   ├── config_validator.py       # Configuration validation
│   ├── conflict_detector.py      # Documentation vs code conflict detection
│   ├── constants.py              # Centralized constants
│   ├── utils.py                  # Utility functions
│   └── run_tests.py              # Test runner with colored output
├── skill_seeker_mcp/              # MCP server for Claude Code integration
│   ├── server.py                 # Main MCP server (9 tools)
│   └── requirements.txt          # MCP-specific dependencies
├── configs/                       # Preset configurations for popular frameworks
│   ├── godot.json                # Godot Engine
│   ├── react.json                # React framework
│   ├── vue.json                  # Vue.js
│   ├── django.json               # Django web framework
│   ├── fastapi.json              # FastAPI
│   ├── *_unified.json            # Multi-source configurations (NEW)
│   └── ...                       # 20+ total configurations
├── tests/                         # Comprehensive test suite
│   ├── test_*.py                 # 299 tests (100% pass rate)
│   └── conftest.py               # Test configuration
├── docs/                          # Additional documentation
├── output/                        # Generated output (git-ignored)
├── requirements.txt               # Python dependencies
├── setup_mcp.sh                   # MCP server setup script
├── demo_conflicts.py             # Conflict detection demonstration
└── .claude/                       # Claude Code project configuration
    ├── agents/                   # Available agents
    │   ├── architectural-critic.md    # Architectural complexity specialist
    │   ├── code-analyzer.md           # Deep code analysis specialist
    │   ├── cognitive-resonator.md     # Cognitive flow and developer experience specialist
    │   ├── intelligence-orchestrator.md # Multi-Domain Intelligence Synthesis Specialist
    │   ├── orchestrator-agent.md      # Chief-of-staff orchestrator
    │   ├── performance-auditor.md     # Performance optimization specialist
    │   ├── possibility-weaver.md      # Creative catalyst agent
    │   ├── precision-editor.md        # Surgical code modification specialist
    │   ├── referee-agent-csp.md       # Convergent Synthesis Primitive for deterministic evaluation
    │   ├── security-analyst.md        # Practical security specialist for development workflows
    │   └── test-generator.md          # Comprehensive test generation specialist
    ├── commands/                 # Custom commands
    │   ├── check-hook.md          # Comprehensive hook validation system
    │   ├── create-agent.md        # Enhanced agent creation system with atomic operations and validation
    │   ├── refine-agent.md        # Multi-mental model agent refinement workflow
    │   └── update-CLAUDE.md      # Automatic documentation synchronization
    ├── hooks/                     # Hooks
    ├── skills/                    # Available skills
    │   └── agent-scaffolding-toolkit/  # Agent creation toolkit
    │       ├── SKILL.md
    │       ├── scripts/
    │       ├── assets/templates/
    │       └── references/
    └── mcp_config.example.json    # MCP configuration
```

## Development Commands

### Environment Setup

```bash
# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
=======
**🎉 MAJOR MILESTONE: Published on PyPI! (v2.0.0)**
- **📦 PyPI Publication**: Install with `pip install skill-seekers` - https://pypi.org/project/skill-seekers/
- **🔧 Modern Python Packaging**: pyproject.toml, src/ layout, entry points
- **✅ CI/CD Fixed**: All 5 test matrix jobs passing (Ubuntu + macOS, Python 3.10-3.12)
- **📚 Documentation Complete**: README, CHANGELOG, FUTURE_RELEASES.md all updated
- **🚀 Unified CLI**: Single `skill-seekers` command with Git-style subcommands
- **🧪 Test Coverage**: 379 tests passing, 39% coverage
- **🌐 Community**: GitHub Discussion, Release notes, announcements published

**🚀 Unified Multi-Source Scraping (v2.0.0)**
- **NEW**: Combine documentation + GitHub + PDF in one skill
- **NEW**: Automatic conflict detection between docs and code
- **NEW**: Rule-based and AI-powered merging
- **NEW**: 5 example unified configs (React, Django, FastAPI, Godot, FastAPI-test)
- **Status**: ⚠️ 12 unified tests need fixes (core functionality stable)

**✅ Community Response (H1 Group):**
- **Issue #8 Fixed** - Added BULLETPROOF_QUICKSTART.md and TROUBLESHOOTING.md for beginners
- **Issue #7 Fixed** - Fixed all 11 configs (Django, Laravel, Astro, Tailwind) - 100% working
- **Issue #4 Linked** - Connected to roadmap Tasks A2/A3 (knowledge sharing + website)
- **PR #5 Reviewed** - Approved anchor stripping feature (security verified, 32/32 tests pass)
- **MCP Setup Fixed** - Path expansion bug resolved in setup_mcp.sh

**📦 Configs Status:**
- ✅ **24 total configs available** (including unified configs)
- ✅ 5 unified configs added (React, Django, FastAPI, Godot, FastAPI-test)
- ✅ Core selectors tested and validated
- 📝 Single-source configs: ansible-core, astro, claude-code, django, fastapi, godot, godot-large-example, hono, kubernetes, laravel, react, steam-economy-complete, tailwind, vue
- 📝 Multi-source configs: django_unified, fastapi_unified, fastapi_unified_test, godot_unified, react_unified
- 📝 Test/Example configs: godot_github, react_github, python-tutorial-test, example_pdf, test-manual

**📋 Next Up (Post-PyPI v2.0.0):**
- **✅ DONE**: PyPI publication complete
- **✅ DONE**: CI/CD fixed - all checks passing
- **✅ DONE**: Documentation updated (README, CHANGELOG, FUTURE_RELEASES.md)
- **Priority 1**: Fix 12 failing unified tests in tests/test_unified.py
  - ConfigValidator expecting dict instead of file path
  - ConflictDetector expecting dict pages, not list
- **Priority 2**: Task H1.3 - Create example project folder
- **Priority 3**: Task A3.1 - GitHub Pages site (skillseekersweb.com)
- **Priority 4**: Task J1.1 - Install MCP package for testing

**📊 Roadmap Progress:**
- 134 tasks organized into 22 feature groups
- Project board: https://github.com/users/yusufkaraaslan/projects/2
- See [FLEXIBLE_ROADMAP.md](FLEXIBLE_ROADMAP.md) for complete task list

---

## 🔌 MCP Integration Available

**This repository includes a fully tested MCP server with 9 tools:**
- `mcp__skill-seeker__list_configs` - List all available preset configurations
- `mcp__skill-seeker__generate_config` - Generate a new config file for any docs site
- `mcp__skill-seeker__validate_config` - Validate a config file structure
- `mcp__skill-seeker__estimate_pages` - Estimate page count before scraping
- `mcp__skill-seeker__scrape_docs` - Scrape and build a skill
- `mcp__skill-seeker__package_skill` - Package skill into .zip file (with auto-upload)
- `mcp__skill-seeker__upload_skill` - Upload .zip to Claude (NEW)
- `mcp__skill-seeker__split_config` - Split large documentation configs
- `mcp__skill-seeker__generate_router` - Generate router/hub skills

**Setup:** See [docs/MCP_SETUP.md](docs/MCP_SETUP.md) or run `./setup_mcp.sh`

**Status:** ✅ Tested and working in production with Claude Code

## Overview

Skill Seeker automatically converts any documentation website into a Claude AI skill. It scrapes documentation, organizes content, extracts code patterns, and packages everything into an uploadable `.zip` file for Claude.

## Prerequisites

**Python Version:** Python 3.10 or higher (required for MCP integration)

**Installation:**

### Option 1: Install from PyPI (Recommended - Easiest!)
```bash
# Install globally or in virtual environment
pip install skill-seekers

# Use the unified CLI immediately
skill-seekers scrape --config configs/react.json
skill-seekers --help
```

### Option 2: Install from Source (For Development)
```bash
# Clone the repository
git clone https://github.com/yusufkaraaslan/Skill_Seekers.git
cd Skill_Seekers

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux (Windows: venv\Scripts\activate)

# Install in editable mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

**Why use a virtual environment?**
- Keeps dependencies isolated from system Python
- Prevents package version conflicts
- Standard Python development practice
- Required for running tests with pytest

**Optional (for API-based enhancement):**
```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

## Core Commands

### Quick Start - Use a Preset

```bash
# Single-source scraping (documentation only)
skill-seekers scrape --config configs/godot.json
skill-seekers scrape --config configs/react.json
skill-seekers scrape --config configs/vue.json
skill-seekers scrape --config configs/django.json
skill-seekers scrape --config configs/laravel.json
skill-seekers scrape --config configs/fastapi.json
```

### Unified Multi-Source Scraping (**NEW - v2.0.0**)

```bash
# Combine documentation + GitHub + PDF in one skill
skill-seekers unified --config configs/react_unified.json
skill-seekers unified --config configs/django_unified.json
skill-seekers unified --config configs/fastapi_unified.json
skill-seekers unified --config configs/godot_unified.json

# Override merge mode
skill-seekers unified --config configs/react_unified.json --merge-mode claude-enhanced

# Result: One comprehensive skill with conflict detection
```

**What makes it special:**
- ✅ Detects discrepancies between documentation and code
- ✅ Shows both versions side-by-side with ⚠️ warnings
- ✅ Identifies outdated docs and undocumented features
- ✅ Single source of truth showing intent (docs) AND reality (code)

**See full guide:** [docs/UNIFIED_SCRAPING.md](docs/UNIFIED_SCRAPING.md)

### First-Time User Workflow (Recommended)

```bash
# 1. Install from PyPI (one-time, easiest!)
pip install skill-seekers

# 2. Estimate page count BEFORE scraping (fast, no data download)
skill-seekers estimate configs/godot.json
# Time: ~1-2 minutes, shows estimated total pages and recommended max_pages

# 3. Scrape with local enhancement (uses Claude Code Max, no API key)
skill-seekers scrape --config configs/godot.json --enhance-local
# Time: 20-40 minutes scraping + 60 seconds enhancement

# 4. Package the skill
skill-seekers package output/godot/

# Result: godot.zip ready to upload to Claude
```

### Interactive Mode

```bash
# Step-by-step configuration wizard
skill-seekers scrape --interactive
```

### Quick Mode (Minimal Config)

```bash
# Create skill from any documentation URL
skill-seekers scrape --name react --url https://react.dev/ --description "React framework for UIs"
```

### Skip Scraping (Use Cached Data)

```bash
# Fast rebuild using previously scraped data
skill-seekers scrape --config configs/godot.json --skip-scrape
# Time: 1-3 minutes (instant rebuild)
```

### Async Mode (2-3x Faster Scraping)

```bash
# Enable async mode with 8 workers for best performance
skill-seekers scrape --config configs/react.json --async --workers 8

# Quick mode with async
skill-seekers scrape --name react --url https://react.dev/ --async --workers 8

# Dry run with async to test
skill-seekers scrape --config configs/godot.json --async --workers 4 --dry-run
```

**Recommended Settings:**
- Small docs (~100-500 pages): `--async --workers 4`
- Medium docs (~500-2000 pages): `--async --workers 8`
- Large docs (2000+ pages): `--async --workers 8 --no-rate-limit`

**Performance:**
- Sync: ~18 pages/sec, 120 MB memory
- Async: ~55 pages/sec, 40 MB memory (3x faster!)

**See full guide:** [ASYNC_SUPPORT.md](ASYNC_SUPPORT.md)

### Enhancement Options

**LOCAL Enhancement (Recommended - No API Key Required):**
```bash
# During scraping
skill-seekers scrape --config configs/react.json --enhance-local

# Standalone after scraping
skill-seekers enhance output/react/
```

**API Enhancement (Alternative - Requires API Key):**
```bash
# During scraping
skill-seekers scrape --config configs/react.json --enhance

# Standalone after scraping
skill-seekers-enhance output/react/
skill-seekers-enhance output/react/ --api-key sk-ant-...
```

### Package and Upload the Skill

```bash
# Package skill (opens folder, shows upload instructions)
skill-seekers package output/godot/
# Result: output/godot.zip

# Package and auto-upload (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-ant-...
skill-seekers package output/godot/ --upload

# Upload existing .zip
skill-seekers upload output/godot.zip

# Package without opening folder
skill-seekers package output/godot/ --no-open
```

### Force Re-scrape

```bash
# Delete cached data and re-scrape from scratch
rm -rf output/godot_data/
skill-seekers scrape --config configs/godot.json
```

### Estimate Page Count (Before Scraping)

```bash
# Quick estimation - discover up to 100 pages
skill-seekers estimate configs/react.json --max-discovery 100
# Time: ~30-60 seconds

# Full estimation - discover up to 1000 pages (default)
skill-seekers estimate configs/godot.json
# Time: ~1-2 minutes

# Deep estimation - discover up to 2000 pages
skill-seekers estimate configs/vue.json --max-discovery 2000
# Time: ~3-5 minutes

# What it shows:
# - Estimated total pages
# - Recommended max_pages value
# - Estimated scraping time
# - Discovery rate (pages/sec)
```

**Why use estimation:**
- Validates config URL patterns before full scrape
- Helps set optimal `max_pages` value
- Estimates total scraping time
- Fast (only HEAD requests + minimal parsing)
- No data downloaded or stored

## Repository Architecture

### File Structure (v2.0.0 - Modern Python Packaging)

```
Skill_Seekers/
├── pyproject.toml              # Modern Python package configuration (PEP 621)
├── src/                        # Source code (src/ layout best practice)
│   └── skill_seekers/
│       ├── __init__.py
│       ├── cli/                # CLI tools (entry points)
│       │   ├── doc_scraper.py      # Main scraper (~790 lines)
│       │   ├── estimate_pages.py   # Page count estimator
│       │   ├── enhance_skill.py    # AI enhancement (API-based)
│       │   ├── package_skill.py    # Skill packager
│       │   ├── github_scraper.py   # GitHub scraper
│       │   ├── pdf_scraper.py      # PDF scraper
│       │   ├── unified_scraper.py  # Unified multi-source scraper
│       │   ├── merge_sources.py    # Source merger
│       │   └── conflict_detector.py # Conflict detection
│       └── mcp/                # MCP server integration
│           └── server.py
├── tests/                      # Test suite (379 tests passing)
│   ├── test_scraper_features.py
│   ├── test_config_validation.py
│   ├── test_integration.py
│   ├── test_mcp_server.py
│   ├── test_unified.py         # (12 tests need fixes)
│   └── ...
├── configs/                    # Preset configurations (24 configs)
│   ├── godot.json
│   ├── react.json
│   ├── django_unified.json     # Multi-source configs
│   └── ...
├── docs/                       # Documentation
│   ├── CLAUDE.md               # This file
│   ├── ENHANCEMENT.md          # Enhancement guide
│   ├── UPLOAD_GUIDE.md         # Upload instructions
│   └── UNIFIED_SCRAPING.md     # Unified scraping guide
├── README.md                   # User documentation
├── CHANGELOG.md                # Release history
├── FUTURE_RELEASES.md          # Roadmap
└── output/                     # Generated output (git-ignored)
    ├── {name}_data/            # Scraped raw data (cached)
    │   ├── pages/*.json        # Individual page data
    │   └── summary.json        # Scraping summary
    └── {name}/                 # Built skill directory
        ├── SKILL.md            # Main skill file
        ├── SKILL.md.backup     # Backup (if enhanced)
        ├── references/         # Categorized documentation
        │   ├── index.md
        │   ├── getting_started.md
        │   ├── api.md
        │   └── ...
        ├── scripts/            # Empty (user scripts)
        └── assets/             # Empty (user assets)
```

**Key Changes in v2.0.0:**
- **src/ layout**: Modern Python packaging structure
- **pyproject.toml**: PEP 621 compliant configuration
- **Entry points**: `skill-seekers` CLI with subcommands
- **Published to PyPI**: `pip install skill-seekers`

### Data Flow

1. **Scrape Phase** (`scrape_all()` in src/skill_seekers/cli/doc_scraper.py):
   - Input: Config JSON (name, base_url, selectors, url_patterns, categories)
   - Process: BFS traversal from base_url, respecting include/exclude patterns
   - Output: `output/{name}_data/pages/*.json` + `summary.json`

2. **Build Phase** (`build_skill()` in src/skill_seekers/cli/doc_scraper.py):
   - Input: Scraped JSON data from `output/{name}_data/`
   - Process: Load pages → Smart categorize → Extract patterns → Generate references
   - Output: `output/{name}/SKILL.md` + `output/{name}/references/*.md`

3. **Enhancement Phase** (optional via enhance_skill.py or enhance_skill_local.py):
   - Input: Built skill directory with references
   - Process: Claude analyzes references and rewrites SKILL.md
   - Output: Enhanced SKILL.md with real examples and guidance

4. **Package Phase** (via package_skill.py):
   - Input: Skill directory
   - Process: Zip all files (excluding .backup)
   - Output: `{name}.zip`

5. **Upload Phase** (optional via upload_skill.py):
   - Input: Skill .zip file
   - Process: Upload to Claude AI via API
   - Output: Skill available in Claude

### Configuration File Structure

Config files (`configs/*.json`) define scraping behavior:

```json
{
  "name": "godot",
  "description": "When to use this skill",
  "base_url": "https://docs.godotengine.org/en/stable/",
  "selectors": {
    "main_content": "div[role='main']",
    "title": "title",
    "code_blocks": "pre"
  },
  "url_patterns": {
    "include": [],
    "exclude": ["/search.html", "/_static/"]
  },
  "categories": {
    "getting_started": ["introduction", "getting_started"],
    "scripting": ["scripting", "gdscript"],
    "api": ["api", "reference", "class"]
  },
  "rate_limit": 0.5,
  "max_pages": 500
}
```

**Config Parameters:**
- `name`: Skill identifier (output directory name)
- `description`: When Claude should use this skill
- `base_url`: Starting URL for scraping
- `selectors.main_content`: CSS selector for main content (common: `article`, `main`, `div[role="main"]`)
- `selectors.title`: CSS selector for page title
- `selectors.code_blocks`: CSS selector for code samples
- `url_patterns.include`: Only scrape URLs containing these patterns
- `url_patterns.exclude`: Skip URLs containing these patterns
- `categories`: Keyword mapping for categorization
- `rate_limit`: Delay between requests (seconds)
- `max_pages`: Maximum pages to scrape

## Key Features & Implementation

### Auto-Detect Existing Data
Tool checks for `output/{name}_data/` and prompts to reuse, avoiding re-scraping (check_existing_data() in doc_scraper.py:653-660).

### Language Detection
Detects code languages from:
1. CSS class attributes (`language-*`, `lang-*`)
2. Heuristics (keywords like `def`, `const`, `func`, etc.)

See: `detect_language()` in doc_scraper.py:135-165

### Pattern Extraction
Looks for "Example:", "Pattern:", "Usage:" markers in content and extracts following code blocks (up to 5 per page).

See: `extract_patterns()` in doc_scraper.py:167-183

### Smart Categorization
- Scores pages against category keywords (3 points for URL match, 2 for title, 1 for content)
- Threshold of 2+ for categorization
- Auto-infers categories from URL segments if none provided
- Falls back to "other" category

See: `smart_categorize()` and `infer_categories()` in doc_scraper.py:282-351

### Enhanced SKILL.md Generation
Generated with:
- Real code examples from documentation (language-annotated)
- Quick reference patterns extracted from docs
- Common pattern section
- Category file listings

See: `create_enhanced_skill_md()` in doc_scraper.py:426-542

## Common Workflows

### First Time (With Scraping + Enhancement)

```bash
# 1. Scrape + Build + AI Enhancement (LOCAL, no API key)
skill-seekers scrape --config configs/godot.json --enhance-local
>>>>>>> upstream/development

# Install dependencies
pip install -r requirements.txt

# Optional: Install PDF support
pip install PyMuPDF

<<<<<<< HEAD
# Optional: Install GitHub support
pip install PyGithub
=======
# 4. Package
skill-seekers package output/godot/
>>>>>>> upstream/development

# Optional: Install for API-based enhancement
pip install anthropic
```

### Testing

```bash
<<<<<<< HEAD
# Run all tests with colored output
python3 cli/run_tests.py

# Run specific test suites
python3 cli/run_tests.py --suite config
python3 cli/run_tests.py --suite features
python3 cli/run_tests.py --suite integration
=======
# 1. Use existing data + Local Enhancement
skill-seekers scrape --config configs/godot.json --skip-scrape
skill-seekers enhance output/godot/

# 2. Package
skill-seekers package output/godot/
>>>>>>> upstream/development

# Verbose testing
python3 cli/run_tests.py --verbose

# Run tests using pytest directly
pytest tests/ -v
pytest tests/test_mcp_server.py -v
```

### Core Development Workflows

```bash
<<<<<<< HEAD
# 1. Test with small dataset first
python3 cli/estimate_pages.py configs/react.json

# 2. Run a basic scrape
python3 cli/doc_scraper.py --config configs/react.json
=======
# 1. Scrape + Build (no enhancement)
skill-seekers scrape --config configs/godot.json

# 2. Package
skill-seekers package output/godot/
>>>>>>> upstream/development

# 3. Enhanced skill creation (recommended)
python3 cli/doc_scraper.py --config configs/react.json --enhance-local

# 4. Package the skill
python3 cli/package_skill.py output/react/

# 5. Test multi-source scraping (NEW v2.0.0)
python3 cli/unified_scraper.py --config configs/react_unified.json

# 6. Run conflict detection demo
python3 demo_conflicts.py
```

### MCP Server Development

```bash
<<<<<<< HEAD
# Setup MCP server for Claude Code integration
./setup_mcp.sh

# Test MCP server manually
python3 skill_seeker_mcp/server.py

# Test MCP server tools
python3 -m pytest tests/test_mcp_server.py -v
```

### Configuration Management

```bash
# Validate configuration files
python3 cli/config_validator.py configs/react.json

# Generate new configuration interactively
python3 cli/doc_scraper.py --interactive

# Create unified multi-source config
python3 cli/unified_scraper.py --create-config
=======
skill-seekers scrape --interactive
# Follow prompts, it creates the config for you
>>>>>>> upstream/development
```

## 🚀 Agent Scaffolding Toolkit (NEW)

**Location**: `.claude/skills/agent-scaffolding-toolkit/`

A surgical toolkit for creating specialized agents with interactive wizard-guided generation. Eliminates human-in-the-loop dependency while maintaining developer flexibility.

### **Quick Start**

```bash
# Setup agent scaffolding toolkit
cd .claude/skills/agent-scaffolding-toolkit/
./setup.sh

# Create agents interactively (60 seconds)
source .venv/bin/activate
python scripts/create_agent.py

<<<<<<< HEAD
# Available templates
python scripts/list_templates.py --detailed
=======
# Test with limited pages first
# Set "max_pages": 20 in config

# Use it
skill-seekers scrape --config configs/myframework.json
>>>>>>> upstream/development
```

### **Available Agents**

| Agent | Description | Use Case |
|--------|-------------|---------|
| **@architectural-critic** | Architectural complexity specialist that detects phase boundaries, system transitions, and structural evolution patterns in codebases through multi-dimensional analysis. Provides pre-emptive intervention strategies before architectural breakdown occurs. | Pre-emptive Architecture Review** |
| **@code-analyzer** | Deep code analysis agent specializing in complexity metrics, design patterns, anti-patterns, and technical debt. Provides quantifiable assessments with actionable refactoring recommendations. | Pre-commit Review** |
| **@cognitive-resonator** | Cognitive flow specialist that analyzes code harmony, mental model alignment, and developer experience optimization through psychological and computational analysis. Enhances developer productivity by ensuring code patterns resonate with natural cognitive processes. | Developer Experience Optimization** |
| **@orchestrator-agent** | The single interface pattern applied to agent fleets. Manages, delegates, and synthesizes results from parallel subagents. | orchestration |
| **@performance-auditor** | Performance optimization specialist that identifies bottlenecks, memory leaks, and inefficient algorithms through systematic profiling and data-driven analysis. Provides quantifiable performance improvements with ROI calculations. | API Endpoint Optimization** |
| **@possibility-weaver** | Creative catalyst agent that introduces novel perspectives and beneficial constraints to break developers out of local optima. Uses constraint innovation and perspective synthesis to expand solution spaces while maintaining core system invariants. | Innovation & Problem Solving** |
| **@precision-editor** | Surgical code modification specialist that performs precise, system-aware edits with minimal side effects and maximum architectural integrity. Uses gene-editing precision to make targeted modifications while preserving system coherence and design intent. | Surgical Code Modifications** |
| **@referee-agent-csp** | Convergent Synthesis Primitive for deterministic outcome evaluation and autonomous selection. Performs metric-driven synthesis of multiple parallel agent outputs. | synthesis |
| **@security-analyst** | Practical security specialist for development workflows. Analyzes code, configurations, and dependencies for common vulnerabilities without requiring security expertise. | security |
| **@intelligence-orchestrator** | Multi-Domain Intelligence Synthesis Specialist that enhances the entire Skill_Seekers ecosystem through agent intelligence enhancement, testing intelligence, and workflow orchestration. | Intelligence Enhancement, Testing Optimization, Workflow Orchestration** |
| **@test-generator** | Comprehensive test generation specialist that creates unit, integration, performance, and security tests with coverage optimization and CI/CD integration. Generates maintainable test suites using the T.E.S.T. methodology for maximum effectiveness and developer productivity. | New Feature Testing** |


### **Agent Creation Workflow**

1. **Interactive Wizard**: 4 surgical decisions (type, tools, model, customization)
2. **Template Selection**: Choose from battle-tested templates
3. **Instant Generation**: Creates validated agents in project-wide `.claude/agents/`
4. **Zero Learning Curve**: Immediate productivity from first use

### **Agent Refinement Workflow**

**Multi-Mental Model Agent Refinement**:
- **Command**: `/refine-agent <agent-name> [focus-area]`
- **Methodology**: check → plan → recheck → pause → create → recheck → refine → recheck → exit
- **Mental Models**: First principles, second order effects, interdependencies, systems thinking, inversion
- **Automation**: Systematic validation, YAML compliance, user scenario testing
- **Example**: Applied to security-analyst agent (expanded from 3 lines to 172 lines of practical security guidance)

### **Documentation Synchronization**

**Automatic CLAUDE.md Updates**:
- **Command**: `/update-CLAUDE.md [options]`
- **Detection**: Monitors agents, commands, skills, and structural changes
- **Automation**: Updates agent tables, command descriptions, structure diagrams
- **Validation**: Ensures consistency across all documentation sections
- **Integration**: Git hooks and CI/CD pipeline support

### **Hook Validation System**

**Comprehensive Hook Health Monitoring**:
- **Command**: `/check-hook [options]`
- **Validation**: JSON syntax, path resolution, executable permissions, environment health
- **Testing**: Functional testing with sample data and performance impact assessment
- **Auto-Fix**: Automatic resolution of common issues (permissions, paths, syntax)
- **Scoring**: Overall hook health score with detailed diagnostics

**Usage Examples**:
```bash
# Quick validation
/check-hook

# Full validation with fixes and testing
/check-hook --fix --test --verbose

# Test specific hook types
/check-hook --hooks PreToolUse --test
```

### **Key Features**

- **60-Second Agent Creation**: Interactive wizard with intelligent defaults
- **Battle-Tested Templates**: Orchestrator, Referee, Specialist patterns
- **Automatic Validation**: Structural compliance checking via hooks
- **Project-Wide Availability**: Agents created in `.claude/agents/` for immediate use
- **Progressive Documentation**: Layer 1 (immediate) + Layer 2 (detailed)
- **Comprehensive Test Suite**: 21 tests with 95% coverage target
- **Skill Seekers Export**: Convert agents to skills with conflict detection
- **Git Integration**: Pre-commit hooks for agent validation

### **Testing & Quality**

**Test Suite**: `.claude/tests/`
- **21 comprehensive tests** (unit, integration, E2E)
- **95% coverage target** across all hook scripts
- **Fixtures & mocks** for isolated testing
- **CI/CD ready** with GitHub Actions support

```bash
# Run tests
cd .claude/tests
source .venv/bin/activate
pip install -r requirements.txt
pytest -v

# With coverage
pytest --cov=../ --cov-report=html
```

### **Export Integration**

**Export to Skill Seekers**: `.claude/skills/agent-scaffolding-toolkit/scripts/export_to_skill_seekers.py`

```bash
# Export all agents to Skill Seekers format
cd .claude/skills/agent-scaffolding-toolkit
source .venv/bin/activate
python scripts/export_to_skill_seekers.py --detect-conflicts --package
```

**Features:**
- Maps agents → SKILL.md + configs
- Preserves delegation relationships
- Detects conflicts with existing skills
- Optional .zip packaging
- Registry integration for usage stats

## Key Architectural Components

### 1. Multi-Source Architecture (v2.0.0)

The unified scraper combines multiple data sources:
- **Documentation websites** - Traditional HTML docs scraping
- **GitHub repositories** - Code analysis, API extraction, issues/PRs
- **PDF files** - Text, table, and image extraction
- **Conflict Detection** - Identifies discrepancies between sources

### 2. MCP Integration

9 MCP tools available in Claude Code:
- `list_configs` - List available preset configurations
- `generate_config` - Create new configuration files
- `validate_config` - Validate configuration structure
- `estimate_pages` - Estimate scraping time and page count
- `scrape_docs` - Scrape documentation and build skills
- `package_skill` - Package skills with auto-upload capability
- `upload_skill` - Upload existing .zip files to Claude
- `split_config` - Split large documentation into focused skills
- `generate_router` - Create router/hub skills for sub-skill navigation

### 3. Conflict Detection System

Automatically detects 4 types of conflicts:
- **Missing in docs** (high): Features implemented but not documented
- **Missing in code** (high): Documented but not implemented
- **Signature mismatch** (medium): Different parameters/types
- **Description mismatch** (low): Different explanations

### 4. AI Enhancement

Two enhancement modes:
- **LOCAL**: Uses Claude Code Max plan (no API costs)
- **API**: Uses Anthropic API (~$0.15-0.30 per skill)

## Technical Architecture Deep Dive

### Single-File Design Philosophy

The core scraper (`cli/doc_scraper.py`) follows a class-based architecture with a single `DocToSkillConverter` class at **line 70** that handles:
- **Web scraping**: BFS traversal with URL validation
- **Content extraction**: CSS selectors for title, content, code blocks
- **Language detection**: Heuristic-based detection from code samples (Python, JavaScript, GDScript, C++, etc.)
- **Pattern extraction**: Identifies common coding patterns from documentation
- **Categorization**: Smart categorization using URL structure, page titles, and content keywords with scoring
- **Skill generation**: Creates SKILL.md with real code examples and categorized reference files

### Critical Code Locations (Verified)

| Function | Line | Purpose |
|----------|------|---------|
| `DocToSkillConverter` class | 70 | Main converter class |
| `scrape_all()` | 566 | Primary scraping loop (sync) |
| `scrape_all_async()` | 727 | Async scraping (3x faster) |
| `create_enhanced_skill_md()` | 1005 | SKILL.md generation with examples |
| `smart_categorize()` | ~280-321 | Smart categorization logic |
| `extract_patterns()` | ~165-181 | Pattern extraction from docs |
| `detect_language()` | ~133-163 | Code language detection |

### Data Flow Architecture

**Phase 1: Scrape**
```
Input: Config JSON → BFS Traversal → URL Validation → Content Extraction
Output: output/{name}_data/pages/*.json + summary.json
```

**Phase 2: Build**
```
Input: Scraped JSON → Smart Categorize → Extract Patterns → Generate References
Output: output/{name}/SKILL.md + references/*.md
```

### Selector Testing with BeautifulSoup

To find the right CSS selectors for a documentation site:

```python
from bs4 import BeautifulSoup
import requests

url = "https://docs.example.com/page"
soup = BeautifulSoup(requests.get(url).content, 'html.parser')

# Try different selectors
print(soup.select_one('article'))        # Common in modern docs
print(soup.select_one('main'))           # HTML5 semantic
print(soup.select_one('div[role="main"]')) # Accessibility markup
print(soup.select_one('div.content'))    # Classic pattern
```

**Common selector patterns:**
- `article` - Modern documentation (React, Vue)
- `main` - HTML5 semantic (MDN, W3C)
- `div[role="main"]` - Accessibility-first sites
- `div.content`, `div.docs` - Classic documentation

### llms.txt Support Detection Order

Skill_Seekers automatically detects llms.txt files before HTML scraping:

**Detection Priority:**
1. `{base_url}/llms-full.txt` (complete documentation)
2. `{base_url}/llms.txt` (standard version)
3. `{base_url}/llms-small.txt` (quick reference)
4. Falls back to HTML scraping if none found

**Benefits:**
- ⚡ **10x faster**: < 5 seconds vs 20-60 seconds
- ✅ **More reliable**: Maintained by docs authors
- 🎯 **Better quality**: Pre-formatted for LLMs
- 🚫 **No rate limiting**: Single file download

**Example:** Hono framework at https://hono.dev/llms-full.txt

### Output Quality Validation

After building, verify quality with these commands:

```bash
# Check SKILL.md has real code examples
cat output/godot/SKILL.md | grep -A 5 "```"

# Verify categorization worked
cat output/godot/references/index.md

# Check category files exist
ls -lh output/godot/references/

# Count total pages processed
jq '.total_pages' output/godot_data/summary.json

# Check for language detection
grep -o 'language-[a-z]*' output/godot/SKILL.md | sort | uniq -c
```

### Smart Categorization Algorithm

**Scoring system** (minimum 2 points for categorization):
- **3 points**: Keyword found in URL path
- **2 points**: Keyword found in page title
- **1 point**: Keyword found in content preview (first 500 chars)

**Category inference**: If no categories provided in config, auto-infers from URL segments:
- `/docs/api/` → "api" category
- `/guide/getting-started/` → "getting_started" category
- Falls back to "other" if no match

**Example categorization:**
```
Page: https://docs.godot.org/en/stable/tutorials/scripting/gdscript/
URL contains "scripting" (3 pts) + "gdscript" (3 pts) = 6 points
→ Categorized as "scripting"
```

## Configuration System

### Standard Config Structure

```json
{
  "name": "skill-name",
  "description": "When to use this skill",
  "base_url": "https://docs.example.com/",
  "selectors": {
    "main_content": "article",
    "title": "h1",
    "code_blocks": "pre code"
  },
  "url_patterns": {
    "include": ["/docs", "/guide"],
    "exclude": ["/blog", "/search"]
  },
  "categories": {
    "getting_started": ["intro", "quickstart"],
    "api": ["reference", "api"]
  },
  "rate_limit": 0.5,
  "max_pages": 500
}
```

### Unified Config Structure (v2.0.0)

<<<<<<< HEAD
=======
### No Content Extracted
**Problem:** Pages scraped but content is empty

**Solution:** Check `main_content` selector in config. Try:
- `article`
- `main`
- `div[role="main"]`
- `div.content`

Use the BeautifulSoup testing approach above to find the right selector.

### Poor Categorization
**Problem:** Pages not categorized well

**Solution:** Edit `categories` section in config with better keywords specific to the documentation structure. Check URL patterns in scraped data:

```bash
# See what URLs were scraped
cat output/godot_data/summary.json | grep url | head -20
```

### Data Exists But Won't Use It
**Problem:** Tool won't reuse existing data

**Solution:** Force re-scrape:
```bash
rm -rf output/myframework_data/
skill-seekers scrape --config configs/myframework.json
```

### Rate Limiting Issues
**Problem:** Getting rate limited or blocked by documentation server

**Solution:** Increase `rate_limit` value in config:
>>>>>>> upstream/development
```json
{
  "name": "skill-name",
  "description": "Comprehensive skill from multiple sources",
  "merge_mode": "rule-based",
  "sources": [
    {
      "type": "documentation",
      "base_url": "https://docs.example.com/",
      "extract_api": true,
      "max_pages": 200
    },
    {
      "type": "github",
      "repo": "owner/example",
      "include_code": true,
      "code_analysis_depth": "surface"
    }
  ]
}
```

## Core Constants and Limits

Key constants defined in `cli/constants.py`:
- `DEFAULT_RATE_LIMIT`: 0.5 seconds between requests
- `DEFAULT_MAX_PAGES`: 500 pages maximum
- `CONTENT_PREVIEW_LENGTH`: 500 characters for categorization
- `MIN_CATEGORIZATION_SCORE`: 2 points minimum for category assignment
- `API_CONTENT_LIMIT`: 100,000 characters for API enhancement
- `LOCAL_CONTENT_LIMIT`: 50,000 characters for local enhancement

## Testing Strategy

### Test Coverage
- **299 tests** with 100% pass rate
- Unit tests for all core components
- Integration tests for end-to-end workflows
- MCP server tests for all 9 tools
- Conflict detection tests

### Test Categories
- Configuration validation
- Scraping functionality (sync and async)
- PDF extraction features
- GitHub repository analysis
- Unified multi-source scraping
- MCP tool functionality
- Enhancement processes

## Performance Characteristics

### Scraping Performance
- **Sync mode**: ~18 pages/sec, 120 MB memory
- **Async mode**: ~55 pages/sec, 40 MB memory (3x faster)
- **Async workers**: 4-8 workers recommended
- **Rate limiting**: Configurable to avoid server blocks

### Processing Time
- Page estimation: 1-3 minutes
- Documentation scraping: 15-45 minutes
- GitHub analysis: 5-10 minutes
- PDF extraction: 2-15 minutes (varies by size)
- Skill building: 1-3 minutes
- Enhancement: 30-60 seconds (local), 20-40 seconds (API)
- Packaging: 5-10 seconds

## Development Methodology: Multi-Model Approach

This project follows a rigorous **check → plan → recheck → pause → create → recheck → refine → recheck → exit** methodology, enhanced by multiple mental models:

### **Mental Models Applied**

1. **First Principles**: Break problems down to fundamental truths
2. **Second Order Effects**: Consider consequences of consequences
3. **Interdependencies**: Map system relationships and feedback loops
4. **Systems Thinking**: View the project as an integrated whole
5. **Inversion**: Approach problems by considering what to avoid

### **Workflow Phases**

**CHECK Phase** (First Principles + Systems Thinking)
- Verify current state and identify structural issues
- Map existing dependencies and relationships
- Assess robustness of existing components

**PLAN Phase** (Second Order Effects + Interdependencies)
- Design solutions considering cascading impacts
- Plan for ripple effects across the system
- Create structured implementation roadmap

**RECHECK Phase** (Systems Thinking)
- Validate plan against system requirements
- Check for unintended consequences
- Verify integration points

**PAUSE Phase** (Inversion)
- Consider what could go wrong
- Identify failure modes and mitigation strategies
- Challenge assumptions

**CREATE Phase** (First Principles)
- Implement based on fundamental requirements
- Build with minimal complexity
- Focus on core functionality

**RECHECK Phase** (All Models)
- Validate implementation works correctly
- Check for second order effects
- Verify system integration

**REFINE Phase** (Continuous Improvement)
- Optimize based on testing results
- Address discovered issues
- Enhance robustness

**FINAL RECHECK Phase** (Holistic Validation)
- Complete system validation
- Cross-model verification
- Final quality assurance

**EXIT**: Document decisions and lessons learned

### **Practical Application**

This methodology was applied to:
- Agent scaffolding toolkit development
- Path calculation corrections (nested .claude folder elimination)
- YAML structure validation
- Multi-agent system orchestration design

## Development Guidelines

### Adding New Features

1. **Apply methodology**: Use check→plan→recheck→pause→create→recheck→refine→recheck→exit
2. **Create constants** in `cli/constants.py` for magic numbers
3. **Write tests** in appropriate `tests/test_*.py` file
4. **Update configurations** if adding new config options
5. **Document changes** in relevant docs files
6. **Run full test suite** before committing
7. **Consider second order effects** of changes
8. **Validate system integration** thoroughly

### Configuration Development

1. **Test selectors** using browser dev tools
2. **Validate with** `python3 cli/config_validator.py`
3. **Start with small** `max_pages` (20-50) for testing
4. **Use estimate_pages** to validate URL patterns
5. **Test categorization** with sample data

### MCP Tool Development

1. **Add tool** to `skill_seeker_mcp/server.py`
2. **Update tool list** in documentation
3. **Write tests** in `tests/test_mcp_server.py`
4. **Test with** `./setup_mcp.sh` script
5. **Update README.md** with new tool examples

## Important File Locations

- **Main scraper**: `cli/doc_scraper.py:228-251` (scrape_all)
- **Enhanced SKILL.md generation**: `cli/doc_scraper.py:426-542`
- **Conflict detection**: `cli/conflict_detector.py`
- **MCP server**: `skill_seeker_mcp/server.py`
- **Configuration validation**: `cli/config_validator.py`
- **Constants**: `cli/constants.py`
- **Test runner**: `cli/run_tests.py`

## Common Issues and Solutions

### Virtual Environment
Always use a virtual environment to avoid dependency conflicts:
```bash
<<<<<<< HEAD
source venv/bin/activate  # Required for each new terminal session
=======
skill-seekers package output/godot/
>>>>>>> upstream/development
```

### Rate Limiting
If getting blocked by documentation servers:
1. Increase `rate_limit` in config (try 1.0 or 2.0)
2. Use `--async` mode for better performance
3. Add more exclude patterns for non-essential URLs

### Memory Issues
For large documentation (>10K pages):
1. Use `--async` mode (66% less memory)
2. Split config using `split_config.py`
3. Use checkpoint/resume functionality

<<<<<<< HEAD
### MCP Integration Issues
1. Ensure Python 3.10+ is installed
2. Run `./setup_mcp.sh` for proper configuration
3. Restart Claude Code after configuration
4. Check Claude Code logs for errors

## Additional Documentation

- **Complete User Guide**: [README.md](README.md)
- **Beginner's Guide**: [BULLETPROOF_QUICKSTART.md](BULLETPROOF_QUICKSTART.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **MCP Setup**: [docs/MCP_SETUP.md](docs/MCP_SETUP.md)
- **Multi-Source Scraping**: [docs/UNIFIED_SCRAPING.md](docs/UNIFIED_SCRAPING.md)
- **Enhancement Guide**: [docs/ENHANCEMENT.md](docs/ENHANCEMENT.md)
- **Testing Documentation**: [docs/TESTING.md](docs/TESTING.md)
=======
## Key Code Locations (v2.0.0)

**Documentation Scraper** (`src/skill_seekers/cli/doc_scraper.py`):
- **URL validation**: `is_valid_url()`
- **Content extraction**: `extract_content()`
- **Language detection**: `detect_language()`
- **Pattern extraction**: `extract_patterns()`
- **Smart categorization**: `smart_categorize()`
- **Category inference**: `infer_categories()`
- **Quick reference generation**: `generate_quick_reference()`
- **SKILL.md generation**: `create_enhanced_skill_md()`
- **Scraping loop**: `scrape_all()`
- **Main workflow**: `main()`

**Other Key Files**:
- **GitHub scraper**: `src/skill_seekers/cli/github_scraper.py`
- **PDF scraper**: `src/skill_seekers/cli/pdf_scraper.py`
- **Unified scraper**: `src/skill_seekers/cli/unified_scraper.py`
- **Conflict detection**: `src/skill_seekers/cli/conflict_detector.py`
- **Source merger**: `src/skill_seekers/cli/merge_sources.py`
- **Package tool**: `src/skill_seekers/cli/package_skill.py`
- **Upload tool**: `src/skill_seekers/cli/upload_skill.py`
- **MCP server**: `src/skill_seekers/mcp/server.py`
- **Entry points**: `pyproject.toml` (project.scripts section)

## Enhancement Details

### LOCAL Enhancement (Recommended)
- Uses your Claude Code Max plan (no API costs)
- Opens new terminal with Claude Code
- Analyzes reference files automatically
- Takes 30-60 seconds
- Quality: 9/10 (comparable to API version)
- Backs up original SKILL.md to SKILL.md.backup

### API Enhancement (Alternative)
- Uses Anthropic API (~$0.15-$0.30 per skill)
- Requires ANTHROPIC_API_KEY
- Same quality as LOCAL
- Faster (no terminal launch)
- Better for automation/CI

**What Enhancement Does:**
1. Reads reference documentation files
2. Analyzes content with Claude
3. Extracts 5-10 best code examples
4. Creates comprehensive quick reference
5. Adds domain-specific key concepts
6. Provides navigation guidance for different skill levels
7. Transforms 75-line templates into 500+ line comprehensive guides

## Performance

| Task | Time | Notes |
|------|------|-------|
| Scraping | 15-45 min | First time only |
| Building | 1-3 min | Fast! |
| Re-building | <1 min | With --skip-scrape |
| Enhancement (LOCAL) | 30-60 sec | Uses Claude Code Max |
| Enhancement (API) | 20-40 sec | Requires API key |
| Packaging | 5-10 sec | Final zip |

## Available Configs (24 Total)

### Single-Source Documentation Configs (14 configs)

**Web Frameworks:**
- ✅ `react.json` - React (article selector, 7,102 chars)
- ✅ `vue.json` - Vue.js (main selector, 1,029 chars)
- ✅ `astro.json` - Astro (article selector, 145 chars)
- ✅ `django.json` - Django (article selector, 6,468 chars)
- ✅ `laravel.json` - Laravel 9.x (#main-content selector, 16,131 chars)
- ✅ `fastapi.json` - FastAPI (article selector, 11,906 chars)
- ✅ `hono.json` - Hono web framework **NEW!**

**DevOps & Automation:**
- ✅ `ansible-core.json` - Ansible Core 2.19 (div[role='main'] selector, ~32K chars)
- ✅ `kubernetes.json` - Kubernetes (main selector, 2,100 chars)

**Game Engines:**
- ✅ `godot.json` - Godot (div[role='main'] selector, 1,688 chars)
- ✅ `godot-large-example.json` - Godot large docs example

**CSS & Utilities:**
- ✅ `tailwind.json` - Tailwind CSS (div.prose selector, 195 chars)

**Gaming:**
- ✅ `steam-economy-complete.json` - Steam Economy (div.documentation_bbcode, 588 chars)

**Development Tools:**
- ✅ `claude-code.json` - Claude Code documentation **NEW!**

### Unified Multi-Source Configs (5 configs - **NEW v2.0!**)
- ⚠️ `react_unified.json` - React (docs + GitHub + code analysis)
- ⚠️ `django_unified.json` - Django (docs + GitHub + code analysis)
- ⚠️ `fastapi_unified.json` - FastAPI (docs + GitHub + code analysis)
- ⚠️ `fastapi_unified_test.json` - FastAPI test config
- ⚠️ `godot_unified.json` - Godot (docs + GitHub + code analysis)

### Test/Example Configs (5 configs)
- 📝 `godot_github.json` - GitHub-only scraping example
- 📝 `react_github.json` - GitHub-only scraping example
- 📝 `python-tutorial-test.json` - Python tutorial test
- 📝 `example_pdf.json` - PDF extraction example
- 📝 `test-manual.json` - Manual testing config

**Note:** ⚠️ = Unified configs have 12 failing tests that need fixing
**Last verified:** November 11, 2025 (v2.0.0 PyPI release)

## Additional Documentation

**User Guides:**
- **[README.md](README.md)** - Complete user documentation
- **[BULLETPROOF_QUICKSTART.md](BULLETPROOF_QUICKSTART.md)** - Complete beginner guide
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Comprehensive troubleshooting

**Technical Documentation:**
- **[docs/CLAUDE.md](docs/CLAUDE.md)** - Detailed technical architecture
- **[docs/ENHANCEMENT.md](docs/ENHANCEMENT.md)** - AI enhancement guide
- **[docs/UPLOAD_GUIDE.md](docs/UPLOAD_GUIDE.md)** - How to upload skills to Claude
- **[docs/UNIFIED_SCRAPING.md](docs/UNIFIED_SCRAPING.md)** - Multi-source scraping guide
- **[docs/MCP_SETUP.md](docs/MCP_SETUP.md)** - MCP server setup

**Project Planning:**
- **[CHANGELOG.md](CHANGELOG.md)** - Release history and v2.0.0 details **UPDATED!**
- **[FUTURE_RELEASES.md](FUTURE_RELEASES.md)** - Roadmap for v2.1.0+  **NEW!**
- **[FLEXIBLE_ROADMAP.md](FLEXIBLE_ROADMAP.md)** - Complete task catalog (134 tasks)
- **[NEXT_TASKS.md](NEXT_TASKS.md)** - What to work on next
- **[TODO.md](TODO.md)** - Current focus
- **[STRUCTURE.md](STRUCTURE.md)** - Repository structure
>>>>>>> upstream/development

## Project Status

<<<<<<< HEAD
- **Active Development**: Yes, task-based incremental approach
- **Production Ready**: Yes, v2.0.0 with unified scraping
- **Test Coverage**: 299 tests, 100% pass rate
- **MCP Integration**: Fully functional with 9 tools
- **Documentation**: Comprehensive guides and examples

The project is actively maintained with a flexible roadmap approach. See [FLEXIBLE_ROADMAP.md](FLEXIBLE_ROADMAP.md) for planned features and development tasks.
=======
**Project Status (v2.0.0):**
- ✅ **Published on PyPI**: Install with `pip install skill-seekers`
- ✅ **Modern Python Packaging**: pyproject.toml, src/ layout, entry points
- ✅ **Unified CLI**: Single `skill-seekers` command with Git-style subcommands
- ✅ **CI/CD Working**: All 5 test matrix jobs passing (Ubuntu + macOS, Python 3.10-3.12)
- ✅ **Test Coverage**: 379 tests passing, 39% coverage
- ✅ **Documentation**: Complete user and technical documentation

**Architecture:**
- **Python-based documentation scraper** with multi-source support
- **Main scraper**: `src/skill_seekers/cli/doc_scraper.py` (~790 lines)
- **Unified scraping**: Combines docs + GitHub + PDF with conflict detection
- **Modern packaging**: PEP 621 compliant with proper dependency management
- **MCP Integration**: 9 tools for Claude Code Max integration

**Development Workflow:**
1. **Install**: `pip install -e .` (editable mode for development)
2. **Run tests**: `pytest tests/` (379 tests)
3. **Build package**: `uv build` or `python -m build`
4. **Publish**: `uv publish` (PyPI)

**Key Points:**
- Output is cached and reusable in `output/` (git-ignored)
- Enhancement is optional but highly recommended
- All 24 configs are working and tested
- CI workflow requires `pip install -e .` to install package before running tests
>>>>>>> upstream/development
