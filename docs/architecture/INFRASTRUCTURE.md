 
# INFRASTRUCTURE

Networking, scaling limits, and dependencies for RUNE.

 
## External Dependencies

- **Vast.ai API**: For provisioning GPU compute. Requires `VAST_API_KEY`.
- **Ollama API**: For model inference. Standard port `11434`.
- **S3-Compatible Object Store**: For long-term result persistence (SeaweedFS, AWS S3).
- **Kubernetes API**: For HolmesGPT to query cluster state (Pods, Events, Logs).

 
## Networking

- **Port 8080**: RUNE API server (internal or public).
- **Port 11434**: Ollama server.
- **Port 8333**: SeaweedFS S3 API.

 
## Scaling Limits

- **Concurrency**: SQLite-backed job storage is simple and reliable for
  single-node or single-pod deployments, but it limits high-volume concurrent
  writes and does not provide a shared store for multiple `rune-api` replicas.
  The accepted PostgreSQL direction is documented in
  **[ADR 0006](adrs/0006-storage-abstraction-postgres.md)**.
- **Vast.ai Limits**: Subject to provider availability and account limits.
- **Model Size**: Limited by target machine GPU memory (VRAM).

 
## Security Boundaries

- **HolmesGPT**: Runs with read-only RBAC by default in target clusters.
- **RUNE API**: Uses tenant-scoped tokens for authorization.
