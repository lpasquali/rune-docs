
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
| rune-docs | `v0.0.0a0` (yanked `v0.1.0`) | 52 | Active development |
| rune-airgapped | unversioned | 14 | Pre-scaffolding |
| rune-audit | `v0.0.0a0` (yanked `v0.1.1`) | 15 | Scaffolding complete |

 
## Recent Changes

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
| rune | [#166](https://github.com/lpasquali/rune/issues/166) | EPIC: Abstract LLM Backend Layer | Phases 1-3 complete; #170-#172 (agent interface, provisioning, API endpoints) remain |
| rune | [#182](https://github.com/lpasquali/rune/issues/182) | EPIC: 100% Test Coverage Campaign | Created, not started |
| rune-docs | [#57](https://github.com/lpasquali/rune-docs/issues/57) | EPIC: Legal & Licensing Compliance | #38 (SPDX), #40 (copyright years), rune-charts#27 remain |
| rune-docs | [#48](https://github.com/lpasquali/rune-docs/issues/48) | Epic: Unified theming and accessibility | Not started |
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
