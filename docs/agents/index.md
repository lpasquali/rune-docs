# Agents SDK

**For human developers building agents that integrate with RUNE.**

This section is for the agent author — someone writing a new agent (Tier 1 OSS, Tier 2 freemium-API, or Tier 3 closed-SaaS driver stub) and wanting it discoverable, callable, and scorable inside RUNE. If you're an operator running RUNE, start at [Deployment](../operations/DEPLOYMENT.md). If you're a coding-assistant LLM ingesting this repo as boot context, [Context](../context/SYSTEM_PROMPT.md) is your starting point.

## When to write a custom agent

- Your organization has a domain-specific agent (e.g., an internal triage bot, a specialized legal assistant) and wants **apples-to-apples benchmarking** against the public catalog.
- You're evaluating a **new OSS project** and want to add it to `chains.csv` for community comparison.
- You need a **non-standard transport** (a legacy Unix socket, a message queue, a vendor SDK that doesn't fit stdio or HTTP). Custom `DriverTransport` implementations let you extend the protocol surface without forking RUNE.
- You want to **wrap a Tier 3 closed SaaS** behind the uniform `AgentRunner.ask(...)` interface so your team has one API to call regardless of vendor.

## Tier implications — what you're committing to

The agent's [tier](../usage/PRICING.md) determines coverage expectations and RUNE's support posture.

| Tier | Coverage floor | Support |
|---|---|---|
| **Tier 1** (OSS, measurable) | Targeted 100% (floor 97%), measured by `.coveragerc` | Full — code-path inspection, reproducibility, scoring |
| **Tier 2** (freemium, partial API) | Best-effort; may be omitted with justification | Best-effort — integration tested where feasible |
| **Tier 3** (closed SaaS) | Excluded from measurement | Protocol-only — RUNE calls your `DriverTransport`; nothing else is introspectable |

## What's on this page

| Page | Topic |
|---|---|
| **[DriverTransport](DRIVER_TRANSPORT.md)** | The protocol surface: `call(action, params) -> dict`. Stdio / HTTP / async / manual / browser variants. Env-var conventions. |
| **[AgentRunner](AGENT_RUNNER.md)** | Agent-level contract: `ask` / `ask_async` / `ask_structured`, `AgentConfig`, `AgentResult`. |
| **[Registry](REGISTRY.md)** | `get_agent` / `register_agent`, custom shadowing of built-ins, lazy `importlib`. |
| **[Transports](TRANSPORTS.md)** | Transport variants — sync HTTP, `AsyncHttpTransport`, `ManualDriverTransport`, `BrowserDriverTransport`. |
| **[Testing](TESTING.md)** | Harness, `respx` mocking pattern, tier-based coverage expectations, stub contract. Scaffold — full content tracked as follow-up. |
| **[Example](EXAMPLE.md)** | End-to-end: ship a new OSS agent as a pip package, register it, run it. Scaffold — full content tracked as follow-up. |

## Out of scope

- The `context/` section (SYSTEM_PROMPT, CURRENT_STATE, CODING_STANDARDS) is **agent boot context** for coding assistants ingesting this repo; it is **not** the Agents SDK docs. Those files document RUNE itself, not how to build agents for RUNE.
- Benchmark scoring and chain execution — see [Benchmarks](https://github.com/lpasquali/rune-docs/issues/281).
- Deploying your agent into production — see [Deployment](../operations/DEPLOYMENT.md).
