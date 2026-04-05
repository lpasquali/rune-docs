# CONFIGURATION

Environment variables and configuration files for RUNE.

## Environment Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_BACKEND` | `local` | Backend mode: `local` or `http`. |
| `RUNE_API_BASE_URL` | — | Base URL for remote API in `http` mode. |
| `RUNE_API_TOKEN` | — | Authentication token for the remote API. |
| `RUNE_API_TENANT` | `default` | Tenant name for the remote API. |
| `RUNE_API_DB_PATH` | `.rune-api/jobs.db` | Path to the SQLite job store database. |
| `RUNE_API_TOKENS` | — | Comma-separated map of `tenant:token` for the server. |
| `RUNE_API_AUTH_DISABLED` | `0` | Disable API authentication (dev-only). |

### Driver Layer Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_HOLMES_DRIVER_MODE` | `stdio` | Transport mode: `stdio` or `http`. |
| `RUNE_HOLMES_DRIVER_CMD` | `python -m rune_bench.drivers.holmes` | Stdio command to spawn. |
| `RUNE_HOLMES_DRIVER_URL` | — | Base URL for the remote HTTP driver. |
| `RUNE_HOLMES_DRIVER_TOKEN` | — | Bearer token for the HTTP driver. |

### Vast.ai Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VAST_API_KEY` | — | Your Vast.ai API key (usually at `~/.vast_api_key`). |
| `RUNE_VASTAI_TEMPLATE` | — | Default Vast.ai template hash. |

### S3 Results Sink

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNE_S3_ENABLED` | `false` | Enable the S3 results sink. |
| `RUNE_S3_BUCKET` | — | S3 bucket name for job results. |
| `RUNE_S3_PREFIX` | `results/` | S3 key prefix. |
| `RUNE_S3_ENDPOINT` | — | S3-compatible endpoint (e.g., MinIO or SeaweedFS). |

## Configuration Files

- `~/.kube/config`: Standard Kubernetes configuration.
- `~/.vast_api_key`: Default location for your Vast.ai API key.
- `rune.yaml.example`: Example configuration file template.
