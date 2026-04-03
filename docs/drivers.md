# Drivers

The driver layer decouples agent implementations (HolmesGPT, future SRE agents)
from the core `rune_bench` package.  Agents run in a separate process and
communicate with the core via a well-defined wire protocol.  This means:

- The core API server and CLI do **not** require `holmesgpt` to be installed.
- Agent implementations can be upgraded or replaced independently.
- Custom agents can be plugged in without modifying core code.

## DriverTransport Protocol

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DriverTransport(Protocol):
    def call(self, action: str, params: dict) -> dict:
        """Call a driver action and return the result dict.

        Raises RuntimeError on failure.
        """
        ...
```

Any object with a matching `call` signature satisfies the protocol — no
inheritance required.  Two concrete implementations ship with `rune_bench`:

| Class | Module | Description |
|-------|--------|-------------|
| `StdioTransport` | `rune_bench.drivers.stdio` | Spawns a subprocess, sends one JSON line on stdin, reads one JSON line from stdout. |
| `HttpTransport` | `rune_bench.drivers.http` | POSTs to `/v1/actions/{action}`, polls `/v1/jobs/{job_id}` until terminal status. |

## Factory function

```python
from rune_bench.drivers import make_driver_transport

transport = make_driver_transport("holmes")
result = transport.call("ask", {
    "question": "Why is the cluster degraded?",
    "model": "llama3.1:8b",
    "kubeconfig_path": "/home/user/.kube/config",
    "ollama_url": "http://localhost:11434",
})
answer = result["answer"]
```

`make_driver_transport(driver_name)` reads environment variables at call time.
The variable prefix is `RUNE_<NAME>_DRIVER` where `<NAME>` is the driver name
uppercased.

## Stdio mode (default)

The driver subprocess is spawned for each request, receives one JSON line on
stdin, and must write one JSON line to stdout before exiting.

### Wire protocol (v1)

**Request (stdin):**

```json
{"action": "ask", "params": {"question": "...", "model": "...", ...}, "id": "UUID"}
```

**Response (stdout):**

```json
{"status": "ok", "result": {"answer": "..."}, "id": "UUID"}
```

or on failure:

```json
{"status": "error", "error": "human-readable message", "id": "UUID"}
```

The `id` field echoes the request UUID and is used for correlation in debug logs.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_HOLMES_DRIVER_MODE` | `stdio` | Must be `stdio` (or omit) |
| `RUNE_HOLMES_DRIVER_CMD` | `python -m rune_bench.drivers.holmes` | Shell command for the subprocess (parsed with `shlex.split`) |

### Custom stdio command

```bash
# Use a pre-installed console script (pip install rune-bench[holmes])
export RUNE_HOLMES_DRIVER_CMD=rune-holmes-driver

# Use a different interpreter
export RUNE_HOLMES_DRIVER_CMD="/opt/venv-holmes/bin/python -m rune_bench.drivers.holmes"
```

## HTTP mode

The driver server runs as a long-lived process (or sidecar container).  Requests
are submitted as jobs; the transport polls until completion.

### HTTP mode: environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_HOLMES_DRIVER_MODE` | — | Must be `http` |
| `RUNE_HOLMES_DRIVER_URL` | — | Base URL of the driver server (required) |
| `RUNE_HOLMES_DRIVER_TOKEN` | — | Bearer token sent in `Authorization` and `X-API-Key` headers |
| `RUNE_HOLMES_DRIVER_TENANT` | `default` | Value of the `X-Tenant-ID` header |

### HTTP endpoints (driver server must implement)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/actions/{action}` | Submit an action; body: `{"params": {...}}`; returns `202 {"job_id": "..."}` |
| GET | `/v1/jobs/{job_id}` | Poll job status; returns `{"status": "...", "result": {...}}` |

Terminal statuses: `succeeded`, `success`, `completed`, `failed`, `error`, `cancelled`.

### Example

```bash
export RUNE_HOLMES_DRIVER_MODE=http
export RUNE_HOLMES_DRIVER_URL=http://holmes-sidecar:8080
export RUNE_HOLMES_DRIVER_TOKEN=secret
```

## Built-in drivers

### `holmes`

The only built-in driver.  Entry point: `python -m rune_bench.drivers.holmes`.

Requires `pip install rune-bench[holmes]` in the subprocess environment.

**Supported actions:**

| Action | Required params | Optional params | Result |
|--------|----------------|----------------|--------|
| `ask` | `question`, `model`, `kubeconfig_path` | `ollama_url`, `context_window`, `max_output_tokens` | `{"answer": str}` |
| `info` | — | — | `{"name": "holmes", "version": "1", "actions": [...]}` |

The driver sets `OVERRIDE_MAX_CONTENT_SIZE` and `OVERRIDE_MAX_OUTPUT_TOKEN`
environment variables from `context_window` / `max_output_tokens` before
invoking HolmesGPT.

`HolmesDriverClient` (in `rune_bench.drivers.holmes`) is the high-level client
used by the rest of `rune_bench`.  `rune_bench.agents.sre.holmes.HolmesRunner`
is a backward-compatible alias.

## Writing a custom driver

1. Create an executable that reads one JSON line from stdin and writes one JSON
   line to stdout (stdio mode), or implement the HTTP job protocol (HTTP mode).

2. Register it via env var:

   ```bash
   export RUNE_MYAGENT_DRIVER_CMD="python -m mypackage.myagent"
   ```

3. Call it from Python:

   ```python
   from rune_bench.drivers import make_driver_transport

   transport = make_driver_transport("myagent")
   result = transport.call("ask", {"question": "...", ...})
   ```

The driver must handle at least the `ask` action and return `{"answer": str}`.

## Troubleshooting

Enable debug logging to see request/response details:

```bash
export RUNE_DEBUG=1
```

Debug output includes the subprocess command, action name, request ID, and HTTP
polling URLs.

Common errors:

| Error | Cause |
|-------|-------|
| `Failed to spawn driver process` | Command not found or not executable |
| `Driver process produced no output` | Subprocess exited without writing to stdout |
| `Driver process returned invalid JSON` | Subprocess wrote non-JSON to stdout (check stderr) |
| `HTTP mode selected … URL is not set` | `RUNE_HOLMES_DRIVER_MODE=http` set without `RUNE_HOLMES_DRIVER_URL` |
| `Driver job timed out after 3600s` | HTTP driver job did not reach a terminal status within 1 hour |
