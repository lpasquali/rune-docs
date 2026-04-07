 
# OBSERVABILITY

Metrics, logs, and tracing formats for RUNE.

 
## Metrics

RUNE features a lightweight, thread-safe metrics layer in `rune_bench/metrics.py`.

### Collectors

- **`InMemoryCollector`**: Accumulates events for CLI summary printing.
- **`SQLiteMetricsCollector`**: Persists events to the job store for analysis.
- **`NullCollector`**: Default no-op collector.

### Key Metrics Events

- `vastai.offer_search`: Duration and outcome of finding GPU offers.
- `vastai.instance_create`: Provisioning success/failure and timing.
- `backend.warmup`: Time taken to warm up / pull a model via `LLMBackend.warmup()`.
- `agent.ask`: Duration of the agentic analysis question (includes `backend_type` attribute).
- `backend.list_models`: Time to enumerate available models on a backend.
- `backend.get_capabilities`: Time to fetch model capabilities (context window, max tokens).

 
## Logs

RUNE uses standard Python `logging`.

### Structured Logging

In `http` mode, logs include:
- `job_id`: The ID of the currently executing job.
- `tenant_id`: The tenant associated with the request.
- `event`: Specific lifecycle events.

 
## Observability Boundaries

Metrics and traces are emitted at the following layer boundaries:

| Layer | Span / Metric | Attributes |
|---|---|---|
| `DriverTransport` | `driver.call` | `driver_name`, `action`, `transport_type` (stdio/http) |
| `AgentRunner` | `agent.ask` | `agent_name`, `model`, `backend_url`, `backend_type` |
| `LLMBackend` | `backend.warmup`, `backend.list_models`, `backend.get_capabilities` | `backend_type`, `base_url` |
| `LLMResourceProvider` | `provider.provision`, `provider.teardown` | `provider_type` (vastai/existing), `backend_type` |
| `CostEstimation` | `cost.estimate` | `provider` (vastai/aws/gcp/azure/local), `confidence_score` |

All spans include `job_id` when executing within a job context. The `backend_type` attribute replaced the former Ollama-specific instrumentation as part of the backend abstraction (rune#170-#172).

 
## Results Persistence

- **SQLite**: Local/Kubernetes persistence for immediate job state.
- **S3 Sink**: JSON results pushed to S3/SeaweedFS for long-term storage and audit.
  - Path: `results/{tenant}/{kind}/{date}/{job_id}.json`
