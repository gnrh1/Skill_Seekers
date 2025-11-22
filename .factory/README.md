# Factory Configuration for Skill_Seekers

This directory contains the Factory Droid configuration for the Skill_Seekers repository, implementing a comprehensive development environment optimized for AI-assisted development.

## Structure

```
.factory/
├── droids/                    # Specialized AI droids (agents)
│   ├── scraper-expert.md      # Documentation scraping specialist
│   ├── test-engineer.md       # Test generation & validation
│   ├── mcp-specialist.md      # MCP server integration expert
│   └── security-guardian.md   # Security & secrets detection
├── commands/                  # Custom workflow commands
│   ├── scrape-docs.md        # End-to-end scraping workflow
│   └── run-tests.md          # Intelligent test execution
├── memory/                    # Persistent context
│   ├── tech-stack.md         # Technology stack documentation
│   └── patterns.md           # Code patterns & conventions
├── scripts/                   # Validation & automation scripts
│   └── validate_execution.py # Pre-execution command validation
├── docs/                      # Specification mode outputs
└── README.md                 # This file
```

## Root-Level Configuration

**AGENTS.md** (repository root)
- Primary agent configuration for the entire project
- Defines development role, tech stack, commands, and boundaries
- 441 lines of comprehensive guidance

**.droid.yaml** (repository root)
- Code review automation configuration
- Security scanning patterns
- Workflow definitions
- Testing requirements

## Droids (Specialized Agents)

### @scraper-expert
**File:** `droids/scraper-expert.md`

**Specialization:**
- BeautifulSoup selector engineering
- Async/await optimization (3x speed, 66% memory)
- llms.txt detection (10x faster than HTML)
- Multi-source conflict detection

**Use for:** Scraping issues, CSS selector problems, performance optimization

**Invoke:** `@scraper-expert analyze cli/doc_scraper.py`

### @test-engineer
**File:** `droids/test-engineer.md`

**Specialization:**
- Maintaining 299 tests with 100% pass rate
- Pytest fixtures and mocking
- Test coverage optimization
- CI/CD integration

**Use for:** Test generation, fixing failing tests, coverage analysis

**Invoke:** `@test-engineer create tests for cli/github_scraper.py`

### @mcp-specialist
**File:** `droids/mcp-specialist.md`

**Specialization:**
- 9 MCP tools for Claude Code
- Natural language interfaces
- Error handling patterns
- Tool parameter validation

**Use for:** MCP integration issues, adding new tools, testing MCP server

**Invoke:** `@mcp-specialist review skill_seeker_mcp/server.py`

### @security-guardian
**File:** `droids/security-guardian.md`

**Specialization:**
- Secret detection (API keys, tokens)
- Secure coding practices
- Git history scanning
- Pre-commit validation

**Use for:** Security audits, secret leak prevention, code review

**Invoke:** `@security-guardian scan for secrets`

## Commands (Workflow Automation)

### /validate-droids
**File:** `commands/validate-droids.md`

**Purpose:** Comprehensive validation of Factory Droid configuration

**Validates:**
- AGENTS.md and .droid.yaml syntax
- Droid YAML frontmatter (name, description, etc.)
- Command parameter definitions
- Memory file structure
- Overall configuration health

**Usage:**
```bash
/validate-droids                    # Quick validation
/validate-droids --verbose         # Detailed per-file output
```

**Example Output:**
```
🔍 Factory Droid Validation Report
Root Configuration: ✅
Factory Structure: ✅
Droids: ✅ 4/4 valid
Commands: ✅ 3/3 valid
Memory: ✅ 2/2 valid
Overall Health: 🟢 Excellent (100%)
```

**See Also:** `.factory/commands/validate-droids.md` for detailed documentation

### /scrape-docs
**File:** `commands/scrape-docs.md`

**Workflow:**
1. Validate configuration
2. Estimate page count (optional)
3. Scrape documentation
4. Enhance SKILL.md with AI
5. Package into .zip

**Parameters:**
- `config` (required): Path to config file
- `enhance` (default: true): AI enhancement
- `estimate-first` (default: true): Estimate before scraping
- `async-mode` (default: false): Use async scraping

