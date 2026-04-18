# What's New

Human-readable per-version changelog for RUNE. Pulled from [CURRENT_STATE](../context/CURRENT_STATE.md) Recent Changes and translated into user-facing release notes. `CURRENT_STATE.md` is the authoritative living memory; this page is the reader-friendly view.

RUNE is pre-alpha today (`v0.0.0a5`). API surfaces, configuration keys, and CRD field names are not stable.

## 2026-04-17 — Pre-PR E2E verification gap: Phase 0 spec

Documentation-only release: adds the binding contract for Level-1 E2E runs (spec landing via PR [#272](https://github.com/lpasquali/rune-docs/pull/272)) — one-command wrapper surface (`scripts/e2e.sh --mode compose|kind|cli`), `e2e-artifacts/` directory layout, `<!-- e2e-artifacts/summary.md -->` PR-body marker, and an agent-compatible background-execution recipe. Narrows the "HUMAN INTERVENTION REQUIRED" escape clause in the SOP so it only covers UX review of already-captured screenshots, not the old blanket fallback. Per-repo wrapper scripts ship in Phase 1 under the same epic; `rune-ci` content validator ships in Phase 2. Tracked under [rune-docs#271](https://github.com/lpasquali/rune-docs/issues/271).

## 2026-04-17 — Shared controllers test scheme (rune-operator)

Pure test refactor in `rune-operator`: new `controllersTestScheme(t)` helper (sync.Once-backed) replaces 11 inline `runtime.NewScheme()+AddToScheme(...)` blocks across controller tests. No production code change; coverage unchanged at 98.9% / 100% / 100% / 100% / 93.3% across the five measured packages. Merged as [rune-operator#113](https://github.com/lpasquali/rune-operator/pull/113).

## 2026-04-16 — Test & coverage audit

Cross-repo audit ([rune-docs#249](https://github.com/lpasquali/rune-docs/issues/249)) removed dead `scripts/*.py` files from rune-docs that were no longer referenced by CI (superseded by rune-ci composite actions), removed one no-op test in `rune`, and tightened the PyMarkdown scan in `rune-ci/docs-quality.yml` so failures now fail the job. Per-repo measure → classify → PR loop continues for remaining children.

## 2026-04-11 — FinOps telemetry and provisioning refactor (rune#251)

Major `rune` merge with user-visible changes:

- **`GET /v1/finops/simulate`** — cost-simulation endpoint with `max_cost_usd` gating and fine-grained event metrics per operation.
- **Nested provisioning** — provider-agnostic `{"providers": {"<type>": {...}}}` structure (was flat `vastai: true`). Migration: see [MIGRATION](MIGRATION.md).
- **SSE trace streaming** — real-time workflow event stream over HTTP Server-Sent Events.
- **Resource-leak fixes** — SQLite connection and async task leaks causing OOM on long-running benchmarks are fixed.
- **Token comparison** — switched from SHA-256 hashing to raw `hmac.compare_digest` (constant-time) per CodeQL hardening. Test-socket binds narrowed to `127.0.0.1`.

## 2026-04-11 — Standalone CodeQL workflows

All Python repos now use a standalone `.github/workflows/codeql.yml` (pinned `codeql-action`, PR/push/weekly, `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`). Where CodeQL default setup was previously enabled (`rune-ui`, `rune-charts`, `rune-audit`), it was set to `not-configured` so advanced SARIF upload works.

## 2026-04-10 — Cross-repo hygiene session

- `.claude/` added to `.gitignore` in all 8 repos (`rune-docs#199`, `rune#250`).
- `RuneBenchmark.spec.budget.maxCostUSD` lands in `rune-operator`; GET `/v1/finops/simulate` is used before job submit; `Ready=BudgetExceeded` on violation (`rune-operator#94`). CRD vendored into `rune-charts` (`bench.rune.ai` group, `v1alpha1`).
- External OSS docs for rune-audit: quickstart, `init`, `sr2 dashboard` command (HTML/JSON/Markdown with `--base-path` and `--previous` trend), index refresh (`rune-docs#212`, `#231`).

## 2026-04-09 — Project board automation (hybrid sync)

Project #1 Status is now managed entirely by GitHub's built-in Projects v2 workflows (Item added → Todo; Item closed → Done; Item reopened → In progress; PR merged → Done). `rune-ci/project-sync-logic.yml` slimmed to only: (a) add items manually since filter-based built-in is gated to Team/Enterprise, and (b) map Agent Lane from `<agent>_cli` labels.

## 2026-04-09 — Database roadmap (ADR 0006)

SQLite remains the shipped default. PostgreSQL is the accepted direction for multi-pod and audit-heavy deployments ([ADR 0006](../architecture/adrs/0006-storage-abstraction-postgres.md)). Postgres adapter / config / chart / docs work remains open. `DATABASE.md` and `DATABASE_HA.md` were rewritten to distinguish the current SQLite reality from the planned PostgreSQL rollout.

## 2026-04-07 — Backend abstraction

The Ollama-specific vocabulary across `rune` was generalized to **backend**:

- `ollama_url` → `backend_url`; `RUNE_OLLAMA_URL` → `RUNE_BACKEND_URL`.
- `run-ollama-instance` → `run-llm-instance`; `/v1/jobs/ollama-instance` → `/v1/jobs/llm-instance` (deprecated alias retained).
- `GET /v1/ollama/models` → `GET /v1/llm/models` (deprecated alias retained).
- `OllamaURL`/`OllamaWarmup` → `BackendURL`/`BackendWarmup` in the `RuneBenchmark` CRD.
- `AgentRunner.ask(...)` gained `backend_type` parameter; `ExistingBackendProvider` replaces `ExistingOllamaProvider`.

Migration notes: [MIGRATION](MIGRATION.md). All 22 agent drivers updated; `Holmes` driver now uses `get_backend()` rather than `OllamaClient`.

## 2026-04-06 — Foundation session

Large foundational merge (45+ PRs, 60+ issues closed):

- **Holmes agent decoupling** — `get_agent()` generic factory replaced `_get_holmes_runner()`; `agent` is now a required API field. Default agent is now a config-level setting in `rune.yaml`, not hardcoded.
- **Cost estimation abstraction** — `CostEstimation` supports VastAI, AWS, GCP, Azure, LocalHardware. `RuneBenchmark.spec.vastai=true` shim still works but the nested structure is preferred.
- **rune-audit buildout** — Python scaffolding, Pydantic models (SBOM, CVE, SLSA, VEX, Gate), GitHub Actions artifact collector, IEC 62443 ML4 evidence matrix, SLSA L3 provenance verifier, Typer+Rich CLI.
- **rune-airgapped buildout** — OCI bundle build, 7-phase bootstrap, K8s security manifests (PSA restricted, RBAC, NetworkPolicies), Helmfile deployment, offline cosign verification.
- **rune-ui fixes** — estimation env-var fallback (`RUNE_API_URL` → `RUNE_API_BASE_URL`), real configuration page, `/dashboard` route, `/healthz` endpoint, Solarized CSS, Python 3.13 base image for CVE-2025-13836.
- **Compliance rollout** — SPDX headers on all Python files (rune: 191; rune-ui: 3; rune-audit: 51), copyright standardization, ROLLBACK_PROCEDURES, SECURITY_TRAINING, `.coveragerc` explicit Tier 2/3 omissions.

For the full granular history, see [CURRENT_STATE](../context/CURRENT_STATE.md).
