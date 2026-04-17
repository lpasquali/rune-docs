# Agent Access Tiers

!!! info "RUNE itself is not sold"
    RUNE is open source (Apache-2.0). There is no "RUNE pricing" — you run
    RUNE yourself, on your own infrastructure, and adopt its components
    (`rune-audit`, `rune-operator`, `rune-ui`, `rune-airgapped`, the driver
    SDK) as libraries or services you host. This page is about the
    **access and licensing posture of the agents RUNE benchmarks against** —
    which vary wildly from fully open-source to closed SaaS — and what that
    means for your ability to run, inspect, and measure them.

RUNE categorizes agents into three tiers by **access and licensing model**. The tier determines RUNE's support posture and which cost gates apply when you invoke that agent.

The authoritative tier-to-agent mapping lives in `rune_bench/catalog/defaults/chains.csv` (the `Tier` column). The table below is a human-readable summary — when it drifts from `chains.csv`, the CSV is canonical.

## Tier matrix

| Tier | Access & licensing | Who pays for inference | RUNE support posture |
|---|---|---|---|
| **Tier 1** | Open Source (OSS) — agent code and model weights both public | You, for your own compute (local CPU/GPU, or cloud GPU provisioned via RUNE's fail-closed cost gate) | **Full.** Measured by `.coveragerc`; 100% coverage target; code path inspectable. |
| **Tier 2** | Freemium / partial API — agent may be closed but a public API exists (often free quota + paid tier) | Upstream vendor charges per call; RUNE applies cost estimation gates only for provisioning RUNE itself performs | **Best-effort.** Tested where feasible; may be omitted from coverage measurement with justification. |
| **Tier 3** | Closed SaaS / proprietary — agent is a managed service; only a protocol surface is reachable | Upstream vendor charges on subscription or per-call basis; RUNE never provisions these | **Protocol-only.** Excluded from coverage measurement; integration via `DriverTransport`; no code path inspection. |

## Tier 1 — Open Source (OSS)

Agent code and model weights are both open. RUNE can run these agents fully on-premises or in a private cloud; the only costs are your own infrastructure.

- **Example agents** (partial list — see `chains.csv` for the full catalog): K8sGPT, HolmesGPT, LangGraph, PentestGPT, Dagger.
- **What you get**: 100% data privacy (nothing leaves your environment), full code-path inspection, reproducible benchmarks.
- **Cost handling**: when you ask RUNE to provision cloud GPU for a Tier-1 run (e.g., `rune run-benchmark --vastai`), RUNE's **fail-closed cost estimation gate** rejects the provisioning unless `confidence_score >= 0.95`. Local-only runs skip the gate and use a TDP energy model instead.

## Tier 2 — Freemium / partial API

The agent itself may be closed or behind a managed API, but a usable API surface exists (often with a free quota plus a paid tier for heavier usage).

- **Example agents** (partial list): Metoro, Elicit, ComfyUI, BurpGPT, Consensus.
- **What you get**: working integration via `DriverTransport`; RUNE's cost-estimation gate applies to any provisioning RUNE performs (e.g., supporting compute for the agent's backend).
- **What you don't get**: upstream vendor API fees are pass-through — RUNE can't estimate or limit what the vendor charges for an API call. Budget that separately if it matters for compliance.

## Tier 3 — Closed SaaS

The agent is a fully managed service. RUNE ships a `DriverTransport` implementation that calls the vendor's API; nothing beyond that surface is introspectable.

- **Example agents** (partial list): PagerDuty AI, Perplexity Pro, Midjourney, Radiant Security, Harvey AI.
- **What you get**: uniform `AgentRunner.ask(...)` surface — same way you invoke an OSS agent.
- **What you don't get**: coverage measurement, failure-mode introspection, customization of the agent's internal reasoning. You also inherit the vendor's availability, pricing, and data-handling terms.
- **Why they're in the catalog anyway**: for apples-to-apples benchmarking. A team that already pays for PagerDuty AI or Harvey AI can compare it against Tier-1 agents on the same problem set and decide whether the managed offering justifies the SaaS cost.

## Compute costs (RUNE provisioning)

Separate from agent licensing: when RUNE provisions compute itself (GPU on Vast.ai; future cloud providers per the nested provisioning structure from [rune#251](https://github.com/lpasquali/rune/pull/251)), the cost is yours and is gated before provisioning starts.

- **Gate contract**: `CostEstimationRequest` → `CostEstimationResponse` with a `confidence_score`. Fail-closed: below `0.95`, provisioning is rejected. See [SYSTEM_PROMPT §Cost gates](../context/SYSTEM_PROMPT.md#cost-gates-api-contracts).
- **Drivers today**: `vastai`, `local` (local skips gates; TDP energy model).
- **Design reference**: [ADR 0002: Cost Estimation](../architecture/adrs/0002-cost-estimation.md).

## Further reading

- **Catalog source of truth**: `rune_bench/catalog/defaults/chains.csv` ships as package data.
- **Benchmark methodology** (how tiers feed into scoring, representative agents per scope, sample runs): landing under [epic #273](https://github.com/lpasquali/rune-docs/issues/273) child [#281](https://github.com/lpasquali/rune-docs/issues/281).
- **RUNE components you can adopt standalone**: [External projects](../external-projects/index.md).
