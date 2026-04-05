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
- `ollama.model_pull`: Time taken to download a model.
- `agent.ask`: Duration of the agentic analysis question.

## Logs
RUNE uses standard Python `logging`.

### Structured Logging
In `http` mode, logs include:
- `job_id`: The ID of the currently executing job.
- `tenant_id`: The tenant associated with the request.
- `event`: Specific lifecycle events.

## Results Persistence
- **SQLite**: Local/Kubernetes persistence for immediate job state.
- **S3 Sink**: JSON results pushed to S3/SeaweedFS for long-term storage and audit.
  - Path: `results/{tenant}/{kind}/{date}/{job_id}.json`
