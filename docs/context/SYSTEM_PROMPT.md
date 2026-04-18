
# SYSTEM_PROMPT

## Core identity

RUNE (Reliability Use-case Numeric Evaluator) is an AI agent benchmarking and compute provisioning platform across 23+ agents (SRE, research, cybersecurity, legal/ops, art/creative) with pluggable LLM backends and optional cloud GPU provisioning. **Agent-neutral and backend-neutral**: no agent or backend is privileged in code; defaults live in `rune.yaml`, not hardcoded.

## Read first (in order)

1. **This file** — mandates, SOP, constraints.
2. **[CURRENT_STATE.md](CURRENT_STATE.md)** — WIP and known issues.
3. **[Workstation Setup](../operations/WORKSTATION.md)** — Ubuntu 24.04 tooling.
4. **[Developer Guide](../usage/DEVELOPER_GUIDE.md)** — repos, env, build/test/lint, deployment DoD steps.
5. **[Coding Standards](CODING_STANDARDS.md)** — style, coverage floors, tier layout.
6. **[Audit Agents](../delivery/AUDIT_AGENTS.md)** — legal/cyber checks (when and how).
7. **[External Links](../reference/EXTERNAL_LINKS.md)** — official docs and spec URLs for every standard RUNE complies with and every tool RUNE uses; canonical source for citation URLs.

Repos under `~/Devel/`: `rune/`, `rune-operator/`, `rune-ui/`, `rune-charts/`, `rune-docs/`, `rune-audit/`, `rune-airgapped/`, `rune-ci/`.

## Core constraints

- **Decoupling**: Agents use pluggable **`DriverTransport`** (stdio or HTTP).
- **Thin CLI**: `rune/` is a shell; business logic in **`rune_bench/`**.
- **Reproducibility**: Benchmarks reproducible and documented.
- **Security**: Branch protection, SLSA L3-style provenance, scanning.
- **Pre-alpha** (0.0.0a4): no API stability guarantee.
- **Cost safety**: Fail-closed GPU cost estimation; **`confidence_score < 0.95`** rejects; local-only workflows skip gates.
- **Vulnerabilities**: Resolve known issues; risk acceptance only below CVSS 8.8 with no fix; above threshold with no upstream fix → fork/patch + `dep-security-patch` label. [VEX Register](../delivery/VEX.md).

## Architecture (where things live)

| Layer | Location | Rule |
|---|---|---|
| CLI | `rune/` | Thin only |
| Orchestration | `rune_bench/workflows.py` | Business flow |
| Drivers | `rune_bench/drivers/` | `DriverTransport` |
| Agents | `rune_bench/agents/` | By scope; registry `registry.py` |
| Backends | `rune_bench/backends/` | `get_backend(...)` |
| Resources | `rune_bench/resources/` | Vast.ai, etc. |
| Catalog | `rune_bench/catalog/defaults/` | `chains.csv`, `scopes.csv` |
| Config | `rune_bench/common/config.py` | YAML + profiles |
| Cost contracts | `rune_bench/api_contracts.py` | `CostEstimation*` |
| HTTP API | `rune_bench/api_server.py` | ThreadingHTTPServer + storage |

## Extension points (protocols)

New integrations MUST implement one protocol (signatures in source):

| Protocol | Module | Role |
|---|---|---|
| **DriverTransport** | `rune_bench/drivers/base.py` | `call(action, params) -> dict` — stdio/HTTP factories via `RUNE_<NAME>_DRIVER_*` env |
| **AgentRunner** | `rune_bench/agents/base.py` | `ask(...)` + `AgentConfig` / `AgentResult` |
| **LLMBackend** | `rune_bench/backends/base.py` | Models, warmup, `normalize_model_name`, etc. |
| **LLMResourceProvider** | `rune_bench/resources/base.py` | `provision` / `teardown` → `ProvisioningResult` |

**Registries**: `get_agent` / `get_backend` (and `register_*`); custom entries shadow built-ins; lazy `importlib` for built-ins. Missing required config → `RuntimeError` with env hint.

## Catalog & drivers

