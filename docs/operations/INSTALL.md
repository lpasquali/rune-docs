# Install — cloud and on-prem

Parameterized install guides for production Kubernetes deployments of RUNE. Each target (on-prem, AWS, GCP, Azure, Alibaba Cloud) follows the same shape so you can skim one, pick another, and know where to look.

All cloud targets build on the **Crossplane baseline** from [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md) for provisioning the stateful dependencies (PostgreSQL, S3-compatible object storage). On-prem uses CNPG for PostgreSQL and local/Ceph/Longhorn for storage — documented in [DATABASE_HA](DATABASE_HA.md).

## Choose your target

| Target | Status | Page |
|---|---|---|
| On-prem k8s (Talos / Rancher / OpenShift / bare-metal) | **Full** | [INSTALL_ONPREM](INSTALL_ONPREM.md) |
| AWS (EKS) | **Scaffold** (structure + TODO markers) | [INSTALL_AWS](INSTALL_AWS.md) |
| GCP (GKE) | **Scaffold** | [INSTALL_GCP](INSTALL_GCP.md) |
| Azure (AKS) | **Scaffold** | [INSTALL_AZURE](INSTALL_AZURE.md) |
| Alibaba Cloud (ACK) | **Scaffold** | [INSTALL_ALICLOUD](INSTALL_ALICLOUD.md) |

**Scaffold** pages have the correct structure (Prerequisites / Provisioning / Chart install / Secret wiring / Validation) but the cloud-specific detail needs hands-on validation on a real cluster. Flesh-out issues are filed as follow-ups under [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277).

## Shared baseline

Every install path shares this shape:

### 1. Prerequisites

- Kubernetes ≥ 1.27 (RUNE's tested floor).
- `kubectl` ≥ 1.35, `helm` ≥ 3.17.
- Crossplane installed in the cluster (or equivalent provisioning path per-cloud).
- Credentials with enough authority to provision the cloud's managed PostgreSQL + object storage, or an opt-out to bring-your-own stateful services.

### 2. Provisioning

Crossplane manages the **stateful** dependencies (database, object store) as Kubernetes CRs. The benefit over hand-written Terraform: the lifecycle of Postgres and S3 bucket is declarative Kubernetes resources — `kubectl apply` creates them, `kubectl delete` tears them down.

```yaml
# common pattern — provider/resource names vary per cloud
apiVersion: example.crossplane.io/v1beta1
kind: DBInstance
metadata:
  name: rune-db
spec:
  forProvider:
    engine: postgres
    version: "16"
    storage: 100  # GiB
```

Alternative: bring your own managed service. Point RUNE's Helm values at an existing endpoint via `rune.storage.postgresql.url` + `rune.storage.s3.endpoint`.

### 3. Chart install

Charts live in [rune-charts](https://github.com/lpasquali/rune-charts):

```bash
helm install rune ./charts/rune \
  --namespace rune \
  --create-namespace \
  --values ./my-values.yaml \
  --wait --timeout=5m

helm install rune-operator ./charts/rune-operator \
  --namespace rune \
  --wait --timeout=5m
```

Optional: `rune-ui` and `rune-audit` per their own charts.

### 4. Secret wiring

The API server reads:

- **Database URL**: `rune.storage.postgresql.url` or env `RUNE_DB_URL`.
- **S3 endpoint + access/secret keys**: `rune.storage.s3.*` values or `RUNE_S3_*` env.
- **API tokens**: `rune.api.tokens` (format: `team:token[,team:token]`). Comparison is constant-time with `hmac.compare_digest` — see [MIGRATION §Token handling](https://github.com/lpasquali/rune-docs/issues/283).
- **Agent driver credentials**: `RUNE_<AGENT>_DRIVER_TOKEN` etc. per [DriverTransport](https://github.com/lpasquali/rune-docs/issues/280).

All secrets injected via Kubernetes Secret objects; Vault integration available per [Vault](VAULT.md).

### 5. Validation

```bash
kubectl -n rune get pods -l app.kubernetes.io/part-of=rune
kubectl -n rune port-forward svc/rune-api 8080:8080 &
curl -sf http://127.0.0.1:8080/healthz
```

Then run one benchmark end-to-end:

```bash
curl -X POST http://127.0.0.1:8080/v1/benchmarks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent":"holmesgpt","backend_type":"ollama","backend_url":"http://rune-ollama.rune.svc:11434","model":"llama3.1:8b","question":"test"}'
```

## Further reading

- [ADR 0007: Crossplane infrastructure provisioning](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md) — why Crossplane was chosen over Terraform.
- [ADR 0006: Storage Abstraction and PostgreSQL](../architecture/adrs/0006-storage-abstraction-postgres.md) — the DB roadmap.
- [DATABASE_HA](DATABASE_HA.md) — CNPG planning for on-prem high availability.
- [SCENARIOS](https://github.com/lpasquali/rune-docs/issues/278) — decision matrix (airgap / edge / multi-tenant / regulated / local-dev / CI-inline).
