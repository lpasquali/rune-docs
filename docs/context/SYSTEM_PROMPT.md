
# SYSTEM_PROMPT

 
## Core Identity

RUNE (Reliability Use-case Numeric Evaluator) is an AI agent benchmarking and compute provisioning platform. It orchestrates benchmarkable operations across 23+ agents spanning SRE, research, cybersecurity, legal/ops, and art/creative domains — with pluggable LLM backends and optional cloud GPU provisioning. RUNE is agent-neutral and backend-neutral by design; no single agent or backend is privileged in code.

 
## Essential References

Before starting any development task, read these documents in order:

1. **This file** (`SYSTEM_PROMPT.md`) — architecture, protocols, constraints, and SOP.
2. **[CURRENT_STATE.md](CURRENT_STATE.md)** — WIP, recent changes, known issues.
3. **[Workstation Setup](../operations/WORKSTATION.md)** — Ubuntu 24.04 LTS provisioning with all required tooling.
4. **[Developer Guide](../usage/DEVELOPER_GUIDE.md)** — repo locations, environment setup, build/test/lint commands, DoD validation steps.
5. **[Coding Standards](CODING_STANDARDS.md)** — language-specific style, coverage floors, tier registry, agent filesystem layout.

All repositories live under `~/Devel/`: `rune/`, `rune-operator/`, `rune-ui/`, `rune-charts/`, `rune-docs/`, `rune-audit/`, `rune-airgapped/`, `rune-ci/` (shared CI workflows and composite actions).

 
## Core Constraints

- **Agent Neutrality**: Code is agent-neutral. The default agent is a config-level setting (`rune.yaml`), not a code-level assumption. All 23+ agents are equal peers in the registry.
- **Backend Neutrality**: Code is backend-neutral. The default backend type is a config-level setting (`rune.yaml`), not a code-level assumption. Ollama, OpenAI, Bedrock, and future backends (including Gateway API Inference Extension / k8s-inference) are equal peers.
- **Decoupling**: All agents are decoupled via the pluggable `DriverTransport` protocol (stdio or HTTP).
- **Thin Entrypoints**: CLI commands are lightweight; business logic resides in `rune_bench/`.
- **Reproducibility**: Benchmarks must be fully reproducible and documented.
- **Security**: Mandatory branch protection, signed provenance (SLSA L3), and vulnerability scanning.
- **Pre-alpha**: Version 0.0.0a4. No backward compatibility guarantees. API shapes may change without notice.
- **Cost Safety**: Fail-closed cost estimation gates GPU provisioning. If confidence drops below 95%, the operation is rejected. Local-only workflows skip cost gates entirely.
- **Vulnerability Closure**: Always aim to resolve all known vulnerabilities, not just those above the CVSS 8.8 threshold. Risk acceptance is permitted **only** for vulnerabilities below the threshold where no fix exists. Vulnerabilities above the threshold with no upstream fix **must** be remediated by forking and patching the dependency in-house, tracked under a `dep-security-patch` issue label. See [VEX Register](../delivery/VEX.md) for exception tracking.

 
## Architecture Layers

| Layer | Location | Rule |
|---|---|---|
| CLI (Typer + Rich) | `rune/` | Thin shell only — no business logic |
| Orchestration | `rune_bench/workflows.py` | All business flow lives here |
| Agent drivers | `rune_bench/drivers/` | Pluggable transport layer (`DriverTransport`) |
| Agent runners | `rune_bench/agents/` | 23+ agents grouped by domain (sre, research, cybersec, legal, ops, art) |
| Agent registry | `rune_bench/agents/registry.py` | `get_agent(name, **kwargs)` factory with lazy import |
| LLM backends | `rune_bench/backends/` | `get_backend(type, url, **kwargs)` factory with lazy import |
| Resource providers | `rune_bench/resources/` | Vast.ai and existing-backend providers |
| Catalog | `rune_bench/catalog/defaults/` | `chains.csv` (agent catalog), `scopes.csv` (benchmark scopes) |
| Config | `rune_bench/common/config.py` | YAML loader with profile support and env-var injection |
| Cost estimation | `rune_bench/api_contracts.py` | `CostEstimationRequest` / `CostEstimationResponse` |
| HTTP API | `rune_bench/api_server.py` | stdlib `ThreadingHTTPServer` + SQLite |

 
## Extension Points (Protocols)

These four protocols are the critical extension points of the platform. All new integrations MUST implement one of these protocols.

### DriverTransport — `rune_bench/drivers/base.py`

