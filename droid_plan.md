Overview:

The initiation of Factory's Droid agent, whether in a standalone terminal environment or integrated within Visual Studio Code (VS Code), is fundamentally driven by the Factory Command Line Interface (CLI). As a 40+ year Claude Code AI coding veteran, I mandate a foundational, two-part strategy: first, establishing the CLI environment; second, leveraging the Model Context Protocol (MCP) to bootstrap the IDE integration and context sharing. Achieving productivity requires moving beyond simple installation to immediately implementing context management via `AGENTS.md` and enabling the appropriate machine connection (Factory Bridge for local access or Remote Workspaces for cloud parity).

### IMMEDIATE ANSWER: Droid Initialization Path

The concise, actionable solution for getting started in both VS Code and the terminal relies on installing the Droid CLI first, as the VS Code plugin often auto-installs upon initial execution within the IDE’s terminal.

**1. Terminal (CLI) Quickstart (5 Minutes):**
Install the CLI and navigate to your project root.
```bash
curl -fsSL https://app.factory.ai/cli | sh
cd /path/to/your/project
droid
```
**2. VS Code Integration Quickstart:**
Launch the Droid CLI from the integrated terminal within VS Code; the extension will often bootstrap itself.
```bash
# Inside VS Code Integrated Terminal
droid 
```

| Rank | Insight (Impact/Tradeoff/Likelihood) | Description | Emoji |
| :--- | :--- | :--- | :--- |
| **1** | **Prioritize AGENTS.md Setup** (High / Minimal Time Cost / 95%) | This single Markdown file immediately grants Droid tribal knowledge (build/test commands, conventions), maximizing accuracy and reducing iteration cycles. | 🎯 |
| **2** | **Factory Bridge Connection** (High / Setup Complexity / 90%) | Essential for local workflow access (CLI commands, file edits, local processes). Without it, Droid is limited to Q&A on indexed repos and remote execution. | 🚀 |
| **3** | **Leverage IDE Diagnostics** (Medium / Low Setup / 85%) | The VS Code integration automatically feeds Droid real-time diagnostics (errors, warnings) via MCP, eliminating context explanation back-and-forth. | 💡 |
| **4** | **Autonomy Level Audit** (High / Risk Exposure / 99%) | Before executing complex tasks, understand the tiered risk model (Low/Medium/High) to ensure Droid cannot perform irreversible or destructive actions without explicit human approval. | ⚠️ |

---

### 🔧 THE APPROACH: Structured Initialization via CLI and IDE

The methodology follows a progression from foundational system installation to specialized environment configuration.

### 1. CLI Installation and Initial Session
The Droid CLI is the fundamental component, enabling the core agentic system and facilitating subsequent IDE integration.

| # | 📋 What to do | ⚙️ How to do it | 🎯 Why it matters | 📚 Sources |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Install the Droid CLI executable. | Execute the curl command in your preferred terminal: `curl -fsSL https://app.factory.ai/cli \| sh`. | Establishes the core binary required for all Droid interactions, including interactive sessions and headless execution. | |
| **1.2** | Start the interactive session. | Navigate to your target repository directory (`cd /path/to/project`) and run `droid`. | Launches the full-screen terminal user interface (TUI) and begins the authentication flow, connecting your local environment to the Factory platform. | |
| **1.3** | Select Droid and Model. | Choose a Droid (e.g., **Code Droid** for coding tasks) and the appropriate Model (e.g., **GPT-5 Codex** or **Claude Opus 4.1**) based on complexity/cost. | Droids are specialized AI assistants optimized with system prompts and tools for tasks like coding or reliability engineering. | |
| **1.4** | Connect the local machine. | Launch Factory Bridge (downloaded from Factory platform) and enter the pairing code displayed in the session view. | Creates a secure connection to your local machine, enabling Droid to run CLI commands (`npm install`, `git status`) and access local repositories directly. | |
| **1.5** | Test initial engagement. | Ask Droid a question about your project structure: `Analyze this codebase and explain the overall architecture`. | Verifies that the repository context is indexed and Droid can perform deep codebase understanding (Step 3: Codebase Q&A in the Quickstart). | |

