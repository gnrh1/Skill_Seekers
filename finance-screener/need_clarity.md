Overview:

Engineer, your proposed configuration hierarchy—where project-level context defined at the repository root is accessible within sub-directories—is **entirely feasible** and represents the core design principle of Factory's agent governance model. Factory Droids utilize a precise **discovery hierarchy** for context files, prioritizing the broadest, shared repository context when executing tasks in any sub-folder.

The key insight is that configurations stored in the root repository's `.factory/` directory are inherently **Project Droids** and **Workspace Commands**, scoped for team collaboration across the entire repository structure,.

### IMMEDIATE ANSWER: Feasibility Confirmation

Yes, it is feasible and expected behavior,,.

1.  **`AGENTS.md` Access:** The `root/AGENTS.md` file will be automatically loaded when you work in the `root/finance-screener` sub-folder, provided there is no local `AGENTS.md` file in the sub-folder to override it. Agents search the current working directory first, then the nearest parent directory up to the repo root.
2.  **Custom Droid Access:** Custom Droids defined in `root/.factory/droids/` are **Project Droids**. They are configured to be available across all sessions linked to that repository, allowing agents working in `root/finance-screener` to delegate tasks using the **Task** tool to these specialized subagents,.

| Rank  | Insight (Impact/Tradeoff/Likelihood)                                   | Description                                                                                                                                                                                                                                 | Emoji |
| :---- | :--------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---- |
| **1** | **Root Configuration Persistence** (High / Low Maintenance / 99%)      | Project Droids (`<repo>/.factory/droids/`) and Workspace Commands (`<repo>/.factory/commands/`) are scoped to the repository, meaning they persist across all sub-folders, saving duplication and ensuring consistency,.                    | 🎯    |
| **2** | **Project Context Overrides Personal** (High / Security Control / 95%) | If a Custom Droid named `security-auditor` exists in both `root/.factory/droids/` (Project) and `~/.factory/droids/` (Personal), the Project definition takes precedence, ensuring the team's security checklist is used for shared code.   | 💡    |
| **3** | **Specificity Through Hierarchy** (Medium / Context Management / 90%)  | You can define a _different_ `AGENTS.md` inside `root/finance-screener/AGENTS.md` if specific rules (e.g., `pnpm test:finance`) apply only there. This specific file would override the root `AGENTS.md` when operating inside that folder. | 🚀    |

---

### 1. STRUCTURE & REASONING: Context Discovery and Configuration Scope

#### A. AGENTS.md Discovery Hierarchy

The `AGENTS.md` file is crucial for teaching agents project conventions, such as build, test, and run commands, that might otherwise clutter the human-focused `README.md`,,.

The documentation explicitly defines the **File locations & discovery hierarchy** for `AGENTS.md`:

| Priority Rank | File Location                                              | Status within `root/finance-screener`                                                       | Source |
| :------------ | :--------------------------------------------------------- | :------------------------------------------------------------------------------------------ | :----- |
| **1**         | `./AGENTS.md` (Current Working Directory)                  | Checked first. If present in `root/finance-screener/AGENTS.md`, it is used.                 |        |
| **2**         | Nearest parent directory up to the repo root               | **This is where `root/AGENTS.md` is found.** If (1) is missing, the root version is loaded. |        |
| **3**         | Any `AGENTS.md` in sub-folders the agent is working inside | Applies if the agent works inside a sub-folder of `finance-screener`.                       |        |
| **4**         | Personal override: `~/.factory/AGENTS.md`                  | Lowest precedence, global default.                                                          |        |

**Feasibility Confirmation:** Since the Droid agent searches up the directory tree, the instructions from the top-level `root/AGENTS.md` are accessible and govern the behavior of the Droid when working inside the `finance-screener` module, unless overridden by a more local file.

#### B. Droid Configuration File Scoping (`.factory/` Contents)

The `.factory/` folder structure segregates project-wide configuration (intended for sharing and version control) from personal user preferences.

