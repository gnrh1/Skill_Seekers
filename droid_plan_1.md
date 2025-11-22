Overview:
Affirmative. I have conducted a rigorous, multi-vector verification of the requested operational parameters against the current Factory documentation matrix. The roadmap details you possess are largely accurate and represent the established standard operating procedure for Droid deployment and configuration. However, critical adversarial insight reveals that while Factory Bridge and Remote Workspaces coexist, they serve distinct operational domains (local execution versus cloud-hosted persistence). Furthermore, memory usage requires disciplined engineering beyond simple constraints, focusing on the contextual hierarchy.

**IMMEDIATE ANSWER:**
The critical details are largely validated.

1.  **CLI Installation Command:** The command `curl -fsSL https://app.factory.ai/cli | sh` is the confirmed, standard installation method for the Droid CLI.
2.  **Configuration Structure:** The primary settings file is confirmed as `~/.factory/settings.json` (for macOS/Linux users).
3.  **Autonomy Levels:** The configuration options remain **Auto (Low), Auto (Medium),** and **Auto (High)**.
4.  **Platform Status:** Factory Droids are **Generally Available (GA)** since May 28, 2025, and are accessible across all interfaces (CLI, IDE, Web, etc.).

**Top 5 Synthesized Insights:**

| Rank | Insight (Aperture Focus) | Impact | Tradeoffs | Likelihood of Success |
| :--- | :--- | :--- | :--- | :--- |
| **1** 💡 | **The Binary Split of Machine Connection:** Factory deliberately maintains two distinct connection vectors: **Factory Bridge** for local machine sovereignty (CLI/Process execution) and **Remote Workspaces** for consistent, cloud-hosted environment isolation (Cloud Machine). | High. Prevents local environment drift and enables secure, ephemeral task execution. | Requires maintaining two separate setup configurations and managing Bridge pairing codes. | Very High. Critical for scalable enterprise adoption. |
| **2** ⚠️ | **Mandatory Security Guardrails:** The `commandAllowlist` and `commandDenylist` settings supersede the runtime autonomy levels, ensuring that dangerous commands like `rm -rf /` are categorically prevented, even if `Auto High` is selected. | Extreme. Mitigates accidental operational self-destruction when running in autonomous modes. | Adds overhead to security configuration management, especially across varied team scripts. | Critical. Non-negotiable safety layer. |
| **3** 🎯 | **Context is Scarce (The Token Budget):** Effective performance hinges on disciplined context curation (Factory's Context Stack/ByteRank), not just increasing model window size. | High. Directly impacts inference quality, latency, and cost by minimizing wasted tokens. | Requires proactive use of tools like AGENTS.md and focused prompting to guide the Droid effectively. | Medium. Requires developer discipline (a human factor). |
| **4** 🚀 | **IDE Integration Auto-Pilot:** The most efficient method for activating IDE features (real-time diagnostics, selection context) is initiating the `droid` CLI within the IDE's integrated terminal, triggering auto-installation/activation. | Medium. Eliminates manual setup steps and immediately provides high-fidelity context awareness. | Requires ensuring the IDE's CLI command (`code`, `cursor`, etc.) is correctly configured in the PATH. | High. Streamlines onboarding (minutes vs. days). |
| **5** 💰 | **Model-Agnostic Performance:** Droid's superior agent design allows cheaper models (e.g., Sonnet) to outperform competitors using more expensive frontier models (Opus), providing significant cost savings without sacrificing capability. | High. Allows cost optimization and model vendor optionality (Bring Your Own Key, Ollama, etc.). | Requires continuous testing and awareness of model-specific quirks (e.g., path handling preferences). | Very High. Core value proposition of the platform. |

---

### 🔧 THE APPROACH: Structured Verification Protocol

This Droid veteran will verify each detail through first principles, tracing the documentation structure to confirm currency and context.

### 1. Installation & Setup Verification

#### 1.1 CLI Installation Command
📋 **What to do**
Verify the exact shell command used for installing the Droid CLI.

⚙️ **How to do it**
Cross-reference the quickstart guides and installation prerequisites.

🎯 **Why it matters**
This is the critical entry point for terminal interaction. An incorrect command introduces immediate user friction.

📚 **Cite supporting sources**
The official command to install Droid CLI is confirmed: `curl -fsSL https://app.factory.ai/cli | sh`. Note that Linux users may also need `sudo apt-get install xdg-utils` for proper functionality.

👉 **Next Step:** Execute the confirmed `curl` command in a clean terminal environment.

#### 1.2 Factory Bridge Application
📋 **What to do**
Determine if Factory Bridge (local connection) is deprecated or superseded by Remote Workspaces.

⚙️ **How to do it**
Analyze the function and scope of both Factory Bridge and Remote Workspaces.

🎯 **Why it matters**
Ensuring the correct pathway for executing local commands (e.g., `npm start`, accessing local repos) is paramount.

📚 **Cite supporting sources**
Factory Bridge is explicitly defined for connecting to your **Local Machine**, enabling capabilities like running CLI commands and managing local processes. Local connection requires downloading and pairing the Bridge application.

Remote Workspaces are defined as cloud-hosted development environments (Cloud Machine).

Factory Bridge is confirmed as the correct and current method for **local machine connections**, operating distinctly from the cloud-based Remote Workspaces functionality **[LOGICAL INFERENCE]**.

📞 **Verify This:** Confirm the Bridge pairing code process (5 steps) is functional, including setting the Root Directory.

#### 1.3 VS Code Extension
📋 **What to do**
Confirm the recommended method for installing the VS Code extension: manual marketplace install versus CLI auto-install.

⚙️ **How to do it**
Consult the IDE Integrations guide for installation sequence and benefits.

🎯 **Why it matters**
The extension enables the Model Context Protocol (MCP) functionality, allowing Droid to see real-time context (diagnostics, selected lines) which drastically reduces back-and-forth communication.

📚 **Cite supporting sources**
The setup sequence states that running `droid` in the integrated VS Code terminal will **auto-install** the extension. This is the recommended pathway for Visual Studio Code and its forks (Cursor, VSCodium). The extension acts as an MCP server, providing immediate context awareness.

### 2. Configuration Verification

#### 2.1 Configuration File Structure
📋 **What to do**
Verify the existence and primary purpose of `~/.factory/settings.json`.

⚙️ **How to do it**
Identify the documented location and the scope of configurations stored within this file.

🎯 **Why it matters**
Ensuring configuration persistence and portability across user sessions.

📚 **Cite supporting sources**
User-specific Droid settings are stored in `~/.factory/settings.json` on macOS/Linux. This file stores the default model, `diffMode`, and the security-critical `commandAllowlist`/`commandDenylist`.

Custom model definitions (Bring Your Own Key/BYOK) are stored in a separate, but related file: `~/.factory/config.json`.

👉 **Next Step:** Review the JSON structure of `~/.factory/settings.json` to confirm the presence of security arrays and model defaults.

#### 2.2 Autonomy Levels
📋 **What to do**
Confirm the current discrete autonomy configuration options.

⚙️ **How to do it**
Cross-reference the definitions in the Auto-Run Mode and Droid Exec documentation.

🎯 **Why it matters**
Autonomy levels dictate the system's risk tolerance and govern whether Droid operates autonomously or requires explicit human confirmation for tool calls and changes.

📚 **Cite supporting sources**
The three primary autonomy levels are confirmed:
1.  **Auto (Low)**: Allows file creation/editing in project directories and read-only commands (`ls`, `git status`).
2.  **Auto (Medium)**: Adds reversible development operations (`npm install`, `git commit`, build tooling).
3.  **Auto (High)**: Permits all non-blocked operations (`git push`, migrations, `docker compose up`).

These modes can be set via `/settings`, cycled with `Shift+Tab`, or specified using `droid exec --auto <level>`.

🎯 **Decision Point:** Decide on the default autonomy level for the team. **Recommendation:** Use **Auto (Medium)** for day-to-day feature development to balance speed and reversibility.

### 3. Performance & Security Verification

#### 3.1 Memory Limits and Optimization
📋 **What to do**
Identify official Factory AI recommendations for optimal memory usage patterns, specifically regarding token limits and optimization strategies.

⚙️ **How to do it**
Analyze the Context Window problem and Factory's solutions (Context Stack, Hierarchy, Tooling).

🎯 **Why it matters**
Inefficient context consumption increases operational cost (tokens billed at \$2.70 per million tokens overage) and leads to agent drift or poor reasoning quality.

📚 **Cite supporting sources**
Factory’s recommendations center on minimizing tokens per task, disciplined context curation, and leveraging specialized system components:
1.  **Context Stack & Retrieval:** Rely on Droid’s intelligent retrieval systems (HyperCode and ByteRank) which dynamically select context based on task.
2.  **External Document Utilization:** Reference external sources (Jira, Notion, Google Docs) via `@` commands or links, rather than pasting large documents into the chat.
3.  **AGENTS.md:** Store project standards and common commands here (aim for $\le 150$ lines) so Droid doesn't waste tokens asking or searching for conventions.
4.  **Local Model Tuning:** For local Ollama models, explicitly configure the context window to at least $32,000$ tokens for optimal performance.

$$ \text{Token Cost Optimization} = \frac{\text{Efficiency}(\text{Context Stack}) \times \text{Specificity}(\text{Prompting})}{\text{Complexity}(\text{Task})} $$

⚠️ **GAP:** While optimization strategies are detailed, no single numeric *maximum memory constraint* for general LLM context window use is universally stated, as limits vary per model (e.g., $1$ million tokens is cited as a large LLM limit). The focus is on *relative* context management.

#### 3.2 Security Requirements (Allowlist/Denylist)
📋 **What to do**
Verify if `commandAllowlist`/`commandDenylist` configurations are still relevant security controls.

⚙️ **How to do it**
Check the latest Droid settings documentation for explicit inclusion and function of these controls.

🎯 **Why it matters**
These configurations provide a vital, declarative safety layer that complements the heuristic nature of autonomous execution levels.

📚 **Cite supporting sources**
These controls are listed under "Available settings" in the Configuration documentation.
*   `commandAllowlist`: Commands here run without confirmation, overriding autonomy prompts (e.g., `ls`, `pwd`).
*   `commandDenylist`: Commands here always require confirmation and are used to block destructive/unsafe operations (e.g., `rm -rf /`, `mkfs`).
Commands listed in both default to the Denylist behavior. This confirms they are highly relevant and maintained security features.

### 4. Current Implementation Status

#### 4.1 Platform Availability
📋 **What to do**
Confirm the current deployment status of Factory Droids.

⚙️ **How to do it**
Consult recent press releases and overview documentation.

🎯 **Why it matters**
Confirms readiness for production deployment and availability to novice users.

📚 **Cite supporting sources**
Factory announced General Access (GA) for Droids across the entire SDLC on May 28, 2025. Furthermore, Droids are available to anyone, with any model, in any interface (CLI, IDE, Slack, Linear, Browser).

### 📐 VISUAL DIAGRAMS

#### Comparison Chart: Connection Mechanisms

| Feature | Factory Bridge (Local Machine) | Remote Workspaces (Cloud Machine) |
| :--- | :--- | :--- |
| **Purpose** | Local CLI execution, process management, local resource access. | Cloud-hosted development environment, isolation, reproducibility. |
| **Setup Method** | Download Bridge app, pair with 6-digit code, set Root Directory. | Create workspace via Session Settings, configure setup script, clone repo. |
| **Primary Benefit** | Uses your local hardware and permissions; keeps sensitive data local. | Disposable per-task isolation; consistent setup across teams. |
| **Limitation** | Max 6 concurrent sessions. | Potential terminal latency; data outside `/workspaces` is cleared on rebuild. |

#### Architecture Diagram: Context Management Hierarchy

```
[Repository]
  (Code, Files, History)
     |
[External Integrations]
 (Jira, Notion, Sentry, PagerDuty)
     |
[AGENTS.md & User/Org Memory] <---- Mandatory Standards/History
 (Conventions, Preferences, Acronyms)
     |
[Context Stack (HyperCode/ByteRank)]
 (Semantic Search, Repo Overviews)
     |
[Droid Engine] ──> [LLM (Opus, GPT-5)] ──> [Action Plan]
   (Filters and Curates Tokens)
```

### 🛠️ TROUBLESHOOTING

| Failure Mode (🔴) | Diagnostic Question (❓) | Precise Remedy (✅) | Contrarian Approach (💭) |
| :--- | :--- | :--- | :--- |
| **CLI Installation fails** after `curl`. | Is `xdg-utils` installed (if Linux)? Are corporate proxy variables blocking `curl`?. | ✅ Install `xdg-utils` or set `HTTP_PROXY`/`HTTPS_PROXY` environment variables before running the script. | 💭 Use the IDE environment setup first; if `droid` runs there, the PATH setup is correct, mitigating manual environment tracing. |
| **Autonomy Level Exceeded** (`droid exec` stops abruptly). | What is the command's risk rating, and is it above the `--auto` level selected?. | ✅ If it is a safe command, move it to the `commandAllowlist` in `settings.json`. If critical, elevate `--auto` level for the specific script. | 💭 Define an exit routine in the automation pipeline that triggers a human review session based on the non-zero exit code, instead of immediate task failure. |
| **Stale IDE Diagnostics** (Droid misses current errors). | Has the VS Code/JetBrains extension correctly synced the diagnostics via MCP?. | ✅ Run the **↻ Refresh Diagnostics** command from the VS Code Command Palette or restart the JetBrains IDE completely. | 💭 Audit IDE integration logs to trace why the real-time MCP server context stream was interrupted. |

***

Final Takeaways: Synthesized insights that are overt and cryptic (missed by superficial thinkers)

The core technical framework is stable, but robustness relies heavily on human action.

**Overt Insights:**
1. Factory prioritizes security by keeping all risky execution local via Factory Bridge or contained in cloud-isolated Remote Workspaces.
2. The platform is designed for interoperability, confirmed by its GA status and ubiquitous availability across interfaces and model providers (BYOK, Ollama).
3. Structured configuration via `AGENTS.md` and `~/.factory/settings.json` is essential for team consistency and maintaining the security boundary layer.

**Cryptic Insights (Second-Order Effects):**
1. **The Sovereignty of Local Execution:** The continued emphasis on Factory Bridge signals a long-term commitment to developer control and security against cloud dependency. By executing commands locally with user permissions, Factory outsources the execution risk back to the local developer environment, aligning liability (per the ToS, the Customer retains sole responsibility for the Customer Environment).
2. **The AGENTS.md/Linter Imperative:** The collaboration on AGENTS.md and the push for linters writing the law reveals a design philosophy where AI governance shifts from human review to *machine-verifiable standards*. This lowers the cognitive load of human reviewers by replacing subjective style suggestions with deterministic compliance checks, transforming the PR process from opinion sharing to standard conformance.
3. **The Hidden Cost of Ambiguity:** The need for explicit optimization around context/tokens confirms that even with large context windows, the economic and performance costs of vague prompting remain substantial. Poorly specified requests translate directly into higher cloud compute costs ($2.70/million overage tokens) and delayed task completion. This mandates a shift in prompt engineering to focus on absolute clarity and brevity. ✅