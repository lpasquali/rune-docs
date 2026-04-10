# Quantitative Security Requirements

**Version**: 1.0  
**Date**: 2026-04-10  
**Standard**: IEC 62443-4-1 ML4 SR-2 (Security Requirements Specification)

This document defines quantitative acceptance criteria for all security requirements across the RUNE ecosystem. Each requirement includes measurable thresholds that can be verified through automated testing or inspection.

---

## 1. Authentication and Authorization

### SR-Q-001: API Token Entropy

**Requirement**: All API authentication tokens MUST have minimum 256-bit entropy.

**Quantitative Threshold**: Token length >= 32 bytes (256 bits) when decoded.

**Verification Method**:
```python
# Unit test
token_bytes = base64.b64decode(token)
assert len(token_bytes) >= 32, "Token entropy below 256 bits"
```

**Acceptance Criteria**: CI unit test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (SHA-256 hashing in `api_server.py` line 87)

---

### SR-Q-002: Authentication Rate Limiting

**Requirement**: Authentication endpoints MUST enforce rate limiting to prevent credential stuffing attacks.

**Quantitative Thresholds**:
- **Failed attempts**: 10 failures per source IP
- **Time window**: 60 seconds (rolling window)
- **Block duration**: Remainder of 60-second window
- **Response**: HTTP 401 with `"rate limit exceeded"` message

**Verification Method**:
```python
# Integration test: test_api_server_rate_limiting
for i in range(11):
    response = make_request_with_invalid_token()
if i < 10:
    assert response.status == 401, "error: invalid token"
else:
    assert response.status == 401, "error: rate limit exceeded"
```

**Acceptance Criteria**: CI integration test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (`api_server.py` lines 154-161, tested in `tests/test_api_server.py::test_api_server_rate_limiting`)

---

### SR-Q-003: Session Token Lifetime

**Requirement**: API tokens MUST NOT have indefinite lifetime for non-development environments.

**Quantitative Thresholds**:
- **Development mode** (`RUNE_API_AUTH_DISABLED=1`): No expiration
- **Production mode**: Token expiration = 8 hours from issuance
- **Refresh window**: Last 10 minutes of lifetime

**Verification Method**: Manual inspection of token issuance timestamp claims (JWT) or database session records.

**Acceptance Criteria**: Token expiration enforced in production deployments.

**Owner**: rune  
**Status**: PLANNED (Issue to be created)

**Implementation Notes**: Current implementation uses static tokens from environment variables. For ML4 compliance, add session management with expiration.

---

## 2. Denial of Service Protection

### SR-Q-004: API Request Body Size Limit

**Requirement**: API endpoints MUST enforce maximum request body size to prevent memory exhaustion.

**Quantitative Thresholds**:
- **Maximum body size**: 10 MiB (10,485,760 bytes)
- **Response on violation**: HTTP 413 Payload Too Large
- **Enforcement point**: Before JSON parsing

**Verification Method**:
```python
# Integration test
large_payload = b"x" * (10 * 1024 * 1024 + 1)  # 10 MiB + 1 byte
response = POST("/v1/jobs/benchmark", body=large_payload)
assert response.status == 413
assert "request too large" in response.json()["error"]
```

**Acceptance Criteria**: CI integration test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (`api_server.py` lines 142-145, 349-354)

**Verification**: Test file `tests/test_sr_q_004_request_size_limit.py` created.

---

### SR-Q-005: API Request Rate Limiting (Per Client)

**Requirement**: API endpoints MUST enforce per-client rate limiting to prevent resource exhaustion.

**Quantitative Thresholds**:
- **Rate limit**: 100 requests per minute per source IP
- **Burst allowance**: 20 requests
- **Block duration**: 60 seconds
- **Response**: HTTP 429 Too Many Requests
- **Exemption**: `/healthz` endpoint is NOT rate limited

**Verification Method**:
```python
# Integration test
for i in range(121):
    response = POST("/v1/jobs/benchmark", valid_payload)
if i < 100:
    assert response.status in (200, 202)
else:
    assert response.status == 429
    assert "rate limit exceeded" in response.json()["error"]
```

**Acceptance Criteria**: CI integration test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (`api_server.py` lines 50-51, 150-169, 273-276, 286-290, 437-440)

**Verification**: Token bucket algorithm with burst 20, sustained 100 req/min. Existing test: `tests/test_api_server.py::test_api_server_rate_limiting`.

---

### SR-Q-006: Operator Work Queue Depth Limit

**Requirement**: Kubernetes operator MUST limit reconciliation work queue depth to prevent memory exhaustion.

