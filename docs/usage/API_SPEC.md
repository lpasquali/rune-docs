 
# RUNE API Specification

This document defines the formal REST API for the RUNE platform.

 
## Base URL

The default base URL is `http://localhost:8080`.

 
## Authentication

RUNE uses tenant-scoped authentication with strict security controls.
- **Header**: `X-Tenant-ID` (optional, defaults to `default`)
- **Header**: `Authorization: Bearer <token>` or `X-API-Key: <key>`
- **Storage**: Tokens configured via `RUNE_API_TOKENS` are immediately hashed (SHA-256) in memory on server startup. Plaintext tokens are never stored in memory.
- **Validation**: Incoming tokens are hashed and compared against stored hashes using constant-time comparison (`hmac.compare_digest`).
- **Rate Limiting**: Authentication endpoints enforce a strict rate limit. Accumulating 10 failed authentication attempts from a single source IP within a 60-second rolling window will result in a temporary block (HTTP 401).

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

#### Run LLM Instance

`POST /v1/jobs/llm-instance`
- **Request Body**: `RunLLMInstanceRequest`
- **Response**: `{"job_id": "...", "status": "accepted"}`
- **Deprecated alias**: `POST /v1/jobs/ollama-instance` (still functional)

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

#### List LLM Backend Models

`GET /v1/llm/models?backend_url=<url>&backend_type=ollama`
- **Response**: `{"backend_url": "...", "backend_type": "ollama", "models": [...], "running_models": [...]}`
- **Deprecated alias**: `GET /v1/ollama/models?backend_url=<url>` (still functional)

### Metrics

`GET /v1/metrics/summary?job_id=<id>`
- **Response**: `{"events": [...]}` (aggregated metrics)

### Chain Visualization

#### Get Chain State

`GET /v1/chains/{run_id}/state`
- **Response**: `{"run_id": "...", "nodes": [...], "edges": [...], "overall_status": "pending|running|success|failed|skipped"}`
- **404**: Unknown run or tenant-scoped miss
- **Notes**:
  - Existing runs with no recorded chain state return an empty shell:
    `{"run_id": "...", "nodes": [], "edges": [], "overall_status": "pending"}`
  - `nodes[*]` include per-step status and timestamps; `edges[*]` use
    `{"from": "...", "to": "..."}` pairs.

### Audit Artifacts

#### List Audit Artifacts

`GET /v1/audits/{run_id}/artifacts`
- **Response**:
  `{"run_id": "...", "summary": {"total_count": 0, "kinds_present": []}, "artifacts": [...]}`
- **Artifact metadata shape**:
  `{"artifact_id": "...", "kind": "sbom", "name": "sbom.json", "size_bytes": 1234, "sha256": "...", "created_at": 1712660100.0, "download_url": "/v1/audits/{run_id}/artifacts/{artifact_id}"}`
- **404**: Unknown run or tenant-scoped miss
- **Notes**:
  - The list response excludes raw bytes.
  - An existing run with no audit evidence returns `200` with an empty list.

#### Download Audit Artifact

`GET /v1/audits/{run_id}/artifacts/{artifact_id}`
- **Response**: Raw artifact bytes with `Content-Disposition: attachment`
- **Content-Type**:
  - `application/json` for JSON-backed artifacts such as SLSA provenance,
    SBOMs, or TLA+ reports
  - `application/octet-stream` for binary or opaque artifacts such as Sigstore,
    Rekor, or TPM evidence

 
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
  "backend_warmup": true,
  "vastai_stop_instance": true
}
```