👉 **Next Step:** Confirm Factory Bridge shows "Bridge Paired" with a green indicator.
🎯 **Decision Point:** Choose **Code Droid** unless the task is explicitly incident response (Reliability Droid) or documentation (Knowledge Droid).
📞 **Verify This:** Run `git status` via the Droid prompt to confirm local command execution through Factory Bridge.

### 2. VS Code Integration (IDE-Native Experience)
The VS Code integration is built upon the established Droid CLI installation and leverages the Model Context Protocol (MCP) for real-time context sharing.

| # | 📋 What to do | ⚙️ How to do it | 🎯 Why it matters | 📚 Sources |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Install the IDE Plugin. | Open the VS Code integrated terminal and run `droid`. The extension should auto-install. If auto-install fails, install the Factory extension from the VS Code marketplace. | Provides features like interactive diff viewing, selection context sharing, and diagnostic sharing. | |
| **2.2** | Enable Path for IDE CLI. | Ensure the CLI command for your editor (e.g., `code` for VS Code) is installed in your system PATH. | Crucial for the Droid CLI to communicate with and control the specific IDE environment. | |
| **2.3** | Leverage Context Awareness. | Simply open relevant files or select code snippets. Droid automatically receives open files, selected lines, and VSCode error highlighting/diagnostics. | Eliminates the cognitive load and token cost associated with explaining the current view or copying error messages. | |
| **2.4** | Configure Interrupt Key. | (JetBrains specific) Ensure the ESC key is correctly configured to interrupt Droid operations by unchecking "Move focus to the editor with Escape" in terminal settings. | Allows immediate interruption of Droid operations when troubleshooting or refining a plan, essential for maintaining human control. | |

👉 **Next Step:** Test the IDE integration by fixing an intentional TypeScript error. Prompt: `Fix error` while the cursor is on the error line.
🎯 **Decision Point:** If facing performance issues, consider pausing real-time spell-checkers or disabling file watchers in dev tools.
📞 **Verify This:** Run `/settings` and check that `diffMode` is configured appropriately for visual review (recommended: `github`).

---

### 🚀 ADVANCED OPTIMIZATION: Context and Autonomy

A veteran developer understands that the initial setup is just establishing the physics engine; true velocity comes from optimizing the inputs and tuning the control mechanisms.

#### 1. Context Injection via AGENTS.md
The `AGENTS.md` file acts as the primary source of tribal knowledge for Droid. It complements `README.md` by providing agent-specific instructions that would clutter human documentation (build steps, conventions, test runners).

| AGENTS.md Section | Example Concrete Command | Second-Order Effect | 📚 Sources |
| :--- | :--- | :--- | :--- |
| **Build & Test** | `pnpm test --run --no-color` | Enables Droid to run objective proof tests **after** generating code edits to verify success (Explore → Plan → Code → Verify loop). | |
| **Conventions & Patterns** | `TypeScript strict mode, single quotes, no semicolons` | Reduces style drift and eliminates code review comments related to formatting, allowing Droid to self-correct until lint-green. | |
| **Project Layout** | `├─ client/ → React + Vite frontend` | Steers tool selection (e.g., `edit_file`, `create_file`) toward the correct architectural boundaries, preventing edits in unrelated directories. | |
| **Evidence Required for Every PR** | `- All tests green (pnpm test) - Proof artifact (Bug fix → failing test added first, now passes)` | Establishes a verifiable definition of "Done," ensuring high-quality, traceable changes. | |

**Efficiency Hack (⚡):** Aim for **$\le 150$ lines** in `AGENTS.md`. Long files slow the agent and bury signal. Wrap all commands in back-ticks (`\``) so Droid can copy-paste without guessing.

#### 2. Mastering Specification Mode (Spec Mode)
For complex tasks (e.g., refactoring 100+ files or implementing a large feature spanning 30+ files), Specification Mode is mandatory to prevent token waste from false starts.

