# DEPLOYMENT

Hosting environments and provisioning for RUNE.

## Mode 1: CLI-Only (Local)
The CLI runs every workflow in-process. No server or database required.

```bash
export RUNE_BACKEND=local
rune run-benchmark --vastai ...
```

## Mode 2: Kubernetes (Production)
The API server runs as a Kubernetes Deployment via the `rune` Helm chart.

### Installation
```bash
helm install rune ./charts/rune \
  --set rune.api.authDisabled=false \
  --set rune.api.tokens="myteam:mytoken" \
  --set rune.s3.enabled=true
```

### Components
- **rune-api**: Python API server handling jobs.
- **SQLite**: Persistent volume for job storage.
- **S3 Sink**: Results pushed to S3/SeaweedFS.
- **rune-operator**: Cron-based job scheduling via Custom Resources.
- **Vault**: Optional secret injection via **[Vault Agent](VAULT.md)**.

## Mode 3: Docker Compose (Development)
A self-contained stack with API, Ollama, and SeaweedFS.

```bash
docker-compose up -d
```

## Infrastructure Dependencies
- **Vast.ai**: For GPU instance provisioning.
- **Ollama**: Inference server (local or provisioned).
- **Kubernetes**: Target cluster for HolmesGPT analysis.
- **S3-Compatible Storage**: For long-term result persistence.