Send an action + params to a driver process and return a result dict.

```python
class DriverTransport(Protocol):
    def call(self, action: str, params: dict) -> dict: ...
```

Two implementations: `StdioTransport` (subprocess, JSON over stdin/stdout) and `HttpTransport` (HTTP polling). Factory: `make_driver_transport(driver_name)` resolves via env vars (`RUNE_<NAME>_DRIVER_MODE`, `_CMD`, `_URL`).

### AgentRunner — `rune_bench/agents/base.py`

Execute an agent investigation and return results.

```python
class AgentRunner(Protocol):
    def ask(self, question: str, model: str, backend_url: str | None = None) -> str: ...
```

Supporting types: `AgentConfig` (per-agent auth/endpoint resolution), `AgentResult` (structured output with artifacts and metadata).

### LLMBackend — `rune_bench/backends/base.py`

Communicate with an LLM inference endpoint.

```python
class LLMBackend(Protocol):
    @property
    def base_url(self) -> str: ...
    def get_model_capabilities(self, model: str) -> ModelCapabilities: ...
    def list_models(self) -> list[str]: ...
    def list_running_models(self) -> list[str]: ...
    def normalize_model_name(self, model_name: str) -> str: ...
    def warmup(self, model_name: str, *, timeout_seconds: int = 120, ...) -> str: ...
```

Supporting types: `ModelCapabilities` (context window, max tokens, raw metadata), `BackendCredentials` (api_key, base_url, vendor-specific extras).

### LLMResourceProvider — `rune_bench/resources/base.py`

Provision or locate compute for LLM inference.

```python
class LLMResourceProvider(Protocol):
    def provision(self) -> ProvisioningResult: ...
    def teardown(self, result: ProvisioningResult) -> None: ...
```

`ProvisioningResult` returns `backend_url` (endpoint) + `model` + `provider_handle` (opaque ID for teardown).

 
## Factory Registries

Both agents and backends use the same pattern: custom registrations shadow built-in entries, lazy `importlib.import_module` for built-ins.

### Agent Registry — `rune_bench/agents/registry.py`

```python
get_agent(name, **kwargs) -> AgentRunner     # Resolve and instantiate
register_agent(name, factory, required_config=[...])  # Custom override
list_agents() -> list[str]                   # All known agent names
```

Resolution: custom registry -> built-in map -> ValueError. Config resolution: `resolve_agent_config(name, kwargs)` merges CLI kwargs with env vars. Missing required config raises RuntimeError with the expected env var name.

### Backend Registry — `rune_bench/backends/__init__.py`

```python
get_backend(backend_type, base_url, **kwargs) -> LLMBackend  # Resolve and instantiate
register_backend(name, cls)                  # Custom override
list_backends() -> list[str]                 # All known backend types
```

Built-in: `ollama` -> `OllamaBackend`. Planned: `k8s-inference` (Gateway API Inference Extension). Resolution order mirrors the agent registry.

 
## Driver Ecosystem

All 23+ agents communicate through `DriverTransport`. Every agent is equal — no agent has special code paths. Agents are classified by tier in `chains.csv`:

| Tier | Meaning | Coverage | Examples |
|---|---|---|---|
| 1 | OSS, fully testable | 100% target, measured | K8sGPT, HolmesGPT, LangGraph, PentestGPT, Dagger, CrewAI |
| 2 | Partial API / freemium | Best-effort, may omit | Metoro, Elicit, ComfyUI, BurpGPT, Consensus |
| 3 | Closed SaaS, no public API | Protocol-only, excluded | PagerDuty AI, Perplexity, Midjourney, Radiant, Harvey AI |

Scopes: SRE, Research, Art/Creative, Cybersec, Legal/Ops. The `chains.csv` `Scope` column maps to `rune_bench/agents/<scope>/` directories.

 
## Catalog System

- **`chains.csv`**: Authoritative agent catalog. Defines agent name, tier, scope, rating, capabilities, and recommended Ollama model. This is the single source of truth for which agents exist and their classification.
- **`scopes.csv`**: Benchmarking scope definitions with evaluation questions per domain.
- Both files live in `rune_bench/catalog/defaults/` and are shipped as package data.

 
## Config System — `rune.yaml`

Precedence (highest wins):

1. **CLI flags** (`--backend-url`, `--agent`, `--model`, etc.)
2. **Environment variables** (`RUNE_BACKEND_URL`, `RUNE_MODEL`, etc.)
3. **Project-level config** (`./rune.yaml` or `./rune.yml`)
4. **User-level config** (`~/.rune/config.yaml`)
5. **Built-in defaults** (Typer `default=` values)

