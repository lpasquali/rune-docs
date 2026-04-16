# ADR 0006: Storage Abstraction and External PostgreSQL

## Status

Accepted (implementation in progress)

## Context

RUNE's job persistence is currently backed by embedded SQLite. That is still the
right default for local development, single-pod Kubernetes deployments, and
simple airgapped installations, but it creates structural limits:

1. A single SQLite file is not the right coordination point for multiple
   `rune-api` replicas behind one Service.
2. Compliance-heavy deployments want audit evidence and run state in a managed
   database, not an embedded file inside the application pod.
3. New storage-backed features such as chain state and audit artifacts should
   inherit a backend-neutral storage contract instead of deepening the
   SQLite-only assumption.

The implementation has already started. `rune` now exposes a `StoragePort`
protocol, a `SQLiteStorageAdapter`, and a hand-rolled SQL migration framework.
What is not finished yet is the Postgres adapter, runtime config selection, and
the deployment story around it.

## Decision

RUNE will support two storage backends behind the same storage interface:

1. **SQLite remains the default** for low-complexity installs.
2. **PostgreSQL becomes the supported external database** for multi-pod,
   production, and audit-heavy deployments.

### Runtime shape

- The storage layer is selected by URL, not by branching application logic.
- The current shipped URL support is `sqlite://...`.
- `RUNE_DB_URL` is the planned runtime selector for both SQLite and Postgres
  once the config work is complete.
- Application code continues to depend on the storage interface, not on
  backend-specific SQL.

### Migrations

- RUNE uses a hand-rolled migration loader with a `schema_version` table.
- Migration files live as ordered `.sql` files and are applied in lexicographic
  order inside explicit transactions.
- Re-applying migrations is designed to be idempotent.

### Deployment

#### Development / Local Deployments
- SQLite remains the default; no database provisioning needed.
- In-cluster Postgres (via optional `rune-charts/postgres` subchart) is
  available for development and lab environments that need a managed database.
- The subchart wraps the official `docker.io/library/postgres:17-alpine` image.

#### Production Airgapped Deployments (Tier 1 — Recommended)
- **PostgreSQL is a customer-managed prerequisite**, not bundled.
- Customers provision PostgreSQL externally: CloudNativePG operator, AWS RDS,
  Cloud SQL, or other managed services.
- RUNE configures the database via `RUNE_DB_URL` Secret.
- The OCI bundle ships RUNE suite images only; no embedded Postgres image.
- This model aligns with production airgapped practices: all external services
  (database, storage, inference) are customer-operated prerequisites.

#### High-Availability PostgreSQL
- **HA PostgreSQL is documented as BYO CloudNativePG** or equivalent operator,
  not a bundled dependency.
- CNPG (CloudNativePG) is the recommended Kubernetes-native option for HA.
- Managed services (AWS RDS Multi-AZ, Cloud SQL HA) are production-ready
  alternatives when available in the deployment environment.

## Licensing and Supply-Chain Constraints

The database choice is constrained by licensing and by the project-wide
no-proprietary / no-fragile-supply-chain rules.

| Option | Decision | Why |
|---|---|---|
| PostgreSQL upstream + `postgres:17-alpine` | Approved | PostgreSQL License plus Docker Official Image maintenance |
| First-party `rune-charts/charts/postgres` subchart | Approved | No third-party chart dependency; minimal supply chain |
| CloudNativePG | Approved as BYO | Apache 2.0, CNCF path for HA, not bundled |
| `psycopg[binary]` / `psycopg[pure]` | Approved | Apache 2.0 wrapper around `libpq` |
| Bitnami PostgreSQL chart | Rejected | Legacy Broadcom/Tanzu transition and supply-chain concerns |
| StackGres | Rejected | AGPLv3 |
| Bundled MariaDB / MySQL server | Rejected | GPL server bundling risk for shipped images |
| CockroachDB | Rejected | BUSL on current releases |

## Implementation Status

As of **2026-04-16**:

- Done:
  - `rune#231` — `StoragePort` extraction and `SQLiteStorageAdapter`
  - `rune#232` — hand-rolled migrations framework
- In progress / still open:
  - `rune#233` — `PostgresStorageAdapter`
  - `rune#234` — `RUNE_DB_URL` config and backend selection
  - `rune#235` — `rune db migrate-to-postgres`
  - `rune#236` — Postgres integration test matrix
  - `rune-charts#71` — first-party Postgres subchart
  - `rune-charts#82` — Helm airgapped production values (external services)
  - `rune-airgapped#72` — make Postgres opt-in in OCI bundle
  - `rune-airgapped#73` — prerequisites matrix (external DB, S3, inference)
  - `rune-docs#196` — end-user database operations guides
  - `rune-docs#253` — align DATABASE*.md with production airgap model (THIS ADR)

### Airgapped Deployment Model (Epic #252)

The production airgapped deployment model treats PostgreSQL, S3, and inference
backends as **customer-managed prerequisites** (not bundled). This is reflected in:

- `rune-airgapped#72`: OCI bundle ships RUNE-suite-only; `--include-postgres` is
  opt-in for dev/lab.
- `rune-airgapped#73`: Prerequisites matrix documents external DB, S3, inference
  setup examples.
- `rune-charts#82`: Production Helm values reference external services via Secrets.
- This ADR section **Deployment**: Clarifies production airgap uses external Postgres.
- `rune-docs#196`: Database operations guides to document production path.

## Consequences

- **SQLite users**: Remain on stable default path; no forced migration.
- **Development users**: Optional in-cluster Postgres via Helm subchart.
- **Production airgapped users**: PostgreSQL is a customer-managed prerequisite,
  provisioned out-of-band. The OCI bundle ships RUNE-suite-only; all external
  services (database, S3, inference) are customer-operated.
- **Storage interface**: Becomes the boundary for future persistence changes.
- **HA users**: CNPG operator or equivalent is the recommended Kubernetes-native
  path for high-availability PostgreSQL.
- **Documentation**: Must clearly distinguish between development (SQLite default,
  optional in-cluster Postgres) and production (external Postgres, prerequisite).
- **Airgapped deployments**: The bundle never bundles data-plane services;
  external services are required prerequisites documented in deployment guides.
