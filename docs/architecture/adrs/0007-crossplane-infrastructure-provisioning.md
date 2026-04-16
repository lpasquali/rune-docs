# ADR 0007: Crossplane Infrastructure Provisioning

## Status

Accepted (implementation in progress)

## Context

Epic #252 established that RUNE's production airgapped deployments treat PostgreSQL and S3 as
**customer-managed prerequisites**, not bundled components. Operators currently provision
infrastructure out-of-band (CNPG operator, AWS RDS, Cloud SQL, etc.) and manually create
Kubernetes Secrets before `helm install rune`.

This works but creates friction:
1. No infrastructure-as-code declarative provisioning in the cluster
2. Manual Secret creation is error-prone and not idempotent
3. Credential rotation, Secret cleanup, and lifecycle management are manual

Crossplane closes this gap by enabling declarative, Kubernetes-native infrastructure
provisioning behind the same `existingSecret` interface that `rune-charts` already expects.

## Decision

RUNE will support **Crossplane as an optional, opt-in provisioning layer** for PostgreSQL and
S3 resources in Kubernetes environments.

### Architecture

- **XRDs (Composite Resource Definitions)**: Two RUNE-specific abstractions — `RuneDatabase`
  and `RuneObjectStore` — that abstract away cloud provider differences.
- **Compositions**: Implementations of these XRDs for AWS (RDS + S3), GCP (Cloud SQL + GCS),
  Azure (Flexible Server + Blob), and on-prem (CNPG + MinIO).
- **Secret Bridge**: `provider-kubernetes` writes connection Secrets (`rune-db-secret`,
  `rune-s3-secret`) that `rune-charts` already consumes via `existingSecret`.

### Stable Contract (Zero Chart Changes)

The `rune-charts` `deployment.yaml` template consumes Secrets at fixed names:
- `rune-db-secret` with key `RUNE_DB_URL` (consumed by `rune.database.existingSecret`)
- `rune-s3-secret` with keys `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY` (consumed by `s3.existingSecret`)

Crossplane's only job is to **write these exact Secrets** when a Claim is applied. No Helm
template changes. No chart dependency on `rune-crossplane`.

### API Versions and Claims

- **XRD API**: `apiextensions.crossplane.io/v1` (not v2) with `scope: LegacyCluster` to preserve
  the Crossplane **Claims** UX — cluster admins apply a `RuneDatabase` Claim, not a raw XR.
- **Composition**: Function-based pipeline (`function-patch-and-transform` +
  `function-go-templating` + `function-auto-ready`) to handle complex wiring (e.g., CNPG's
  multi-key Secret bridging into a single `RUNE_DB_URL`).
- **provider-kubernetes**: `kubernetes.crossplane.io/v1alpha2` Object API for writing Secrets.

### Deployment Model

#### Development / Lab
- Crossplane optional; SQLite or in-cluster CNPG (via `rune-charts` subchart or BYO).
- On-prem path: `RuneDatabase` Claim with `provider: cnpg` provisions CNPG cluster and
  writes connection Secret.

#### Production Airgapped (Tier 1 — Recommended in Epic #252)
- **Crossplane only useful for partially-connected deployments** — cluster must have network
  access to cloud control plane (AWS/GCP/Azure APIs) OR run completely on-prem (CNPG).
- Fully disconnected (no cloud, no on-prem operator): Use manual Secret + CNPG on-prem or
  external managed database.
- Optional `--include-crossplane` in OCI bundle (Phase 2) for partially-connected airgap.

#### High-Availability PostgreSQL (Unchanged from ADR 0006)
- CNPG operator or equivalent is still the recommended HA path (not bundled by Crossplane).
- Crossplane via `provider-kubernetes` can manage CNPG Cluster CR declarations.

### Secret Lifecycle and Deletion Policy

When a `RuneDatabase` Claim is deleted, the managed Secret `rune-db-secret` is **cascade-deleted**
(via `deletionPolicy: Delete` on the `provider-kubernetes` Object). This couples the claim
lifecycle to the Secret lifecycle — operators must be aware that deleting a Claim disrupts
running RUNE instances.

Rationale: Tight coupling prevents "orphaned" credentials and makes lifecycle clear. Alternative
(Orphan) would preserve the Secret but violate the principle of least surprise — a deleted Claim
should not leave active infrastructure behind.

## Licensing and Supply-Chain Rationale

The provider choice is constrained by the same rules as ADR 0006:

| Option | Decision | Why |
|---|---|---|
| Crossplane core (`crossplane/crossplane`) | Approved | Apache-2.0, CNCF sandbox |
| `upbound/provider-aws` (Upbound-official) | Approved | Apache-2.0, supply chain maintained by Upbound |
| `upbound/provider-gcp` (Upbound-official) | Approved | Apache-2.0, Upbound-maintained |
| `upbound/provider-azure` (Upbound-official) | Approved | Apache-2.0, Upbound-maintained |
| `crossplane-contrib/provider-kubernetes` | Approved | Apache-2.0, community-maintained (stable) |
| `crossplane-contrib/function-patch-and-transform` | Approved | Apache-2.0, core transformation library |
| `crossplane-contrib/function-go-templating` | Approved | Apache-2.0, URL assembly and key mapping |
| Bitnami Crossplane Helm chart | Rejected | Broadcom/Tanzu supply-chain concerns (same as ADR 0006) |

### SLSA L3 and Observability Gap

Upbound provider images (e.g., `provider-aws`) do not yet carry **SLSA L3 provenance**
attestations. This is a documented exception (same pattern as the `INFRA_IMAGES` array in
`build-bundle.sh`). Document in the VEX register and update relevant configuration.

## Implementation Status

As of **2026-04-16**:

### Phases
- **Phase 0**: ADR 0007 + `crossplane/` skeleton in `rune-charts`, CI job
- **Phase 1a**: XRDs + CNPG/MinIO compositions (on-prem path)
- **Phase 1b**: AWS/GCP/Azure compositions (cloud path)
- **Phase 2**: `--include-crossplane` in OCI bundle
- **Phase 3** (deferred): `rune-operator` readiness gate for `RuneBenchmark`

### Blockers
- `rune#233` and `rune#234` — PostgreSQL adapter and `RUNE_DB_URL` config (must merge for
  end-to-end validation, but Crossplane infrastructure provisioning can proceed independently).

## Consequences

- **Cluster admins**: Gain declarative infrastructure-as-code provisioning as an option;
  Crossplane is opt-in, not required.
- **Developers**: Must document that `existingSecret` remains the stable interface.
- **On-prem deployments**: CNPG remains first-class option; Crossplane provides a unified
  declarative syntax for managing it.
- **Supply chain**: Added dependency on Upbound provider images (SLSA gap noted; accepted
  exception).
- **Airgapped**: Only partially-connected deployments benefit from Crossplane; fully offline
  environments should stick to manual/CNPG.
- **Documentation**: Must distinguish between development (SQLite default, optional Crossplane)
  and production (external Postgres, Crossplane optional for cloud, CNPG for on-prem).

## Related References

- ADR 0006: Storage abstraction and external PostgreSQL
- Epic #252: Production airgapped deployment model
- Epic #266: Crossplane infrastructure provisioning (child issues #267, #92–#94, #84, #107)
- Crossplane v2.2 documentation: https://docs.crossplane.io/latest/
- provider-kubernetes: `kubernetes.crossplane.io/v1alpha2`

