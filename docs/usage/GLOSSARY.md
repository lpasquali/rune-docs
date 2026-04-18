# Glossary

Alphabetized terminology for RUNE. When a term has an authoritative source (a protocol in code, a catalog column, a config key), the entry links there.

## Agent

A software entity that answers a question in a given scope (SRE / Research / Cybersec / Legal-Ops / Art-Creative). In RUNE, every agent implements the [`AgentRunner`](#agentrunner) protocol, is listed in `rune_bench/catalog/defaults/chains.csv`, and belongs to a [Tier](#tier). See [CODING_STANDARDS §Agent filesystem layout](../context/CODING_STANDARDS.md) for per-scope directory mapping.

## AgentConfig / AgentResult

Dataclasses defined in `rune_bench/agents/base.py`. `AgentConfig` carries the settings a driver needs to invoke an agent; `AgentResult` carries the structured response (text, optional images, optional structured data). See [SYSTEM_PROMPT §Extension points](../context/SYSTEM_PROMPT.md#extension-points-protocols).

## AgentRunner

One of the four extension-point protocols. Surface: `ask(question, model, backend_url=None, backend_type="ollama")` plus `ask_async` and `ask_structured` variants. Every agent implements this.

## Backend

An LLM provider (Ollama, a hosted API, a custom backend). Distinct from the agent; the same agent can run against different backends. See [`LLMBackend`](#llmbackend).

## Benchmark

A scored run of one or more agents against a defined question set in a defined scope, under a cost envelope. Scoring produces a numeric result plus a `confidence_score`. Confidence below `0.95` fails cost gates.

## Catalog

`rune_bench/catalog/defaults/chains.csv` and `scopes.csv`. Ships as package data. Authoritative source for which agents exist, their tier, and which scopes are defined.

## Chain

A directed-acyclic-graph of agents executed in sequence for a single benchmark run. Chain execution is orchestrated by `ChainExecutionEngine` (from `rune#86`). The chain's structure is authored by the user; the engine handles async dependency management.

## ConfidenceScore

Numeric confidence in a cost estimate, produced by `CostEstimationResponse`. Below `0.95`, cloud-GPU provisioning is rejected (fail-closed). Local backends skip the gate.

## Cost gate

A pre-provisioning check that rejects the run if `confidence_score < 0.95`. Implemented via the `CostEstimationRequest` → `CostEstimationResponse` contract. See [SYSTEM_PROMPT §Cost gates](../context/SYSTEM_PROMPT.md#cost-gates-api-contracts) and [ADR 0002](../architecture/adrs/0002-cost-estimation.md).

## Driver

A concrete implementation of [`DriverTransport`](#drivertransport) wiring a specific agent into RUNE. Examples: `holmes.py`, `k8sgpt.py`. Filenames follow the lower-case, first-word-only convention documented in [CODING_STANDARDS](../context/CODING_STANDARDS.md).

## DriverTransport

One of the four extension-point protocols. Surface: `call(action, params) -> dict`. Factories for stdio and HTTP transports live in `rune_bench/drivers/base.py`. Configured via `RUNE_<NAME>_DRIVER_*` environment variables.

## Epic

A GitHub issue labeled `type/epic`. Closed only when every listed child issue is closed AND every linked PR is merged or closed. Children are linked with `Closes` in the PR that closes each.

## Fail-closed

Design posture where a check defaults to rejecting the operation when it cannot prove safety. RUNE's cost gate is fail-closed: missing data → reject, not approve.

## LLMBackend

One of the four extension-point protocols. Surface: model listing, warmup, `normalize_model_name`, strip LiteLLM `ollama/` prefix. Implementations live in `rune_bench/backends/`. Selected via `get_backend(...)` factory.

## LLMResourceProvider

One of the four extension-point protocols. Surface: `provision(...)` / `teardown(...)` returning typed `ProvisioningResult`. Implementations in `rune_bench/resources/`. `vastai` ships today; cloud stubs exist; `local` skips cost gates.

## ML4

Maturity Level 4 from IEC 62443-4-1 (Security for industrial automation and control systems — product development requirements). RUNE's process is aligned to ML4 practices across SDL / SM / SVV / DM / SUM. See the landing [compliance matrix](https://github.com/lpasquali/rune-docs/issues/282) and [security/SDL.md](../security/SDL.md).

## Profile

Named configuration set selected via `--profile` or `RUNE_PROFILE`. Precedence: CLI → env → `./rune.yaml` → `~/.rune/config.yaml` → Typer defaults.

## Protocol

Python `typing.Protocol` (structural subtyping). RUNE exposes four extension-point protocols: `DriverTransport`, `AgentRunner`, `LLMBackend`, `LLMResourceProvider`. New integrations implement one of these; nothing privileges built-in implementations.

## Provider

Either (a) a compute-provisioning provider (`LLMResourceProvider` — Vast.ai, cloud, local), or (b) a backend provider (`LLMBackend` — Ollama, hosted APIs). Context disambiguates.

## rune-audit

Sibling repository implementing quantitative compliance checks (IEC 62443 / SLSA / VEX evidence). Usable standalone against non-RUNE codebases — see [External projects](../external-projects/index.md).

## rune-operator

Sibling repository: Kubernetes operator implementing the `RuneBenchmark` CRD. Schedules benchmark runs against a cluster.

## rune-ui

Sibling repository: HTMX + FastAPI + Jinja2 dashboard. Zero NPM. Runs standalone against any rune-api.

## Scope

Classification axis for agents: SRE, Research, Art/Creative, Cybersec, Legal/Ops. Defined in `scopes.csv`; agents live under `rune_bench/agents/<scope>/`.

## SLSA

Supply-chain Levels for Software Artifacts. RUNE targets **L3-style provenance** on releases (signed, non-falsifiable build metadata). `rune-audit` verifies SLSA attestations on upstream dependencies.

## Tier

Classification axis for agents by access and licensing: **Tier 1** (OSS, fully inspectable, measured), **Tier 2** (freemium / partial API, best-effort), **Tier 3** (closed SaaS, protocol-only, excluded from coverage). See [Agent Access Tiers](TIERS.md) (file rename to `TIERS.md` tracked separately).

## Transport

Wire-level carrier for `DriverTransport`. Variants: stdio, HTTP (sync), `AsyncHttpTransport` (async via `httpx`), `ManualDriverTransport` (human-in-the-loop), `BrowserDriverTransport` (Playwright automation — ADR 0005).

## VEX

Vulnerability Exploitability eXchange. Per-CVE statements declaring whether the vulnerability is actually exploitable in RUNE's deployment context. Register: [delivery/VEX.md](../delivery/VEX.md).

## Warmup

Deterministic inference warmup phase before benchmark scoring, to eliminate cold-start variance. The `ollama_warmup: true` (now `backend_warmup: true`) config key controls this.
