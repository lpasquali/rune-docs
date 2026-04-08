# Agent Pricing & Access Tiers

RUNE categorizes agents into three tiers based on their accessibility, licensing, and operational costs.

## Access Tiers Matrix

| Tier | Meaning | Pricing Model | LLM Requirements | Support Level |
|---|---|---|---|---|
| **Tier 1** | Open Source (OSS) | **Free** (Self-hosted) | Open Weights (Ollama/Local) | Community + RUNE Core |
| **Tier 2** | Freemium / Partial API | **Pay-as-you-go** | Hybrid (Local + SaaS API) | Best Effort |
| **Tier 3** | Closed SaaS / Proprietary | **Subscription** | SaaS Managed | Protocol-only (No code access) |

## Tier Details

### Tier 1 — Open Source (OSS)
Agents in this tier are fully open-source and can be run entirely on-premises or in private cloud environments without external API costs.
- **Example Agents**: K8sGPT, HolmesGPT, LangGraph, PentestGPT, Dagger.
- **Benefits**: 100% data privacy, no recurring fees, fully testable.

### Tier 2 — Freemium / Partial API
These agents offer an API but may have usage limits or require a paid plan for advanced features.
- **Example Agents**: Metoro, Elicit, ComfyUI, BurpGPT, Consensus.
- **Costs**: Varies by provider. RUNE cost estimation gates apply to these drivers.

### Tier 3 — Closed SaaS
Agents in this tier are closed-source products delivered as a service. RUNE provides a `DriverTransport` implementation but cannot inspect or control the agent's internal logic.
- **Example Agents**: PagerDuty AI, Perplexity, Midjourney, Radiant, Harvey AI.
- **Costs**: Requires external subscription with the provider.

## Compute Costs (Compute Provisioning)

While Tier 1 agents are free to license, they incur **compute costs** when provisioned via RUNE's GPU resource providers (e.g., Vast.ai). These costs are separate from agent licensing and are estimated before every run.

See **[ADR 0002: Cost Estimation](../architecture/adrs/0002-cost-estimation.md)** for details on how these costs are calculated.