**Example:**
```bash
/scrape-docs --config configs/react.json --async-mode true
```

### /run-tests
**File:** `commands/run-tests.md`

**Functionality:**
- Execute test suites (all, config, features, integration, mcp)
- Colored output with failure analysis
- Automatic diagnosis and suggestions

**Parameters:**
- `suite` (default: all): Test suite to run
- `verbose` (default: false): Verbose output

**Example:**
```bash
/run-tests --suite mcp --verbose true
```

## Memory (Persistent Context)

### tech-stack.md
**Purpose:** Technology stack documentation for Factory's Context Stack

**Contains:**
- Core dependencies (Python 3.10+, requests, beautifulsoup4, pytest)
- Optional features (anthropic, PyGithub, PyMuPDF)
- Architecture decisions (async-first, llms.txt priority, single-file design)
- Performance characteristics
- Version history

**Why:** Ensures Factory Droid has consistent understanding of project tech without re-analyzing

### patterns.md
**Purpose:** Code patterns and conventions reference

**Contains:**
- Async scraping patterns
- Error handling patterns
- Configuration patterns
- Logging patterns
- Testing patterns
- File operations patterns
- Type hints patterns

**Why:** Provides executable code examples for Factory Droid to follow project style

## Scripts (Automation)

### validate_execution.py
**Purpose:** Pre-execution command validation

**Checks:**
- Secret patterns (API keys, tokens)
- Virtual environment activation
- Destructive operations (rm -rf, git push --force)

**Integration:** Called by PreToolUse hooks in `.claude/settings.json`

**Result:**
- `block` → Prevents execution (secrets detected)
- `warn` → Allows with warning (missing venv)
- `approve` → Executes normally

## How It Works

### Context Stack Integration

Factory Droid uses a layered Context Stack to manage information:

1. **Memory Context** (persistent)
   - User preferences
   - Organization standards
   - Technology stack (`.factory/memory/tech-stack.md`)
   - Code patterns (`.factory/memory/patterns.md`)

2. **Repository Overviews** (generated)
   - Project structure
   - Key packages
   - Build commands
   - Architectural info

3. **Semantic Search** (ByteRank)
   - Vector embeddings optimized for code
   - Ranked file lists by relevance
   - Folder summaries

4. **Dynamic File Access**
   - Targeted retrieval of specific files
   - Line numbers and diffs
   - Runtime context (test results, linter output)

### Droid Discovery

Factory Droid automatically discovers and loads:

**Project-Level:**
- `.factory/droids/*.md` → Shared team droids
- `.factory/commands/*.md` → Workflow commands
- `.factory/memory/*.md` → Persistent context
- `AGENTS.md` (root) → Primary agent configuration

**User-Level:**
- `~/.factory/droids/*.md` → Personal droids
- `~/.factory/AGENTS.md` → Personal overrides

### Execution Flow

**Example: User asks to fix scraper bug**

1. **Task Analysis:** Factory Droid parses request
2. **Context Stack:**
   - Loads `AGENTS.md` (project guidelines)
   - Loads `.factory/memory/tech-stack.md` (Python 3.10+, async patterns)
   - Loads `.factory/memory/patterns.md` (async scraping examples)
3. **Semantic Search:** Finds relevant files (`cli/doc_scraper.py`)
4. **Droid Consultation:** May invoke `@scraper-expert` for specialized help
5. **Validation:** `validate_execution.py` checks commands before running
6. **Execution:** Runs tests via `/run-tests` to verify fix

## Usage Examples

### Invoke Specialist Droid

```bash
# In Factory Droid CLI or interface
@scraper-expert analyze async performance in cli/doc_scraper.py

@test-engineer generate tests for cli/unified_scraper.py

@security-guardian check for hardcoded secrets in skill_seeker_mcp/

@mcp-specialist add new tool for PDF extraction
```

### Execute Workflow Command

```bash
# Automated workflows
/scrape-docs --config configs/django.json --async-mode true

/run-tests --suite integration

/validate-config configs/new-framework.json
```

### Query Memory Context

Factory Droid automatically references memory files when relevant:

- "What's the async scraping pattern?" → Loads `.factory/memory/patterns.md`
- "What Python version do we use?" → Loads `.factory/memory/tech-stack.md`
- "How do we handle errors?" → Loads patterns and AGENTS.md boundaries

## Benefits

### For Developers

1. **Consistent Guidance:** All developers get same high-quality AI assistance
2. **Faster Onboarding:** New team members learn patterns from droids
3. **Security Enforcement:** Automatic secret detection prevents leaks
4. **Quality Assurance:** Tests run automatically, pre-commit validation

### For Factory Droid

1. **Context Efficiency:** Persistent memory reduces token usage
2. **Specialized Expertise:** Droids provide domain-specific knowledge
3. **Workflow Automation:** Commands reduce repetitive tasks
4. **Deterministic Behavior:** Structured Markdown → executable configuration

### For the Project

1. **Code Quality:** Enforced patterns and testing standards
2. **Security:** Proactive secret detection and scanning
3. **Velocity:** Automated workflows save time
4. **Knowledge Preservation:** Team knowledge captured in droids

## Maintenance

### Adding New Droids

1. Create `droids/my-droid.md` with YAML frontmatter
2. Define specialization and core files
3. Add commands, standards, and boundaries
4. Test with `@my-droid` invocation

### Adding New Commands

1. Create `commands/my-command.md` with parameters
2. Define workflow steps and error handling
3. Add usage examples
4. Test with `/my-command` invocation

### Updating Memory

1. Edit `memory/tech-stack.md` when dependencies change
2. Edit `memory/patterns.md` when adding new code patterns
3. Commit changes to version control
4. Factory Droid will use updated context in next session

## Integration with Existing .claude/

The `.factory/` configuration **complements** the existing `.claude/` structure:

**`.claude/` (Claude Code specific):**
- `agents/` → Claude Code agents (orchestrator, specialists)
- `commands/` → Claude Code commands (create-agent, refine-agent)
- `hooks/` → Pre/Post tool use hooks
- `settings.json` → Claude Code configuration

**`.factory/` (Factory Droid specific):**
- `droids/` → Factory droids (scraper-expert, test-engineer)
- `commands/` → Factory commands (scrape-docs, run-tests)
- `memory/` → Persistent context (tech-stack, patterns)
- `scripts/` → Validation scripts

Both systems can coexist and provide complementary functionality.

## Success Metrics

After implementing Factory configuration:

1. **Context Efficiency:** 80%+ queries resolved without generic responses
2. **Security:** Zero secrets committed (validated by hooks)
3. **Workflow Speed:** 30%+ faster for common tasks
4. **Developer Experience:** < 30 min onboarding for new contributors
5. **Reliability:** All 299 tests pass, pre-commit hooks prevent regressions

## Troubleshooting

### Droids Not Found

**Issue:** `@scraper-expert` not recognized

**Fix:** Ensure `.factory/droids/scraper-expert.md` exists and has valid YAML frontmatter

### Commands Not Working

**Issue:** `/scrape-docs` not recognized

**Fix:** Check `.factory/commands/scrape-docs.md` has parameters section in frontmatter

### Memory Not Loading

**Issue:** Factory Droid doesn't seem to know tech stack

**Fix:** Verify `.factory/memory/tech-stack.md` exists and contains current information

### Validation Script Errors

**Issue:** `validate_execution.py` blocking legitimate commands

**Fix:** Review script logic, add exception patterns if needed

## See Also

- **AGENTS.md** (root) - Primary agent configuration
- **.droid.yaml** (root) - Review and workflow automation
- **CLAUDE.md** - Technical architecture documentation
- **docs/LARGE_DOCUMENTATION.md** - Handling massive docs
- **ASYNC_SUPPORT.md** - Async scraping guide

## Questions?

This configuration implements the robust Factory setup described in the specification. For details on the design decisions, see:

- `AGENTS_md_guideline` - Six core areas for agent definitions
- `droid_plan_2` - Factory Context Stack architecture
- Specification: `~/.factory/specs/2025-11-21-robust-factory-configuration-for-skill_seekers-repository.md`
