 
# SYSTEM_PROMPT

 
## Core Identity

RUNE (Reliability Use-case Numeric Evaluator) is an AI model benchmarking and provisioning platform. It orchestrates benchmarkable DevOps/SRE operations, with optional Vast.ai provisioning for Ollama and agentic investigation via HolmesGPT.

 
## Essential References

Before starting any development task, read these documents in order:

1. **This file** (`SYSTEM_PROMPT.md`) — architecture, constraints, policies, and SOP.
2. **[CURRENT_STATE.md](CURRENT_STATE.md)** — WIP, recent changes, known issues.
3. **[Workstation Setup](../operations/WORKSTATION.md)** — Ubuntu 24.04 LTS provisioning with all required tooling (Python, Go, Docker, Kind, Helm, kubectl, scanners). Read if on a fresh machine or if a tool is missing.
4. **[Developer Guide](../usage/DEVELOPER_GUIDE.md)** — repo locations, environment setup, build/test/lint commands per repo, and concrete DoD validation steps (docker-compose, kind, CLI).
5. **[Coding Standards](CODING_STANDARDS.md)** — language-specific style, coverage floors, tier registry, agent filesystem layout.

All repositories live under `~/Devel/`: `rune/`, `rune-operator/`, `rune-ui/`, `rune-charts/`, `rune-docs/`, `rune-audit/`, `rune-airgapped/`.

 
## Core Constraints

- **Decoupling**: HolmesGPT is decoupled via a pluggable driver transport layer.
- **Thin Entrypoints**: CLI commands are lightweight; business logic resides in `rune_bench/`.
- **Reproducibility**: Benchmarks must be fully reproducible and documented.
- **Security**: Mandatory branch protection, signed provenance (SLSA L3), and vulnerability scanning.
- **Compatibility**: Maintain backward compatibility for CLI and public APIs.
- **Cost Safety**: Fail-closed cost estimation gates GPU provisioning. If estimation confidence drops below 95%, the operation is rejected.
- **Vulnerability Closure**: Always aim to resolve all known vulnerabilities, not just those above the CVSS 8.8 threshold. Risk acceptance is permitted **only** for vulnerabilities below the threshold where no fix exists. Vulnerabilities above the threshold with no upstream fix **must** be remediated by forking and patching the dependency in-house, tracked under a `dep-security-patch` issue label. See [VEX Register](../delivery/VEX.md) for exception tracking.

 
## Architecture Layers

| Layer | Location | Rule |
|---|---|---|
| CLI (Typer + Rich) | `rune/` | Thin shell only — no business logic |
| Orchestration | `rune_bench/workflows.py` | All business flow lives here |
| Agent drivers | `rune_bench/drivers/` | Pluggable transport layer (`DriverTransport`) |
| Agent runners | `rune_bench/agents/` | Grouped by domain (sre, research, legal, etc.) |
| LLM backends | `rune_bench/backends/` | Ollama, OpenAI, Bedrock |
| Resource providers | `rune_bench/resources/` | Vast.ai and existing-Ollama |
| HTTP API | `rune_bench/api_server.py` | stdlib `ThreadingHTTPServer` + SQLite |

 
## Key Protocols

- `DriverTransport`: Send action + params to a driver process.
- `AgentRunner`: Execute an agent investigation and return results.
- `LLMBackend`: Communicate with an LLM inference endpoint.
- `LLMResourceProvider`: Provision or locate compute for LLM inference.

 
## Conventions & Style

- **API Versioning**: Avoid bumping API versions (e.g., v1 to v2, or v1alpha1 to v1alpha2) unless it is a hard blocker. Prefer additive changes to existing schemas to minimize disruption to users.
- Raise `RuntimeError` with user-facing messages at boundaries.
- Normalize URLs in client/workflow helpers.
- Strip LiteLLM prefixes (`ollama/`) before API calls.
- Warmup unloads other running models for deterministic memory.
- For Vast.ai, prefer reusing matching running instances.
- Secrets (tokens, keys) must stay in env vars — never in `rune.yaml`.
- Offline testing: Mock all network/provider boundaries (97% coverage gate).
- No automated tests for real cloud resources (Vast.ai lifecycle is manual).

 
## Agent Workflow & Efficiency (Mandates)

