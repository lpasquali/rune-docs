# Mission

## Problem

Organizations are integrating LLM-backed agents into workloads where reliability matters — site-reliability incident response, research discovery, cybersecurity triage, regulated-industry compliance, and content generation. These agents differ wildly in licensing (open-source, partial API, closed SaaS), backend requirements (local Ollama, hosted LLM APIs, rented GPU), and cost envelopes (zero-marginal-cost local inference vs. per-request SaaS vs. rented cloud GPU).

No existing platform lets a team compare them on **reproducible**, **cost-controlled**, **audit-ready** workloads. Ad-hoc benchmarks suffer three failure modes: (1) vendor lock-in — a benchmark written against one agent's stdout format doesn't transfer; (2) unbounded cost — a benchmark that provisions cloud GPU without a budget gate can blow past an approved spend; (3) unauditable results — pre-alpha-era reports with no provenance can't be used for regulated procurement decisions.

## Approach

RUNE is an **agent-neutral, backend-neutral** benchmarking and compute-provisioning platform built around four pluggable protocols:

- **`DriverTransport`** — stdio or HTTP factories that call `(action, params) -> dict`. Every agent integration implements this; no agent is privileged in code.
- **`AgentRunner`** — `ask` / `ask_async` / `ask_structured` with typed `AgentConfig` / `AgentResult`. Uniform surface across 23+ agents.
- **`LLMBackend`** — model listing, warmup, normalization. Swap Ollama, a hosted API, or a custom backend without touching orchestration.
- **`LLMResourceProvider`** — `provision` / `teardown` returning typed `ProvisioningResult`. Vast.ai ships today; cloud providers, local-TDP, and air-gapped are protocol variants.

Defaults live in `rune.yaml` (CLI → env → `./rune.yaml` → `~/.rune/config.yaml` → Typer defaults). Secrets never land in YAML — env only. Catalog data (`chains.csv`, `scopes.csv`) ships as package data, surfacing a Tier 1/2/3 support matrix so consumers know which agents are measurable versus protocol-only stubs.

## Differentiators

- **Agent-neutral by construction** — the codebase has no hardcoded "default agent"; picking one is a config decision, not a patch. This is enforced by the registry model (`get_agent` / `register_agent` with custom entries shadowing built-ins) and validated by the test suite.
- **Backend-neutral by construction** — same rule for LLM backends. A benchmark written today against Ollama runs unchanged against a future backend via `get_backend(...)`.
- **Fail-closed cost gates** — `CostEstimationRequest` / `CostEstimationResponse` contracts reject any provisioning where `confidence_score < 0.95`. Local-only workflows (TDP energy model supported) skip gates. There is no "oops, I provisioned $500 of GPU" path.
- **Supply-chain hardened** — SLSA L3-style provenance on releases, `pip-audit` / `govulncheck` / Grype / Trivy in CI, VEX register tracking false-positive CVEs, image signing with cosign via sigstore.
- **ML4-aligned process** — IEC 62443-4-1 Maturity Level 4 practices around SDL (Security Development Lifecycle), SM (Security Management), SVV (Security Verification & Validation), DM (Defect Management), and SUM (Security Update Management). Evidence is collected automatically by `rune-audit`.

## Target readers

- **SRE teams** running HolmesGPT / K8sGPT / PagerDuty AI for cluster triage and wanting an apples-to-apples comparison on their own question set.
- **Research organizations** benchmarking Perplexity / Harvey / CrewAI on their own research-discovery problem set with reproducible provenance.
- **Regulated-industry compliance teams** evaluating agent adoption under FedRAMP / SOC 2 / ISO 27001 / HIPAA frameworks and needing SLSA-attested evidence.
- **Platform engineering teams** building internal AI agent platforms where cost safety and backend portability are non-negotiable.
- **Downstream component adopters** who want `rune-audit` (quantitative code audit against IEC 62443 / SLSA), `rune-operator` (standalone Kubernetes CRD scheduler for scheduled benchmarks), `rune-ui` (standalone HTMX dashboard), or the driver SDK as a library.

## What RUNE is NOT

- **Not production-stable yet.** The current version is `v0.0.0a5` (pre-alpha). API surfaces, configuration keys, and CRD field names are still moving. See [CURRENT_STATE](../context/CURRENT_STATE.md) for the living changelog and known breaks.
- **Not a single-vendor agent SaaS.** RUNE is infrastructure you run yourself (or adopt as components). There is no hosted RUNE endpoint; there is no vendor-owned leaderboard.
- **Not a proprietary benchmark harness.** The repo is Apache-2.0; the catalog is author-editable; the scoring model is documented, not gated.
- **Not certified against any specific regulatory regime.** ML4 alignment is documented and evidence-collected; it is not an ML4 audit conclusion issued by a conformance body. Controls likely to be met for various regimes are listed in the [compliance matrix](https://github.com/lpasquali/rune-docs/issues/282) (landing under epic [#273](https://github.com/lpasquali/rune-docs/issues/273)); gaps are listed alongside.
- **Not a replacement for production observability.** RUNE benchmarks agents; it does not replace Prometheus, Grafana, Datadog, or any other runtime monitoring. Benchmark results feed agent-selection decisions, not real-time alerting.