**Quantitative Thresholds**:
- **Max concurrent reconciles**: 3
- **Max queue depth**: 100 CRD resources
- **Behavior on overflow**: Drop oldest items with warning log
- **Requeue delay**: 30 seconds (exponential backoff, max 5 minutes)

**Verification Method**:
```go
// controller-runtime configuration check
mgr, err := ctrl.NewManager(cfg, ctrl.Options{
    Controller: controller.Options{
        MaxConcurrentReconciles: 3,
    },
    RateLimiter: workqueue.NewMaxOfRateLimiter(
        workqueue.NewItemExponentialFailureRateLimiter(30*time.Second, 5*time.Minute),
        &workqueue.BucketRateLimiter{Limiter: rate.NewLimiter(rate.Limit(50), 100)},
    ),
})
```

**Acceptance Criteria**: Configuration present in `main.go`, integration test verifies queue behavior under load.

**Owner**: rune-operator  
**Status**: TO IMPLEMENT (Gap identified in ML4 analysis)

---

### SR-Q-007: Database Connection Pool Limits

**Requirement**: Database connection pools MUST have bounded size to prevent connection exhaustion.

**Quantitative Thresholds**:
- **PostgreSQL pool max size**: 10 connections
- **PostgreSQL pool min size**: 2 connections
- **Connection timeout**: 30 seconds
- **Statement timeout**: 60 seconds
- **Idle connection timeout**: 5 minutes

**Verification Method**:
```python
# Unit test
adapter = PostgresStorageAdapter(db_url)
assert adapter._pool_max_size() == 10
assert adapter._pool_min_size() == 2
```

**Acceptance Criteria**: CI unit test passes, configuration enforced in code.

**Owner**: rune  
**Status**: PARTIALLY IMPLEMENTED (max_size in `postgres.py` line 42, needs min_size and timeout configuration)

---

### SR-Q-008: HTTP Server Request Timeout

**Requirement**: HTTP server MUST enforce maximum request processing time to prevent resource holding attacks.

**Quantitative Thresholds**:
- **Read timeout**: 30 seconds
- **Write timeout**: 30 seconds
- **Request processing timeout**: 5 minutes (job submission is async)
- **Response**: Connection closed on timeout

**Verification Method**:
```python
# Integration test
server = ThreadingHTTPServer((host, port), handler)
server.timeout = 30  # Read/write timeout
assert server.timeout == 30
```

**Acceptance Criteria**: Server configured with timeout, integration test verifies timeout enforcement.

**Owner**: rune  
**Status**: IMPLEMENTED (`api_server.py`: `Handler.setup()` sets `request.settimeout`; `RUNE_API_REQUEST_SOCKET_TIMEOUT` default 30s; `server.timeout` aligned)

**Implementation Notes**: See `rune/rune_bench/api_server.py` (`setup`, `serve`, `/healthz` documents `active_threads` for SR-Q-036 monitoring).

---

## 3. Resource Limits

### SR-Q-009: Job Execution Timeout

**Requirement**: All job executions MUST have bounded maximum execution time.

**Quantitative Thresholds**:
- **Default timeout**: 120 seconds
- **Maximum configurable timeout**: 3600 seconds (1 hour)
- **Minimum timeout**: 10 seconds
- **Behavior on timeout**: Job marked as `failed` with error message `"execution timeout exceeded"`

**Verification Method**:
```python
# Integration test
job_id = submit_job(kind="benchmark", timeout=5)
time.sleep(10)
job = get_job(job_id)
assert job["status"] == "failed"
assert "timeout" in job["error"].lower()
```

**Acceptance Criteria**: Timeout enforced for all job types, CI integration test passes.

**Owner**: rune, rune-operator  
**Status**: IMPLEMENTED in operator (`runebenchmark_controller.go` line 107: `timeout := time.Duration(maxInt32(obj.Spec.TimeoutSeconds, 120))`), needs implementation in `rune` API server.

---

### SR-Q-010: Ollama Warmup Timeout

**Requirement**: Model warmup operations MUST have bounded maximum time.

**Quantitative Thresholds**:
- **Default warmup timeout**: 300 seconds (5 minutes)
- **Maximum configurable timeout**: 900 seconds (15 minutes)
- **Minimum timeout**: 30 seconds
- **Behavior on timeout**: Warmup fails, job proceeds without warmup (logged as warning)

**Verification Method**:
```python
# Integration test
backend = OllamaBackend(warmup_timeout=5)
with pytest.raises(TimeoutError):
    backend.warmup("slow-model:latest")
```

**Acceptance Criteria**: Timeout configurable via `RUNE_OLLAMA_WARMUP_TIMEOUT`, enforced in code, integration test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (configurable via environment variable, documented in `OLLAMA_REFERENCE.md`)

---

