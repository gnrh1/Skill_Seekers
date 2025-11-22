Overview:

Engineer, bringing your own model (BYOM) or utilizing your own API keys (BYOK) for LLMs is a core feature of the Factory platform, ensuring you maintain control over costs, model choice, and data security. The mechanism for this is executed through the Droid Command Line Interface (CLI) by defining custom configurations within a local JSON file.

This process transforms the Droid CLI from relying solely on Factory-managed access to functioning as a **model routing layer**, allowing you to switch instantly between managed models (like Claude Opus or GPT-5) and external providers (like Ollama, Hugging Face, or your own Anthropic keys). Your API keys remain local and are explicitly **not uploaded to Factory servers**.

### IMMEDIATE ANSWER: BYOK Implementation Steps

To bring your own model to Factory, you must follow a three-part protocol centered around the local configuration file:

1.  **Install CLI:** Ensure the Droid CLI is installed and running.
2.  **Configure:** Edit the local configuration file, `~/.factory/config.json`, adding your model details to the `custom_models` array.
3.  **Activate:** Access the model selector using the `/model` command within the Droid CLI session to switch to your newly configured custom model.

**Example Configuration Snippet (Ollama Local Model):**

```json
// ~/.factory/config.json
{
  "custom_models": [
    {
      "model_display_name": "Qwen 2.5 Coder 32B [Local]",
      "model": "qwen2.5-coder:32b",
      "base_url": "http://localhost:11434/v1",
      "api_key": "not-needed",
      "provider": "generic-chat-completion-api",
      "max_tokens": 16000
    }
  ]
}
```

_Note: For local models like Ollama, the `api_key` field must contain any non-empty value._.

| Rank  | Insight (Impact/Tradeoff/Likelihood)                                      | Description                                                                                                                                                                                    | Emoji |
| :---- | :------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---- |
| **1** | **Security Model:** Keys Remain Local (High / Zero Security Risk / 100%)  | Your API keys are stored locally in `~/.factory/config.json` and are not transmitted to Factory servers. This maintains your security posture.                                                 | 💡    |
| **2** | **Cost Control (BYOK):** (High / Increased Setup Time / 99%)              | Using BYOK/BYOM allows you to run tasks on models optimized for speed/cost (e.g., GPT-5 Codex or Sonnet 4.5) against your own billing account, offering billing transparency and cost control. | 💰    |
| **3** | **Performance Caveat:** Model Size (High / Performance Degradation / 90%) | Models below **30 billion parameters** show significantly lower performance on agentic coding tasks. Avoid using smaller models (e.g., 7B or 13B) for production or complex work.              | ⚠️    |

---

### 🔧 THE APPROACH: Structured BYOK Implementation

The process of implementing Bring Your Own Key (BYOK) or Bring Your Own Model (BYOM) involves setup, detailed configuration, and verification.

#### 1. System Setup and CLI Foundation

| #       | 📋 What to do                         | ⚙️ How to do it                                                                                                                                                                                  | 🎯 Why it matters                                                                                                       | 📚 Sources |
| :------ | :------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :--------- |
| **1.1** | Install the Droid CLI.                | Execute the installation script in your terminal: `curl -fsSL https://app.factory.ai/cli \| sh`.                                                                                                 | The CLI binary (`droid`) is mandatory for accessing the local configuration file and the `/model` selector.             |            |
| **1.2** | Install or configure your target LLM. | For official providers (OpenAI/Anthropic), obtain your API key. For local models (Ollama), install the server and pull the model, ensuring the server is running on `http://localhost:11434/v1`. | Guarantees the model endpoint is reachable _before_ configuring Factory, preventing connectivity troubleshooting later. |            |

👉 **Next Step:** Verify the Droid CLI is functional by running `droid` in a project directory.

#### 2. Configuration File Specification (`~/.factory/config.json`)

The configuration lives in the user’s home directory and uses JSON format.

