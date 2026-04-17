# DriverTransport

The lowest-level extension protocol. A driver transport wraps whatever wire-level mechanism your agent uses (stdio, HTTP, async HTTP, manual human-in-the-loop, headless browser) behind a uniform `call(action, params) -> dict` surface.

Source: `rune_bench/drivers/base.py` in [the rune repo](https://github.com/lpasquali/rune/blob/main/rune_bench/drivers/base.py). Protocol defined with `@runtime_checkable` so structural subtyping works without explicit subclassing.

## Signature

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DriverTransport(Protocol):
    def call(self, action: str, params: dict) -> dict:
        """Invoke an action against the underlying agent.

        Args:
            action: A verb understood by the target agent (e.g., "ask",
                "warmup", "shutdown"). The set of valid verbs is driver-
                specific and should be documented by the driver.
            params: JSON-serializable keyword arguments for the action.

        Returns:
            A JSON-serializable result dict. Driver implementations may
            include vendor-specific keys, but must include the keys
            documented by the invoking AgentRunner for the action.

        Raises:
            ValueError: the action is unknown to this driver.
            RuntimeError: transport failure (network error, subprocess
                crash) or a well-defined domain error from the agent.
        """
```

For async-native agents, the parallel protocol `AsyncDriverTransport` exposes `async def call_async(...)`. See [Transports](TRANSPORTS.md).

## Factory pattern

RUNE's built-in transports are constructed via factories that read environment variables. The convention for a driver named `NAME`:

| Variable | Purpose |
|---|---|
| `RUNE_<NAME>_DRIVER_TYPE` | `stdio` or `http` (or `async_http`, `manual`, `browser` for variants) |
| `RUNE_<NAME>_DRIVER_URL` | Endpoint URL (for HTTP-family transports) |
| `RUNE_<NAME>_DRIVER_CMD` | Subprocess command (for stdio transport) |
| `RUNE_<NAME>_DRIVER_TOKEN` | Bearer token for authenticated HTTP |
| `RUNE_<NAME>_DRIVER_HEADERS` | JSON dict of extra headers |
| `RUNE_<NAME>_DRIVER_TIMEOUT` | Per-call timeout in seconds |

Uppercase `NAME` matches the driver module name (e.g., `RUNE_HOLMES_DRIVER_URL` for `holmes.py`).

Missing required env for the configured transport produces `RuntimeError` with a message pointing at the specific missing variable.

## Stdio transport

Subprocess speaks newline-delimited JSON on stdin/stdout. Each request is one JSON line; response is one JSON line. Errors: stderr is captured and included in `RuntimeError` on non-zero exit.

```python
from rune_bench.drivers.base import stdio_transport

tx = stdio_transport(cmd=["./my-agent-binary", "--mode=rune"])
result = tx.call("ask", {"question": "why is my pod crashlooping?"})
```

## HTTP transport

Synchronous HTTP. Submits to `POST /v1/actions/{action}` with the params as JSON body. Returns `job_id`; polls `GET /v1/jobs/{job_id}` until completion. Headers: `X-Tenant-ID`, `Authorization: Bearer <token>`, optional `X-API-Key` for vendor APIs that use a separate auth mechanism.

```python
from rune_bench.drivers.base import http_transport

tx = http_transport(
    base_url="http://my-agent:8080",
    token=os.environ["RUNE_MYAGENT_DRIVER_TOKEN"],
    tenant_id="team-a",
)
result = tx.call("ask", {"question": "..."})
```

Poll interval and max wait are configurable via env or constructor kwargs. 5xx responses retry with exponential backoff (bounded); 4xx responses raise `RuntimeError` immediately.

## Writing a minimal driver

```python
# my_toy_driver.py
from rune_bench.drivers.base import DriverTransport

class ToyDriver(DriverTransport):
    """Echo driver for integration testing."""

    def call(self, action: str, params: dict) -> dict:
        if action == "ask":
            return {
                "answer": f"Echo: {params.get('question', '')}",
                "confidence": 1.0,
            }
        if action == "warmup":
            return {"status": "ok"}
        raise ValueError(f"Unknown action: {action}")
```

Register it (see [Registry](REGISTRY.md)) and RUNE picks it up via the catalog.

## Error handling

- **`ValueError`** — the action verb is unknown to this driver. Do **not** use for bad params — those are `RuntimeError` with a descriptive message.
- **`RuntimeError`** — transport failure, auth failure, upstream 4xx/5xx after retries, subprocess crash, timeout. Include a message that a human reader can diagnose without access to the driver internals.
- **Never raise generic `Exception`** — it bypasses RUNE's boundary normalization.

## Further

- [AgentRunner](AGENT_RUNNER.md) — the agent-level layer that calls into `DriverTransport`.
- [Transports](TRANSPORTS.md) — async, manual, browser variants.
- [Driver SDK quickstart](https://github.com/lpasquali/rune-docs/issues/279) — package-and-ship workflow.
