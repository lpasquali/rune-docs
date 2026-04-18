# Driver SDK — protocol integration library

The "Driver SDK" is `rune_bench.drivers` imported as a library: the set of protocols (`DriverTransport`, `AgentRunner`, `LLMBackend`, `LLMResourceProvider`) plus transport helpers (stdio, HTTP, async HTTP, manual, browser-via-Playwright) that let you wire **your own agent** into the RUNE catalog — without forking RUNE itself.

## When to use standalone

- You maintain an agent or a backend and want to ship a pip-installable integration package that RUNE picks up via registry shadowing.
- You have an internal tool that needs the same protocol discipline RUNE uses (fail-closed gates, normalized URLs, typed contracts) but doesn't need the full benchmark harness.
- You're prototyping a new integration style (custom transport, custom provisioner) and want to validate it against RUNE's registry model before upstreaming.

## What you get

- **`DriverTransport`** — stdio or HTTP surface via `call(action, params) -> dict`. Factories live in `rune_bench.drivers.base`. Env-var convention: `RUNE_<NAME>_DRIVER_*`.
- **`AgentRunner`** — the uniform agent surface: `ask` / `ask_async` / `ask_structured` with typed `AgentConfig` / `AgentResult`.
- **`LLMBackend`** — model listing, warmup, URL normalization (strips LiteLLM `ollama/` prefix), etc.
- **`LLMResourceProvider`** — `provision(...)` / `teardown(...)` → typed `ProvisioningResult`. Cost estimation is fail-closed; local skips gates.
- **Registry** — `register_agent(name, factory)` / `get_agent(name)`; custom registrations shadow built-ins. Lazy `importlib` for built-ins.
- **Transport variants** — `AsyncHttpTransport` (via `httpx`), `ManualDriverTransport` (human-in-the-loop), `BrowserDriverTransport` (Playwright; see [ADR 0005](../../architecture/adrs/0005-advanced-cognitive-architecture.md)).

## What you give up vs full RUNE

- No CLI, no UI, no catalog harness. You're linking protocols, not adopting the product.
- No scoring model — that's the benchmark harness's job. You provide agent behavior; scoring happens upstream.

## Next

- **[Quickstart](quickstart.md)** — build a minimal driver for a toy agent, install it, and see it shadow the built-in registry.
- **Agents SDK deep dive** — the forthcoming `agents/` section (landing under [#280](https://github.com/lpasquali/rune-docs/issues/280)) will document each protocol in detail with full signatures and edge cases.
- **[rune repo](https://github.com/lpasquali/rune)** — source for `rune_bench/drivers/`, `agents/base.py`, `backends/base.py`, `resources/base.py`.
