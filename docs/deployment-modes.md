# Deployment Modes

RUNE supports three deployment modes, from a single binary on a laptop to a fully
Kubernetes-native scheduled pipeline. All three share the same core logic — the
difference is where jobs run and where results land.

---

## Mode 1 — CLI only (`RUNE_BACKEND=local`)

The simplest path. The CLI runs every workflow in-process: it talks directly to
Vast.ai to provision a GPU, pulls the model onto the resulting Ollama server, and
then runs HolmesGPT against your Kubernetes cluster. No server, no database, no
extra infrastructure.

```mermaid
flowchart LR
    U([User])

    subgraph local["Local Machine"]
        CLI["rune CLI\nRUNE_BACKEND=local"]
        HOLMES["HolmesGPT\nin-process"]
    end

    subgraph vastai["Vast.ai Cloud"]
        GPU["GPU Instance\n+ Ollama server"]
    end

    K8S[("Kubernetes Cluster\nread-only, optional")]

    U -->|"rune run-benchmark --vastai\n--question '...' --model llama3.1:8b"| CLI
    CLI -->|"1 · provision GPU via Vast.ai SDK"| GPU
    GPU -->|"ollama_url"| CLI
    CLI -->|"2 · pull model + warm up"| GPU
    CLI -->|"3 · ask question"| HOLMES
    HOLMES -.->|"read pods / events / logs"| K8S
    HOLMES -->|"answer"| CLI
    CLI -->|"4 · stop instance"| GPU
    CLI -->|"print result to stdout"| U
```

### Quick start

```bash
pip install rune

export VAST_API_KEY=...
export RUNE_VASTAI_TEMPLATE=<hash>

rune run-benchmark \
  --vastai \
  --question "Why is the cluster degraded?" \
  --model llama3.1:8b \
  --kubeconfig ~/.kube/config \
  --vastai-stop-instance
```

---

## Mode 2 — CLI + API in Kubernetes

The API server runs as a Kubernetes Deployment (via the `rune` Helm chart).
The CLI switches to HTTP mode and submits jobs to the remote API instead of
executing them locally. The `rune-operator` adds declarative scheduling: apply
a `RuneBenchmark` CR with a cron expression and the operator drives the rest.

Results are stored in SQLite (persistent volume) **and** pushed to S3 after
each job succeeds via the S3 results sink (`rune_bench/s3_sink.py`).

```mermaid
flowchart TD
    USER([User / CI])

    subgraph external["External"]
        VAST["Vast.ai Cloud"]
        EXTOLLAMA["Ollama server\nexternal or sidecar"]
    end

    subgraph cluster["Kubernetes Cluster"]
        subgraph ops["rune-system namespace"]
            OP["rune-operator\nGo — leader-elected\nrobfig/cron scheduler"]
            CRD[("RuneBenchmark CR\nspec.schedule: '*/15 * * * *'\nspec.workflow / question / model")]
        end

        subgraph app["rune namespace"]
            SVC["Service :8080"]
            API["rune API server\nPython"]
            DB[("SQLite\njobs.db — PersistentVolume")]
            SINK["S3 sink\nrune_bench/s3_sink.py\nboto3 put_object"]
            SA["ServiceAccount\nread-only RBAC"]
        end

        K8SAPI["Kubernetes API Server"]
    end

    subgraph storage["Object Storage"]
        S3[("S3 Bucket\nresults/{tenant}/{kind}/{date}/{job_id}.json")]
    end

    USER -->|"rune run-benchmark\nRUNE_BACKEND=http"| SVC
    USER -->|"kubectl apply RuneBenchmark"| CRD
    CRD -->|"watched by"| OP
    OP -->|"cron fires\nPOST /v1/jobs/benchmark\nX-Tenant-ID + Bearer"| SVC
    SVC --> API
    API --> DB
    API -->|"job succeeded → push result"| SINK
    SINK -->|"boto3"| S3
    API -->|"provision GPU"| VAST
    API -->|"pull model / warmup / ask"| EXTOLLAMA
    API -->|"HolmesGPT reads"| SA
    SA -->|"pods / events / logs"| K8SAPI
```

### Quick start (Mode 2)

