
# Agent Pricing and Access Tiers

This page provides a comprehensive matrix of all agents supported by the RUNE platform, organized by access tier and domain scope. The authoritative source for agent data is [`chains.csv`](https://github.com/lpasquali/rune/blob/main/rune_bench/catalog/defaults/chains.csv) in the rune repository.

---

## Tier Definitions

RUNE classifies agents into three tiers based on licensing, API availability, and testability:

| Tier | Name | Description | Cost Implications |
|------|------|-------------|-------------------|
| **1** | OSS / Fully Testable | Open-source agents with public APIs or self-hostable runtimes. Full test coverage is achievable. | Free / self-hosted. No API keys required for core functionality. |
| **2** | Partial API / Freemium | Agents with limited free tiers, freemium APIs, or partial open-source components. Testing is best-effort. | May require API keys. Free tiers have rate limits; full access requires paid subscriptions. |
| **3** | Closed SaaS | Proprietary agents with no public API or closed commercial access only. Integration is protocol-only via `DriverTransport`. | Requires commercial subscription. RUNE provides protocol stubs but cannot execute these agents directly. |

### Coverage and Testing Obligations

- **Tier 1**: 100% coverage target, included in `.coveragerc` measurement. All code paths must be tested.
- **Tier 2**: Best-effort coverage. May be omitted from measurement with justification.
- **Tier 3**: Protocol-only integration via `DriverTransport`. Excluded from coverage measurement. Stub tests verify importability and `NotImplementedError` contract.

---

## Agent Matrix

### SRE Agents

| Rank | Agent Name | Tier | Rating | Agentic Capability | License/Access | Recommended Model | Link |
|------|-----------|------|--------|-------------------|----------------|-------------------|------|
| 1 | K8sGPT | 1 | 5.0 | Scans clusters for issues and provides automated RCA | OSS (CNCF Sandbox) | `qwen3:14b-instruct` | [GitHub](https://github.com/k8sgpt-ai/k8sgpt) |
| 2 | HolmesGPT | 1 | 4.5 | Investigates alerts by autonomously running CLI commands | OSS (CNCF / Open Standards) | `qwen3:14b-instruct` | [GitHub](https://github.com/robusta-dev/holmesgpt) |
| 3 | PagerDuty AI | 3 | 4.5 | Autonomous alert correlation and triage automation | Closed SaaS (LSF Security) | `qwen3:14b-instruct` | [Docs](https://support.pagerduty.com/) |
| 4 | Metoro | 2 | 4.0 | Uses eBPF for autonomous service mapping and debugging | Partial API (CNCF / eBPF) | `qwen3:14b-instruct` | [Docs](https://metoro.io/docs) |
| 5 | Cleric | 2 | 3.5 | Mimics an engineer's parallel investigation loop | Partial API (Infra Interop) | `qwen3:14b-instruct` | [GitHub](https://github.com/ClericHQ) |

### Research Agents

| Rank | Agent Name | Tier | Rating | Agentic Capability | License/Access | Recommended Model | Link |
|------|-----------|------|--------|-------------------|----------------|-------------------|------|
| 1 | Perplexity Pro | 3 | 5.0 | Multi-step research with autonomous source validation | Closed SaaS (Open Web Standards) | `deepseek-r1:32b` | [Website](https://www.perplexity.ai/) |
| 2 | Glean | 3 | 4.8 | Autonomous internal knowledge discovery for enterprises | Closed SaaS (Enterprise Search) | `deepseek-r1:32b` | [Website](https://www.glean.com/) |
| 3 | Elicit | 2 | 4.0 | Automates literature review and data extraction | Freemium (Open Science) | `deepseek-r1:32b` | [Website](https://elicit.com/) |
| 4 | LangGraph | 1 | 4.0 | Framework for building stateful multi-agent flows | OSS Framework | `deepseek-r1:32b` | [GitHub](https://github.com/langchain-ai/langgraph) |
| 5 | Consensus | 2 | 3.5 | Synthesizes answers from 200M+ academic papers | Freemium (Evidence-Based) | `deepseek-r1:32b` | [Website](https://consensus.app/) |

### Art/Creative Agents

| Rank | Agent Name | Tier | Rating | Agentic Capability | License/Access | Recommended Model | Link |
|------|-----------|------|--------|-------------------|----------------|-------------------|------|
| 1 | Midjourney | 3 | 5.0 | Iterative agentic refinement via Remix modes | Closed SaaS (AI Ethics) | `llama4:8b-instruct` | [Docs](https://docs.midjourney.com/) |
| 2 | ComfyUI | 2 | 4.5 | Node-based autonomous art pipeline orchestration | Partial OSS (OSS Community) | `llama4:8b-instruct` | [GitHub](https://github.com/comfy-org/ComfyUI) |
| 3 | Krea AI | 3 | 4.0 | Real-time generative enhancement and upscaling | Closed SaaS (Open Weights) | `llama4:8b-instruct` | [Website](https://www.krea.ai/) |

### Cybersecurity Agents

| Rank | Agent Name | Tier | Rating | Agentic Capability | License/Access | Recommended Model | Link |
|------|-----------|------|--------|-------------------|----------------|-------------------|------|
| 1 | PentestGPT | 1 | 4.5 | Automates penetration testing workflows | OSS (OpenSSF / OSS) | `qwen3:32b-instruct` | [GitHub](https://github.com/GreyD0ne/PentestGPT) |
| 2 | Radiant Security | 3 | 4.5 | Autonomous SOC incident investigation and response | Closed SaaS (SOC Automation) | `qwen3:32b-instruct` | [Website](https://radiantsecurity.ai/) |
| 3 | Mindgard | 3 | 4.0 | Autonomous Red Teaming for AI model safety | Closed SaaS (AI Security) | `qwen3:32b-instruct` | [Website](https://mindgard.ai/) |
| 4 | BurpGPT | 2 | 3.5 | Autonomous web vulnerability scanning via LLM | Partial API (OWASP Standards) | `qwen3:32b-instruct` | [GitHub](https://github.com/v87/burpgpt) |
| 5 | XBOW | 3 | 3.5 | Autonomous web vulnerability discovery and exploit | Closed SaaS (Sec Automation) | `qwen3:32b-instruct` | [Website](https://xbow.com/) |

### Legal/Ops Agents

| Rank | Agent Name | Tier | Rating | Agentic Capability | License/Access | Recommended Model | Link |
|------|-----------|------|--------|-------------------|----------------|-------------------|------|
| 1 | Harvey AI | 3 | 4.8 | Specialist legal reasoning and analysis agent | Closed SaaS (Transparency) | `deepseek-r1:70b` | [Website](https://www.harvey.ai/) |
| 2 | Spellbook | 3 | 4.0 | AI-powered contract drafting and review specialist | Closed SaaS (Legal Standards) | `deepseek-r1:70b` | [Website](https://www.spellbook.legal/) |
| 3 | MultiOn | 2 | 4.5 | Browser-based Action agent for web automation | Partial API (AAIF / Agentic) | `qwen3:14b-instruct` | [Docs](https://docs.multion.ai/) |
| 4 | Dagger | 1 | 4.5 | Infrastructure-as-Code pipeline agent | OSS (CNCF / LSF) | `qwen3:14b-instruct` | [GitHub](https://github.com/dagger/dagger) |
| 5 | CrewAI | 1 | 4.0 | Multi-agent workflow manager and orchestrator | OSS Framework | `deepseek-r1:32b` | [GitHub](https://github.com/joaomdmoura/crewai) |
| 6 | Sierra | 3 | N/A | Stub — no public API available | Closed SaaS | N/A | N/A |
| 7 | SkillFortify | 3 | N/A | Stub — no public API available | Closed SaaS | N/A | N/A |

---

## Summary by Tier

| Tier | Count | Agents |
|------|-------|--------|
| **1** (OSS) | 6 | K8sGPT, HolmesGPT, LangGraph, PentestGPT, Dagger, CrewAI |
| **2** (Partial API) | 5 | Metoro, Cleric, Elicit, Consensus, ComfyUI, BurpGPT, MultiOn |
| **3** (Closed SaaS) | 14 | PagerDuty AI, Perplexity Pro, Glean, Midjourney, Krea AI, Radiant Security, Mindgard, XBOW, Harvey AI, Spellbook, Sierra, SkillFortify |

!!! note "Authoritative Source"
    The single source of truth for agent classification is
    [`chains.csv`](https://github.com/lpasquali/rune/blob/main/rune_bench/catalog/defaults/chains.csv)
    in the rune repository. This page is derived from that file. If any
    discrepancy exists, `chains.csv` takes precedence.

---

## Recommended Models by Scope

Each scope has a recommended Ollama model family optimized for the domain:

| Scope | Recommended Model | Rationale |
|-------|-------------------|-----------|
| SRE | `qwen3:14b-instruct` | Strong at structured infrastructure reasoning |
| Research | `deepseek-r1:32b` | Excels at multi-step analytical and citation tasks |
| Art/Creative | `llama4:8b-instruct` | Efficient for prompt engineering and creative workflows |
| Cybersecurity | `qwen3:32b-instruct` | Larger context for security analysis and exploit chains |
| Legal/Ops | `deepseek-r1:70b` / `qwen3:14b-instruct` | Legal reasoning benefits from larger models; ops tasks use smaller models |