| 🔄 Spec Mode Iteration Cycle | Description | Hard Choice / Tradeoff (⚖️) | 📚 Sources |
| :--- | :--- | :--- | :--- |
| **Phase 1: Planning** | Activate with **Shift+Tab**. Droid performs a read-only analysis, creates a detailed plan (phases, dependencies, testing strategy), and assesses risk. | **Tradeoff:** Time investment upfront (Phase 1 can take minutes) vs. guaranteed safe pathfinding and reduced downstream rework. | |
| **Phase 2: Review & Approval** | Review the generated plan. You can choose to proceed manually or enable **Auto-Run (Low/Medium/High)** for implementation. | **Hard Choice:** Approving Auto-Run *before* code starts execution trades continuous oversight for speed/autonomy. | |
| **Phase 3: Iterative Implementation** | Break the large feature into smaller, discrete sessions, each referencing the saved master plan (`IMPLEMENTATION_PLAN.md`). | **Tradeoff:** Maintain clean, focused context (fresh session) vs. potential loss of nuanced conversation history from the previous session. | |

#### 3. Configuring Autonomy (Risk Management)
Autonomy levels control Droid's permission profile in both interactive sessions and Droid Exec (headless mode).

| Autonomy Level | Risk Profile | Typical Commands Auto-Executed | Source |
| :--- | :--- | :--- | :--- |
| **Auto (Low)** | Low Risk (Read-Only & File Edits) | `Edit`, `Create`, `ls`, `git status`, `rg` (ripgrep) | |
| **Auto (Medium)** | Medium Risk (Reversible Workspace Changes) | `npm install`, `pip install`, `git commit`, `build tooling` | |
| **Auto (High)** | High Risk (Destructive/Irreversible Scripts) | `docker compose up`, `git push`, migrations, custom scripts | |
| **--skip-permissions-unsafe** | DANGEROUS | ALL operations without confirmation (only for isolated, disposable containers) | |

**Interdependency:** Setting permissions via the CLI's `commandAllowlist` or `commandDenylist` (in `~/.factory/settings.json`) overrides the general autonomy level for specific commands. For instance, adding `rm -rf /` to the `commandDenylist` ensures it *always* requires confirmation, even if the session is set to Auto (High).

---

### 🛠️ TROUBLESHOOTING: Failure Modes and Diagnostics

Addressing inevitable failure modes is critical for AI-assisted development novices.

| 🔴 Failure Mode | ❓ Diagnostic Question | ✅ Precise Remedy (with Source) | ⚖️ Tradeoff |
| :--- | :--- | :--- | :--- |
| **CLI `droid` command not found** | Is the installation script fully executed, and is the install location (`$HOME/.local/bin`) included in your user's `$PATH`? | Rerun the installation script: `curl -fsSL https://app.factory.ai/cli \| sh`. Manually add `$HOME/.local/bin` to your shell's PATH environment variable. | Requires manual system configuration outside of Droid's scope. |
| **Factory Bridge connection failure** | Did you ensure the Bridge app is running (check system tray) and that the pairing code was correctly entered? | Verify Bridge is running. Check for the green "Bridge Paired" indicator. Restart Factory Bridge and try entering a new pairing code. | Brief disruption (restart) for connection reset. Limited to 6 concurrent connections. |
| **IDE Plugin (VS Code) not installing** | Is the IDE's corresponding shell command (`code`, `cursor`, etc.) available in the terminal PATH? | If running VS Code, use `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Win/Linux) and search for "Shell Command: Install 'code' command in PATH". | Requires IDE restart for the plugin to fully engage. |
| **File context missing/stale in IDE** | Are the files saved, and is the file size excessively large (>$500\text{ KB}$ unsaved)? | **Save the files.** Unsaved buffers larger than $500 \text{ KB}$ are skipped for performance. If diagnostics are stale, run `↻ Refresh Diagnostics` command from the VS Code command palette. | Requires periodic manual refresh for diagnostics or adherence to file size limits for unsaved buffers. |
| **Droid won't execute changes in CI** | Is the `droid exec` command missing the required autonomy flag (`--auto low`, `medium`, or `high`)? | Use `droid exec --auto low` at minimum to enable file creation/editing in project directories. **Example:** `droid exec "fix bug" --auto medium`. | Must explicitly opt-in to mutations (secure-by-default execution model). |

