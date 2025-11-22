# Z.AI Model Integration - Quick Reference Card

## ✅ What's Been Completed

1. ✓ Factory Droid CLI verified at `/Users/docravikumar/.local/bin/droid`
2. ✓ Configuration directory created at `~/.factory/`
3. ✓ Configuration file created at `~/.factory/config.json`
4. ✓ Z.AI GLM-4.6 model configured with OpenAI-compatible provider
5. ✓ Documentation created at [`docs/Z_AI_INTEGRATION_GUIDE.md`](docs/Z_AI_INTEGRATION_GUIDE.md)
6. ✓ Setup script created at [`setup_zai_model.sh`](setup_zai_model.sh)

## 🔑 NEXT: Add Your API Key (Required)

**Edit the configuration file and replace the placeholder:**

```bash
# Option 1: Use nano editor
nano ~/.factory/config.json

# Option 2: Use VS Code
code ~/.factory/config.json

# Option 3: Use TextEdit (macOS)
open -e ~/.factory/config.json
```

**Find this line:**
```json
"api_key": "YOUR_Z_AI_API_KEY_HERE",
```

**Replace with your actual Z.AI API key:**
```json
"api_key": "your-actual-zai-api-key-here",
```

**Save the file!**

## 🚀 Quick Start Commands

### Run the Setup Script (Recommended)
```bash
./setup_zai_model.sh
```
This script will:
- Verify your configuration
- Validate JSON syntax
- Set secure file permissions
- Test API connectivity
- Show next steps

### Manual Verification
```bash
# View current configuration
cat ~/.factory/config.json

# Validate JSON syntax
cat ~/.factory/config.json | python3 -m json.tool

# Set secure permissions
chmod 600 ~/.factory/config.json
```

## 🎯 Activate Your Model

### 1. Start Droid CLI
```bash
droid
```

### 2. Select Your Model
Inside the Droid CLI session:
```
/model
```
Look for: **Z.AI GLM-4.6 [Custom]** in the Custom models section

### 3. Test It
```
Write a Python function to calculate fibonacci numbers
```

### 4. Check Costs (Optional)
```
/cost
```

## 📋 Configuration Details

**File Location:** `~/.factory/config.json`

**Your Model Configuration:**
```json
{
  "custom_models": [
    {
      "model_display_name": "Z.AI GLM-4.6 [Custom]",
      "model": "GLM-4.6",
      "base_url": "https://api.z.ai/api/coding/pass/v4",
      "api_key": "YOUR_Z_AI_API_KEY_HERE",
      "provider": "openai",
      "max_tokens": 32000
    }
  ]
}
```

## 🔧 Troubleshooting

### Model Not Appearing?
1. Check JSON syntax: `cat ~/.factory/config.json | python3 -m json.tool`
2. Restart Droid CLI
3. Verify all required fields are present

### Authentication Error?
1. Verify API key is correct (no extra spaces)
2. Check Z.AI dashboard for quota/billing
3. Ensure API key has proper permissions

### Connection Error?
1. Test endpoint: `curl -I https://api.z.ai/api/coding/pass/v4`
2. Check internet connectivity
3. Verify base_url is correct

## 📚 Resources

- **Full Integration Guide:** [`docs/Z_AI_INTEGRATION_GUIDE.md`](docs/Z_AI_INTEGRATION_GUIDE.md)
- **Setup Script:** [`setup_zai_model.sh`](setup_zai_model.sh)
- **Configuration File:** `~/.factory/config.json`
- **Factory Docs:** https://docs.factory.ai

## 🔒 Security Notes

- ✓ API key stored locally only (NOT uploaded to Factory servers)
- ✓ File permissions set to 600 (owner read/write only)
- ✓ Never commit config.json to version control
- ✓ Rotate API keys periodically

## ⚡ Performance Tips

- **Max Tokens:** 32,000 is optimized for agentic coding tasks
- **Model Switching:** Use `/model` to switch between models mid-session
- **Cost Optimization:** Start with Z.AI for planning, switch to cheaper models for boilerplate
- **Best Results:** Models with 30B+ parameters perform best on complex tasks

---

**Status:** Configuration ready - API key required to activate
**Last Updated:** 2025-11-21
