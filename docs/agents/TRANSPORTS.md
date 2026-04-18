# Transports

Concrete implementations of the `DriverTransport` protocol. Pick the one that matches your wire-level mechanism.

Source: `rune_bench/drivers/base.py` plus `rune_bench/drivers/` for browser + manual variants.

## Sync HTTP — `http_transport`

Default choice for REST-style agents.

```python
from rune_bench.drivers.base import http_transport

tx = http_transport(
    base_url="http://my-agent:8080",
    token="...",
    tenant_id="team-a",
    timeout_s=60,
)
```

- Submits to `POST /v1/actions/{action}` with params as JSON.
- Polls `GET /v1/jobs/{job_id}` until completion (state transitions documented in [API_SPEC](../usage/API_SPEC.md)).
- Headers: `Authorization: Bearer <token>`, `X-Tenant-ID: <id>`, optional `X-API-Key` when the vendor requires a separate API key.
- Retries 5xx with exponential backoff (bounded to `timeout_s`). 4xx → immediate `RuntimeError` with status + body.

## Stdio — `stdio_transport`

For agents that ship as subprocesses speaking newline-delimited JSON.

```python
from rune_bench.drivers.base import stdio_transport

tx = stdio_transport(
    cmd=["./my-agent", "--mode", "rune"],
    env={"CUSTOM_VAR": "value"},
    cwd="/path/to/agent",
)
```

- One JSON line per request; one JSON line per response.
- Subprocess stderr is captured and included in `RuntimeError` on non-zero exit.
- Subprocess stays alive across multiple `call(...)` invocations (reduces startup cost).

## Async HTTP — `AsyncHttpTransport`

For async-native agents or high-throughput scenarios.

```python
from rune_bench.drivers.base import AsyncHttpTransport

tx = AsyncHttpTransport(
    base_url="http://my-agent:8080",
    token="...",
)

# Use via AgentRunner.ask_async(...)
```

- Built on `httpx.AsyncClient` with connection pooling.
- Same request/response shape as `http_transport`; different awaitable surface.
- Retry and timeout semantics mirror the sync transport.

## Manual — `ManualDriverTransport`

Human-in-the-loop. Used for Tier 3 agents where no API is available — the transport prints the question to a rich prompt, waits for a human to paste the agent's response, returns it.

```python
from rune_bench.drivers.base import ManualDriverTransport

tx = ManualDriverTransport(
    agent_name="Sierra",
    prompt_style="rich",   # uses `rich` library for formatting
)
```

- For benchmarks where Tier 3 agent output must be captured but there's no programmatic interface.
- Each `call(...)` blocks until the human provides a response.
- Response is captured verbatim and wrapped in `AgentResult`.

## Browser — `BrowserDriverTransport`

Playwright-driven for agents available only through a web UI. See [ADR 0005](../architecture/adrs/0005-advanced-cognitive-architecture.md).

```python
from rune_bench.drivers.base import BrowserDriverTransport

tx = BrowserDriverTransport(
    driver_url="https://agent.example.com/chat",
    headless=True,
    screenshot_on_error=True,
)
```

Env vars: `RUNE_<NAME>_DRIVER_URL` + optional `RUNE_<NAME>_DRIVER_HEADLESS` (default `1`).

- Launches headless Chromium via Playwright.
- Navigates to `driver_url`, locates the question-input and response-output via CSS selectors registered per-agent.
- Screenshots on failure land in the configured artifacts directory (tied into [E2E Testing](https://github.com/lpasquali/rune-docs/pull/272) evidence layout; binding spec landing under PR [#272](https://github.com/lpasquali/rune-docs/pull/272)).

## Which to choose

| Your agent looks like | Use |
|---|---|
| REST API | `http_transport` |
| Subprocess with JSON stdin/stdout | `stdio_transport` |
| Async-native Python service | `AsyncHttpTransport` |
| No API, no subprocess, but a human can respond | `ManualDriverTransport` |
| Only a web UI | `BrowserDriverTransport` |
| None of the above | Implement `DriverTransport` directly; see [DRIVER_TRANSPORT §Writing a minimal driver](DRIVER_TRANSPORT.md#writing-a-minimal-driver) |

## Further

- [DriverTransport](DRIVER_TRANSPORT.md) — the protocol these implement.
- [AgentRunner](AGENT_RUNNER.md) — what calls into them.
- [ADR 0005: Advanced Cognitive Architecture](../architecture/adrs/0005-advanced-cognitive-architecture.md) — design motivation for non-API agents.
