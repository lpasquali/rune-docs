 
# DEPLOYMENT

Hosting environments and provisioning for RUNE.

 
## Mode 1: CLI-Only (Standalone)

The CLI runs every workflow in-process. No server or database required.

```bash
cd ~/Devel/rune
. .venv/bin/activate

export RUNE_BACKEND=local
export RUNE_OLLAMA_URL=http://localhost:11434

# Verify CLI is functional
python -m rune --help

# Run a benchmark
python -m rune run-benchmark \
  --model llama3.1:8b \
  --question "Why is the cluster unhealthy?"
```

**When to use**: Quick iteration, unit testing, local debugging.

 
## Mode 2: Docker Compose (Development)

A self-contained stack with API, UI, docs, Ollama, and SeaweedFS (S3). Defined in `~/Devel/rune/docker-compose.yml`.

```bash
cd ~/Devel/rune

# Build and start the full stack
docker compose up -d --build

# Verify services
curl -s http://localhost:8080/healthz   # rune-api
curl -s http://localhost:3000/healthz   # rune-ui

# View logs
docker compose logs -f rune-api
```

### Services and Ports

| Service | Port | Description |
|---|---|---|
| `rune-api` | 8080 | Core API server |
| `rune-ui` | 3000 | HTMX frontend |
| `rune-docs` | 8000 | Documentation site |
| `ollama` | 11434 | LLM inference server |
| `seaweedfs` | 8333 | S3-compatible object storage |

### Teardown

```bash
docker compose down -v   # -v removes volumes (clean state)
```

**When to use**: End-to-end testing, UI development, integration testing without Kubernetes.

 
## Mode 3: Kubernetes via Kind (Testing)

A local Kubernetes cluster using Kind, deployed with Helm charts from `~/Devel/rune-charts/`.

```bash
cd ~/Devel/rune-charts

# Create cluster
kind create cluster --name rune-test

# Deploy
kubectl create namespace rune-test
helm install rune ./charts/rune --namespace rune-test --wait --timeout=2m
helm install rune-operator ./charts/rune-operator --namespace rune-test --wait --timeout=2m

# Verify
kubectl -n rune-test get pods

# Port-forward for local access
kubectl -n rune-test port-forward svc/rune-api 8080:8080 &
curl -s http://localhost:8080/healthz

# Clean up
kind delete cluster --name rune-test
```

**When to use**: Testing Helm charts, operator behavior, CRD validation, Kubernetes-specific features.

 
## Mode 4: Kubernetes (Production)

The API server runs as a Kubernetes Deployment via the `rune` Helm chart. Tokens passed via Helm are securely hashed (SHA-256) by the application before being stored in memory.

```bash
helm install rune ./charts/rune \
  --set rune.api.authDisabled=false \
  --set rune.api.tokens="myteam:mytoken" \
  --set rune.s3.enabled=true
```

### Components

- **rune-api**: Python API server handling jobs.
- **SQLite**: Current default persistence model. A single persistent volume backs
  the embedded job store for local and single-pod installs.
- **S3 Sink**: Results pushed to S3/SeaweedFS.
- **rune-operator**: Cron-based job scheduling via Custom Resources.
- **Vault**: Optional secret injection via **[Vault Agent](VAULT.md)**.

### Storage Status

Today, released deployments should assume **SQLite-only runtime support** via
`RUNE_API_DB_PATH`.

External PostgreSQL support is an accepted architecture direction, but it is not
complete in the current release line. Track the design and rollout sequence in
**[DATABASE.md](DATABASE.md)** and
**[ADR 0006](../architecture/adrs/0006-storage-abstraction-postgres.md)**.

 
## Infrastructure Dependencies

| Dependency | Required for | Notes |
|---|---|---|
| **Ollama** | All modes | Inference server (local or provisioned) |
| **Vast.ai** | GPU provisioning | Cloud GPU rental; requires `VAST_API_KEY` |
| **Kubernetes** | Modes 3 and 4 | Target cluster for operator and HolmesGPT |
| **S3-Compatible Storage** | Result persistence | SeaweedFS (compose) or any S3 endpoint |
| **Kind** | Mode 3 | Local Kubernetes for testing |
| **Helm** | Modes 3 and 4 | Chart-based deployment |