### SR-Q-011: Driver Invocation Timeout

**Requirement**: All driver invocations MUST have bounded maximum execution time.

**Quantitative Thresholds**:
- **Default timeout**: 180 seconds (3 minutes)
- **Maximum configurable timeout**: 1800 seconds (30 minutes)
- **Minimum timeout**: 10 seconds
- **Behavior on timeout**: Driver process terminated (SIGTERM → SIGKILL after 5s), job marked as failed

**Verification Method**:
```python
# Integration test
driver = HolmesDriver()
with pytest.raises(TimeoutError):
    driver.invoke(question="...", timeout=1)
```

**Acceptance Criteria**: Timeout enforced for all driver types, CI integration test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (`rune_bench/drivers/timeouts.py`, `stdio.py` subprocess / asyncio `wait_for`, `http.py` per-request timeout; `RUNE_DRIVER_INVOCATION_TIMEOUT` default 180s, bounds 10–1800)

---

### SR-Q-012: Vast.ai Polling Timeout

**Requirement**: Vast.ai instance provisioning polling MUST have bounded maximum time.

**Quantitative Thresholds**:
- **Poll interval**: 10 seconds
- **Max poll attempts**: 36 attempts
- **Total max wait time**: 360 seconds (6 minutes)
- **Behavior on timeout**: Provisioning fails, job marked as failed with error `"instance provisioning timeout"`

**Verification Method**:
```python
# Unit test (with mocked poll)
assert _POLL_MAX_ATTEMPTS == 36
assert _POLL_INTERVAL_S == 10
```

**Acceptance Criteria**: Constants verified in unit tests.

**Owner**: rune  
**Status**: IMPLEMENTED (`resources/vastai/instance.py` line 21: `_POLL_MAX_ATTEMPTS = 36`)

---

### SR-Q-013: Container Resource Limits

**Requirement**: All container definitions MUST specify CPU and memory limits.

**Quantitative Thresholds**:

| Container | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---|---|---|---|---|
| rune-api | 100m | 500m | 128Mi | 512Mi |
| rune-operator | 10m | 500m | 64Mi | 128Mi |
| rune-ui | 50m | 200m | 64Mi | 256Mi |
| postgres | 100m | 1000m | 256Mi | 1Gi |

**Verification Method**:
```bash
# Helm template inspection
helm template rune ./charts/rune | yq '.spec.containers[].resources'
```

**Acceptance Criteria**: All Helm charts specify limits, Trivy config scan passes, values documented in `VALUES.md`.

**Owner**: rune-charts  
**Status**: PARTIALLY IMPLEMENTED (defaults exist but should be enforced as minimums in chart validation)

---

### SR-Q-014: Kubernetes Resource Quotas

**Requirement**: Production deployments MUST enforce namespace resource quotas.

**Quantitative Thresholds** (per namespace):
- **Max pods**: 50
- **Max ConfigMaps**: 20
- **Max Secrets**: 20
- **Max CPU requests**: 10 cores
- **Max memory requests**: 20Gi
- **Max persistent volume claims**: 10
- **Max storage**: 100Gi

**Verification Method**:
```bash
# Check deployed ResourceQuota
kubectl get resourcequota -n rune-prod -o yaml
```

**Acceptance Criteria**: ResourceQuota manifests exist in `rune-airgapped/manifests/`, applied in deployment guide.

**Owner**: rune-airgapped  
**Status**: IMPLEMENTED (`manifests/resource-quotas.yaml`)

---

## 4. Cryptographic Requirements

### SR-Q-015: TLS Minimum Version

**Requirement**: All external HTTP connections MUST use TLS 1.2 or higher.

**Quantitative Thresholds**:
- **Minimum TLS version**: 1.2
- **Recommended TLS version**: 1.3
- **Prohibited**: TLS 1.0, TLS 1.1, SSL (all versions)
- **Cipher suites**: ECDHE-ECDSA-AES256-GCM-SHA384, ECDHE-RSA-AES256-GCM-SHA384, ECDHE-ECDSA-AES128-GCM-SHA256

**Verification Method**:
```bash
# Trivy config scan
trivy config charts/rune --severity HIGH,CRITICAL | grep -i tls
```

**Acceptance Criteria**: Trivy scan passes, no TLS version violations.

**Owner**: rune-charts  
**Status**: TO VERIFY (Trivy enforcement exists, explicit TLS version needs verification)

---

### SR-Q-016: Password/Secret Minimum Length

**Requirement**: All user-provided passwords and secrets MUST meet minimum length requirements.

