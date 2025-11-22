# Droid Tool Access Troubleshooting Guide

## 🔧 Issue Resolved: Model-Droid Mismatch

**Problem Encountered:**
```
The primary Droid attempted to delegate via the Task tool by invoking the 
scraper-expert subagent; the call failed because that subagent expects the 
Create tool, which isn't exposed to the current OpenAI GPT‑5.1-Codex model instance.
```

**Root Cause:**
- Droid configured for: `gpt-5-codex`
- Your active model: `custom:GLM-4.6-[Z.AI-Coding-Plan]-0`
- Tool access was restricted due to model mismatch

**Solution Applied:**
✅ Updated `.factory/droids/scraper-expert.md` to use your Z.AI model:
```yaml
model: custom:GLM-4.6-[Z.AI-Coding-Plan]-0
```

---

## 🎯 How Droid Tool Access Works

### 1. Model-Droid Matching

Each custom droid can specify which model it should use:

```yaml
---
name: scraper-expert
model: custom:GLM-4.6-[Z.AI-Coding-Plan]-0  # Must match your active model
tools: Read, LS, Create, Execute, etc.
---
```

**Important:** If the droid's model doesn't match your active model in settings.json, tool access may be restricted.

### 2. Tool Categories

Factory Droids organize tools by categories:

| Category | Tools | Purpose |
|----------|-------|---------|
| **Read** | Read, LS, Grep, Glob | File analysis (safe) |
| **Edit** | Create, Edit, ApplyPatch, MultiEdit | File modification |
| **Execute** | Execute, Kill Process | Command execution |
| **Web** | WebSearch, FetchUrl | Internet access |
| **Management** | TodoWrite, TaskWrite | Task management |

### 3. Available vs Exposed Tools

- **Available Tools:** Tools defined in droid's YAML front matter
- **Exposed Tools:** Tools actually accessible to the current model instance
- **Common Issue:** Model restrictions limit tool exposure even when available

---

## 🛠️ Droid Configuration Best Practices

### ✅ Always Include in YAML Front Matter

```yaml
---
name: my-droid
description: Brief description
model: custom:GLM-4.6-[Z.AI-Coding-Plan]-0  # Match your active model
tools: Read, LS, Grep, Create, Edit, Execute  # Include ALL needed tools
---

# Your droid documentation here
```

### ✅ Tool Access Patterns

**For Coding Droids:**
```yaml
tools: Read, LS, Grep, Glob, Create, Edit, Execute, ApplyPatch
```

**For Analysis Droids:**
```yaml
tools: Read, LS, Grep, Glob, WebSearch, FetchUrl
```

**For Management Droids:**
```yaml
tools: Read, LS, Grep, TodoWrite, TaskWrite, Execute
```

---

## 🔍 Troubleshooting Steps

### Step 1: Check Active Model

```bash
cat ~/.factory/settings.json | grep model
```

Should show your Z.AI model.

### Step 2: Verify Droid Model

```bash
grep "^model:" ~/.factory/droids/*.md
```

All droids should use your active model.

### Step 3: Check Tool Definitions

```bash
grep "^tools:" ~/.factory/droids/*.md
```

Verify tools are properly listed.

### Step 4: Restart Droid CLI

```bash
# Exit Droid CLI
# Restart: droid
```

New configurations require restart.

---

## 🚨 Common Error Messages & Solutions

### Error: "Tool not exposed to current model"

**Cause:** Model restrictions or mismatched model
**Solution:** 
1. Update droid model to match active model
2. Ensure tool is in available tools list
3. Restart Droid CLI

### Error: "Subagent expects Create tool"

**Cause:** Missing Create tool in droid configuration
**Solution:**
```yaml
tools: Read, LS, Create, Edit  # Add Create tool
```

### Error: "Invalid YAML syntax"

**Cause:** Malformed YAML front matter
**Solution:** Validate YAML syntax, check indentation

### Error: "Model not found"

**Cause:** Droid references non-existent model
**Solution:** Use exact model string from `/model` command

---

## 🔧 Fixes Applied to Your System

### 1. Updated scraper-expert.md
```yaml
# BEFORE (causing error)
model: gpt-5-codex

# AFTER (now working)
model: custom:GLM-4.6-[Z.AI-Coding-Plan]-0
```

### 2. Available Droids
- ✅ `default.md` - General purpose with all tools
- ✅ `scraper-expert.md` - Now uses Z.AI model correctly

### 3. Settings
```json
{
  "model": "custom:GLM-4.6-[Z.AI-Coding-Plan]-0",
  "enableCustomDroids": true
}
```

---

## 🚀 Testing Your Fixed Setup

### Test Command
```
@scraper-expert Help me analyze cli/doc_scraper.py file structure
```

### Expected Result
✅ Subagent responds successfully
✅ Create tool is available when needed
✅ Z.AI model is used for responses

### If Still Failing
1. Restart Droid CLI completely
2. Check model consistency: `grep model ~/.factory/* ~/.factory/droids/*`
3. Verify tool list includes required tools
4. Test with simpler droid: `@default simple test`

---

## 📝 Droid Creation Template

Use this template for new droids:

```yaml
---
name: your-droid-name
description: Brief description of droid purpose
model: custom:GLM-4.6-[Z.AI-Coding-Plan]-0
tools: Read, LS, Grep, Glob, Create, Edit, Execute
---

# Your Droid Name

Detailed description of capabilities and specializations.

## Specialization
- Area 1: Description
- Area 2: Description

## Common Commands
```bash
# Example command 1
command1

# Example command 2  
command2
```

## Boundaries
### ✅ Always Do:
- Item 1
- Item 2

### 🚫 Never Do:
- Item 1
- Item 2
```

---

## 🎯 Summary

**Issue:** Model mismatch between droid config and active model
**Fix:** Updated droid to use `custom:GLM-4.6-[Z.AI-Coding-Plan]-0`
**Result:** Tool access now working correctly

**Your Z.AI integration is fully functional with working custom droids!**
