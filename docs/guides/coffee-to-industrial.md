# Coffee-to-Industrial: End-to-End RUNE Setup Guide

This guide walks you from a blank machine to a fully operational RUNE deployment
running scheduled AI benchmarks against a Kubernetes cluster.

> **Time to complete:** ~30 minutes (plus GPU provisioning time ~5 minutes)

---

## Section 1 — Prerequisites

### Required tools

| Tool | Version | Install |
|------|---------|---------|
| `kubectl` | ≥ 1.27 | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| `helm` | ≥ 3.12 | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |
| Python | ≥ 3.11 | [python.org/downloads](https://www.python.org/downloads/) |
| `rune` CLI | latest | `pip install rune-bench` |

### Required accounts / credentials

- **Vast.ai account** with an API key — [console.vast.ai](https://console.vast.ai)
- A reachable **Kubernetes cluster** (local `kind`/`k3s` or cloud-managed)
- A valid `kubeconfig` pointing at the target cluster

### Verify prerequisites

```bash
kubectl version --client --short
helm version --short
python --version
rune --version

# Export secrets (never commit these)
export VAST_API_KEY=<your-vast-ai-api-key>
```

---

## Section 2 — Deploy RUNE API Server (Helm)

Add the chart repository and deploy to the `rune` namespace:

```bash
# Clone the charts repository (or use the packaged chart from a release)
git clone https://github.com/lpasquali/rune-charts
cd rune-charts

# Create namespace
kubectl create namespace rune

# Install with a production token
helm install rune ./charts/rune \
  --namespace rune \
  --set rune.api.tokens="myteam:$(openssl rand -hex 24)" \
  --set rune.api.authDisabled=false \
  --set rune.persistentVolume.enabled=true

# Wait for the pod to be ready
kubectl rollout status deployment/rune-api -n rune --timeout=120s

# Confirm the health endpoint responds
kubectl port-forward svc/rune-api 8080:8080 -n rune &
curl -s http://localhost:8080/healthz
# Expected: {"status": "ok"}
```

!!! note "Cost philosophy"
    Before deploying, review the [cost estimation drivers](../drivers.md) to
    understand how RUNE projects Vast.ai spend (`min_dph` / `max_dph`) and local
    hardware amortization.  The `POST /v1/estimates` endpoint lets you preview
    costs *before* any GPU is provisioned.

---

## Section 3 — Configure `rune.yaml`

Create a `rune.yaml` in your working directory (never commit secrets):

```yaml
version: "1"

defaults:
  model: llama3.1:8b
  question: "What is unhealthy in this Kubernetes cluster?"
  kubeconfig: ~/.kube/config
  backend: http
  ollama_warmup: true
  ollama_warmup_timeout: 300
  vastai: false
  vastai_stop_instance: true
  template_hash: c166c11f035d3a97871a23bd32ca6aba

profiles:
  # Full Vast.ai GPU provisioning (cloud-grade benchmarks)
  cloud-gpu:
    vastai: true
    min_dph: 2.3
    max_dph: 3.0
    reliability: 0.99
    ollama_warmup: true

  # Lightweight local testing (no Vast.ai)
  local:
    vastai: false
    backend: local
    ollama_url: http://localhost:11434
    ollama_warmup: false
```

Export the API connection details:

```bash
export RUNE_BACKEND=http
export RUNE_API_BASE_URL=http://localhost:8080   # adjust for your cluster ingress
export RUNE_API_TENANT=myteam
export RUNE_API_TOKEN=<the-token-set-during-helm-install>
```

Verify the configuration is parsed correctly:

```bash
rune config
```

---

## Section 4 — Run Your First Benchmark

### Option A — Cloud GPU (Vast.ai provisioning)

```bash
rune --profile cloud-gpu run-benchmark \
  --question "Why is the cluster degraded?" \
  --model llama3.1:8b \
  --kubeconfig ~/.kube/config \
  --vastai-stop-instance
```

RUNE will:

1. Search Vast.ai for a GPU offer matching your `min_dph` / `max_dph` / `reliability`.
2. Provision the instance and wait up to 6 minutes for it to start.
3. Pull the requested Ollama model and warm it up.
4. Submit the question to HolmesGPT against your cluster.
5. Destroy the instance and return the answer.

### Option B — Existing Ollama server (no Vast.ai)

```bash
rune run-benchmark \
  --ollama-url http://your-ollama-server:11434 \
  --model llama3.1:8b \
  --question "What is unhealthy in this Kubernetes cluster?" \
  --kubeconfig ~/.kube/config
```

### Pre-flight cost check

Before provisioning any GPU you can request a cost estimate:

```bash
curl -s -X POST http://localhost:8080/v1/estimates \
  -H "Authorization: Bearer $RUNE_API_TOKEN" \
  -H "X-Tenant-ID: $RUNE_API_TENANT" \
  -H "Content-Type: application/json" \
  -d '{
    "vastai": true,
    "min_dph": 2.3,
    "max_dph": 3.0,
    "estimated_duration_seconds": 1800
  }' | python -m json.tool
```

Expected response:

```json
{
  "projected_cost_usd": 1.5,
  "cost_driver": "vastai",
  "resource_impact": "low",
  "local_energy_kwh": 0.0,
  "confidence_score": 0.9,
  "warning": "Vast.ai cost based on your Max DPH setting."
}
```

---

## Section 5 — View Results in rune-ui

Job results are stored in SQLite and optionally pushed to S3. You can query them
directly via the API or integrate with rune-ui.

### Poll a running job

```bash
# Submit a job and capture its ID
JOB_ID=$(curl -s -X POST http://localhost:8080/v1/jobs/benchmark \
  -H "Authorization: Bearer $RUNE_API_TOKEN" \
  -H "X-Tenant-ID: $RUNE_API_TENANT" \
  -H "Content-Type: application/json" \
  -d '{
    "vastai": false,
    "template_hash": "c166c11f035d3a97871a23bd32ca6aba",
    "min_dph": 2.3, "max_dph": 3.0, "reliability": 0.99,
    "ollama_url": "http://localhost:11434",
    "question": "What is degraded?",
    "model": "llama3.1:8b",
    "ollama_warmup": true, "ollama_warmup_timeout": 120,
    "kubeconfig": "",
    "vastai_stop_instance": true
  }' | python -c "import sys,json; print(json.load(sys.stdin)['job_id'])")

echo "Job ID: $JOB_ID"

# Poll until terminal status
curl -s "http://localhost:8080/v1/jobs/$JOB_ID" \
  -H "Authorization: Bearer $RUNE_API_TOKEN" \
  -H "X-Tenant-ID: $RUNE_API_TENANT" | python -m json.tool
```

### Schedule recurring benchmarks (Kubernetes operator)

Apply a `RuneBenchmark` CRD to have the operator drive benchmarks on a cron
schedule:

```yaml
apiVersion: bench.rune.ai/v1alpha1
kind: RuneBenchmark
metadata:
  name: nightly-health-check
  namespace: rune-system
spec:
  apiBaseUrl: http://rune-api.rune.svc.cluster.local:8080
  apiTokenSecretRef: "rune-system/rune-api-token"
  tenant: myteam
  workflow: run-benchmark
  question: "What is degraded in the cluster?"
  model: llama3.1:8b
  schedule: "0 2 * * *"        # 02:00 UTC nightly
  timeoutSeconds: 300
  backoffSeconds: 60
```

```bash
kubectl apply -f nightly-health-check.yaml
kubectl get runebenchmarks -n rune-system
```

---

## Section 6 — Cost Philosophy

### Why cost estimation matters

Every benchmark involves either real GPU-hours on Vast.ai or local hardware
energy draw.  RUNE surfaces spend *before* provisioning so you can make informed
decisions.

| Driver | Billing model | RUNE estimation |
|--------|--------------|-----------------|
| **Vast.ai** | Real-time $/hr spot market | `max_dph × duration_hours` — uses your configured ceiling |
| **Azure** | VM retail price (no-auth API) | Live fetch from `prices.azure.com`; falls back to $3.06/hr stub |
| **AWS** | Spot price | Documented stub at $2.50/hr for GPU-class instances |
| **GCP** | Spot price | Documented stub at $2.20/hr for GPU-class instances |
| **Local** | Energy + amortization | `(TDP_W/1000 × hours × rate_$/kWh) + (purchase_price / lifetime_hours × hours)` |

### Key levers

- **`min_dph` / `max_dph`** — Hard bounds on what RUNE will pay per GPU-hour.
  Narrowing the range reduces cost variance but may reduce offer availability.
- **`reliability`** — Filters out unreliable instances.  Higher reliability
  typically means a slightly higher $/hr but fewer interruptions.
- **`--vastai-stop-instance`** — Always pass this flag in production to destroy
  the GPU instance after the benchmark; otherwise the meter keeps running.
- **`estimated_duration_seconds`** — Used only for cost projection; the actual
  benchmark runs until HolmesGPT returns an answer.

See the [Drivers documentation](../drivers.md) for the full cost driver
architecture and how to plug in custom estimators.

### Resource impact thresholds

| Impact | Condition |
|--------|-----------|
| `low` | projected cost ≤ $5.00 |
| `medium` | $5.00 < projected cost ≤ $20.00 |
| `high` | projected cost > $20.00 |

A `high` resource impact will surface a warning in the CLI and the rune-ui
pre-flight screen.

---

## Next Steps

- Review [Deployment Modes](../deployment-modes.md) for Docker Compose and
  multi-node Kubernetes configurations.
- Read the [Architecture documentation](../architecture.md) to understand the
  full reconciliation loop.
- Check the [API Compatibility Plan](../API_COMPATIBILITY_PLAN.md) before
  integrating external tooling.
- Explore the [Ollama Quick Reference](../OLLAMA_QUICK_REFERENCE.md) for model
  management tips.