**`chains.csv`**: Authoritative agents, tier (1 = OSS measurable, 2 = partial API, 3 = closed/protocol-only), scope, capabilities. **`scopes.csv`**: Benchmark scopes. Shipped as package data. Scope → `rune_bench/agents/<scope>/`.

## Config — `rune.yaml`

**Precedence** (high → low): CLI → env → `./rune.yaml` → `~/.rune/config.yaml` → Typer defaults.

**Resolution**: Agent/backend: CLI → YAML → **error** (no silent code default). Backend URL: CLI → YAML → `RUNE_BACKEND_URL` → dynamic provision.

**Profiles**: `--profile` / `RUNE_PROFILE`. **Secrets**: never in YAML — env only. **`rune init`**: starter from `INIT_TEMPLATE`.

## Cost gates & API contracts

Fail-closed **`CostEstimationRequest` / `CostEstimationResponse`**; drivers include `vastai`, cloud, `local` (local skips gates; TDP energy model supported).

**Contracts** (all use `backend_url`, `backend_type`): `RunLLMInstanceRequest`, `RunAgenticAgentRequest`, `RunBenchmarkRequest`, `CostEstimation*`.

## Conventions

- `RuntimeError` with clear messages at boundaries; normalize URLs; strip LiteLLM `ollama/` via `normalize_model_name`.
- Warmup deterministic memory; reuse matching Vast instances when sensible.
- Mock network/provider in tests (**97%** coverage floor target); no automated real cloud lifecycle tests.
- Optional `pyproject.toml` extras keep base install small (`holmes`, `vastai`, `catalog`, `all`, `dev`).

## Ownership, labels, and board (mandatory)

### Take issue (user-directed)

If the user explicitly asks you to take / implement / work on a specific issue (number, link, or clear reference), that **is** permission to own it. **Do not** halt only because labels are missing or another agent’s `*_cli` label is present.

1. Assign issue to **`lpasquali`** (never self-assign).
2. Add **your** `<agent>_cli` (`claude_cli`, `gemini_cli`, `copilot_cli`, `cursor_cli`); create label in repo if missing.
3. Remove **other** agent `*_cli` labels among those four so **`project-sync-logic.yml`** maps **Agent Lane** unambiguously (first matching label wins).
4. **Isolate** (feature branch; repro first for bugs) — then continue SOP without asking to approve label fixes.
5. Ensure item on **GitHub project #1** (verify auto-add or `gh project item-add 1 --owner lpasquali --url <ISSUE_URL>`), then set **Status → In progress** manually. **Relabeling updates Agent Lane only — not Status.**

### Label isolation & PRs

- Draft/production PRs you open MUST carry the same `<agent>_cli` label.
- **Ownership fence**: Only work on issues/PRs with **your** `*_cli` label; do not rebase/push another agent’s labeled branches/items.
- **Active** issues you work on stay assigned to **lpasquali**.

### Project #1 — Status vs automation

**`rune-ci` `project-sync-logic.yml`** only **adds** items to project #1 and sets **Agent Lane** from `*_cli` labels. It **never** sets **Status**.

| Status | How |
|---|---|
| **Todo** | Built-in when item added to project |
| **In progress** | **You** set (GraphQL or UI) when **Assign + Isolate** are done (from **Todo**); **or** built-in **Item reopened** workflow |
| **Review** (+ **Human** lane) | **You** set when blocked on human input |
| **Done** | Built-in on issue close / PR merge |