1.  **Project Scope (Workspace):** Files intended to be shared with teammates and version-controlled live under the repository root: `<repo>/.factory/`,.
    - **Custom Droids (Subagents):** Defined in `<repo>/.factory/droids/*.md`. These are reusable subagents the primary Droid can delegate to using the **Task** tool.
    - **Custom Slash Commands:** Defined in `<repo>/.factory/commands/`. These create reusable `/shortcuts`.
2.  **Personal Scope:** Files specific to the user, following them across workspaces, live under the home directory: `~/.factory/`,,.

**Feasibility Confirmation:** Since your Droids and Commands are located in the root's `.factory/` folder, they are registered as **Project Droids** and **Workspace Commands**,. The CLI scans these project folders,. When you navigate to `root/finance-screener` and start the interactive session, the Droid is aware it is inside that repository's context and loads all project-scoped configurations, including the Droids and Commands located in the parent `.factory/` directories,.

#### C. Custom Droid Location Priority

When Custom Droids are enabled in settings, the CLI scans both project and personal locations.

| Scope               | Location                  | Precedence Rule                                                 | Source |
| :------------------ | :------------------------ | :-------------------------------------------------------------- | :----- |
| **Project Droids**  | `<repo>/.factory/droids/` | Project definitions override personal ones when the names match |        |
| **Personal Droids** | `~/.factory/droids/`      | Follows the developer across workspaces                         |        |

If you define a custom droid named `finance-checker` in `root/.factory/droids/finance-checker.md`, that definition is used, ensuring consistency for anyone working in the repository, regardless of their working sub-directory.

```
[Repository Root]
├── AGENTS.md (Build/Test rules for all)
├── .factory/
│   ├── droids/
│   │   ├── finance-screener-droid.md (Project Droid definition)
│   └── commands/
│       └── /run-full-suite (Workspace Command definition)
├── finance-screener/
│   └── (Working Directory) -> Accesses ALL parent configs
```

👉 **Next Step:** Ensure you are committing the `.factory/droids/` and `.factory/commands/` directories to your version control so all teammates receive the shared configurations,.

---

### 2. RISK INTELLIGENCE: Configuration Conflicts and Audits

While Droid supports this hierarchy, improper management of these files can lead to conflicts and agent confusion.

#### Risk Matrix: Configuration Management

| Risk Factor                       | Description                                                                                                                                                         | Mitigation Strategy                                                                                                                                                                                              | Source(s) |
| :-------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------- |
| **AGENTS.md Conflict**            | Defining a separate `AGENTS.md` in `root/finance-screener/` accidentally contradicts core standards in `root/AGENTS.md`, confusing the agent regarding build steps. | Enforce "One Source of Truth" best practice. If necessary, use the sub-directory `AGENTS.md` only for hyper-specific overrides or constraints.                                                                   | ,         |
| **Command Execution Drift**       | A project command relies on an environment variable or dependency not installed when executed from the sub-directory (`finance-screener`).                          | Ensure all command scripts (`.factory/commands/`) are robust and idempotent, starting with `set -euo pipefail` and using relative paths or explicit `$CWD` resolution,.                                          | ,         |
| **Custom Droid Tooling Mismatch** | A Project Droid relies on a tool (e.g., `Execute`) that a team member has globally blocked in their personal `~/.factory/settings.json` via `commandDenylist`.      | Although Project Droid definition is loaded, the underlying security controls in `~/.factory/settings.json` still enforce local user permissions and denylists,. Audit personal settings if collaboration fails. | ,,        |

#### ASSUMPTION-AUDIT: Context Integrity