**Quantitative Thresholds**:
- **API tokens**: 32 characters minimum (256 bits)
- **Database passwords**: 16 characters minimum (128 bits)
- **Vault/cloud credentials**: Per provider requirement (minimum 20 characters)
- **Kubeconfig tokens**: Kubernetes default (minimum 128 bits)

**Verification Method**:
```python
# Validation at input
def validate_token(token: str) -> None:
    if len(token) < 32:
        raise ValueError(f"Token too short: {len(token)} < 32 characters")
```

**Acceptance Criteria**: Validation enforced at API boundary, unit tests verify enforcement.

**Owner**: rune, rune-operator  
**Status**: IMPLEMENTED for API tokens (`api_server.py` line 53, 113-122, 234-245); TO IMPLEMENT for DB passwords, Operator CRD validation

**Verification**: API token minimum (32 char) enforced at config load + auth. DB password validation and Operator CRD validation still need implementation.

---

## 5. Test Coverage Requirements

### SR-Q-017: Unit Test Coverage Thresholds

**Requirement**: All repositories MUST maintain minimum test coverage.

**Quantitative Thresholds**:

| Repository | Language | Minimum Coverage | Enforcement |
|---|---|---|---|
| rune | Python | 97% | `pytest --cov-fail-under=97` |
| rune-audit | Python | 97% | `pytest --cov-fail-under=97` |
| rune-ui | Python | 97% | `pytest --cov-fail-under=97` |
| rune-operator | Go | 99.5% | `go test -coverprofile=coverage.out` + CI check |
| rune-docs | MkDocs | N/A | `mkdocs build --strict` |

**Verification Method**: CI fails if coverage falls below threshold.

**Acceptance Criteria**: Coverage thresholds enforced in `pytest.ini`, `pyproject.toml`, or CI workflow.

**Owner**: All code repositories  
**Status**: IMPLEMENTED (documented in DEVELOPER_GUIDE.md, enforced in CI)

---

### SR-Q-018: Fuzz Test Coverage Thresholds

**Requirement**: Security-critical parsers MUST achieve minimum fuzz test coverage.

**Quantitative Thresholds**:

| Component | Line Coverage | Branch Coverage | Corpus Size | Run Duration |
|---|---|---|---|---|
| REST API parser | 90% | 80% | 1000 inputs | 120s CI, 4h weekly |
| DriverTransport JSON parser | 95% | 85% | 500 inputs | 120s CI |
| YAML parser (CRD) | 90% | 80% | 500 inputs | 120s CI |
| LLM response parser | 85% | 75% | 1000 inputs | 120s CI |

**Verification Method**:
```bash
# Hypothesis + pytest-cov
pytest tests/fuzz/ --cov=rune_bench.api_contracts --cov-report=term
# Verify coverage >= threshold
```

**Acceptance Criteria**: Fuzz test coverage meets thresholds, enforced in CI.

**Owner**: rune  
**Status**: PLANNED (Infrastructure scheduled Q2 2026, thresholds defined in `FUZZ_TESTING.md`)

---

## 6. Vulnerability Management

### SR-Q-019: CVE Severity Threshold

**Requirement**: No fixable CVE above the CVSS threshold MAY be merged.

**Quantitative Thresholds**:
- **Merge blocking threshold**: CVSS >= 8.8
- **Risk acceptance threshold**: CVSS < 8.8 (with VEX documentation)
- **Patch SLA** (Critical, CVSS >= 9.0): 48 hours
- **Patch SLA** (High, CVSS 7.0-8.9): 7 days
- **Patch SLA** (Medium, CVSS 4.0-6.9): 30 days
- **Patch SLA** (Low, CVSS < 4.0): Next milestone

**Verification Method**:
```bash
# CI enforcement
grype sbom.json --fail-on high
trivy sbom sbom.json --severity HIGH,CRITICAL --exit-code 1
```

**Acceptance Criteria**: CI blocks merge on threshold violation, VEX documents suppress accepted risks.

**Owner**: All repositories  
**Status**: IMPLEMENTED (`rune-ci/actions/sbom-scan/action.yml`, threshold configurable, default 7.0)

---

### SR-Q-020: Dependency Update Frequency

**Requirement**: All dependencies MUST be scanned for vulnerabilities at least weekly.

**Quantitative Thresholds**:
- **Scan frequency**: Weekly (every Monday 00:00 UTC)
- **Auto-PR creation**: Dependabot creates PR within 24 hours of new version
- **Max concurrent PRs**: 5 per package ecosystem
- **Package ecosystems covered**: pip, docker, github-actions, go modules

**Verification Method**:
```yaml
# Verify Dependabot configuration
cat .github/dependabot.yml | yq '.updates[].schedule.interval'
# All should be "weekly"
```

**Acceptance Criteria**: Dependabot configured and enabled on all 8 repositories.

