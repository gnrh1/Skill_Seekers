# VS Code Droid Installation Guide
## Simple Setup for 16GB Personal Environment

**Target Environment:** Personal computer with 16GB RAM  
**Expected Time:** 20-30 minutes  
**Complexity:** Beginner-friendly  

---

## 🎯 Quick Prerequisites Check

Before starting, verify you have:

- ✅ **16GB RAM** available (check: System Information on Mac, Task Manager on Windows)
- ✅ **Internet connection** for downloading VS Code and extensions
- ✅ **Terminal access** (Terminal app on Mac, Command Prompt on Windows)
- ✅ **Administrator privileges** for installing software

**System Requirements Check:**
```bash
# Check available memory (macOS/Linux)
free -h

# Check available memory (Windows PowerShell)
Get-WmiObject -Class Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum
```

---

## 📦 Step 1: Install VS Code (5 minutes)

### Method 1: Direct Download (Recommended)

1. **Download VS Code**
   - Go to: https://code.visualstudio.com/
   - Click "Download for macOS/Linux/Windows"
   - Install the downloaded package normally

2. **Add to PATH** (Enable CLI access)
   - **macOS:** Open VS Code → Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"
   - **Windows:** VS Code will prompt during installation to add to PATH
   - **Linux:** The package should handle this automatically

### Method 2: Package Manager (Advanced)

```bash
# macOS (Homebrew)
brew install --cask visual-studio-code

# Windows (Chocolatey)
choco install visualstudiocode

# Linux (Snap)
sudo snap install code --classic
```

**Verification:**
```bash
# Test VS Code CLI installation
code --version

# Should output something like:
# 1.74.2
# 50d1e0d8e30ec2ddb0a70ebbe4e16ab0b6eb4d15
```

---

## 🔌 Step 2: Droid CLI Installation (5 minutes)

1. **Install Droid CLI**
   ```bash
   curl -fsSL https://app.factory.ai/cli | sh
   ```

2. **Verify Installation**
   ```bash
   droid --version
   which droid
   ```

3. **Add to PATH** (if needed)
   ```bash
   # Check if droid is in PATH
   echo $PATH | grep -o '[^:]*droid[^:]*' || echo "PATH not configured"
   
   # If not found, add to shell configuration
   export PATH="$HOME/.local/bin:$PATH"
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # macOS
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc # Linux
   ```

---

## ⚙️ Step 3: VS Code Configuration for Droid (10 minutes)

### 3.1 Enable VS Code CLI

**macOS:**
1. Open VS Code
2. Press `Cmd+Shift+P`
3. Type: "Shell Command: Install 'code' command in PATH"
4. Press Enter

**Windows:**
- During installation, ensure "Add to PATH" option is checked

**Linux:**
- Usually installed with CLI access by default

### 3.2 Configure VS Code Settings for 16GB Memory

1. **Open Settings** 
   - Press `Cmd+,` (Mac) or `Ctrl+,` (Windows/Linux)
   - Or File → Preferences → Settings

2. **Add Memory-Optimized Configuration**
   ```json
   {
     "telemetry.enableTelemetry": false,
     "extensions.experimental.affinity": {
       "ms-vscode.vscode-json": -1
     },
     "files.watcherExclude": {
       "**/.git/objects/**": true,
       "**/.git/subtree-cache/**": true,
       "**/node_modules/*/**": true,
       "**/dist/**": true,
       "**/build/**": true,
       "**/.next/**": true,
       "**/.nuxt/**": true
     },
     "search.exclude": {
       "**/node_modules": true,
       "**/dist": true,
       "**/build": true,
       "**/coverage": true
     },
     "git.ignoreLimitWarning": true,
     "extensions.exclude": [],
     "telemetry.enableCrashReporter": false
   }
   ```

3. **Save and Restart VS Code**

### 3.3 Memory Monitoring Setup

Create a simple monitoring script:

```bash
# Create monitoring script
cat > ~/vscode_memory_monitor.sh << 'EOF'
#!/bin/bash
VSCODE_PID=$(pgrep -f "Visual Studio Code" | head -1)
if [ -n "$VSCODE_PID" ]; then
    VSCODE_MEM=$(ps -o rss= -p $VSCODE_PID | awk '{print $1/1024}')
    echo "VS Code Memory: ${VSCODE_MEM}MB"
    if (( $(echo "$VSCODE_MEM > 1024" | bc -l) )); then
        echo "⚠️  High memory usage detected"
    fi
else
    echo "VS Code not running"
fi
EOF

chmod +x ~/vscode_memory_monitor.sh
```

---

## 🔧 Step 4: Install Recommended Extensions (5 minutes)

### Essential Extensions Only (Memory-Efficient)

1. **Droid Extension** (Most Important)
   - Launch VS Code
   - Press `Cmd+Shift+P` (Mac) / `Ctrl+Shift+P` (Windows/Linux)
   - Type: "Extensions: Install Extensions"
   - Search for "Factory Droid"
   - Install and reload VS Code

2. **Git Integration** (Built-in, just enable)
   - Already included in VS Code
   - Enable in: File → Preferences → Features → Git

3. **Language Support** (Install only as needed)
   - **JavaScript/TypeScript**: Built-in support
   - **Python**: Install "Python" extension by Microsoft
   - **React**: Install "ES7+ React/Redux/React-Native snippets"