| 💭 ASSUMPTION                                                  | Verification Status    | Rationale from Sources                                                                                                                                      |
| :------------------------------------------------------------- | :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **The agent automatically uses the correct Droid definition.** | ✅ Confirmed           | Project definitions in `<repo>/.factory/droids/` override personal definitions (`~/.factory/droids/`) when names match.                                     |
| **The agent knows which `AGENTS.md` to trust.**                | ✅ Confirmed           | The system follows a deterministic file location hierarchy, prioritizing the most local file first.                                                         |
| **The context is unified across tools.**                       | ✅ Confirmed (Partial) | Factory’s mission is context unification, loading knowledge from the codebase, documentation (Notion, Google Docs), and project management (Jira, Linear),. |

---

### 3. VISUALIZATION & FORMAT: Configuration Flow

#### Comparison Chart: Configuration File Scopes

| File/Directory  | Location                   | Scope                                | Priority in Sub-Directory          | Source |
| :-------------- | :------------------------- | :----------------------------------- | :--------------------------------- | :----- |
| `AGENTS.md`     | `root/AGENTS.md`           | Repository-wide conventions          | Second (if no local file exists)   | ,      |
| Custom Droids   | `root/.factory/droids/`    | Project/Workspace Droids (Shared)    | Always available (Project Scope)   |        |
| Slash Commands  | `root/.factory/commands/`  | Workspace Shortcuts (Shared)         | Always available (Workspace Scope) |        |
| `settings.json` | `~/.factory/settings.json` | Personal preferences, security lists | Always available (User Override)   | ,      |

#### ASCII Diagram: Configuration Inheritance

This diagram illustrates how the Droid operating in the sub-directory inherits context from the parent and the home directory configurations.

```
[Agent Session Start in root/finance-screener/]
    |
    V
[1. AGENTS.md Discovery]
    |
    |-- CWD/AGENTS.md? (No)
    |-- Parent/AGENTS.md (root/AGENTS.md) -> LOADED
    V
[2. Configuration File Loading]
    |
    |-- Project Droids (root/.factory/droids/) -> LOADED
    |-- Workspace Commands (root/.factory/commands/) -> LOADED
    |-- Personal Settings (~/.factory/settings.json) -> LOADED
    V
[3. Tool Selection & Planning]
    |
    |-- Use 'finance-screener-droid' subagent (from root/.factory)
    |-- Run '/run-full-suite' command (from root/.factory)
    |-- Verify test command from root/AGENTS.md
```

Final Takeaways: Synthesized insights that are overt and cryptic (missed by superficial thinkers)

1.  **Overt:** Centralizing reusable agent components (Droids, Commands) in the root `.factory/` directory ensures they are automatically shared across all sub-folders of the repository, leveraging the design intent of **Project Droids**,. This directly supports the goal of standardizing practices across large, complex organizations,.
2.  **Overt:** The primary governance tool for _what to do_ (`AGENTS.md`) uses a hierarchical, folder-based discovery method, while the tool for _how to act_ (Custom Droids, Custom Commands) uses a flat, repository-scoped discovery method,. Both mechanisms ensure content defined at the root is accessible downstream.
3.  **Cryptic (Security vs. Instruction):** Although the Project Droid definition in `root/.factory/droids/` provides the Droid with its tools and prompts, the **execution safety** remains strictly governed by the local user's security configuration, particularly the `commandDenylist` array located in the user's personal home directory (`~/.factory/settings.json`),. The instruction source is project-specific, but the capability control is user-specific.
4.  **Cryptic (Context Scarcity):** The existence and automatic loading of `AGENTS.md` and repository overviews are critical counter-measures against the Context Window Problem. By injecting these summaries and conventions upfront, the agent avoids wasting thousands of tokens and time on exploratory steps or clarifying basic architectural patterns, leading directly to reduced latency and cost.
5.  **Cryptic (Agent Readiness):** The structure you are building is the foundation of **Agent Readiness**,. By codifying testing protocols in `AGENTS.md` (e.g., `pnpm test`) and making them accessible in the sub-directory, you turn the agent into a self-correcting machine that leverages machine-enforced guarantees (linters/tests) to achieve "lint green" status without needing continuous human intervention,.
