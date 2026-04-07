
# CURRENT_STATE

 
## Incident Log (ML4 Compliance)
- **Version Baseline Reset**: An erroneous release was previously triggered with incorrect versioning (e.g., `v0.1.0`). To maintain strict ML4 traceability and signed provenance, the ecosystem baseline has been forcefully reset. The erroneous tags are marked as "Yanked" in GitHub Releases. Current correct versions are listed below.

## Living Memory

RUNE is currently in active pre-alpha development for its core LLM backends, agentic workflows, and compute provisioning integrations. It is **not yet production-ready**.

 
## Freshness Policy

This file must be updated whenever system state evolves (per CODING_STANDARDS.md "Atomic Persistence"). If information here conflicts with what you observe in the code or git history, trust what you observe now — then update this file to match reality.

Last updated: **2026-04-07**.

 
## Version Baseline

| Repo | Version | Commits | Status |
|---|---|---|---|
| rune | `v0.0.0a5` | 280 | Active development |
| rune-operator | `v0.0.0a0` (yanked `v0.1.0`) | 42 | Active development |
| rune-ui | `v0.0.0a0` (yanked `v0.1.1`) | 34 | Active development |
| rune-charts | `0.0.0-a0` (yanked `v0.1.1`) | 26 | Active development |
| rune-docs | `v0.0.0a1` (yanked `v0.1.0`) | 74 | Active development |
| rune-airgapped | unversioned | 14 | Pre-scaffolding |
| rune-audit | `v0.0.0a0` (yanked `v0.1.1`) | 15 | Scaffolding complete |

 
## Recent Changes

### 2026-04-07 — Backend Abstraction & Compliance Session (26+ issues closed)

**CI/CD Hardening (Cross-Repo — Phase 4, Epic rune-docs#83):**
- **Action Pinning**: All 7 repositories now have GitHub Actions pinned to immutable SHAs for SLSA L3 compliance.
- **Dependency Bumps**: `actions/github-script` bumped to `@v8`; `actions/checkout@v6` fixed to `@v4` in `rune-operator`.
- **Dependabot**: All repos verified to monitor `github-actions`.

**Audit Infrastructure (rune-audit — Phase 5):**
- **Release Workflow** (#20): Added GitHub/PyPI OIDC release workflow with SLSA L3 build attestation.
- **Python 3.14**: `rune-audit` bumped to Python 3.14 for ecosystem consistency.
- **Helm Chart** (#23): Created `rune-audit` Helm chart (CronJob) in `rune-charts`.

**Airgapped Bundle (rune-airgapped — Phase 6):**
- **Manifest Generation** (#15): `build-bundle.sh` now generates `manifest.json` and `SHA256SUMS`.
- **Compliance Artifacts** (#11): Bundle now collects SBOMs, VEX documents, and SLSA attestations.

**Multi-Agent Expansion (rune core — Phase 7a):**
- **AgentRunner Generalization** (#85): Protocol updated with `ask_structured()` to support multi-modal `AgentResult` (text, images, structured data). All 23+ drivers updated. CLI and API backend refactored to handle enriched responses.

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
| rune | [#166](https://github.com/lpasquali/rune/issues/166) | EPIC: Abstract LLM Backend Layer | **Complete** — all 6 phases merged (#167-#172) |
| rune | [#182](https://github.com/lpasquali/rune/issues/182) | EPIC: 100% Test Coverage Campaign | Created, not started |
| rune-operator | [#58](https://github.com/lpasquali/rune-operator/issues/58) | EPIC: Operator ↔ Rune API Feature Parity | **Complete** — all 7 child issues (#59-#65) closed |
| rune-docs | [#48](https://github.com/lpasquali/rune-docs/issues/48) | Epic: Unified theming and accessibility | Not started |
| rune-docs | [#83](https://github.com/lpasquali/rune-docs/issues/83) | EPIC: Node.js 20 Action Deprecation | Not started |
| rune-airgapped | [#23](https://github.com/lpasquali/rune-airgapped/issues/23) | EPIC: Network Isolation & Least-Privilege Security | PRs merged, issues to close |
| rune-airgapped | [#24](https://github.com/lpasquali/rune-airgapped/issues/24) | EPIC: Customer Documentation & Guides | Not started |

 
## Open CVEs (as of 2026-04-07)

| Repo | CVE | Package | Severity | Fix |
|---|---|---|---|---|
| rune, rune-ui, rune-audit | CVE-2026-1703 | pip 25.3 | — | Upgrade to pip 26.0 |
| rune | CodeQL `py/bind-socket-all-network-interfaces` | — | Medium | Change default bind to 127.0.0.1 |
| rune-audit | CodeQL `py/incomplete-url-substring-sanitization` | — | High | Fix URL validation in slsa.py |

**Dependabot is DISABLED** on 5 repos (rune-operator, rune-ui, rune-charts, rune-docs, rune-airgapped). Should be enabled for ML4 compliance.

 
## Next Steps

- Complete backend abstraction phases 4-6 (agent interface, provisioning, API endpoints).
- Run 100% coverage campaign across all repos.
- Enable Dependabot on all repos.
- Fix remaining open CVEs (pip upgrade, CodeQL alerts).
- Implement `/v1/estimates` end-to-end validation in docker-compose.
- Explore Gateway API Inference Extension (`k8s-inference` backend type).

 
## Known Issues

- Manual Vast.ai instance creation/destruction can incur costs and requires careful validation.
- SQLite-backed jobs are persistent but require proper volume management in Kubernetes.
- `/v1/estimates` returns 404 when rune API auth is not configured (docker-compose needs `RUNE_API_AUTH_DISABLED=1` or proper token setup).