Design: [rune-docs#187](https://github.com/lpasquali/rune-docs/issues/187). **Agent lanes**: Claude, Gemini, Copilot, Cursor, Human — synced from labels (`human` label for Human lane where applicable).

### Other process mandates

- **Anti-Rogue**: Do not start **Execute** (editing code) until chat confirms SOP 1–2 complete **and** user permits proceed (even in YOLO).
- **ADRs**: Architectural / cross-repo gaps → ADR in `docs/architecture/adrs/`; note ADR id + title in **CURRENT_STATE.md**.
- **Branches**: Feature branch only; rebase/push **your** assigned branch.
- **PR workflow**: Rebase on latest `main`; wait for CI green. PR body MUST pass **`pr-body-check`**: copy the repo’s **`.github/PULL_REQUEST_TEMPLATE.md`** (layout is shared across `~/Devel/*` repos) — `Closes #NNN`, exactly **one** `[x]` DoD level, **Acceptance Criteria Evidence**, **Audit Checks**, **Breaking Changes**, **Test plan**; audit line must include `PASS`, `FAIL`, or `No triggers fired`.
- **Efficiency**: Parallel tool calls when independent; sub-agents for heavy investigation; validate with repo commands before claiming done.
- **Issue closure**: Do not close an issue while any linked PR (including Draft) is open.
- **Epics**: Close only when every listed child issue is closed **and** linked PRs merged or closed; link new children with `Closes` + Epic body list.

## Documentation expedite

`rune-docs` merges on its own cadence. Stale docs → PR immediately. Docs PRs: **`mkdocs build --strict`** + review — not blocked on feature milestones.

## Definition of Done (pre-PR)

Pick the **highest** applicable level. **CI green alone is not enough.**

- **Level 1** (runtime, API, drivers, agents, charts, Docker): docker-compose E2E; kind E2E (`kind`/`kubectl`/`helm`, `kind load docker-image`); standalone CLI E2E; breaking-change review (API, persistence, protocols). **Deps**: run **`pip-audit`** (not `safety`) before PR; never ship a known new CVE — fix, replace, fork-patch, or escalate to `lpasquali`. Healthchecks: prefer `127.0.0.1`; volume mounts: `chown` in image for non-root. See **[E2E_TESTING.md](../usage/E2E_TESTING.md)** for the binding E2E contract, one-command entrypoint, and evidence layout.
- **Level 2** (tests/CI/coverage/linter config only, no runtime code): full test suite; coverage not degraded; no CI regressions.
- **Level 3** (`rune-docs` content only): `mkdocs build --strict` + review.

**Evidence**: Every checked acceptance criterion needs proof (CI logs count where applicable). **rune-docs** / **rune-ui**: screenshots mandatory when UI matters — headless capture via the [E2E_TESTING.md](../usage/E2E_TESTING.md) recipe + **you** verify the image. If headless capture is impossible in the current environment, open an `area/infra` issue before the PR — not a Draft PR. Draft PR + **HUMAN INTERVENTION REQUIRED** is reserved for UX review of an already-captured screenshot, not for skipping capture. Also logs, diffs, command output as appropriate.

## SOP: issue → merge

1. **Assign** — `lpasquali` + **Take issue** label steps if user-directed (no halt on label mismatch).
2. **Isolate** — branch (+ repro for bugs).
3. **Research** — `rune-docs` + code.
4. **Halt** — confirm 1–2 done; user OK to **Execute**.
5. **Execute** — minimal scope; strong tests.
6. **Verify** — mocks at boundaries; coverage/SLSA expectations.
7. **E2E** — run `scripts/e2e.sh --mode <compose|kind|cli|all>` for every applicable mode per [E2E_TESTING.md](../usage/E2E_TESTING.md); paste the produced `e2e-artifacts/summary.md` verbatim into the PR body (marker `<!-- e2e-artifacts/summary.md -->` must survive).
8. **PR** — template + rebase; green CI.
9. **Persist** — **CURRENT_STATE.md** after merge.

## Audit Agents

When changes match a row, run the checks before PR; **FAIL → no PR**. Full detail: **[Audit Agents](../delivery/AUDIT_AGENTS.md)**.

| Change | Checks (examples) |
|---|---|
| Deps (`requirements.txt`, `pyproject.toml`, `go.mod`) | `legal check:dep` + `cyber check:dep` |
| New agent/driver | `legal check:integration` |
| API/auth/CRD | `cyber check:api` |
| `.github/workflows/` | `cyber check:supply-chain` |
| Dockerfile / base image | `legal check:dep` + `cyber check:supply-chain` |
| Helm values | `cyber check:api` |

License problems → **`priority/p0`**. Milestone / quarterly: full legal + cyber audits as needed.

## Tone

Professional, concise; optimize for reliability, automation, and security.
