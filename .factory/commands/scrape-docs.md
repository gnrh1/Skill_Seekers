---
name: scrape-docs
description: End-to-end documentation scraping workflow with validation, estimation, scraping, enhancement, and packaging.
parameters:
  - name: config
    type: string
    required: true
    description: Path to config file (e.g., configs/react.json)
  - name: enhance
    type: boolean
    default: true
    description: Enhance SKILL.md with AI (local mode, no API key)
  - name: estimate-first
    type: boolean
    default: true
    description: Estimate pages before scraping
  - name: async-mode
    type: boolean
    default: false
    description: Use async scraping (3x faster for 200+ pages)
---

# Scrape Docs Command

Orchestrated workflow for documentation scraping from config validation through final packaging.

## Overview

This command automates the complete workflow for creating a Claude AI skill from documentation:

1. **Validate Config** - Ensure configuration is valid
2. **Estimate Pages** (optional) - Preview page count and scraping time
3. **Scrape Documentation** - Extract all documentation pages
4. **Enhance Skill** (optional) - Generate comprehensive SKILL.md with AI
5. **Package Skill** - Create uploadable .zip file

## Workflow Steps

### Step 1: Validate Configuration

```bash
python3 cli/config_validator.py {config}
```

**Checks:**
- JSON syntax valid
- Required fields present (name, base_url, description)
- Selectors properly formatted
- URL patterns valid regex
- Rate limiting reasonable

**On Error:** Stop workflow, show validation errors

### Step 2: Estimate Pages (Optional)

```bash
python3 cli/estimate_pages.py {config}
```

**Benefits:**
- Know page count before committing to full scrape
- Validate URL patterns actually work
- Estimate total scraping time
- Recommend optimal max_pages setting

**Takes:** 1-2 minutes for most documentation sites

**Skip if:** Documentation is known to be small (< 100 pages)

### Step 3: Scrape Documentation

```bash
# Basic scraping
python3 cli/doc_scraper.py --config {config}

# With async mode (recommended for 200+ pages)
python3 cli/doc_scraper.py --config {config} --async --workers 8

# With local enhancement (recommended)
python3 cli/doc_scraper.py --config {config} --enhance-local
```

**Duration:** 15-45 minutes depending on size and async mode

**Output:** `output/{name}_data/` with scraped JSON files

### Step 4: Build Skill

```bash
# Build from existing data
python3 cli/doc_scraper.py --config {config} --skip-scrape

# Build with enhancement
python3 cli/enhance_skill_local.py output/{name}/
```

**Duration:** 1-3 minutes (build) + 30-60 seconds (enhancement)

**Output:** `output/{name}/` with SKILL.md and references/

### Step 5: Package Skill

```bash
python3 cli/package_skill.py output/{name}/
```

**Duration:** 5-10 seconds

**Output:** `output/{name}.zip` ready for upload to Claude

## Usage Examples

### Basic Usage

```bash
# Full workflow with defaults
/scrape-docs --config configs/react.json

# This runs:
# 1. Validates configs/react.json
# 2. Estimates page count
# 3. Scrapes documentation
# 4. Enhances SKILL.md locally
# 5. Packages react.zip
```

### Skip Estimation (Faster)

```bash
# Skip estimation for small docs
/scrape-docs --config configs/vue.json --estimate-first false

# Saves 1-2 minutes, useful for known small sites
```

### Skip Enhancement (Faster, Basic SKILL.md)

```bash
# No AI enhancement, uses template
/scrape-docs --config configs/godot.json --enhance false

# Saves 30-60 seconds, but SKILL.md will be basic
```

### Async Mode (Faster for Large Docs)

```bash
# Enable async scraping for 200+ pages
/scrape-docs --config configs/react.json --async-mode true

# 3x faster than sync mode, 66% less memory
```

### All Options Combined

```bash
# Fast workflow for large docs
/scrape-docs \
  --config configs/django.json \
  --estimate-first false \
  --async-mode true \
  --enhance true
```

## Error Handling

### Config Invalid

**Error:** Configuration validation fails

**Response:**
- Show specific validation errors
- Suggest fixes based on error type
- Do not proceed with scraping

**Fix:**
```bash
# Edit config to fix issues
nano configs/react.json

# Re-run validation
python3 cli/config_validator.py configs/react.json

# Retry command
/scrape-docs --config configs/react.json
```

### Estimation Shows > 10K Pages

**Warning:** Large documentation detected

**Response:**
- Warn user about long scraping time (1-2 hours)
- Suggest using split_config for better results
- Ask user to confirm before proceeding

**Alternative:**
```bash
# Split large docs into focused sub-skills
python3 cli/split_config.py configs/godot.json --strategy router

# Scrape sub-skills in parallel
python3 cli/doc_scraper.py --config configs/godot-scripting.json &
python3 cli/doc_scraper.py --config configs/godot-2d.json &
python3 cli/doc_scraper.py --config configs/godot-3d.json &
wait
```

### Scraping Fails Mid-Way

**Error:** Network error, timeout, or interruption (Ctrl+C)

**Response:**
- Preserve partial data in output/{name}_data/
- Suggest resuming from checkpoint