- **Anti-Rogue Constraint (Halt & Report)**: Agents MUST NOT begin the "Execute" phase of a task (writing/modifying code) without first explicitly confirming in the chat that SOP Step 1 (Assign) and Step 2 (Isolate) have been fully completed. Agents MUST halt and ask the user for permission to proceed to execution, regardless of whether they are operating in autonomous (YOLO) mode.
- **ADR Protocol**: Any architectural change or cross-repository feature parity gap must be documented as an Architecture Decision Record (ADR) in `rune-docs/docs/architecture/adrs/`. Agents must explicitly declare the ADR number and title in `CURRENT_STATE.md` so subsequent agents are aware of the pending architectural requirement.
- **Branch Isolation**: Agents must operate in isolated feature branches. Only rebase and push the **assigned** branch. Never modify or rebase branches belonging to other agents or tasks.
- **Issue Attribution**: **Active** issues (those being worked on by an agent) must be assigned to **lpsquali**. Inactive/untouched issues can remain unassigned. Agents must **never** assign issues to themselves; they must ensure the issue is assigned to **lpsquali** upon starting work.
- **PR Workflow**: When handling Pull Requests, resolve merge conflicts by pulling the latest target branch (e.g., `main`) and rebasing the assigned branch onto it. Always wait for GitHub Actions/CI to finish before merging.
- **Minimal Commands**: Minimize turns by combining independent tool calls in parallel. Use `wait_for_previous: true` only when necessary for sequential dependencies.
- **Strategic Orchestration**: Use sub-agents (e.g., `codebase_investigator`, `generalist`) to compress complex or repetitive tasks, keeping the main context window lean and efficient.
- **Validation-First**: Every change must be verified via project-specific build/lint/test commands before completion.

 
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
2. **Run RUNE in kind (Kubernetes) mode** and test the change end-to-end.
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

- **Screenshots** of relevant UI or tool output.
- **Log snippets** that are clear, meaningful, and directly demonstrate the criterion is met (not raw multi-page dumps).
- **Before/after diffs** when the change alters measurable behavior (coverage numbers, scan results, config effects).
- **Command output** showing manual verification steps and their results.

A PR with unticked or unsubstantiated acceptance criteria must not be merged. If evidence cannot be produced for a criterion, explain why in the PR body and flag it for review.

 
## Standard Operating Procedure (SOP): Issue-to-Merge

1. **Assign**: Ensure active issue is assigned to **lpsquali** (never self-assign).
2. **Isolate**: Create feature branch; reproduction test-case first (for bugs).
3. **Research**: Read `rune-docs` as the single source of truth.
4. **Halt & Report**: Before writing/modifying code, explicitly halt and ask the user for permission to proceed (even in YOLO mode).
5. **Execute**: Minimize turns (parallel tool calls); 100% coverage target (no "cheating" mocks).
6. **Verify**: Mock all boundaries; 97% coverage floor; check ML4/SLSA L3 gates.
7. **PR & Rebase**: PR to target branch; rebase onto latest `main`; wait for all CI/Gaps to turn green.
8. **Persist**: Update `CURRENT_STATE.md` upon successful merge.

 
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
- Focused checks that FAIL → agent must not open the PR. Resolve or escalate to `lpasquali`.
- Full audits run in the background and do not block other work. Findings become issues for the next milestone.

 
## Tone & Style

- Professional, technical, and concise.
- Focus on reliability, automation, and security.
lock other work. Findings become issues for the next milestone.

 
## Tone & Style

- Professional, technical, and concise.
- Focus on reliability, automation, and security.
