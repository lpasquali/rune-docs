# Quickstart

Get RUNE running in 5, 10, or 15 minutes. Pick the path that matches your goal.

| Path | Time | Good for |
|---|---|---|
| [1. pip-CLI](#path-1-pip-cli) | 5 min | Smallest possible footprint; try the CLI against an existing Ollama or backend |
| [2. docker-compose](#path-2-docker-compose) | 10 min | Full local stack (API + UI + docs + Ollama + S3) for integration testing |
| [3. kind + helm](#path-3-kind-helm) | 15 min | Local Kubernetes cluster running the Helm charts — closest to production |

All three paths target RUNE pre-alpha (`v0.0.0a5`). API surfaces are not stable; see [CURRENT_STATE](../context/CURRENT_STATE.md) for version-to-version status.

## Path 1: pip-CLI

Install `rune-bench` and run one benchmark against an existing Ollama (or any compatible backend) you already have running.

**Prerequisites**: Python ≥ 3.11, `pip`, a reachable Ollama (or other backend) on `http://localhost:11434`.

```bash
# Install core + all optional extras (holmesgpt driver, vastai-sdk, catalog helpers)
pip install rune-bench[all]

# Point at your backend
export RUNE_BACKEND_URL=http://localhost:11434

# Run one benchmark
python -m rune run-benchmark \
  --model llama3.1:8b \
  --question "Why is the cluster unhealthy?"
```

The CLI prints the benchmark result (numeric score + confidence + per-agent detail) or a helpful error if backend connectivity fails.

**Where next**: [Developer Guide](DEVELOPER_GUIDE.md) covers per-repo env setup, `rune.yaml` precedence, and `--profile` usage.

## Path 2: docker-compose

Spin up the full five-service stack defined in `rune/docker-compose.yml`: `rune-api`, `rune-ui`, `rune-docs`, `ollama`, `seaweedfs` (S3-compatible storage).

**Prerequisites**: Docker Engine ≥ 24 with the Compose plugin, ≥ 8 GB free RAM, `git`.

```bash
# Clone the runtime repo
git clone https://github.com/lpasquali/rune.git
cd rune

# Build + start the stack (cold build ≈ 5–10 min on first run)
docker compose up -d --build

# Verify health
curl -s http://127.0.0.1:8080/healthz   # rune-api
curl -s http://127.0.0.1:3000/healthz   # rune-ui
```

### Services

| Service | Port | URL | Purpose |
|---|---|---|---|
| rune-api | 8080 | <http://127.0.0.1:8080> | Core API server |
| rune-ui | 3000 | <http://127.0.0.1:3000> | HTMX frontend dashboard |
| rune-docs | 8000 | <http://127.0.0.1:8000> | Local copy of these docs |
| ollama | 11434 | <http://127.0.0.1:11434> | LLM inference server |
| seaweedfs | 8333 | <http://127.0.0.1:8333> | S3-compatible object store |

### Run a benchmark through the API

```bash
curl -sX POST http://127.0.0.1:8080/v1/benchmarks \
  -H 'Content-Type: application/json' \
  -d '{
    "agent": "holmesgpt",
    "backend_type": "ollama",
    "backend_url": "http://ollama:11434",
    "model": "llama3.1:8b",
    "question": "Why is the cluster unhealthy?"
  }'
```

### Teardown

```bash
docker compose down -v    # -v also removes volumes (clean slate)
```

**Where next**: [Deployment §Mode 2](../operations/DEPLOYMENT.md) has the service table with storage notes; the scenario-specific walkthroughs for air-gapped / edge / multi-tenant land under [epic #273](https://github.com/lpasquali/rune-docs/issues/273) child [#278](https://github.com/lpasquali/rune-docs/issues/278).

## Path 3: kind + helm

Local Kubernetes cluster running the Helm charts from `rune-charts/`. Closest-to-production path you can run on one workstation.

**Prerequisites**: Docker, `kind` ≥ v0.27, `kubectl` ≥ v1.35, `helm` ≥ v3.17, `git`, ≥ 12 GB free RAM. See [Workstation Setup](../operations/WORKSTATION.md) for the pinned versions.

```bash
# Clone the chart repo
git clone https://github.com/lpasquali/rune-charts.git
cd rune-charts

# Create the cluster
kind create cluster --name rune-quickstart

# Namespace + install
kubectl create namespace rune
helm install rune ./charts/rune \
  --namespace rune \
  --set rune.api.authDisabled=true \
  --wait --timeout=3m
helm install rune-operator ./charts/rune-operator \
  --namespace rune \
  --wait --timeout=3m

# Verify pods
kubectl -n rune get pods

# Port-forward the API for local access
kubectl -n rune port-forward svc/rune-api 8080:8080 &
curl -s http://127.0.0.1:8080/healthz
```

### Run a benchmark

```bash
curl -sX POST http://127.0.0.1:8080/v1/benchmarks \
  -H 'Content-Type: application/json' \
  -d '{
    "agent": "holmesgpt",
    "backend_type": "ollama",
    "backend_url": "http://rune-ollama.rune.svc:11434",
    "model": "llama3.1:8b",
    "question": "Why is the cluster unhealthy?"
  }'
```

### Clean up

```bash
kind delete cluster --name rune-quickstart
```

**Where next**: per-cloud install guides (on-prem / AWS / GCP / Azure / Alibaba Cloud) land under [epic #273](https://github.com/lpasquali/rune-docs/issues/273) child [#277](https://github.com/lpasquali/rune-docs/issues/277). For the production Helm values surface, see the `rune-charts/charts/rune/values.yaml` in the runtime repo.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: rune` after `pip install` | Install landed in a different interpreter | Activate your venv first, then `pip install rune-bench[all]` |
| `docker compose up` fails with permission denied on `/var/run/docker.sock` | User not in `docker` group | [WORKSTATION.md §Docker](../operations/WORKSTATION.md#docker) |
| `kind create cluster` hangs pulling `kindest/node` | Constrained bandwidth | Pre-pull the image: `docker pull kindest/node:v1.35.0` |
| `/v1/benchmarks` returns 404 | Auth not disabled and no token set | Either set `--set rune.api.authDisabled=true` as above, or wire tokens via Helm |

For more symptoms, the symptom-first FAQ landing under [#283](https://github.com/lpasquali/rune-docs/issues/283) will be the authoritative troubleshooting index.