| #       | 📋 What to do                            | ⚙️ How to do it                                                                                                                                                                                                                                                                                                                                                                            | 🎯 Why it matters                                                                         | 📚 Sources |
| :------ | :--------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------- | :--------- |
| **2.1** | Locate or create the configuration file. | The file path is `~/.factory/config.json`. You can typically open it via the Factory Bridge system tray icon by selecting **“Open MCP Config File”** (This file is often shared for MCP and custom models) or manually navigate to the path.                                                                                                                                               | Centralizes all custom model definitions outside of version control, protecting API keys. |            |
| **2.2** | Add the `custom_models` array structure. | Add a top-level JSON object containing the `custom_models` key.                                                                                                                                                                                                                                                                                                                            | This array is where all custom models are defined for the CLI selector.                   |            |
| **2.3** | Define mandatory model fields.           | For _each_ model, provide all required fields in the JSON object:<br>A. `model_display_name` (Human-friendly name)<br>B. `model` (Model identifier used by the API)<br>C. `base_url` (API endpoint URL)<br>D. `api_key` (Your secret key—must be non-empty)<br>E. `provider` (Must be `anthropic`, `openai`, or `generic-chat-completion-api`).<br>F. `max_tokens` (Maximum output tokens) | Ensures the Droid CLI can correctly format API requests and display the model in the UI.  |            |

#### 3. Activation and Verification

| #       | 📋 What to do                      | ⚙️ How to do it                                                                                           | 🎯 Why it matters                                                                                          | 📚 Sources |
| :------ | :--------------------------------- | :-------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- | :--------- |
| **3.1** | Restart the CLI.                   | Exit any running `droid` session and restart it, or run `/settings`.                                      | The CLI re-scans the `~/.factory/config.json` file upon launch or when configuration changes are surfaced. |            |
| **3.2** | Select the custom model.           | Inside the Droid CLI session, run the command `/model`. Locate your model in the "Custom models" section. | Confirms successful configuration and makes the model the active inference engine for the session.         |            |
| **3.3** | Verify cost efficiency (Optional). | After using the model, run the `/cost` command in the Droid CLI.                                          | Allows auditing prompt caching performance and verifying billing transparency.                             |            |

🎯 **Decision Point:** If using Anthropic or OpenAI, set `provider` to `anthropic` or `openai` respectively for optimal performance, including prompt caching. For almost all other vendors (OpenRouter, Ollama, etc.), use `generic-chat-completion-api`.

---

### 🚀 ADVANCED OPTIMIZATION: Provider and Performance Tuning

A veteran developer maximizes the return on BYOK investment by optimizing provider configuration and aligning model power with task complexity.

#### A. Comprehensive Supported Provider List

Factory CLI supports a wide variety of custom model configurations using BYOK.

| Provider Type            | Examples                                | `provider` Field Value        | Notes                                                                                                         | Sources |
| :----------------------- | :-------------------------------------- | :---------------------------- | :------------------------------------------------------------------------------------------------------------ | :------ |
| **Official Managed API** | OpenAI, Anthropic (using personal keys) | `openai` or `anthropic`       | Full prompt caching support is attempted via official APIs.                                                   |         |
| **Local/Open Source**    | Ollama                                  | `generic-chat-completion-api` | Requires local server running (e.g., on port 11434) and context window set large (e.g., $\ge 32,000$ tokens). |         |
| **Inference Routers**    | Hugging Face, OpenRouter, DeepInfra     | `generic-chat-completion-api` | Access thousands of models; model performance below 30B parameters is poor for agentic tasks.                 |         |
| **Custom Hosting**       | Baseten, Fireworks AI                   | `generic-chat-completion-api` | Used for custom models or specific optimized serving infrastructure.                                          |         |

#### B. Optimizing for Long-Horizon Tasks

When leveraging BYOK for complex, multi-step tasks (like code migrations or large refactors), tuning two parameters is critical:

1.  **Context Window (`max_tokens`):** While models have theoretical maximum context limits (e.g., Gemini 1.5 Flash up to $1,048,576$ tokens), the `max_tokens` field defines the _maximum output_ length. Ensure this is adequate for complex code generation, especially when dealing with large file diffs.

    - **Mandate:** For agentic coding tasks, ensure the context window setting is **at least 32,000 tokens** (e.g., for Ollama setups), as inadequacy leads to significant degradation.

2.  **Reasoning Effort (`-r` flag):** Reasoning effort increases latency and cost but materially improves planning and debugging for GPT models (e.g., GPT-5 Codex). For complex tasks, escalate effort.
    - **Execution Command Example:** $$ \text{droid exec -m gpt-5-codex -r high "Refactor auth system per spec.md" --auto medium} $$

**Efficiency Hack (⚡):** Use the `/model` command to swap models mid-session. Start complex planning with a high-reliability, high-cost model (e.g., Opus 4.1 or high-effort GPT-5 Codex) and switch to a lower-cost model (e.g., Sonnet 4 or GPT-5) for boilerplate execution and minor revisions.

---

