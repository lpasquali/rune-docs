 
# CURRENT_STATE

 
## Incident Log (ML4 Compliance)
- **Version Baseline Reset**: An erroneous release was previously triggered with incorrect versioning (e.g., `v0.1.0`). To maintain strict ML4 traceability and signed provenance, the ecosystem baseline has been forcefully reset:
  - `rune`: Verified to be correct at `0.0.0a2`.
  - All other repositories (`rune-ui`, `rune-operator`, `rune-charts`, etc.): Reset to `0.0.0a0` (or `0.0.0-a0` for Helm charts).
  - The erroneous tags (`v0.1.0`) will be marked as "Yanked" or "Pre-release" in GitHub Releases to preserve the immutable audit log without polluting the release lineage. Future proper releases of 0.1.0 must use a distinct tag like `v0.1.0-final`.

## Living Memory

RUNE is currently in active development for its core LLM backends, agentic workflows, and compute provisioning integrations. It is **not yet production-ready**.

 
## Freshness Policy

This file must be updated whenever system state evolves (per CODING_STANDARDS.md "Atomic Persistence"). If information here conflicts with what you observe in the code or git history, trust what you observe now — then update this file to match reality.

Last updated: **2026-04-06**.

 
## Recent Changes

- **P0 Issue Resolutions (2026-04-06)**: Resolved 3 critical issues across repositories:
  - Reclassified ComfyUI to Tier 2 and added GPL-3.0 contamination warnings (`rune#131`).
  - Enforced strict license compliance CI gates blocking GPL-2.0 variants in `rune`, `rune-ui`, and `rune-operator` (`rune#132`).
  - Created formal Threat Model and Security Requirements specification for IEC 62443-4-1 compliance (`rune-docs#30`).
- Consolidated documentation into `rune-docs` from all repositories.
- Implemented modular Ollama integration with `OllamaClient` and `OllamaModelManager`.
- Added S3 results sink for job output persistence.
- Decoupled HolmesGPT via `DriverTransport` layer.
- **Documentation Overhaul**: Updated all Mermaid.js diagrams and agent matrices to reflect the latest 2026 cross-repo architecture (Operator, UI, BFF flows).
- **2026 Agent Landscape**: Expanded support matrix to include **DevTools/Code** and **Productivity** domains; formally adopted **MCP** and **A2A** as decoupled integration standards.
- **SSOT Enforcement**: Banned binary diagrams and external state; `rune-docs` is now the definitive project memory.
- **Developer Onboarding Docs (2026-04-06)**: Added Developer Guide, Workstation Setup (Ubuntu 24.04 LTS), Milestones framework, Documentation Expedite Channel policy. Added tier column to `chains.csv`. Introduced proportional DoD levels (Full / Test Infrastructure / Documentation). Enforced vulnerability remediation policy across all delivery docs.
- **6 Open Docs PRs (2026-04-05)**: Centralizing docs into rune-docs; all have blocking review comments requiring code fixes before merge.

 
## Active Work

| Repo | Issue | Summary | Status |
|---|---|---|---|
| rune-operator | [#31](https://github.com/lpasquali/rune-operator/issues/31) | ADR 0004: Operator Feature Parity (Agent routing, AttestationRequired, fail-closed cost gates) | Open |
| rune | [#121](https://github.com/lpasquali/rune/issues/121) | Epic: Eliminate Tooling Configuration Bias (ML4 Compliance) | Open — parent of #122, #123, #124, #125 |
| rune | [#123](https://github.com/lpasquali/rune/issues/123) | Enforce Strict Test Coverage Boundaries in .coveragerc | Open |
| rune-docs | 6 open PRs | Docs centralization into rune-docs | Blocked — all have review comments requiring fixes (2026-04-05) |

 
## Next Steps

- Full implementation of ML4 certification evidence.
- Enhance observability metrics and runbooks.
- Explore MCP-based driver implementations for Tier 2 agents.

 
## Known Issues

- Manual Vast.ai instance creation/destruction can incur costs and requires careful validation.
- SQLite-backed jobs are persistent but require proper volume management in Kubernetes.