```bash
# Install the Helm chart
helm install rune ./charts/rune \
  --set rune.api.authDisabled=false \
  --set rune.api.tokens="myteam:mytoken" \
  --set rune.s3.enabled=true \
  --set rune.s3.bucket=rune-results

# Run a one-off benchmark from the CLI
export RUNE_BACKEND=http
export RUNE_API_BASE_URL=https://rune.example.com
export RUNE_API_TENANT=myteam
export RUNE_API_TOKEN=mytoken

rune run-benchmark \
  --question "Why is the cluster degraded?" \
  --model llama3.1:8b

# Or apply a scheduled RuneBenchmark CRD
kubectl apply -f - <<EOF
apiVersion: bench.rune.ai/v1alpha1
kind: RuneBenchmark
metadata:
  name: nightly-health-check
  namespace: rune-system
spec:
  apiBaseUrl: http://rune.rune.svc.cluster.local:8080
  workflow: run-benchmark
  question: "What is degraded in the cluster?"
  model: llama3.1:8b
  schedule: "0 2 * * *"   # 02:00 UTC daily
  timeoutSeconds: 300
EOF
```

### New component — S3 results sink

| Item | Detail |
|------|--------|
| Module | `rune_bench/s3_sink.py` |
| Hook | called in `api_server.py::_execute_job()` after `store.update_job(status="succeeded")` |
| Library | `boto3` (already available transitively) |
| S3 key | `results/{tenant_id}/{job_kind}/{YYYY-MM-DD}/{job_id}.json` |
| Payload | full job record: id, tenant, kind, status, result, created_at, updated_at |

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_S3_ENABLED` | `false` | Enable the S3 sink |
| `RUNE_S3_BUCKET` | — | Bucket name |
| `RUNE_S3_PREFIX` | `results/` | Key prefix |
| `RUNE_S3_ENDPOINT` | — | Override endpoint (for self-hosted; empty = AWS) |

---

## Mode 3 — Docker Compose (client / server)

A self-contained stack for local development or single-host deployments. The
rune API server runs in a container; the CLI talks to it over HTTP. Results are
persisted to a SQLite volume **and** pushed to
[SeaweedFS](https://github.com/seaweedfs/seaweedfs) — an Apache 2.0-licensed,
S3-compatible object store used in production by Kubeflow.

```mermaid
flowchart LR
    USER([User])

    subgraph host["Host"]
        CLI["rune CLI\nRUNE_BACKEND=http\nRUNE_API_BASE_URL=http://localhost:8080"]
    end

    subgraph compose["Docker Compose — rune-net"]
        API["rune-api :8080\nRUNE_BACKEND=local\nRUNE_OLLAMA_URL=http://ollama:11434"]
        DB[("volume: rune-db\njobs.db")]
        OLLAMA["ollama :11434\nCPU or GPU"]
        SWF["seaweedfs :8333\nS3-compatible\nApache 2.0"]
        DATA[("volume: seaweedfs-data\nrune-results bucket")]
    end

    USER -->|"rune ..."| CLI
    CLI -->|"HTTP REST"| API
    API --- DB
    API -->|"S3 results — boto3"| SWF
    SWF --- DATA
    API -->|"model pull / warmup / infer"| OLLAMA
```

The `docker-compose.yml` is at the root of the `rune` repository. See its inline
comments for GPU and production-S3 override instructions.

---

## Driver configuration

All three modes use the driver layer to invoke HolmesGPT. The transport is
selected per-driver via environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_HOLMES_DRIVER_MODE` | `stdio` | Transport mode: `stdio` or `http` |
| `RUNE_HOLMES_DRIVER_CMD` | `python -m rune_bench.drivers.holmes` | Stdio command to spawn (parsed with `shlex.split`) |
| `RUNE_HOLMES_DRIVER_URL` | — | Base URL for HTTP mode (required when mode is `http`) |
| `RUNE_HOLMES_DRIVER_TOKEN` | — | Bearer token sent to the HTTP driver server |
| `RUNE_HOLMES_DRIVER_TENANT` | `default` | Tenant header sent to the HTTP driver server |

In stdio mode (default) the driver subprocess must have `holmesgpt` installed.
The core rune process does **not** require it.

```bash
# Override with a custom installed binary
export RUNE_HOLMES_DRIVER_CMD=rune-holmes-driver

# Use a remote HTTP driver instead of a local subprocess
export RUNE_HOLMES_DRIVER_MODE=http
export RUNE_HOLMES_DRIVER_URL=http://holmes-sidecar:8080
```

See [Drivers](drivers.md) for the full wire protocol and custom driver guide.