Key config fields: `backend_type` (default: `ollama`), `backend_url`, `model`, `agent` (resolved at call site, not hardcoded), `kubeconfig`, `vastai`, profiles.

- **Profiles**: Named config blocks (`production`, `staging`, `local`, `ci`, `test`). Activate via `--profile` or `RUNE_PROFILE`.
- **Secrets exclusion**: API tokens, `VAST_API_KEY`, and all credentials are intentionally excluded from the YAML schema. They must remain in environment variables.
- **`rune init`**: Generates a starter `rune.yaml` from `INIT_TEMPLATE`.

### Resolution Hierarchies

- **Agent**: CLI `--agent` -> `rune.yaml` `agent:` field -> error (no silent default in code)
- **Backend**: CLI `--backend-type` -> `rune.yaml` `backend_type:` field -> error (no silent default in code)
- **Backend URL**: CLI `--backend-url` -> `rune.yaml` `backend_url:` field -> env `RUNE_BACKEND_URL` -> provisioned dynamically

 
## Cost Safety Gates

Cost estimation is fail-closed. The `CostEstimationRequest` / `CostEstimationResponse` contract enforces:

- **Confidence threshold**: If `confidence_score < 0.95`, the operation is rejected.
- **Cost drivers**: `vastai`, `aws`, `gcp`, `azure`, `local` — each with distinct estimation logic.
- **Local bypass**: Local-only workflows (`vastai: false`, no cloud provider) skip cost gates entirely.
- **Local cost model**: Supports TDP-based energy cost estimation for on-premises hardware.

 
## API Contracts — `rune_bench/api_contracts.py`

Transport-agnostic dataclasses used by CLI and HTTP API:

- `RunLLMInstanceRequest` — provision an LLM instance (`backend_url`, `backend_type`, Vast.ai parameters)
- `RunAgenticAgentRequest` — execute an agent query (`agent`, `model`, `backend_url`, `backend_type`)
- `RunBenchmarkRequest` — full benchmark run (combines provisioning + agent execution)
- `CostEstimationRequest` / `CostEstimationResponse` — cost gates

All contracts use `backend_url` (not `ollama_url`) and `backend_type` (default `"ollama"`) to remain backend-neutral.

 
## Conventions & Style

- Raise `RuntimeError` with user-facing messages at boundaries.
- Normalize URLs in client/workflow helpers.
- Strip LiteLLM prefixes (`ollama/`) before API calls via `normalize_model_name()`.
- Warmup unloads other running models for deterministic memory.
- For Vast.ai, prefer reusing matching running instances.
- Secrets (tokens, keys) must stay in env vars — never in `rune.yaml`.
- Offline testing: Mock all network/provider boundaries (97% coverage gate).
- No automated tests for real cloud resources (Vast.ai lifecycle is manual).
- Optional extras in `pyproject.toml` (`holmes`, `vastai`, `catalog`, `all`, `dev`) keep the base install minimal.

 
## Agent Workflow & Efficiency (Mandates)

- **Label Guard**: Before starting work on an existing issue, agents MUST verify the issue carries a label matching their identity (`claude_cli`, `gemini_cli`, or `copilot_cli`). If the label is missing or belongs to a different agent, the agent MUST halt and ask the user for permission — even in YOLO mode.
- **Agent Label Isolation**: During parallel agent execution, labels provide a lightweight ownership fence that prevents cross-contamination:
    1. **Label on Assign**: When an agent begins work on an issue, it MUST add the label `<agent_name>_cli` (e.g., `claude_cli`, `copilot_cli`, `cursor_cli`) to the issue.
    2. **Label on Draft PR**: All Draft PRs created by an agent MUST carry the same `<agent_name>_cli` label.
    3. **Ownership Fence**: An agent MUST only work on issues, Draft PRs, and PRs that bear its own `<agent_name>_cli` label. It MUST NOT modify, rebase, or push to branches belonging to another agent's labeled items.
    4. **Label Creation**: If the label does not exist in the repo, the agent must create it before applying it.