**Recovery:**
```bash
# Resume from last checkpoint
python3 cli/doc_scraper.py --config configs/react.json --resume

# Skips already-scraped pages, continues from where stopped
```

### Enhancement Fails

**Error:** Claude Code Max plan not available, or API error

**Response:**
- Continue without enhancement (use basic template)
- Log warning about using basic SKILL.md
- Suggest manual enhancement later

**Fix:**
```bash
# Enhance separately after scraping completes
python3 cli/enhance_skill_local.py output/react/

# Or use API-based enhancement (requires API key)
export ANTHROPIC_API_KEY=sk-ant-...
python3 cli/enhance_skill.py output/react/
```

## Performance Tips

### For Small Docs (< 200 pages)

```bash
# Use defaults, skip estimation
/scrape-docs --config configs/small-docs.json --estimate-first false

# Expected time: 5-10 minutes total
```

### For Medium Docs (200-1000 pages)

```bash
# Enable async mode for speed
/scrape-docs --config configs/medium-docs.json --async-mode true

# Expected time: 10-20 minutes total
```

### For Large Docs (1000-10000 pages)

```bash
# Estimate first to confirm size
/scrape-docs --config configs/large-docs.json --estimate-first true

# If > 2000 pages, use async mode
/scrape-docs --config configs/large-docs.json --async-mode true

# Expected time: 30-60 minutes total
```

### For Massive Docs (> 10000 pages)

```bash
# DO NOT USE THIS COMMAND - Use split workflow instead

# 1. Split into sub-skills
python3 cli/split_config.py configs/massive-docs.json --strategy router

# 2. Scrape sub-skills in parallel
for config in configs/massive-docs-*.json; do
  python3 cli/doc_scraper.py --config $config --async &
done
wait

# 3. Generate router skill
python3 cli/generate_router.py configs/massive-docs-*.json

# Expected time: 2-4 hours total (parallelized)
```

## Command Output

**Successful execution outputs:**

```
✅ Step 1/5: Configuration validated
   - Name: react
   - Base URL: https://react.dev/
   - Max pages: 500

✅ Step 2/5: Page estimation complete
   - Pages discovered: 180
   - Estimated total: 230
   - Recommended max_pages: 280
   - Continue? (y/n): y

⏳ Step 3/5: Scraping documentation...
   - Mode: async (8 workers)
   - Rate limit: 0.5s
   - Progress: [=========>  ] 178/230 pages (77%)
   
✅ Step 3/5: Scraping complete
   - Total pages: 230
   - Time elapsed: 12.3 minutes
   - Output: output/react_data/

⏳ Step 4/5: Building skill...
   - Categorizing: 230 pages into 5 categories
   - Extracting: 47 code examples
   - Detecting: Python, JavaScript languages

⏳ Step 4/5: Enhancing SKILL.md (local mode)...
   - Claude Code Max will open in new terminal
   - Please review and confirm enhancement
   - Waiting for enhancement to complete...

✅ Step 4/5: Skill built and enhanced
   - SKILL.md: 542 lines (enhanced)
   - References: 5 categories, 230 pages
   - Output: output/react/

⏳ Step 5/5: Packaging skill...
   
✅ Step 5/5: Packaging complete
   - Package: output/react.zip (2.3 MB)
   - Upload to: https://claude.ai/skills

🎉 Skill creation complete!
   - Total time: 15.7 minutes
   - Output: output/react.zip
   - Next: Upload to Claude and start using!
```

## Quality Checklist

After command completes:
- [ ] output/{name}.zip exists
- [ ] SKILL.md is comprehensive (if enhanced)
- [ ] References organized by category
- [ ] No scraping errors in output
- [ ] Page count matches estimation (±10%)
- [ ] Package < 10 MB (if larger, consider splitting)
- [ ] Ready to upload to Claude

## Troubleshooting

### Command Hangs

**Symptom:** No output for > 5 minutes

**Possible Causes:**
- Network issue (check connection)
- Documentation site blocking (rate limit too aggressive)
- Large page taking long time to parse

**Fix:**
1. Press Ctrl+C to interrupt
2. Check logs in terminal
3. Increase rate_limit in config
4. Retry with --resume flag

### Out of Memory

**Symptom:** Python process killed, "Killed: 9" error

**Possible Causes:**
- Too many pages being processed at once
- Sync mode with large docs

**Fix:**
1. Enable async mode (66% less memory)
2. Reduce max_pages temporarily
3. Process in batches using split_config

### Slow Performance

**Symptom:** Taking > 1 hour for < 1000 pages

**Possible Causes:**
- Sync mode (should use async)
- rate_limit too conservative (0.1s or less)
- Network latency high

**Fix:**
1. Enable async mode: --async-mode true
2. Adjust rate_limit in config (try 0.3 or 0.2)
3. Check if llms.txt available (10x faster)

## Related Commands

- `/validate-config` - Validate configuration without scraping
- `/run-tests` - Run test suite to ensure system working
- `/package-skill` - Package existing skill directory

## See Also

- **Large Documentation Guide:** `docs/LARGE_DOCUMENTATION.md`
- **Async Support Guide:** `ASYNC_SUPPORT.md`
- **Enhancement Guide:** `docs/ENHANCEMENT.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`