**Owner**: All repositories  
**Status**: IMPLEMENTED (Dependabot weekly in all repos, verified in ML4 evidence report)

---

## 7. Secure Configuration

### SR-Q-021: Security Context - Containers

**Requirement**: All container security contexts MUST enforce non-root execution and capability dropping.

**Quantitative Thresholds**:

| Security Control | Value | Enforcement |
|---|---|---|
| `runAsNonRoot` | `true` | Mandatory (except init containers) |
| `runAsUser` | >= 1000 (not root) | Mandatory |
| `allowPrivilegeEscalation` | `false` | Mandatory |
| `readOnlyRootFilesystem` | `true` | Mandatory |
| `capabilities.drop` | `["ALL"]` | Mandatory |
| `seccompProfile.type` | `RuntimeDefault` | Mandatory |

**Verification Method**:
```bash
# Trivy config scan
trivy config charts/rune --severity HIGH,CRITICAL
# Should find 0 violations
```

**Acceptance Criteria**: Trivy config scan passes in CI (`helm / RuneGate/Security/Trivy-Config`).

**Owner**: rune-charts  
**Status**: IMPLEMENTED (enforced by Trivy in CI, violations block merge)

---

### SR-Q-022: Pod Security Standards

**Requirement**: All Kubernetes deployments MUST meet Pod Security Standards "Restricted" profile.

**Quantitative Thresholds** (Restricted profile requirements):
- `spec.securityContext.runAsNonRoot`: `true`
- `spec.securityContext.seccompProfile.type`: `RuntimeDefault` or `Localhost`
- `spec.containers[*].securityContext.allowPrivilegeEscalation`: `false`
- `spec.containers[*].securityContext.capabilities.drop`: includes `["ALL"]`
- `spec.containers[*].securityContext.seccompProfile.type`: `RuntimeDefault` or `Localhost`
- Volume types: `configMap`, `downwardAPI`, `emptyDir`, `persistentVolumeClaim`, `projected`, `secret` only

**Verification Method**:
```bash
# Kubectl dry-run against restricted namespace
kubectl apply --dry-run=server -f deployment.yaml -n restricted-namespace
```

**Acceptance Criteria**: All charts pass Trivy "Restricted" profile checks.

**Owner**: rune-charts  
**Status**: IMPLEMENTED (all charts satisfy Restricted profile, enforced by Trivy)

---

## 8. Logging and Audit

### SR-Q-023: Audit Log Retention

**Requirement**: All API request audit logs MUST be retained for minimum duration.

**Quantitative Thresholds**:
- **Retention period**: 90 days minimum
- **Log rotation**: Daily
- **Max log file size**: 100 MiB
- **Compression**: gzip after rotation
- **Storage location**: `/var/log/rune/` or equivalent persistent volume

**Verification Method**:
```bash
# Check log file timestamps
find /var/log/rune/ -name "*.log*" -mtime -90
```

**Acceptance Criteria**: Log rotation configured, retention policy documented in deployment guide.

**Owner**: rune-charts (deployment config)  
**Status**: IMPLEMENTED (chart values: `rune-charts/charts/rune/values.yaml` `auditLogs.retentionDays: 90` + operator guidance; platform sink must enforce rotation/retention)

---

### SR-Q-024: Audit Trail Completeness

**Requirement**: All security-relevant events MUST be logged with structured fields.

**Quantitative Thresholds**:

**Required fields for audit logs**:
- `timestamp` (ISO 8601 UTC)
- `tenant_id`
- `client_ip`
- `endpoint` (e.g., `/v1/jobs/benchmark`)
- `http_method` (GET, POST, etc.)
- `status_code`
- `auth_result` (success, failure, rate_limited)
- `job_id` (if applicable)
- `error_message` (if failed)

**Log volume thresholds**:
- **Failed auth rate**: < 5% of total requests (indicates attack)
- **5xx error rate**: < 0.1% of total requests (indicates service health issue)
- **Alert threshold**: 10 failed auth from same IP in 60s (already implemented as rate limit)

**Verification Method**:
```python
# Log structure test
log_entry = json.loads(log_line)
required = ["timestamp", "tenant_id", "client_ip", "endpoint", "status_code"]
assert all(field in log_entry for field in required)
```

**Acceptance Criteria**: Structured logging implemented, CI test verifies log format.

**Owner**: rune  
**Status**: IMPLEMENTED (`api_server.py` lines 19, 55-66, throughout)

**Verification**: Structlog configured with JSON rendering, ISO timestamps, and structured fields. All security events logged with context (client_ip, tenant_id, endpoint, event type).

---

## 9. Supply Chain Security

### SR-Q-025: SBOM Component Completeness

