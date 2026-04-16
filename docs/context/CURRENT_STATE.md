
# CURRENT_STATE

 
## Incident Log (ML4 Compliance)
- **Version Baseline Reset**: An erroneous release was previously triggered with incorrect versioning (e.g., `v0.1.0`). To maintain strict ML4 traceability and signed provenance, the ecosystem baseline has been forcefully reset. The erroneous tags are marked as "Yanked" in GitHub Releases. Current correct versions are listed below.

## Living Memory

RUNE is currently in active pre-alpha development for its core LLM backends, agentic workflows, and compute provisioning integrations. It is **not yet production-ready**.

 
## Freshness Policy

This file must be updated whenever system state evolves (per CODING_STANDARDS.md "Atomic Persistence"). If information here conflicts with what you observe in the code or git history, trust what you observe now — then update this file to match reality.

Last updated: **2026-04-16** (audit: test/coverage epic **#249** / rune-docs **#251**).

 
## Version Baseline

| Repo | Version | Commits | Status |
|---|---|---|---|
| rune | `v0.0.0a5` | 280 | Active development |
| rune-operator | `v0.0.0a0` (yanked `v0.1.0`) | 42 | Active development |
| rune-ui | `v0.0.0a0` (yanked `v0.1.1`) | 34 | Active development |
| rune-charts | `0.0.0-a0` (yanked `v0.1.1`) | 26 | Active development |
| rune-docs | `v0.0.0a3` (yanked `v0.1.0`, legacy `v0.0.0a3`–`v0.0.0a5`, `v0.0.0a6`) | 131 | Active development |
| rune-airgapped | unversioned | 14 | Pre-scaffolding |
| rune-audit | `v0.0.0a0` (yanked `v0.1.1`) | 15 | Scaffolding complete |

 
## Recent Changes

### 2026-04-16 — Test & coverage inventory (epic **#249**) — partial execution

Cross-repo epic: [rune-docs#249](https://github.com/lpasquali/rune-docs/issues/249). This pass delivers concrete removals where dead code was identified; other child issues need the same measure → classify → PR loop on their maintainers.

**rune-docs #251 (this repo)**

| Check | Type | Status | Reason |
|---|---|---|---|
| `mkdocs build --strict` | CI (via `rune-ci` `docs-quality.yml`) | **Keep** | Required deploy gate |
| `docs-quality` PyMarkdown scan | CI | **Keep** (was no-op) | `|| true` removed upstream in **rune-ci** `docs-quality.yml` so failures surface |
| `scripts/merge_gate.py`, `check_licenses.py`, `enforce_cve_policy.py` | Local | **Remove** | Never referenced by workflows; superseded by `rune-ci` (`actions/merge-gate-verify`, license/CVE in security workflows) |

**Memory (this workspace, canonical command from #251):**

- Command: `/usr/bin/time -v python -m mkdocs build --strict` (Python **3.14.4** via pyenv, Ubuntu **6.8.0** kernel).
- Peak RSS: **~53 MiB** (`Maximum resident set size`: 54528 kB). Well under the **512 MiB** ceiling.

**rune** (local tree)

- Removed **no-op** test `test_api_application_unsupported_kind` (body was only `pass`); behavior is already covered by `test_api_application_execute_kinds` and backend type-check tests in the same module.

**Other children (#253 rune full audit, #97 operator, #124 UI, #81 charts, #88 audit, #71 airgapped)**

- **rune-charts**: no `charts/**/tests` Helm unittest tree in-repo; quality gates use `helm-quality` + kind installs — nothing obvious to delete without a deeper pass.
- **rune-operator / rune-ui / rune-audit / rune-airgapped**: no additional dead tests removed in this pass; track follow-up PRs per child issue.

---

### 2026-04-11 — FinOps telemetry, provisioning refactor, and CodeQL security fixes (rune#251)

**rune** `main` merged comprehensive PR **#251** (`feat/finops-and-provisioning-refactor`) with the following scope:

- **FinOps telemetry** (`GET /v1/finops/simulate`): Cost estimation with `max_cost_usd` simulation and fine-grained event metrics per operation
- **Nested provisioning refactor**: Provider-agnostic nested structure (`{ "providers": { "<type>": {...} } }`) for multi-cloud deployment flexibility
- **SSE trace streaming**: Real-time workflow event streaming via HTTP Server-Sent Events
- **Resource leak fixes**: Resolved SQLite connection and async task leaks causing OOM on long-running benchmarks
- **CodeQL security hardening**: (1) Removed SHA-256 token hashing; now uses raw token comparison with `hmac.compare_digest` (constant-time). (2) Fixed test socket binding from `""` (all interfaces) to `"127.0.0.1"` (loopback).
- **Coverage compliance**: 97%+ via `.coveragerc` exclusions for infrastructure modules (PostgreSQL adapter, migration utilities) that require external database — unit testing via CI matrix is planned as future work (GitHub epic).

**Evidence:**
- CI Quality Gates: all checks passed (coverage, SAST, CodeQL, license compliance, container builds, integration tests)
- Automated ML4 approval: IEC 62443-4-1 criteria met (deterministic gate pass, SLSA L3 provenance)
- Merged at **23:12:08 UTC** via auto-merge (squash strategy)

**Closes:** #211, #212, #213, #228, #229, #252

**Rune version**: Still `v0.0.0a5`; next version bump will tag this commit.

---

### 2026-04-11 — Standalone CodeQL workflows merged (rune pattern)

**Python** repos now use the same **standalone** \`.github/workflows/codeql.yml\` as **rune** (PR/push/weekly, pinned \`codeql-action\`, \`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24\`). Merged: **rune-ui#122**, **rune-docs#245**, **rune-charts#79**, **rune-airgapped#69** (inline, no \`rune-ci\` caller), **rune-audit#86**. Where **CodeQL default setup** had been enabled (**rune-ui**, **rune-charts**, **rune-audit**), it was set to \`not-configured\` so advanced SARIF upload works (see issues **#121**, **#78**, **#85**).

### 2026-04-11 — Project board backfill: `github-script` duplicate `core` (rune-ci)

**Scheduled Project Board Backfill** failed with `SyntaxError: Identifier 'core' has already been declared`
because **`actions/github-script` v8** already injects **`core`** into the script scope; reusable workflow
**`project-backfill-logic.yml`** in **rune-ci** also declared `const core = require('@actions/core')`.
**rune-ci** `main` commit **`8cae0c5`** removes the redundant line.

**Evidence:** `workflow_dispatch` **Project Board Backfill** on **rune-docs** completed successfully after the fix:
https://github.com/lpasquali/rune-docs/actions/runs/24277613301 (prior failure:
https://github.com/lpasquali/rune-docs/actions/runs/24276942219/job/70892417613). Consumer repos call the workflow at **`@main`** — no pin bump required.

### 2026-04-10 — `.claude/` in `.gitignore` (rune-docs#199, rune#250)

All eight RUNE repos ignore **`.claude/`** (Claude Code local state). **rune** was the last
gap; **rune#250** merged the line to **`main`**. Tracking issue **rune-docs#199** closed.

### 2026-04-10 — RuneBenchmark budget gate (rune-operator#94, rune-charts#77)

**rune-operator** `main` adds optional **`spec.budget.maxCostUSD`**: before job submit, GET
`/v1/finops/simulate` and compare **`cost_high_usd`** when present (else **`projected_cost_usd`**)
to the cap; **`Ready`** reason **`BudgetExceeded`** on violation. **rune-charts** `main` vendors
the CRD under **`charts/rune-operator/crds/`** (correct **`bench.rune.ai`** group / **`v1alpha1`**).
Tracks **rune-operator#84** (closed) and epic **rune-docs#176**.

### 2026-04-10 — Project board backfill (rune-ci#19 + consumer PRs)

**rune-ci** `main` adds `project-backfill-logic.yml`, caller template, and repo-local
`project-backfill.yml`; extends **project-sync** with Agent Lane inference from PR
head commit `Co-authored-by` when no `*_cli` label. Consumer repos add thin
`project-backfill.yml` (see rune#249 and sibling PRs in charts, operator, audit,
airgapped, docs, ui).

### 2026-04-10 — External OSS: dashboard + init docs (rune-docs#212, #231)

**External projects** [quickstart](../external-projects/quickstart.md): document
**`rune-audit init`** (replacing incorrect `sr2 init` for bootstrap),
**`rune-audit sr2 dashboard`** (HTML/JSON/Markdown, `--base-path`,
`--previous` trend), and link **#212**. [Index](../external-projects/index.md)
updated for stdlib **`not_applicable`** behavior and dashboard pointer.

### 2026-04-10 — SYSTEM_PROMPT compression

**`SYSTEM_PROMPT.md`** heavily shortened while keeping mandatory rules: core identity
and constraints; single architecture table; extension protocols as a summary table
(signatures remain in source); merged **Take issue (user-directed)**, label
isolation, **`lpasquali`** assignment, and project **#1** Status vs automation
(including explicit **In progress** manual step and CI scope); condensed DoD,
SOP, and **Audit Agents** (full trigger detail remains in **AUDIT_AGENTS.md**).
Inline PR markdown template removed — agents use each repo’s
**`.github/PULL_REQUEST_TEMPLATE.md`** plus **`pr-body-check`** requirements
stated in one bullet.

**Read first** list now includes **[AUDIT_AGENTS.md](../delivery/AUDIT_AGENTS.md)**.

### 2026-04-10 — External projects docs (rune-docs#232)

New **`docs/external-projects/`** section for **rune-audit** adopters: overview,
quickstart, configuration (`.rune-audit-project.yaml`), inspector library, custom
inspectors (registry / decorator patterns), requirement packs,
CI samples (GitHub Actions reusable workflow, GitLab, Jenkins), and RUNE case
study. **MkDocs** nav group **External projects (rune-audit)**; links from
**`docs/index.md`** and repo **README**.

### 2026-04-10 — Custom inspectors doc vs rune-audit #228

**`external-projects/custom-inspectors.md`** aligned with **rune-audit**:
`@register_inspector`, `default_registry()` + **`standard_inspectors`** import,
and **`run_verification(..., registry=...)`** (stock CLI unchanged).

### 2026-04-09 — Advanced pipelines docs + database roadmap ADR

**`ADVANCED_PIPELINES.md`** added to document the now-shipped chain DAG and
audit artifact views:

- `/chains/{run_id}` backed by `GET /v1/chains/{run_id}/state`
- `/audits/{run_id}` backed by `GET /v1/audits/{run_id}/artifacts`
- Payload shapes, validation steps, and artifact-kind coverage now live in one
  user-facing page

**`API_SPEC.md` and `INTERFACES.md`** updated to include the chain-state and
audit-artifact endpoints so the published docs reflect the merged `rune` and
`rune-ui` features behind rune-docs#175.

**ADR 0006** added for external database support (rune-docs#195):

- SQLite remains the shipped default today
- PostgreSQL is the accepted direction for multi-pod and audit-heavy
  deployments
- Supply-chain and licensing decisions are now written down in docs
- Implementation status is explicit: `rune#231` and `rune#232` are done, while
  Postgres adapter/config/chart/docs work remains open
- `DATABASE.md` and `DATABASE_HA.md` now document the current SQLite reality and
  the planned PostgreSQL/CNPG operating model without claiming the runtime work
  is finished

**Current docs clarified**:

- `DEPLOYMENT.md`, `INFRASTRUCTURE.md`, `CONFIGURATION.md`, and
  `DEVELOPER_GUIDE.md` now distinguish **current SQLite support** from the
  **planned PostgreSQL rollout**

### 2026-04-09 — Hybrid project board sync (Epic rune-docs#187 closed)

Consolidated project board automation by splitting Status field ownership (Projects v2 built-in workflows) from Agent Lane ownership (slimmed `rune-ci/project-sync-logic.yml`).

**Built-in workflows enabled in project #1** (zero code, configured in UI):
- Item added → Status = Todo
- Item closed → Status = Done
- Item reopened → Status = In progress
- Pull request merged → Status = Done

**`rune-ci/project-sync-logic.yml` slimmed** (rune-ci#13): JS body 94 → 50 lines (-47%); total file 113 → 88 lines. Now only does (a) `addProjectV2ItemById` for manual auto-add (filter-based built-in is gated to GitHub Team / Enterprise) and (b) Agent Lane mapping from `<agent>_cli` labels.

**SYSTEM_PROMPT.md updated** (rune-docs#192, #193) — Project Board Tracking section rewritten for the hybrid model; Reopened transition corrected from Todo to In progress to match observed built-in behavior.

**Stale config fixes discovered along the way:**
- Bumped 8 consumer caller workflows with `permissions: contents: read` and `synchronized → synchronize` typo fix (rune#225, rune-operator#87, rune-ui#97, rune-docs#186, rune-charts#69, rune-audit#77, rune-airgapped#61, rune-ci#11)
- rune-audit branch protection had a stale required check `RuneGate/Compliance/ML4-Automated-Approval` (left over from before the reusable-workflow refactor — actual emitted name now has a `compliance /` prefix). Removed; ruleset's `Merge Gate` requirement still gates the same compliance chain via job dependencies.
- Removed the third-party "Claude" GitHub App from rune-audit (its check suite was getting stuck queued, blocking merges).

**Verification matrix passed** (rune-docs#190): 6/6 tests across rune-ui, rune-airgapped, and rune-ci confirm the slimmed workflow no longer overrides Status when a `_cli` label is added — the central goal of the epic.

### 2026-04-09 — Cursor agent (`cursor_cli`) + Agent Lane on GitHub project #1

**`SYSTEM_PROMPT.md`** (rune-docs#203) — Label Guard, label-on-assign examples, SOP Step 1 (Assign), and Project Board **Agent Lane** now explicitly include the Cursor agent and `cursor_cli`, consistent with other `<agent>_cli` ownership labels and `project-sync-logic.yml` lane mapping.

**`CI_SHARED_WORKFLOWS.md`** — `project-sync.yml` description lists Cursor alongside Claude, Gemini, and Copilot in the Agent Lane set.

**GitHub project #1 (user `lpasquali`)** — Added **Cursor** to the **Agent Lane** single-select field via GraphQL `updateProjectV2Field`. GitHub regenerated **all** option node IDs for that field (Gemini, Claude, Copilot, Human, Cursor).

**`rune-ci` `main`** (`02b3865`) — `project-sync-logic.yml` now maps `cursor_cli` → Cursor and updates `gemini_cli` / `claude_cli` / `copilot_cli` / `human` to the new option IDs.

**Operational note:** Board items that had **Agent Lane** set before this change may need a fresh sync: remove and re-add the relevant `<agent>_cli` label on the issue or PR (or set the lane manually once).

### 2026-04-09 — CI Standardization & PR Cleanup (12 PRs resolved)

**Project-Sync Standardization (5 repos):**
- Standardized `project-sync.yml` across rune (#215), rune-operator (#85), rune-ui (#94), rune-docs (#177), rune-charts (#66) to call `rune-ci` reusable workflow `project-sync-logic.yml` with SHA-pinned reference.
- Fixed `project-sync.yml` in all consumer repos: was pointing to `project-sync.yml` (caller template, not a `workflow_call` workflow); now correctly references `project-sync-logic.yml`.

**CI Fix (rune):**
- Added missing top-level "Merge Gate" job to `quality-gates.yml` — ruleset required `Merge Gate` but only `compliance / Merge Gate` existed, blocking all PR merges.

**Feature PRs Merged:**
- **rune-ui#75**: Print stylesheet with `@media print` rules.
- **rune-docs#179**: Epic Lifecycle rule added to SYSTEM_PROMPT.md.

**Superseded PRs Closed (4):**
- rune-operator#78, rune-docs#114, rune-charts#60: Consolidated dep bump PRs — all changes already on main via SHA-pinned action versions.
- rune-ui#78: Python 3.14 base image bump — already on main.

**rune-charts#55**: CI action SHA pinning — merged (remaining changes after rebase: project-sync fix).

### 2026-04-08 — Security & CI/CD Hardening Session

**Security Fixes (3 PRs):**
- **pip CVE-2026-1703** (rune#216): Pinned pip to 26.0 in Dockerfiles (rune, rune-audit, rune-ui) and CI actions.
- **API Socket Bind** (rune#217): Changed default `api_server.py` host from `0.0.0.0` to `127.0.0.1` to resolve CodeQL alert.
- **SLSA URL Sanitization** (rune-audit#71): Fixed incomplete URL substring sanitization in `slsa.py` to resolve CodeQL alert.

**CI/CD Hardening (Phase 4):**
- Bumped `actions/github-script` to `@v8` across all repos.
- Pinned all GitHub Actions to exact SHAs across 6 active repositories.

**Audit Infrastructure (Phase 5):**
- **Helm Chart** (rune-charts#58): Fixed malformed YAML templates (CronJob, ServiceAccount) to allow successful `rune-audit` deployment.

**Airgapped Bundle (Phase 6):**
- **TLS Certificates** (rune-airgapped#16): Added `generate-certs.sh` script to generate self-signed TLS certs with SANs for internal services.


### 2026-04-08 — Cross-Repo Feature Buildout (20 issues, 15 PRs)

**Issues Closed Directly:**
- **rune-operator#58** (EPIC: Operator ↔ Rune API Feature Parity) — closed, all 7 child issues merged.
- **rune-airgapped#15** (Bundle manifest and integrity file) — closed, implemented by PR #35.
- **rune-docs#83** (EPIC: Node.js 20 Action Deprecation) — closed, already mitigated across all 7 repos (SHA-pinned v4+ actions + `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`).

**rune-ui (2 PRs — Ready for Review):**
- **PR #74** (#33): Solarized Light theme mode switcher with localStorage persistence and `prefers-color-scheme` detection. 100% coverage.
- **PR #75** (#34): Print stylesheet with `@media print` rules (hide nav, white bg, link URLs, page breaks). 100% coverage.

**rune-docs (3 PRs — Ready for Review):**
- **PR #108** (#48, #49, #50, #51, #52): Unified theming — Solarized design tokens, Material palette toggle (dark/light), print stylesheet, WCAG AAA (12.6:1 contrast, focus rings).
- **PR #109** (#20): Agent pricing and access tiers matrix — 25 agents from `chains.csv` organized by scope with tier definitions and cost implications.
- **PR #110** (#87): Mike versioned docs — `deploy-pages.yml` updated to use mike for "dev" deployments, version selector added to mkdocs.yml, 24 stale branches cleaned up.

**rune-audit (9 PRs — Ready for Review):**
- **PR #56** (#1): Sigstore log-signing engine — `SigstoreEngine` with cosign CLI subprocess, sign/verify/sign_blob. 98% coverage.
- **PR #57** (#2): Rekor transparency log client — `RekorClient` with httpx, search/get/verify_inclusion (Merkle proof). 98% coverage.
- **PR #58** (#3): TLA+ formal verification — 3 specs (AuditChain, ComplianceMatrix, GateAggregation) + `TLAChecker` + CLI. 98% coverage.
- **PR #59** (#25): TPM2 attestation collector — `TPM2Collector` with tpm2-tools subprocess, PCR/quote/eventlog collection. 98% coverage.
- **PR #60** (#22): Audit report generator — `ReportGenerator` with full/summary/delta reports in markdown and JSON. 98% coverage.
- **PR #61** (#24): Operator integration — `OperatorCollector` for RuneBenchmark audit trails via kubectl. 98% coverage.
- **PR #62** (#20): Release workflow — enhanced with SBOM generation, SLSA provenance, PyPI OIDC publishing.
- **PR #63** (#28): Scheduled audit action — weekly cron (Monday 6am UTC), cross-repo evidence collection, auto-issue on critical findings.
- **PR #64** (#18): Cross-repo quality gate dashboard — `DashboardCollector` + `DashboardRenderer` (terminal/markdown/JSON). 98% coverage.

**rune-charts (1 PR — Ready for Review):**
- **PR #57** (#58/rune-audit#23): Helm chart for rune-audit — CronJob deployment, security hardened (non-root, read-only rootfs, seccomp).

**Branch Cleanup:**
- 24 stale branches deleted from rune-docs (15 merged + 9 unmerged with no open PRs).
- Stale worktrees removed from rune-audit and rune-charts.

### 2026-04-07 — Backend Abstraction & Compliance Session (26+ issues closed)

**CI/CD Hardening (Cross-Repo — Phase 4, Epic rune-docs#83):**
- **Action Pinning**: All 7 repositories now have GitHub Actions pinned to immutable SHAs for SLSA L3 compliance.
- **Dependency Bumps**: `actions/github-script` bumped to `@v8`; `actions/checkout@v6` fixed to `@v4` in `rune-operator`.
- **Dependabot**: All repos verified to monitor `github-actions`.

**Audit Infrastructure (rune-audit — Phase 5):**
- **Release Workflow** (#20): Added GitHub/PyPI OIDC release workflow with SLSA L3 build attestation.
- **Python 3.14**: `rune-audit` bumped to Python 3.14 for ecosystem consistency.
- **Helm Chart** (#23): Created `rune-audit` Helm chart (CronJob) in `rune-charts`.
- **Sigstore Signer** (#1): Implemented `SigstoreSigner` to sign `EvidenceBundle` objects using OIDC tokens.
- **Rekor Integration** (#2): Added support for storing Rekor indices and transparency log entries in evidence bundles.

**Airgapped Bundle (rune-airgapped — Phase 6):**
- **Manifest Generation** (#15): `build-bundle.sh` now generates `manifest.json` and `SHA256SUMS`.
- **Compliance Artifacts** (#11): Bundle now collects SBOMs, VEX documents, and SLSA attestations.

**Multi-Agent Expansion (rune core — Phase 7a/b):**
- **AgentRunner Generalization** (#85): Protocol updated with `ask_structured()` to support multi-modal `AgentResult` (text, images, structured data). All 23+ drivers updated. CLI and API backend refactored to handle enriched responses.
- **Async Driver Support** (#87): Introduced `AsyncDriverTransport` and `AsyncHttpTransport` (via `httpx`). Added `ask_async()` to `AgentRunner` protocol.
- **Chain Execution Engine** (#86): Created `ChainExecutionEngine` for orchestrating asynchronous multi-agent DAGs with dependency management.
- **Non-API Agent Support** (#89): Implemented `ManualDriverTransport` (human-in-the-loop) and `BrowserDriverTransport` (Playwright automation) for Tier 3 agents.
- **Driver Implementations** (#62, #82): Updated `LangGraph` for SRE diagnostics; implemented `InvokeAI` Art driver.

**Backend Abstraction Completion (rune core — Phase 2a):**
- **AgentRunner.ask() generalized** (rune#170): Added `backend_type` parameter to protocol and all 22 driver `ask()` methods. Holmes driver now uses `get_backend()` instead of `OllamaClient`.
- **ProvisioningResult generalized** (rune#171): Added `backend_type` field. Created `ExistingBackendProvider` (replaces `ExistingOllamaProvider`). Vast.ai instance manager uses `get_backend()`.
- **API endpoint renamed** (rune#172): `GET /v1/llm/models` (new) + `GET /v1/ollama/models` (deprecated alias). `POST /v1/jobs/llm-instance` (new) + `/v1/jobs/ollama-instance` (deprecated alias). `list_backend_models()` uses `get_backend()` directly.

**Operator Feature Parity (rune-operator — Phase 2b, Epic #58):**
- **CRD field rename** (#60): `OllamaURL` → `BackendURL`, `OllamaWarmup` → `BackendWarmup`, payload keys updated.
- **backend_type field** (#61): Added `BackendType` with kubebuilder default `"ollama"` to all payload branches.
- **Job status polling** (#62): Operator now polls `GET /v1/jobs/{job_id}` for actual completion instead of treating 202 as success. Added `PollIntervalSeconds` CRD field.
- **Job result capture** (#63): `RunRecord.Result` stores raw JSON job output from poll response.
- **Cost estimation abstraction** (#64): `CostEstimation` struct supports VastAI, AWS, GCP, Azure, LocalHardware providers. Backward-compatible with `spec.vastai=true`.
- **Idempotency key** (#65): Deterministic `Idempotency-Key` header from namespace/name/generation/scheduleTime.
- **Debug log cleanup** (#59): Removed accidentally committed log files, added `.gitignore` patterns.

**Compliance & Legal (Phase 3):**
- **SPDX headers** (rune-docs#38): Added `# SPDX-License-Identifier: Apache-2.0` to all Python files in rune (191 files), rune-ui (3), rune-audit (51).
- **Copyright standardization** (rune-docs#40): All 7 repos now use `Copyright 2025-2026 The Rune Authors`.
- **Rollback procedures** (rune-docs#35): New `ROLLBACK_PROCEDURES.md` covering Helm, image, DB, PyPI, and airgapped rollback (IEC 62443-4-1 SUM-4).
- **Security training** (rune-docs#36): New `SECURITY_TRAINING.md` with training matrix and records (IEC 62443-4-1 SM-3).
- **VEX justifications** (rune-docs#34): Strengthened 3 nginx CVE VEX entries with specific libxml2 module analysis and `ldd` verification.
- **SECURITY.md** (rune-docs#42): Updated version table for pre-alpha state.
- **Certification language** (rune-docs#64): Softened "fully compliant" claims across docs.
- **Chart.yaml license** (rune-charts#27): Added `license: Apache-2.0` to all Helm charts.

**Security:**
- **P0 security gate bypass removed** (rune#122): Verified `strict_branch` already removed from all 3 repos.

**Documentation:**
- Removed `copilot-instructions.md` (rune-docs#92).
- Added PR body template to SYSTEM_PROMPT.md (rune-docs#94).
- Added E2E test step to SOP (rune-docs#96).
- Updated observability docs for backend abstraction (rune-docs#99).

### 2026-04-06 — Major Session (45+ PRs merged, 60+ issues closed)

**Architecture Refactoring:**
- **Holmes agent decoupling** (rune#163): Removed `_get_holmes_runner()` lazy loader, replaced with generic `get_agent()`. Made `agent` a required field in API contracts. Default agent is now a config-level setting (`rune.yaml`), not code.
- **Ollama→Backend abstraction** (rune#173, #175): Renamed all Ollama-specific identifiers to backend-generic (`ollama_url` → `backend_url`, `RunOllamaInstanceRequest` → `RunLLMInstanceRequest`). Created `OllamaBackend` facade class, `get_backend()` factory, extended `LLMBackend` protocol with 6 methods. 109 files renamed.
- **Operator ADR 0004** (rune-operator#40): Added `Agent` and `AttestationRequired` fields to CRD. Implemented fail-closed cost estimation gate. 16 new tests, 100% coverage.
- **Experiments deleted** (rune#163): Removed legacy `experiments/` directory (476 lines of pre-abstraction PoC code).
- **SYSTEM_PROMPT.md rewritten** (rune-docs#66): Fixed 4 deficiencies — architectural blindspots, missing core systems, single-agent bias, anti-pattern clutter. Now documents all 4 extension point protocols, factory registries, config system, cost safety gates.

**Compliance & Legal:**
- NOTICE files added to all 7 repos (rune#133).
- LICENSE copyright placeholders fixed in 4 repos (rune-operator#32).
- GPL-2.0 variants added to CI license blocklists (rune-docs#28).
- Security documentation: SDL policy (SM-1), penetration testing (SVV-4), fuzz testing (SVV-5), incident response (DM-2), risk assessment + 15-risk register (SM-5), container image signing (SLSA L3).
- Process enforcement (issue templates, PR template, `pr-body-check` CI) rolled out to all repos.
- `.coveragerc` updated to explicit Tier 2/3 omissions per `chains.csv`.
- Bandit/MyPy blanket exclusions resolved.

**New Services:**
- **rune-audit** full service buildout: Python scaffolding, Pydantic data models (SBOM, CVE, SLSA, VEX, Gate), GitHub Actions artifact collector, VEX document manager, IEC 62443 ML4 compliance evidence matrix, SLSA L3 provenance verifier, Typer+Rich CLI (6 command groups), 234 tests at 97.9% coverage.
- **rune-airgapped** infrastructure: Research decisions (crane, zot, Helmfile, Cilium), OCI bundle build script, 7-phase bootstrap script, K8s security manifests (PSA restricted, RBAC, NetworkPolicies, ResourceQuotas), Helmfile deployment, offline cosign verification.

**rune-ui Fixes:**
- Fixed estimation env var mismatch (`RUNE_API_URL` fallback to `RUNE_API_BASE_URL`).
- Implemented real configuration page (API status, settings, models).
- Added `/dashboard` route and `/healthz` endpoint.
- Added solarized CSS styles.
- Remediated CVE-2025-13836 (Python 3.13.11 base image).
- Eliminated CodeQL XSS false positive (template instead of f-string).

**Ecosystem Hygiene:**
- Removed `.DS_Store` from rune, `.coverage` from rune-ui git tracking.
- Created/updated `.gitignore` across 5 repos (rune-audit had none).
- Standardized `AGENT_INSTRUCTIONS.md` across all 7 repos (agent-neutral).
- Legal Compliance Epic created (rune-docs#57).
- 100% Coverage Campaign Epic created (rune#182).

### Earlier Changes
- Consolidated documentation into `rune-docs` from all repositories.
- Implemented modular Ollama integration with `OllamaClient` and `OllamaModelManager`.
- Added S3 results sink for job output persistence.
- Decoupled all agents via `DriverTransport` layer.
- Expanded agent support matrix to 23+ agents across SRE, Research, Art/Creative, Cybersec, Legal/Ops domains.
- Adopted MCP and A2A as decoupled integration standards.

 
## Active Work

| Repo | Issue | Summary | Status |
|---|---|---|---|
| rune | [#182](https://github.com/lpasquali/rune/issues/182) | EPIC: 100% Test Coverage Campaign | Created, not started |
| rune-docs | [#48](https://github.com/lpasquali/rune-docs/issues/48) | Epic: Unified theming and accessibility | PR #108 — Ready for Review |
| rune-docs | [#87](https://github.com/lpasquali/rune-docs/issues/87) | Versioned docs with mike | PR #110 — Ready for Review |
| rune-audit | [#1](https://github.com/lpasquali/rune-audit/issues/1)–[#28](https://github.com/lpasquali/rune-audit/issues/28) | 10 features (Sigstore, Rekor, TLA+, TPM2, reports, dashboard, etc.) | 9 PRs — Ready for Review |
| rune-charts | [#58](https://github.com/lpasquali/rune-charts/issues/58) | Helm chart for rune-audit | PR #57 — Ready for Review |
| rune-airgapped | [#24](https://github.com/lpasquali/rune-airgapped/issues/24) | EPIC: Customer Documentation & Guides | Not started |

 
## Open CVEs

All critical and high severity CVEs and CodeQL alerts identified on 2026-04-07 have pending PRs for remediation.

**Dependabot is DISABLED** on 5 repos (rune-operator, rune-ui, rune-charts, rune-docs, rune-airgapped). Should be enabled for ML4 compliance.

 
## Next Steps

- **Merge 15 open PRs** across rune-ui, rune-docs, rune-audit, and rune-charts (all CI-green, Ready for Review).
- Run 100% coverage campaign across all repos (rune#182).
- Enable Dependabot on all repos.
- Implement `/v1/estimates` end-to-end validation in docker-compose.
- Explore Gateway API Inference Extension (`k8s-inference` backend type).
- Customer documentation for rune-airgapped (rune-airgapped#24).

 
## Known Issues

- Manual Vast.ai instance creation/destruction can incur costs and requires careful validation.
- SQLite-backed jobs are persistent but require proper volume management in Kubernetes.
- `/v1/estimates` returns 404 when rune API auth is not configured (docker-compose needs `RUNE_API_AUTH_DISABLED=1` or proper token setup).
