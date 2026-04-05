 
# END-TO-END GUIDE

This guide walks you from a blank machine to a fully operational RUNE deployment running scheduled AI benchmarks against a Kubernetes cluster.

 
## Section 1 — Prerequisites

- `kubectl` ≥ 1.27
- `helm` ≥ 3.12
- Python ≥ 3.11
- `rune-bench` package
- Vast.ai API key
- Kubernetes cluster access

 
## Section 2 — Deploy RUNE API Server (Helm)

```bash
kubectl create namespace rune
helm install rune ./charts/rune \
  --namespace rune \
  --set rune.api.authDisabled=false \
  --set rune.api.tokens="myteam:$(openssl rand -hex 24)"
```

 
## Section 3 — Configure `rune.yaml`

Example configuration for your local environment:
```yaml
version: "1"
defaults:
  model: llama3.1:8b
  question: "What is unhealthy?"
  backend: http
  ollama_warmup: true
```

 
## Section 4 — Run Your First Benchmark

### Cloud GPU (Vast.ai)
```bash
rune --profile cloud-gpu run-benchmark \
  --question "Why is the cluster degraded?" \
  --model llama3.1:8b \
  --vastai-stop-instance
```

### Existing Server

```bash
rune run-benchmark \
  --ollama-url http://your-ollama-server:11434 \
  --model llama3.1:8b \
  --question "What is unhealthy?"
```

 
## Section 5 — Cost Philosophy

RUNE surfaces spend *before* provisioning.
- **Vast.ai**: Based on `max_dph`.
- **Cloud Stubs**: AWS ($2.50/hr), GCP ($2.20/hr), Azure ($3.06/hr).
- **Local**: Based on TDP, energy rates, and amortization.