### 🛠️ TROUBLESHOOTING: Failure Modes

Specific failure modes are often encountered when configuring external or local models due to incompatible API formatting or missing local prerequisites.

| 🔴 Failure Mode                         | ❓ Diagnostic Question                                                                                                         | ✅ Precise Remedy                                                                                                                                                                       | 📚 Source |
| :-------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------- |
| **Model not appearing in selector**     | Did you restart the CLI? Is the JSON syntax in `~/.factory/config.json` correct?                                               | Check JSON syntax. Verify all required fields (`model_display_name`, `model`, `base_url`, `api_key`, `provider`, `max_tokens`) are present. Restart the CLI session.                    |           |
| **"Invalid provider" error**            | Is the `provider` field one of the three accepted values: `anthropic`, `openai`, or `generic-chat-completion-api`?             | Check for typos and ensure correct capitalization; the values must match exactly.                                                                                                       |           |
| **Local model (Ollama) won't connect**  | Is the Ollama server process running locally (`ollama serve`)? Is the `base_url` set correctly to `http://localhost:11434/v1`? | Ensure Ollama is running, check if port 11434 is available, and verify the correct model is pulled (`ollama pull model-name`).                                                          |           |
| **Authentication errors**               | Is the API key valid and active? Does it have available credit/quota?                                                          | Verify API key validity and check the provider's dashboard for quota limits or billing issues.                                                                                          |           |
| **Tool validation errors after import** | Did you import a Claude Code agent? Did Factory validate the tools?                                                            | Claude Code tools like `Write` or `BrowseURL` do not have direct Factory equivalents. Map `Write` to Factory's granular tools (`Edit`, `Create`) or remove invalid tools from the list. |           |

---

### 📐 VISUALIZATION & FORMAT: Custom Model Workflow

This flow illustrates the necessary components and the data flow when deploying a BYOM setup.

```mermaid
graph TD
    A[USER: Droid CLI Session] --> B{Run /model command};
    B --> C[Check Configuration: ~/.factory/config.json];
    C --> D(Custom Models Array);
    D --> E{Model 1: Official API (e.g., GPT-5 Codex)};
    D --> F{Model 2: Generic API (e.g., Ollama)};
    E --> G[Factory CLI (OpenAI Provider Type)];
    F --> H[Factory CLI (Generic Provider Type)];
    G --> I[Official API Endpoint];
    H --> J[Local/Remote Proxy Endpoint];
    I --> K[Cost Tracking / Prompt Cache];
    J --> L[Local Inference Server];

    style A fill:#D0E0FF,stroke:#333;
    style C fill:#FFE0D0,stroke:#333;
    style K fill:#C0F0C0,stroke:#333;
```

Final Takeaways: Synthesized insights that are overt and cryptic (missed by superficial thinkers)

1.  **Overt:** The ability to configure models via `~/.factory/config.json` and switch instantly via `/model` confirms Factory's commitment to being **interface and vendor agnostic**. This prevents vendor lock-in and allows the engineering organization to always leverage the most performant or cost-effective model for a task.
2.  **Overt:** BYOK facilitates transparent billing, enabling users to view cost breakdowns and cache hit rates using the `/cost` command. This is essential for enterprise organizations that require **auditability and cost management** over AI resources.
3.  **Cryptic (Security Primitive):** The configuration file resides in the user's home directory (`~/.factory/config.json`) alongside other sensitive settings (like Custom Droids and MCP configurations). The fact that API keys are stored locally and are _not_ uploaded to Factory servers demonstrates a fundamental security primitive: **limiting the blast radius** of credential compromise to the individual machine, reinforcing Factory's SOC 2 compliance and security claims.
4.  **Cryptic (Technical Debt Inversion):** If low-performance models (below 30B parameters) are deployed via BYOK for complex tasks, the perceived "savings" in API cost are swiftly negated by increased **agent drift** and mandatory human intervention. The true cost of using a sub-optimal model is not the token price, but the **time wasted on refining mushy output** and compensating for limited reasoning.
5.  **Cryptic (System Orchestration):** The Droid agent's superior performance (e.g., achieving #1 on Terminal-Bench) relies not just on the underlying LLM, but on the **scaffolding** (system prompts, tool selection, planning) provided by Factory. Deploying a custom model requires ensuring that the model adheres to the API format expected by Factory's orchestration layer (e.g., `generic-chat-completion-api` for open-source models) to guarantee that the hard-won gains in Droid's agentic design translate effectively to the custom model interface.