### Minimal Extension List for Droid:
```
Required:
- Factory Droid (if available)
- Git (built-in)

Optional (install only if needed):
- Python (for Python projects)
- ES7+ React/Redux/React-Native snippets (for React)
- Prettier - Code formatter (for code formatting)
- ESLint (for linting)
```

---

## 🧪 Step 5: Integration Testing (5 minutes)

### 5.1 Test Droid CLI in VS Code Terminal

1. **Open a Project**
   - `Cmd+O` (Mac) / `Ctrl+O` (Windows/Linux)
   - Select any folder or create a new one

2. **Open Integrated Terminal**
   - `Cmd+`` (Mac) / `Ctrl+`` (Windows/Linux)

3. **Test Droid Integration**
   ```bash
   # Check if droid command works in terminal
   droid --version
   
   # If this shows a version, proceed to next test
   ```

4. **Launch Droid Session**
   ```bash
   # In VS Code terminal
   droid
   ```
   
   **Expected Results:**
   - Droid TUI (Terminal User Interface) opens
   - Authentication screen appears
   - You can navigate and select options

### 5.2 Test Context Sharing

1. **Create a Test File**
   ```bash
   # In VS Code terminal or manually
   echo "console.log('Hello from Droid integration test');" > test.js
   ```

2. **Open in VS Code**
   - Open `test.js` in VS Code
   - Position cursor somewhere in the code

3. **Test Droid Context**
   - Switch to Droid terminal session
   - Type: "Explain what this JavaScript code does"
   - Droid should reference the opened file

### 5.3 Verification Checklist

```
✅ VS Code installed and launches successfully
✅ VS Code CLI accessible (`code --version` works)
✅ Droid CLI installed (`droid --version` works)
✅ Droid launches in VS Code integrated terminal
✅ Can authenticate with Factory platform
✅ File context sharing works
✅ Memory usage remains reasonable (<2GB)
```

---

## 🚨 Basic Troubleshooting

### Issue 1: "code command not found"

**Solution:**
```bash
# macOS
# 1. Open VS Code
# 2. Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"
# 3. Restart terminal

# Windows/Linux
# Reinstall with PATH option checked
```

### Issue 2: "droid command not found"

**Solution:**
```bash
# Check installation location
ls -la ~/.local/bin/droid

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
which droid
```

### Issue 3: High Memory Usage (>2GB)

**Solution:**
```bash
# Run memory monitor
~/vscode_memory_monitor.sh

# If high usage detected:
# 1. Close unnecessary VS Code windows
# 2. Disable unused extensions
# 3. Restart VS Code
```

### Issue 4: VS Code Extension Not Installing

**Solution:**
```bash
# 1. Check internet connection
curl -I https://marketplace.visualstudio.com

# 2. Clear extension cache
# macOS/Linux:
rm -rf ~/.vscode/extensions/*

# Windows:
# Delete %USERPROFILE%\.vscode\extensions\*

# 3. Restart VS Code
```

### Issue 5: Droid Integration Not Working

**Solution:**
```bash
# 1. Verify both tools are installed
code --version
droid --version

# 2. Test in VS Code terminal
cd /tmp
mkdir test-project
cd test-project
code .
# Then try droid in the new VS Code terminal
```

---

## 📊 Performance Optimization for 16GB

### Memory Budget Allocation

| Component | Target Usage | Optimization Tips |
|-----------|-------------|-------------------|
| **System OS** | 4-5GB | Keep background apps minimal |
| **VS Code + Extensions** | 1-2GB | Install only essential extensions |
| **Droid CLI** | 200-500MB | Close unused terminals |
| **Available for Projects** | 8-10GB | Primary development buffer |

### Quick Performance Tips

1. **Limit Extensions**: Install only what you need
2. **Close Unused Windows**: Each VS Code window uses memory
3. **Use Integrated Terminal**: Reduces system overhead
4. **Monitor Usage**: Run `~/vscode_memory_monitor.sh` periodically
5. **Restart VS Code**: If memory usage climbs above 2GB

---

## ✅ Success Metrics

Your installation is successful when:

- [ ] VS Code launches in <10 seconds
- [ ] `code --version` returns version number
- [ ] `droid --version` returns version number  
- [ ] Droid integrates with VS Code terminal
- [ ] Memory usage stays below 2GB for VS Code
- [ ] File context sharing works between VS Code and Droid

**Time to Complete:** 20-30 minutes  
**Skill Level Required:** Beginner  
**System Load:** Minimal impact on 16GB system  

---

## 🔄 Next Steps After Installation

1. **Create AGENTS.md**: Set up project-specific instructions for Droid
2. **Configure Autonomy**: Set appropriate permission levels
3. **Learn VS Code + Droid Workflow**: Practice with small tasks
4. **Monitor Performance**: Use provided monitoring script
5. **Backup Configuration**: Save working settings

**Recommended Learning Path:**
1. Start with "Auto Low" autonomy for safety
2. Practice basic file editing and code review
3. Gradually increase autonomy based on confidence
4. Experiment with complex tasks using Specification Mode

This guide provides a solid foundation for Droid + VS Code integration while respecting your 16GB memory constraints.