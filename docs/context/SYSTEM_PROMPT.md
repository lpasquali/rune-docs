# SYSTEM_PROMPT

## Core Identity
RUNE (Reliability Use-case Numeric Evaluator) is an AI model benchmarking and provisioning platform. It orchestrates benchmarkable DevOps/SRE operations, with optional Vast.ai provisioning for Ollama and agentic investigation via HolmesGPT.

## Core Constraints
- **Decoupling**: HolmesGPT is decoupled via a pluggable driver transport layer.
- **Thin Entrypoints**: CLI commands are lightweight; business logic resides in `rune_bench/`.
- **Reproducibility**: Benchmarks must be fully reproducible and documented.
- **Security**: Mandatory branch protection, signed provenance (SLSA L3), and vulnerability scanning.
- **Compatibility**: Maintain backward compatibility for CLI and public APIs.
- **Cost Safety**: Fail-closed cost estimation gates GPU provisioning. If estimation confidence drops below 95%, the operation is rejected.

## Architecture Layers
| Layer | Location | Rule |
|---|---|---|
| CLI (Typer + Rich) | `rune/` | Thin shell only — no business logic |
| Orchestration | `rune_bench/workflows.py` | All business flow lives here |
| Agent drivers | `rune_bench/drivers/` | Pluggable transport layer (`DriverTransport`) |
| Agent runners | `rune_bench/agents/` | Grouped by domain (sre, research, legal, etc.) |
| LLM backends | `rune_bench/backends/` | Ollama, OpenAI, Bedrock |
| Resource providers | `rune_bench/resources/` | Vast.ai and existing-Ollama |
| HTTP API | `rune_bench/api_server.py` | stdlib `ThreadingHTTPServer` + SQLite |

## Key Protocols
- `DriverTransport`: Send action + params to a driver process.
- `AgentRunner`: Execute an agent investigation and return results.
- `LLMBackend`: Communicate with an LLM inference endpoint.
- `LLMResourceProvider`: Provision or locate compute for LLM inference.

## Conventions & Style
- Raise `RuntimeError` with user-facing messages at boundaries.
- Normalize URLs in client/workflow helpers.
- Strip LiteLLM prefixes (`ollama/`) before API calls.
- Warmup unloads other running models for deterministic memory.
- For Vast.ai, prefer reusing matching running instances.
- Secrets (tokens, keys) must stay in env vars — never in `rune.yaml`.
- Offline testing: Mock all network/provider boundaries (97% coverage gate).
- No automated tests for real cloud resources (Vast.ai lifecycle is manual).

## Agent Workflow & Efficiency (Mandates)
- **Branch Isolation**: Agents must operate in isolated feature branches. Only rebase and push the **assigned** branch. Never modify or rebase branches belonging to other agents or tasks.
- **Issue Attribution**: **Active** issues (those being worked on by an agent) must be assigned to **lpsquali**. Inactive/untouched issues can remain unassigned. Agents must **never** assign issues to themselves; they must ensure the issue is assigned to **lpsquali** upon starting work.
- **PR Workflow**: When handling Pull Requests, resolve merge conflicts by pulling the latest target branch (e.g., `main`) and rebasing the assigned branch onto it. Always wait for GitHub Actions/CI to finish before merging.
- **Minimal Commands**: Minimize turns by combining independent tool calls in parallel. Use `wait_for_previous: true` only when necessary for sequential dependencies.
- **Strategic Orchestration**: Use sub-agents (e.g., `codebase_investigator`, `generalist`) to compress complex or repetitive tasks, keeping the main context window lean and efficient.
- **Validation-First**: Every change must be verified via project-specific build/lint/test commands before completion.

## Standard Operating Procedure (SOP): Issue-to-Merge
1. **Assign**: Ensure active issue is assigned to **lpsquali** (never self-assign).
2. **Isolate**: Create feature branch; reproduction test-case first (for bugs).
3. **Research**: Read `rune-docs` as the single source of truth.
4. **Execute**: Minimize turns (parallel tool calls); 100% coverage target (no "cheating" mocks).
5. **Verify**: Mock all boundaries; 97% coverage floor; check ML4/SLSA L3 gates.
6. **PR & Rebase**: PR to target branch; rebase onto latest `main`; wait for all CI/Gaps to turn green.
7. **Persist**: Update `CURRENT_STATE.md` upon successful merge.

## Tone & Style
- Professional, technical, and concise.
- Focus on reliability, automation, and security.
