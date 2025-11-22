# 🎯 SIMPLE GUIDE: Add Your Z.AI API Key (For Beginners)

## What You Need to Do (Just 3 Steps!)

I've already done all the hard work. You just need to add your API key.

---

## ✅ STEP 1: The file should be open in VS Code

The file `config.json` should now be open in VS Code. It looks like this:

```json
{
  "custom_models": [
    {
      "model_display_name": "Z.AI GLM-4.6 [Custom]",
      "model": "GLM-4.6",
      "base_url": "https://api.z.ai/api/coding/pass/v4",
      "api_key": "YOUR_Z_AI_API_KEY_HERE",    ← CHANGE THIS LINE
      "provider": "openai",
      "max_tokens": 32000
    }
  ]
}
```

---

## ✅ STEP 2: Replace the Placeholder

**Find this line:**
```json
"api_key": "YOUR_Z_AI_API_KEY_HERE",
```

**Replace `YOUR_Z_AI_API_KEY_HERE` with your actual Z.AI API key.**

**Example - BEFORE:**
```json
"api_key": "YOUR_Z_AI_API_KEY_HERE",
```

**Example - AFTER (with your real key):**
```json
"api_key": "zai_abc123xyz456...",
```

⚠️ **IMPORTANT:** 
- Keep the quotes `"` around your key
- Keep the comma `,` at the end
- Don't change anything else!

---

## ✅ STEP 3: Save the File

In VS Code:
- Press `Cmd + S` (Mac) or `Ctrl + S` (Windows/Linux)
- Or go to File → Save

---

## 🎉 That's It! Now Test It

After saving, run this command in your terminal to verify everything works:

```bash
./validate_zai_config.sh
```

If you see "✓ API Key: Configured" - you're done! 🎉

---

## 🚀 Then Use Your Model

1. Start Droid CLI:
   ```bash
   droid
   ```

2. Inside Droid, type:
   ```
   /model
   ```

3. Select: **Z.AI GLM-4.6 [Custom]**

4. Try it:
   ```
   Write a hello world function in Python
   ```

---

## ❓ Need Help?

**If the file didn't open in VS Code, run this command:**
```bash
code ~/.factory/config.json
```

**Or open it manually:**
1. Open VS Code
2. Press `Cmd + O` (Mac) or `Ctrl + O` (Windows)
3. Navigate to your home folder
4. Find the `.factory` folder (you may need to show hidden files)
5. Open `config.json`

**To show hidden files in Finder (Mac):**
- Press `Cmd + Shift + .` (period)

---

## 📍 Where is the file?

**Full path:** `/Users/docravikumar/.factory/config.json`

The `.factory` folder is in your home directory (`~` means home).

---

## 🔒 Is This Safe?

Yes! Your API key is stored on YOUR computer only. It's NOT sent to Factory servers.

---

**That's all you need to do! Just change that one line and save. Easy! 😊**
