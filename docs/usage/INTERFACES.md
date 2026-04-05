 
# INTERFACES

Commands, endpoints, and payloads for interacting with RUNE.

 
## CLI Commands

`python -m rune` provides the following primary commands:

- `run-ollama-instance`: Provision or select an Ollama server.
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

- `POST /v1/jobs/ollama`: Submit an Ollama provisioning job.
- `POST /v1/jobs/agent`: Submit an agent analysis job.
- `POST /v1/jobs/benchmark`: Submit a full benchmark job.
- `GET /v1/jobs/{job_id}`: Poll for job status and results.
- `GET /v1/models/vastai`: List available Vast.ai models.
- `GET /v1/models/ollama`: List models from a target Ollama server.

### Auth Headers

- `Authorization: Bearer <token>`
- `X-API-Key: <key>`
- `X-Tenant-ID: <tenant>`

 
## REST API Reference

For a formal definition of all endpoints and request/reponse schemas, see the **[API Specification](API_SPEC.md)**.

 
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