- **Anti-Rogue Constraint (Halt & Report)**: Agents MUST NOT begin the "Execute" phase of a task (writing/modifying code) without first explicitly confirming in the chat that SOP Step 1 (Assign) and Step 2 (Isolate) have been fully completed. Agents MUST halt and ask the user for permission to proceed to execution, regardless of whether they are operating in autonomous (YOLO) mode.
- **ADR Protocol**: Any architectural change or cross-repository feature parity gap must be documented as an Architecture Decision Record (ADR) in `rune-docs/docs/architecture/adrs/`. Agents must explicitly declare the ADR number and title in `CURRENT_STATE.md` so subsequent agents are aware of the pending architectural requirement.
- **Branch Isolation**: Agents must operate in isolated feature branches. Only rebase and push the **assigned** branch. Never modify or rebase branches belonging to other agents or tasks.
- **Issue Attribution**: **Active** issues (those being worked on by an agent) must be assigned to **lpasquali**. Inactive/untouched issues can remain unassigned. Agents must **never** assign issues to themselves; they must ensure the issue is assigned to **lpasquali** upon starting work.
- **Project Board Tracking**: All issues and Epics must be tracked on GitHub project #1. The sync model is **hybrid** — Status field is owned by Projects v2 built-in workflows (configured in the project UI), Agent Lane is owned by the `rune-ci` reusable workflow. See [rune-docs#187](https://github.com/lpasquali/rune-docs/issues/187) for the design rationale.
    - **Auto-add to board**: Handled by `rune-ci/.github/workflows/project-sync-logic.yml` (calls `addProjectV2ItemById` on every `issues` / `pull_request` event). Filter-based "Auto-add to project" is gated to GitHub Team / Enterprise plans, so we do this manually. As a fallback for items created outside that flow, agents can run `gh project item-add 1 --owner lpasquali --url <ISSUE_URL>`.
    - **Creation** → Status: **Todo**. Set automatically by the built-in **"Item added to project"** workflow. Agents should verify the item lands on the board.
    - **Starting work** → Status: **In progress**. **Manual transition** by the agent (no built-in covers this). Use the GraphQL `updateProjectV2ItemFieldValue` mutation against the `Status` field, or the project board UI. Trigger this when SOP Steps 1–2 (Assign + Isolate) are complete.
    - **Needs human intervention** → Status: **Review**, Agent Lane: **Human**. **Manual transition** by the agent. When an agent cannot proceed without human input (approval, decision, manual step), set both fields.
    - **Closed / merged** → Status: **Done**. Set automatically by the built-in **"Item closed"** and **"Pull request merged"** workflows.
    - **Reopened** → Status: **In progress**. Set automatically by the built-in **"Item reopened"** workflow. (Reopens typically resume active work, so the item lands back in the active column rather than re-queuing at Todo.)
    - **Agent Lane** (Claude / Gemini / Copilot / Human): Set automatically by `rune-ci/project-sync-logic.yml` based on the `<agent>_cli` label on the issue or PR. Adding/removing the label updates the lane on the next event.
- **PR Workflow**: When handling Pull Requests, resolve merge conflicts by pulling the latest target branch (e.g., `main`) and rebasing the assigned branch onto it. Always wait for GitHub Actions/CI to finish before merging. **Your PR bodies must strictly match the template**, checking exactly one DoD level and including all required sections (Acceptance Criteria Evidence, Audit Checks, Breaking Changes) or the `pr-body-check` CI gate will fail the build.
- **PR Body Template** (enforced by CI in all repos):
  ```markdown
  ## Summary
  <bullet points>

  Closes #NNN

  ## DoD Level
  - [ ] **Level 1** — Full Validation
  - [x] **Level 2** — Test Infrastructure
  - [ ] **Level 3** — Documentation Validation

  ## Acceptance Criteria Evidence
  - [x] <criterion with evidence>

  ## Audit Checks
  No triggers fired.
  <!-- OR: | Check | Result | ... | `cyber check:api` | PASS | -->

  ## Breaking Changes
  None.

  ## Test plan
  - [x] <test with evidence>
  ```
  The `pr-body-check` CI gate validates: issue reference (`Closes #NNN`), exactly one checked DoD level (`[x] **Level N**`), all four required sections present, and audit results containing `PASS`, `FAIL`, or `No triggers fired`.
