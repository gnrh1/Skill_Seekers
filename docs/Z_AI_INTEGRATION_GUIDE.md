# Z.AI GLM-4.6 Integration Guide for Factory Droid Platform

## Overview

This guide documents the integration of the Z.AI GLM-4.6 custom model into the Factory Droid platform using the Bring Your Own Key (BYOK) approach.

## Configuration Summary

**Model Details:**
- **Display Name:** Z.AI GLM-4.6 [Custom]
- **Model Identifier:** GLM-4.6
- **API Endpoint:** https://api.z.ai/api/coding/pass/v4
- **Provider Type:** OpenAI-compatible
- **Max Tokens:** 32,000 (optimized for agentic coding tasks)

## Integration Steps Completed

### ✅ Step 1: Verified Factory Droid CLI Installation
- **Location:** `/Users/docravikumar/.local/bin/droid`
- **Status:** Installed and accessible

### ✅ Step 2: Created Configuration Directory
- **Path:** `~/.factory/`
- **Status:** Directory created successfully

### ✅ Step 3: Created Configuration File
- **Path:** `~/.factory/config.json`
- **Status:** File created with Z.AI model configuration

## Next Steps (User Action Required)

### 🔑 Step 4: Add Your Z.AI API Key

**IMPORTANT:** You must add your actual Z.AI API key to the configuration file.

1. Open the configuration file:
   ```bash
   nano ~/.factory/config.json
   # or
   open -e ~/.factory/config.json  # macOS TextEdit
   # or
   code ~/.factory/config.json     # VS Code
   ```

2. Replace `YOUR_Z_AI_API_KEY_HERE` with your actual Z.AI API key:
   ```json
   {
     "custom_models": [
       {
         "model_display_name": "Z.AI GLM-4.6 [Custom]",
         "model": "GLM-4.6",
         "base_url": "https://api.z.ai/api/coding/pass/v4",
         "api_key": "your-actual-zai-api-key-here",
         "provider": "openai",
         "max_tokens": 32000
       }
     ]
   }
   ```

3. Save the file

**Security Note:** Your API key is stored locally only and is NOT uploaded to Factory servers.

### 🔄 Step 5: Activate the Model in Droid CLI

1. Start or restart the Droid CLI:
   ```bash
   droid
   ```

2. Inside the Droid CLI session, run:
   ```
   /model
   ```

3. Look for your model in the "Custom models" section:
   - **Z.AI GLM-4.6 [Custom]**

4. Select it to activate

### ✅ Step 6: Test the Integration

1. After selecting the model, try a simple test prompt:
   ```
   Write a simple Python function to calculate factorial
   ```

2. Verify the model responds correctly

3. Check cost tracking (optional):
   ```
   /cost
   ```

## Configuration File Location

```
~/.factory/config.json
```

**Full Path:** `/Users/docravikumar/.factory/config.json`

## Troubleshooting

### Model Not Appearing in Selector

**Diagnostic:**
- Is the JSON syntax correct? Validate at https://jsonlint.com
- Did you restart the Droid CLI after editing the config?

**Solution:**
```bash
# Validate JSON syntax
cat ~/.factory/config.json | python3 -m json.tool

# Restart Droid CLI
# Exit current session and run: droid
```

### Authentication Errors

**Diagnostic:**
- Is your Z.AI API key valid and active?
- Does it have available credit/quota?

**Solution:**
- Verify API key in Z.AI dashboard
- Check billing status and quota limits
- Ensure no extra spaces in the API key string

### Connection Errors

**Diagnostic:**
- Is the base_url correct?
- Can you reach the Z.AI API endpoint?

**Solution:**
```bash
# Test API endpoint connectivity
curl -I https://api.z.ai/api/coding/pass/v4
```

### Invalid Provider Error

**Diagnostic:**
- Is the provider field exactly `openai` (lowercase)?

**Solution:**
- Ensure provider value is one of: `openai`, `anthropic`, or `generic-chat-completion-api`
- Check for typos and correct capitalization

## Advanced Configuration

### Adding Multiple Models

You can add multiple Z.AI models or models from other providers:

```json
{
  "custom_models": [
    {
      "model_display_name": "Z.AI GLM-4.6 [Custom]",
      "model": "GLM-4.6",
      "base_url": "https://api.z.ai/api/coding/pass/v4",
      "api_key": "your-zai-key",
      "provider": "openai",
      "max_tokens": 32000
    },
    {
      "model_display_name": "Z.AI Advanced [Custom]",
      "model": "GLM-5.0",
      "base_url": "https://api.z.ai/api/coding/pass/v5",
      "api_key": "your-zai-key",
      "provider": "openai",
      "max_tokens": 64000
    }
  ]
}
```

### Switching Models Mid-Session

Use the `/model` command to switch between models during a Droid CLI session:

1. Start with a high-capability model for complex planning
2. Switch to a faster/cheaper model for boilerplate code generation
3. Switch back for debugging or complex refactoring

## Performance Recommendations

Based on Factory documentation:

1. **Context Window:** 32,000 tokens is recommended minimum for agentic coding tasks
2. **Model Size:** Models below 30B parameters show degraded performance on complex tasks
3. **Cost Optimization:** Use `/model` to switch between models based on task complexity

## Security Best Practices

1. ✅ **API keys stored locally only** - Never committed to version control
2. ✅ **File permissions** - Ensure `~/.factory/config.json` has restricted permissions:
   ```bash
   chmod 600 ~/.factory/config.json
   ```
3. ✅ **Backup** - Keep a backup of your configuration (without API keys) for reference
4. ✅ **Rotation** - Rotate API keys periodically per your security policy

## Support Resources

- **Factory Documentation:** https://docs.factory.ai
- **Z.AI Documentation:** [Your Z.AI provider documentation]
- **Configuration File:** `~/.factory/config.json`
- **This Guide:** `docs/Z_AI_INTEGRATION_GUIDE.md`

## Quick Reference Commands

```bash
# View configuration
cat ~/.factory/config.json

# Edit configuration
nano ~/.factory/config.json

# Validate JSON syntax
cat ~/.factory/config.json | python3 -m json.tool

# Start Droid CLI
droid

# Inside Droid CLI:
/model          # Select model
/cost           # View cost tracking
/settings       # Reload configuration
```

## Integration Status

- [x] Factory Droid CLI installed
- [x] Configuration directory created
- [x] Configuration file created with Z.AI model
- [ ] **USER ACTION REQUIRED:** Add Z.AI API key
- [ ] **USER ACTION REQUIRED:** Test model selection via `/model`
- [ ] **USER ACTION REQUIRED:** Verify model connectivity with test prompt

---

**Last Updated:** 2025-11-21  
**Configuration Version:** 1.0  
**Model:** Z.AI GLM-4.6