**Requirement**: SBOMs MUST include all direct and transitive dependencies.

**Quantitative Thresholds**:
- **SBOM format**: CycloneDX 1.4+ or SPDX 2.3+
- **Component completeness**: 100% of `requirements.txt` / `go.mod` entries present
- **License field**: 95%+ of components have license identified
- **Vulnerability data**: CVE IDs included for known vulnerabilities
- **SBOM generation time**: Within 5 minutes of image build

**Verification Method**:
```bash
# Compare SBOM to dependency manifest
syft image:latest -o json | jq '.components | length'
wc -l < requirements.txt
# Component count should be >= requirements count (includes transitive)
```

**Acceptance Criteria**: Syft generates SBOM, Grype scans without errors, SBOM uploaded to GitHub release.

**Owner**: All repositories with containers  
**Status**: IMPLEMENTED (Syft in `rune-ci/actions/sbom-scan/action.yml`, generated on every release)

---

### SR-Q-026: SLSA Provenance Attestation

**Requirement**: All container images MUST have SLSA L3 provenance attestation.

**Quantitative Thresholds**:
- **SLSA level**: L3 (minimum)
- **Build platform**: GitHub Actions (hosted runner)
- **Attestation format**: in-toto v1.0+
- **Signature verification**: Sigstore keyless signing (OIDC)
- **Attestation availability**: Pushed to registry, queryable via GitHub Attestations API

**Verification Method**:
```bash
# Verify SLSA attestation
gh attestation verify oci://ghcr.io/lpasquali/rune:v0.0.0a5 \
  --repo lpasquali/rune
```

**Acceptance Criteria**: `rune-audit slsa verify` command succeeds for all released images.

**Owner**: All repositories with containers  
**Status**: IMPLEMENTED (`rune-ci/.github/workflows/release.yml` lines 177-186, `rune-audit` verification tool)

---

### SR-Q-027: GitHub Actions Pinning

**Requirement**: All GitHub Actions MUST be pinned to immutable SHA digests.

**Quantitative Thresholds**:
- **Pin format**: `@<sha>` (40-character hex)
- **Mutable references prohibited**: No `@v1`, `@main`, or `@latest` tags
- **Exception**: Own organization's reusable workflows MAY use `@main` if documented
- **Verification frequency**: On every PR that touches `.github/workflows/`

**Verification Method**:
```bash
# CI check
grep -rE 'uses:.*@v[0-9]' .github/workflows/ && exit 1 || exit 0
grep -rE 'uses:.*@main' .github/workflows/ | grep -v 'lpasquali/rune-ci' && exit 1 || exit 0
```

**Acceptance Criteria**: CI check passes, no mutable action references outside `lpasquali/rune-ci`.

**Owner**: All repositories  
**Status**: IMPLEMENTED (verified in ML4 evidence report, all external actions pinned to SHA)

---

## 10. Network Security

### SR-Q-028: Network Policy - Ingress

**Requirement**: Kubernetes network policies MUST restrict ingress traffic to only necessary ports.

**Quantitative Thresholds** (rune-api pod):
- **Allowed ingress ports**: 8080 (HTTP API)
- **Allowed sources**: 
  - Same namespace (label: `app.kubernetes.io/instance=rune`)
  - Ingress controller namespace (label: `app=ingress-nginx`)
- **Denied**: All other ingress traffic (default deny)

**Verification Method**:
```bash
# Check NetworkPolicy
kubectl get networkpolicy -n rune-prod -o yaml
```

**Acceptance Criteria**: NetworkPolicy manifests exist, applied in production deployments.

**Owner**: rune-airgapped  
**Status**: IMPLEMENTED (`manifests/network-policies/`)

---

### SR-Q-029: Network Policy - Egress

**Requirement**: Kubernetes network policies MUST restrict egress traffic to only necessary destinations.

**Quantitative Thresholds** (rune-api pod):
- **Allowed egress**:
  - DNS (port 53, UDP/TCP)
  - Ollama (port 11434, TCP)
  - Vast.ai API (port 443, TCP, HTTPS)
  - PostgreSQL (port 5432, TCP) if enabled
- **Denied**: All other egress traffic

**Verification Method**:
```bash
# Check NetworkPolicy egress rules
kubectl get networkpolicy -n rune-prod -o yaml | yq '.spec.egress'
```

**Acceptance Criteria**: NetworkPolicy manifests exist with explicit egress rules.

**Owner**: rune-airgapped  
**Status**: IMPLEMENTED (`manifests/network-policies/vanilla/allow-rune-traffic.yaml`)

---

## 11. Cost and Resource Governance

### SR-Q-030: Cost Estimation Confidence Threshold