- **Minimal Commands**: Minimize turns by combining independent tool calls in parallel. Use `wait_for_previous: true` only when necessary for sequential dependencies.
- **Strategic Orchestration**: Use sub-agents (e.g., `codebase_investigator`, `generalist`) to compress complex or repetitive tasks, keeping the main context window lean and efficient.
- **Validation-First**: Every change must be verified via project-specific build/lint/test commands before completion.
- **Issue Closure Gate**: An issue MUST NOT be closed while any associated PR (including Draft PRs) remains open. Before closing an issue, the agent MUST verify that every linked PR is either merged or closed. If any PR is still open, the issue stays open — no exceptions.
- **Epic Lifecycle**: An Epic issue MUST NOT be closed until **every** child issue listed in its body is closed **and** every associated PR (including Draft PRs) is merged or closed. Before closing an Epic, the agent MUST query all child issue references and verify each is in `CLOSED` state, and verify no open PRs or Draft PRs reference the Epic or its children. If any child issue or PR is still open, the Epic stays open — no exceptions. When creating new issues under an existing Epic, add the `Closes` reference in the child and list it in the Epic body.

 
## Documentation Expedite Channel

Documentation changes to `rune-docs` run on a **parallel expedited channel**, independent of feature milestones. Because `rune-docs` is the single source of truth consumed by all agents at boot, docs PRs must never be blocked behind feature milestone timelines.

- Docs PRs are reviewed and merged on their own cadence.
- Any agent that discovers stale, missing, or incorrect documentation **must** open a docs PR immediately, regardless of its current milestone assignment.
- Docs PRs do not require the full deployment-mode DoD (docker-compose/kind/CLI) — they require only build validation (`mkdocs build`) and peer review.
- Feature milestones reference docs but do not gate them.

 
## Definition of Done (Pre-PR Gate)

The scope of validation must be **proportional to the scope of the change**. Not every PR needs a full Kubernetes deployment. Use the appropriate level below.

### Level 1 — Full Validation (default)

Applies to: changes that affect runtime behavior, APIs, drivers, backends, agents, Helm charts, or Dockerfiles.

1. **Run RUNE in docker-compose mode** and test the change end-to-end.
   - *Note (Networking):* When writing or debugging Docker `healthcheck` commands, prefer using explicit loopback addresses (e.g., `127.0.0.1`) instead of `localhost`.
   - *Note (Volumes):* When mounting named volumes to non-root containers, always explicitly `mkdir -p` and `chown` the mount point path inside the `Dockerfile` before runtime; otherwise, the Docker daemon will create the volume folder as `root`, causing permission denied errors.
2. **Run RUNE in kind (Kubernetes) mode** and test the change end-to-end.
   - *Note (Prerequisites):* Verify the existence of `kind`, `kubectl`, and `helm` before testing. If missing, download and install them headlessly. Images must be loaded into the cluster (`kind load docker-image ...`) before installing the chart.
3. **Run RUNE in standalone CLI mode** and test the change end-to-end.
4. **Check for breaking changes** in component management:
   - API version changes (additive vs. breaking).
   - Persistent data compatibility (SQLite schemas, volume mounts).
   - Cross-component contract changes (DriverTransport, AgentRunner, LLMBackend, LLMResourceProvider).
5. **Dependency CVE audit**: If the change introduces or updates any dependency, the agent **must** run a vulnerability scan (`pip-audit`, `grype`, or equivalent) against the new dependency set **before** opening the PR. *Never use `safety` for Python SCA as it is deprecated and paywalled; rely exclusively on `pip-audit`.* If any new CVE is introduced by the change, the agent **must not** open the PR. Instead, the agent must:
   - Attempt to resolve the CVE (upgrade to a patched version, find an alternative dependency, or fork-and-patch).
   - If resolution is not possible, stop and report the CVE exposure to `lpasquali` with the dependency name, CVE ID, CVSS score, and reason resolution failed.
   - A PR that knowingly introduces a new CVE into the project is **never acceptable**.

### Level 2 — Test Infrastructure Validation

Applies to: changes that only affect test configuration, CI workflows, coverage settings, linter configs, or dev tooling — with no runtime code changes.

1. **Run the full test suite** (`pytest`, `go test ./...`, etc.) and verify it passes with the new configuration.
2. **Verify coverage** is not degraded — if the change expands measurement scope (e.g., removing coverage omits), confirm that sufficient tests exist for the newly-measured code. If coverage drops below the floor, write or update tests before opening the PR.
3. **Check for unintended side effects** — does the config change break any CI job? Does it change what gets measured, linted, or scanned in a way that could mask regressions?

### Level 3 — Documentation Validation

Applies to: changes that only affect `rune-docs` content (Markdown, MkDocs config, diagrams).

1. **Build validation**: `mkdocs build --strict` must pass.
2. **Peer review**: Content must be reviewed for accuracy.

### Choosing the Right Level

