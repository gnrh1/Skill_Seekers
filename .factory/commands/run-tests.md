---
name: run-tests
description: Intelligent test execution with suite selection, coverage reporting, and failure analysis.
parameters:
  - name: suite
    type: string
    enum: [all, config, features, integration, mcp]
    default: all
    description: Test suite to run
  - name: verbose
    type: boolean
    default: false
    description: Enable verbose output
---

# Run Tests Command

Smart test runner with colored output, suite selection, and automatic failure diagnosis.

## Overview

Executes the Skill_Seekers test suite (299 tests) with intelligent reporting and failure analysis.

## Usage

```bash
# Run all tests (299 tests)
/run-tests

# Run specific suite
/run-tests --suite config
/run-tests --suite features
/run-tests --suite integration
/run-tests --suite mcp

# Verbose output for debugging
/run-tests --suite features --verbose true
```

## Execution

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run test runner
python3 cli/run_tests.py --suite {suite} {--verbose if verbose}
```

## Test Suites

### All (Default)

**Contains:** All 299 tests across all categories

**Use when:** Running full validation before commits

**Duration:** 2-5 minutes

```bash
/run-tests
# or
python3 cli/run_tests.py
```

### Config Suite

**Contains:** Configuration validation tests
- JSON parsing
- Required field validation
- Selector format checking
- URL pattern validation

**Use when:** Working on configuration system

**Duration:** 30-60 seconds

```bash
/run-tests --suite config
```

### Features Suite

**Contains:** Core feature tests
- Scraping functionality
- Async operations
- Selector testing
- Categorization logic

**Use when:** Working on scraper features

**Duration:** 1-2 minutes

```bash
/run-tests --suite features
```

### Integration Suite

**Contains:** End-to-end workflow tests
- Full scrape-build-package workflow
- Multi-source integration
- Conflict detection

**Use when:** Testing complete workflows

**Duration:** 2-3 minutes

```bash
/run-tests --suite integration
```

### MCP Suite

**Contains:** MCP server tests
- All 9 MCP tools
- Tool parameter validation
- Error handling

**Use when:** Working on MCP integration

**Duration:** 1-2 minutes

```bash
/run-tests --suite mcp
```

## Output Format

**Successful run:**
```
🧪 Running Skill_Seekers Test Suite
📋 Suite: all (299 tests)

⏳ Executing tests...

✅ test_config_validation.py ........................... 28 passed
✅ test_scraper_features.py ............................ 45 passed
✅ test_async_scraping.py .............................. 32 passed
✅ test_mcp_server.py .................................. 21 passed
✅ test_github_scraper.py .............................. 38 passed
✅ test_pdf_scraper.py ................................. 29 passed
✅ test_integration.py ................................. 42 passed
... (remaining test files)

📊 Summary
   Total: 299 tests
   Passed: 299 ✅
   Failed: 0
   Skipped: 0
   Duration: 3.2 minutes

🎉 All tests passed!
```

**Failed run:**
```
🧪 Running Skill_Seekers Test Suite
📋 Suite: features (77 tests)

⏳ Executing tests...

✅ test_scraper_features.py::test_basic_scraping .......... PASSED
✅ test_scraper_features.py::test_async_scraping .......... PASSED
❌ test_scraper_features.py::test_selector_validation ..... FAILED

📋 Failure Details:

test_scraper_features.py::test_selector_validation
  AssertionError: Expected valid selector, got None
  
  File: tests/test_scraper_features.py, line 145
  Code: assert scraper.validate_selector('article') is True
  
  💡 Suggestion: Check if BeautifulSoup is parsing HTML correctly

... (remaining failures)

📊 Summary
   Total: 77 tests
   Passed: 75 ✅
   Failed: 2 ❌
   Skipped: 0
   Duration: 1.8 minutes

❌ Tests failed! Fix failures before committing.
```

## Failure Handling

### Automatic Diagnosis

When tests fail, the command analyzes failures and provides suggestions:

**Import errors:**
```
💡 Suggestion: Install missing dependency
   Run: pip install missing-package
```

**Virtual environment issues:**
```
💡 Suggestion: Virtual environment not activated
   Run: source venv/bin/activate
```

**File not found errors:**
```
💡 Suggestion: Test fixture missing
   Check: tests/fixtures/ directory
```

**Assertion errors:**
```
💡 Suggestion: Logic change may have broken test
   Review: Recent changes to tested function
```

### Manual Debugging

**Run single failing test:**
```bash
pytest tests/test_scraper_features.py::test_selector_validation -vv
```

**Show local variables:**
```bash
pytest tests/test_scraper_features.py::test_failing -vv -l
```

**Drop into debugger:**
```bash
pytest tests/test_scraper_features.py::test_failing --pdb
```

**Show print statements:**
```bash
pytest tests/test_scraper_features.py -s
```

## Common Issues & Solutions

### Issue: Tests Fail with Import Errors

**Error:** `ModuleNotFoundError: No module named 'requests'`

**Diagnosis:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate venv
source venv/bin/activate

# Verify activation
which python3  # Should show venv path

# Install dependencies
pip install -r requirements.txt

# Retry tests
/run-tests
```

### Issue: Tests Fail But Work Locally

**Error:** Tests pass on your machine, fail in CI or for others

**Common Causes:**
- Hardcoded file paths
- Timing assumptions
- Missing test fixtures
- Platform differences (macOS vs Linux)

**Solution:**
```python
# Bad - hardcoded path
def test_output():
    assert os.path.exists("/tmp/output.txt")

# Good - use fixtures
def test_output(tmp_path):
    output_file = tmp_path / "output.txt"
    assert output_file.exists()
```

### Issue: Tests Are Slow

**Symptom:** Test suite takes > 10 minutes

**Diagnosis:**
```bash
# Find slow tests
pytest tests/ --durations=10
```

**Solution:**
1. Mock external API calls
2. Use appropriate fixture scope
3. Parallelize: `pytest tests/ -n auto`

### Issue: Flaky Tests

**Symptom:** Tests pass sometimes, fail other times

**Common Causes:**
- Race conditions in async code
- Timing dependencies
- Shared state between tests

**Solution:**
```python
# Bad - timing dependent
def test_async():
    start_task()
    time.sleep(0.1)
    assert complete()

# Good - deterministic
@pytest.mark.asyncio
async def test_async():
    result = await run_task()
    assert result == expected
```

## Pre-Commit Checklist

Before committing code:
- [ ] All tests pass: `/run-tests`
- [ ] No new warnings or errors
- [ ] Virtual environment activated
- [ ] Dependencies up to date
- [ ] Test coverage maintained or improved

## Performance Targets

| Suite | Target Duration | Tests | Notes |
|-------|----------------|-------|-------|
| all | < 5 min | 299 | Full suite |
| config | < 1 min | ~30 | Fast validation |
| features | < 2 min | ~80 | Core features |
| integration | < 3 min | ~50 | End-to-end |
| mcp | < 2 min | ~25 | MCP tools |

## Related Commands

- `/scrape-docs` - Run scraping workflow (requires tests to pass)
- Check git hooks for automatic test execution

## See Also

- **Testing Guide:** `docs/TESTING.md`
- **Contributing:** `CONTRIBUTING.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`