💭 **Contrarian View:** Conventional wisdom suggests running only read-only commands initially. However, the sources show that effective integration relies heavily on early setup scripts (`npm install`, `pip install`). Therefore, for remote workspaces, configuring the setup script with `set -euo pipefail` and dependency installation *before* the first interactive session is optimal for high velocity and reproducibility.

---

### 📐 VISUALIZATION & FORMAT: Droid Initialization Flow

This architecture diagram illustrates the dependency chain for successful Droid integration in both interactive and automated environments, emphasizing the critical role of the CLI and context systems.

```
+--------------------------------------------------------------------+
|                         DROID INITIALIZATION ARCHITECTURE                                 |
+--------------------------------------------------------------------+
                                      |
                                      V
+---------------------+           +---------------------+
| 1. CLI INSTALLATION |           | 2. MACHINE CONNECTION |
| (Foundation)        |           | (Execution Layer)     |
+---------------------+           +---------------------+
| curl -fsSL ... | sh | <-----> | [Factory Bridge] (Local) |
| cd /project & droid |         | [Remote Workspace] (Cloud) |
+---------------------+         +---------------------+
           |                                  |
           V                                  V
+--------------------------------------------------------------------+
| 3. CONTEXT INGESTION (Organizational Knowledge)                      |
+--------------------------------------------------------------------+
| [AGENTS.md] (Build/Test/Conventions)  <----> [External Integrations] (@ticket, @pr) |
| [HyperCode/ByteRank] (Codebase Index) <----> [IDE Plugin] (Real-time Diagnostics)  |
+--------------------------------------------------------------------+
           |
           V
+---------------------+   +---------------------------------------+
| 4A. TERMINAL WORKFLOW |   | 4B. VS CODE INTEGRATION (Enhanced)    |
| (TUI)                 |   | (MCP/Diagnostic Sharing)              |
+---------------------+   +---------------------------------------+
| Execute Process       |   | Run 'droid' in Integrated Terminal |
| Kill Process          |   | -> Auto-Install Extension               |
| Pipe Process Input    |   | -> Real-time Errors/Diagnostics   |
+---------------------+   +---------------------------------------+
           |
           V
+---------------------+
| 5. AUTONOMY LOOP (Risk Gating) |
| (Auto Low/Medium/High)       |
+---------------------+
```

---

### Final Takeaways: Synthesized insights that are overt and cryptic (missed by superficial thinkers)

1.  **Overt:** The Droid ecosystem is Model-Agnostic, allowing you to select models like Claude Opus 4.1 for complex reasoning or GPT-5 Codex for implementation speed, ensuring **model choice is a tuning lever, not a vendor lock-in**. The ability to bring your own keys (BYOK) via `~/.factory/config.json` allows for direct cost control and transparent billing against official APIs.
2.  **Overt:** Context is fragmented across Jira, Notion, Slack, and code. Factory’s genius lies in **unifying this context** (Code Context, Documentation Context, Task Context) and automatically retrieving it (Dynamic Retrieval) or accepting external links/`@` commands to focus the Droid's attention.
3.  **Cryptic (First-Principles Thinking):** The IDE integration's true value is not merely aesthetic—it leverages the **Model Context Protocol (MCP)** to establish a high-bandwidth, standardized communication layer between the proprietary agent framework and the editor diagnostics. This effectively transforms the IDE into a live sensor array for the agent, providing instant environmental grounding that far surpasses traditional, passive tools.
4.  **Cryptic (Systems Thinking):** The concept of **Agent Readiness** is achieved by treating lint rules as *machine-enforced guarantees*, not just suggestions. By codifying architectural constraints into lint rules and listing the necessary commands in `AGENTS.md`, you are creating a "compiler-like contract" that forces Droid to self-correct until green, achieving reliability at scale faster than human review alone.
5.  **Cryptic (Inversion Principle):** When an agent experiences drift (e.g., plans rewriting themselves mid-execution or editing outside declared paths), the recovery playbook mandates **tightening the specification** by narrowing the directory or tests the agent may touch. This is an inverse correlation: when autonomy fails, the human must reduce the search space and increase instructional rigor, essentially imposing tighter, deterministic boundaries to resolve the chaotic state.