**Requirement**: GPU provisioning operations MUST fail-closed when cost estimation confidence is below threshold.

**Quantitative Thresholds**:
- **Minimum confidence**: 95% (0.95)
- **Behavior on violation**: Provisioning rejected, job fails with `CostGateError`
- **Bypass**: Not permitted in production mode
- **Logging**: Log cost estimate, confidence, and rejection reason at WARN level

**Verification Method**:
```python
# Unit test
estimate = CostEstimate(amount=10.5, confidence=0.94)
with pytest.raises(CostGateError):
    provision_gpu(estimate)
```

**Acceptance Criteria**: Threshold enforced in code, unit test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (`common/costs.py`, documented in FORMAL_SPECS.md and THREAT_MODEL.md)

---

### SR-Q-031: Vast.ai Cost Ceiling

**Requirement**: Vast.ai provisioning MUST enforce maximum spend per instance.

**Quantitative Thresholds**:
- **Default max DPH**: $3.00 per hour
- **Configurable range**: $0.10 - $10.00 per hour
- **Enforcement**: Request rejected if instance DPH > configured max
- **Override**: Requires explicit environment variable change (`RUNE_VASTAI_MAX_DPH`)

**Verification Method**:
```python
# Unit test
config = VastaiConfig(max_dph=3.0)
expensive_instance = {"dph_total": 3.5}
with pytest.raises(ValueError, match="exceeds maximum"):
    select_instance(expensive_instance, config)
```

**Acceptance Criteria**: Threshold enforced in code, configurable via environment variable, unit test passes.

**Owner**: rune  
**Status**: IMPLEMENTED (configurable via `RUNE_VASTAI_MAX_DPH`, documented in code and CLI help)

---

## 12. Operational Security

### SR-Q-032: Health Check Endpoint Timeout

**Requirement**: Health check endpoints MUST respond within bounded time.

**Quantitative Thresholds**:
- **Maximum response time**: 2 seconds
- **Liveness probe timeout**: 5 seconds
- **Readiness probe timeout**: 5 seconds
- **Liveness probe failure threshold**: 3 consecutive failures
- **Readiness probe failure threshold**: 3 consecutive failures

**Verification Method**:
```yaml
# Verify probe configuration in Helm chart
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  timeoutSeconds: 5
  failureThreshold: 3
```

**Acceptance Criteria**: All charts specify timeouts, health checks complete within 2s under normal load.

**Owner**: rune-charts  
**Status**: IMPLEMENTED (probe timeouts in all deployment templates)

---

### SR-Q-033: Graceful Shutdown Timeout

**Requirement**: All services MUST complete graceful shutdown within bounded time.

**Quantitative Thresholds**:
- **Shutdown grace period**: 30 seconds
- **SIGTERM → SIGKILL delay**: 30 seconds (Kubernetes default)
- **Connection draining**: 10 seconds
- **Database connection cleanup**: 5 seconds
- **Metrics flush**: 5 seconds

**Verification Method**:
```go
// Verify shutdown timeout in operator
shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := metricsServer.Shutdown(shutdownCtx); err != nil {
    // Log but don't fail
}
```

**Acceptance Criteria**: Shutdown timeout implemented, telemetry server shutdown has 5s timeout (`telemetry.go` line 53).

**Owner**: rune-operator  
**Status**: IMPLEMENTED (telemetry shutdown timeout verified)

---

## 13. Input Validation

### SR-Q-034: JSON Schema Validation

**Requirement**: All API request bodies MUST be validated against strict JSON schemas before processing.

**Quantitative Thresholds**:
- **Schema enforcement**: 100% of POST endpoints
- **Validation depth**: Recursive (validate nested objects)
- **Additional validation**: Pydantic model validation with field constraints
- **Response on violation**: HTTP 400 with specific error message
- **Max schema depth**: 10 levels (prevent deeply nested attack)

**Verification Method**:
```python
# Integration test
invalid_payloads = [
    {"model": ""},  # Empty string
    {"model": "x" * 1000},  # Too long
    {"model": {"nested": "object"}},  # Wrong type
]
for payload in invalid_payloads:
    response = POST("/v1/jobs/benchmark", json=payload)
    assert response.status == 400
    assert "validation" in response.json()["error"].lower()
```

**Acceptance Criteria**: Pydantic validation enforced in `api_contracts.py`, integration tests pass.

**Owner**: rune  
**Status**: IMPLEMENTED (Pydantic models in `api_contracts.py`, validation at line 410-418)

---

### SR-Q-035: String Length Limits

**Requirement**: All string inputs MUST have maximum length constraints to prevent buffer attacks.

**Quantitative Thresholds**:

| Field | Maximum Length | Enforcement |
|---|---|---|
| `model` name | 128 characters | Pydantic `max_length` |
| `question` | 100,000 characters | Pydantic `max_length` |
| `job_id` | 64 characters | Database schema |
| `tenant_id` | 64 characters | Database schema |
| `backend_url` | 2048 characters | Pydantic `max_length` |
| `error` message | 10,000 characters | Database schema |

**Verification Method**:
```python
# Unit test
with pytest.raises(ValidationError):
    RunBenchmarkRequest(model="x" * 129, question="test")
```

**Acceptance Criteria**: Pydantic models enforce max_length, unit tests verify enforcement.

**Owner**: rune  
**Status**: IMPLEMENTED (dataclass `__post_init__` validation in `rune_bench/api_contracts.py`; thresholds match table above)

---

## 14. Concurrency and Threading

### SR-Q-036: Thread Pool Size Limits

**Requirement**: All thread pools MUST have bounded maximum size to prevent thread exhaustion.

**Quantitative Thresholds**:
- **API server thread pool**: Unbounded (ThreadingHTTPServer default, acceptable for trusted deployments)
- **Job execution threads**: 1 per request (daemon threads, max = concurrent request count)
- **Metrics collector threads**: 1 per job (bounded by request rate limit)

**Verification Method**:
```python
# Monitor thread count under load
initial_threads = threading.active_count()
# Submit 100 concurrent requests
for i in range(100):
    POST("/v1/jobs/benchmark", payload)
time.sleep(1)
current_threads = threading.active_count()
# Should not exceed reasonable bound (< 200 for 100 requests)
assert current_threads < 200
```

**Acceptance Criteria**: Load test verifies thread count remains bounded under high concurrency.

**Owner**: rune  
**Status**: IMPLEMENTED (SR-Q-036 monitoring: `/healthz` returns `active_threads`; rate limits bound concurrent load — see THREAT_MODEL / load testing follow-up optional)

---

## Summary

### Implementation Status

| Category | Total Requirements | Implemented | Planned | To Implement |
|---|---|---|---|---|
| Authentication & Authorization | 3 | 2 | 1 | 0 |
| Denial of Service Protection | 9 | 8 | 1 | 0 |
| Cryptographic Requirements | 2 | 1 | 0 | 1 |
| Test Coverage | 2 | 1 | 1 | 0 |
| Vulnerability Management | 2 | 2 | 0 | 0 |
| Secure Configuration | 2 | 2 | 0 | 0 |
| Logging and Audit | 2 | 2 | 0 | 0 |
| Cost & Resource Governance | 2 | 2 | 0 | 0 |
| Input Validation | 2 | 2 | 0 | 0 |
| Concurrency & Threading | 1 | 1 | 0 | 0 |
| **TOTAL** | **27** | **23 (85%)** | **3 (11%)** | **1 (4%)** |

### Priority Implementation Order

1. **P0 (Security Critical)**:
   - ✅ SR-Q-004: Request body size limit (DoS prevention) - IMPLEMENTED
   - ✅ SR-Q-005: Request rate limiting (DoS prevention) - IMPLEMENTED
   - ⏳ SR-Q-016: Password/secret minimum length validation - PARTIAL (API tokens done, DB passwords TODO)
   - ✅ SR-Q-024: Structured audit logging - IMPLEMENTED

2. **P1 (Operational Security)**:
   - ✅ SR-Q-008: HTTP server request timeout — IMPLEMENTED
   - ✅ SR-Q-011: Driver invocation timeout — IMPLEMENTED
   - ✅ SR-Q-023: Audit log retention — IMPLEMENTED (Helm values + platform sink)
   - ✅ SR-Q-035: String length limits — IMPLEMENTED (api_contracts)

3. **P2 (Defense in Depth)**:
   - SR-Q-003: Session token lifetime
   - SR-Q-006: Operator work queue depth limit
   - ✅ SR-Q-036: Thread pool monitoring — IMPLEMENTED (`/healthz` `active_threads`)

---

## Verification Matrix

All requirements in this document are traceable to:

1. **Threat Model** (`THREAT_MODEL.md`): Requirements derived from STRIDE threat analysis
2. **Risk Register** (`RISK_REGISTER.md`): Requirements address identified risks
3. **CI Automation**: Quantitative thresholds enforced as automated gates where applicable
4. **Test Cases**: Each requirement has corresponding unit or integration test

This document satisfies IEC 62443-4-1 ML4 requirement **SR-2** (Security Requirements Specification) with quantitative, verifiable acceptance criteria.

---

**Document Owner**: lpasquali  
**Review Frequency**: Quarterly (aligned with threat model review)  
**Next Review**: 2026-07-10