When in doubt, use Level 1. If the change touches only test infrastructure or config files with zero runtime impact, Level 2 is sufficient. If the change is documentation-only, Level 3 applies. A change that spans multiple categories uses the highest applicable level.

Unit tests and CI green alone do **not** satisfy the Definition of Done at any level.

### PR Evidence Requirements

Every issue with a test plan or acceptance criteria must have **attached evidence** for each ticked checkbox. CI-produced artifacts (green checks, coverage reports in CI logs) count automatically. For anything CI does not produce, the agent or developer **must** attach:

- **Screenshots** of relevant UI or tool output. Screenshots are **mandatory** for `rune-docs` and `rune-ui` which are consumed by browsers. AI agents MUST proceed with headless tools (e.g., `playwright screenshot <url> <output.png>`) to take screenshots. **Whenever a screenshot is taken, you MUST subsequently analyze the image to confirm the state of the UI or docs matches the expected results (e.g., new icon is there, new text, changed theme) before attaching it as evidence.** If this is fundamentally impossible, open all PRs as a Draft and append a bold warning: **HUMAN INTERVENTION REQUIRED: Please capture and upload the required DoD screenshots before merging.** Any other tool can have logs and text output pasted nicely in issues (if compliant with our standards).
- **Log snippets** that are clear, meaningful, and directly demonstrate the criterion is met (not raw multi-page dumps).
- **Before/after diffs** when the change alters measurable behavior (coverage numbers, scan results, config effects).
- **Command output** showing manual verification steps and their results.

A PR with unticked or unsubstantiated acceptance criteria must not be merged. If evidence cannot be produced for a criterion, explain why in the PR body and flag it for review.

 
## Standard Operating Procedure (SOP): Issue-to-Merge

1. **Assign**: Ensure active issue is assigned to **lpasquali** (never self-assign). **Perform Label Guard check**: verify the issue carries a label matching your identity (`claude_cli`, `gemini_cli`, or `copilot_cli`).
2. **Isolate**: Create feature branch; reproduction test-case first (for bugs).
3. **Research**: Read `rune-docs` as the single source of truth.
4. **Halt & Report**: Before writing/modifying code, explicitly halt and ask the user for permission to proceed (even in YOLO mode).
5. **Execute**: Minimize turns (parallel tool calls); 100% coverage target (no "cheating" mocks).
6. **Verify**: Mock all boundaries; 97% coverage floor; check ML4/SLSA L3 gates.
7. **E2E Test**: For Level 1 DoD, run the change through docker-compose, kind, and standalone CLI modes. Attach evidence (logs, screenshots) to the PR for each mode tested.
8. **PR & Rebase**: PR to target branch; rebase onto latest `main`; wait for all CI/Gaps to turn green.
9. **Persist**: Update `CURRENT_STATE.md` upon successful merge.

 
## Audit Agents

Legal and cybersecurity audits run as background agents, proportional to the change. Full specs for each audit type are in **[Audit Agents](../delivery/AUDIT_AGENTS.md)**. This section defines **when** to trigger them.

### Automatic Triggers (mandatory)

Agents **must** run the appropriate focused check when they detect these changes. This is part of the DoD — not optional. Focused checks that return FAIL **block the PR**.

| Change detected | Check to run |
|---|---|
| Dependency added/bumped (`requirements.txt`, `pyproject.toml`, `go.mod`) | `legal check:dep <pkg>` + `cyber check:dep <pkg>` |
| New agent integration or driver | `legal check:integration <agent>` |
| New build/CI tool introduced | `legal check:tool <tool>` |
| API endpoint, auth, or CRD schema changed | `cyber check:api` |
| CI workflow modified (`.github/workflows/`) | `cyber check:supply-chain` |
| Dockerfile or base image changed | `legal check:dep <image>` + `cyber check:supply-chain` |
| VEX statement added/modified | `cyber check:vex` |
| Helm chart values changed | `cyber check:api` |

### Cadence

| When | What |
|---|---|
| **Every PR** (when triggers above fire) | Focused checks only |
| **Milestone exit / quarterly / on demand** | Full `legal check` + full `cyber check` |

### Key rules

- **License contamination = always `priority/p0`** — a license problem can invalidate the entire project.
- Focused checks that FAIL -> agent must not open the PR. Resolve or escalate to `lpasquali`.
- Full audits run in the background and do not block other work. Findings become issues for the next milestone.

 
## Tone & Style

- Professional, technical, and concise.
- Focus on reliability, automation, and security.
