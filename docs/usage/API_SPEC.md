 
# RUNE API Specification

This document defines the formal REST API for the RUNE platform.

 
## Base URL

The default base URL is `http://localhost:8080`.

 
## Authentication

RUNE uses tenant-scoped authentication.
- **Header**: `X-Tenant-ID` (optional, defaults to `default`)
- **Header**: `Authorization: Bearer <token>` or `X-API-Key: <key>`
- **Idempotency**: `Idempotency-Key` (optional for POST jobs)

 
## Endpoints

### Health Check

`GET /healthz`
- **Response**: `{"status": "ok"}`

### Cost Estimation

`POST /v1/estimates`
- **Request Body**: `CostEstimationRequest`
- **Response**: `CostEstimationResponse`

### Job Management

Jobs are processed asynchronously. `POST` returns `202 Accepted` with a `job_id`.

#### Run Agentic Agent

`POST /v1/jobs/agentic-agent`
- **Request Body**: `RunAgenticAgentRequest`
- **Response**: `{"job_id": "...", "status": "accepted"}`

#### Run Benchmark

`POST /v1/jobs/benchmark`
- **Request Body**: `RunBenchmarkRequest`
- **Response**: `{"job_id": "...", "status": "accepted"}`

#### Run Ollama Instance

`POST /v1/jobs/ollama-instance`
- **Request Body**: `RunOllamaInstanceRequest`
- **Response**: `{"job_id": "...", "status": "accepted"}`

#### Get Job Status

`GET /v1/jobs/{job_id}`
- **Response**: `JobRecord` (includes status, result, or error)

#### Get Job Events

`GET /v1/jobs/{job_id}/events`
- **Response**: `{"job_id": "...", "events": [...]}`

### Catalog & Discovery

#### List Vast.ai Models

`GET /v1/catalog/vastai-models`
- **Response**: `{"models": [...]}`

#### List Ollama Models

`GET /v1/ollama/models?ollama_url=<url>`
- **Response**: `{"models": [...]}`

### Metrics

`GET /v1/metrics/summary?job_id=<id>`
- **Response**: `{"events": [...]}` (aggregated metrics)

 
## Data Structures

### `CostEstimationRequest`

```json
{
  "vastai": true,
  "min_dph": 0.0,
  "max_dph": 3.0,
  "model": "llama3.1:8b",
  "estimated_duration_seconds": 3600
}
```

### `RunBenchmarkRequest`

```json
{
  "vastai": true,
  "template_hash": "...",
  "min_dph": 2.3,
  "max_dph": 3.0,
  "reliability": 0.99,
  "question": "What is unhealthy?",
  "model": "llama3.1:8b",
  "ollama_warmup": true,
  "vastai_stop_instance": true
}
```
