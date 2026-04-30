 
# INTERFACES

Commands, endpoints, and payloads for interacting with RUNE.

 
## CLI Commands

`python -m rune` provides the following primary commands:

- `run-llm-instance`: Provision or select an Ollama server.
- `run-agentic-agent`: Run HolmesGPT analysis.
- `run-benchmark`: Multi-phase workflow for provisioning + analysis.
- `vastai-list-models`: List configured Vast.ai model catalog.
- `ollama-list-models`: List models exposed by an existing Ollama server.

 
## CLI Options Summary

### Shared Agent Options

- `--question`, `-q`: The analysis question for HolmesGPT.
- `--model`, `-m`: The LLM model name to use.
- `--kubeconfig`: Path to the Kubernetes config file.
- `--ollama-warmup`, `--no-ollama-warmup`: Whether to pre-load the model before use.

### Vast.ai Options (with `--vastai`)

- `--vastai-template`: The Vast.ai template hash.
- `--vastai-min-dph`, `--vastai-max-dph`: Dollars-per-hour range.
- `--vastai-reliability`: Minimum machine reliability percentage.

 
## API Server (HTTP Mode)

Run the server with `python -m rune.api`.

### Endpoints

- `POST /v1/jobs/agentic-agent`: Submit an agent analysis job.
- `POST /v1/jobs/benchmark`: Submit a full benchmark job.
- `POST /v1/jobs/llm-instance`: Submit an LLM backend provisioning job.
- `POST /v1/jobs/llm-instance`: Deprecated alias for `llm-instance`.
- `GET /v1/jobs/{job_id}`: Poll for job status and results.
- `GET /v1/catalog/vastai-models`: List available Vast.ai models.
- `GET /v1/llm/models?backend_url=<url>&backend_type=ollama`: List models from a target backend.
- `GET /v1/llm/models?backend_url=<url>`: Deprecated alias for the backend-generic models endpoint.

### Auth Headers

- `Authorization: Bearer <token>`
- `X-API-Key: <key>`
- `X-Tenant-ID: <tenant>`

 
## REST API Reference

For a formal definition of all endpoints and request/reponse schemas, see the **[API Specification](API_SPEC.md)**.

## Advanced Inspection Views

These routes are primarily surfaced by `rune-ui`, but they are backed by
first-class `rune` API contracts and are useful integration targets in their
own right.

| Surface | UI route | API route | Notes |
|---|---|---|---|
| Run detail | `/runs/{run_id}` | `GET /v1/jobs/{job_id}` | Status, result metadata, telemetry |
| Live trace | `/runs/{run_id}` | `GET /api/v1/runs/{run_id}/trace` | UI proxy for the run event stream |
| Browser live view | `/runs/{run_id}` | `GET /api/v1/runs/{run_id}/browser-stream` | UI proxy for browser screenshots |
| Chain DAG | `/chains/{run_id}` | `GET /v1/chains/{run_id}/state` | Multi-agent graph state (`nodes`, `edges`, `overall_status`) |
| Audit artifacts | `/audits/{run_id}` | `GET /v1/audits/{run_id}/artifacts` | Compliance evidence list grouped by artifact kind |
| Audit download | `/audits/{run_id}` | `GET /v1/audits/{run_id}/artifacts/{artifact_id}` | Streams raw artifact bytes |

See **[Advanced Pipelines](ADVANCED_PIPELINES.md)** for behavior and validation
details.

 
## Wire Protocol (Driver Layer)

HolmesGPT is invoked via the `DriverTransport` layer.

### Protocol JSON

Example `ask` action payload:

```json
{
  "action": "ask",
  "params": {
    "question": "What's wrong?",
    "model": "llama3.1:8b",
    "kubeconfig": "..."
  }
}
```

The driver returns a structured JSON response with analysis results.
