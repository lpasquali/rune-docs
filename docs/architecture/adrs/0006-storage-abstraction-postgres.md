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

- The simple packaged Postgres path is a **first-party Helm subchart** in
  `rune-charts`, wrapping the official `docker.io/library/postgres:17-alpine`
  image.
- High-availability PostgreSQL is documented as **BYO CloudNativePG**, not a
  bundled dependency.
- The airgapped bundle will include the approved Postgres image once the chart
  and runtime support are ready.

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

As of **2026-04-09**:

- Done:
  - `rune#231` — `StoragePort` extraction and `SQLiteStorageAdapter`
  - `rune#232` — hand-rolled migrations framework
- In progress / still open:
  - `rune#233` — `PostgresStorageAdapter`
  - `rune#234` — `RUNE_DB_URL` config and backend selection
  - `rune#235` — `rune db migrate-to-postgres`
  - `rune#236` — Postgres integration test matrix
  - `rune-charts#71` — first-party Postgres subchart
  - `rune-airgapped#63` — bundle Postgres image
  - `rune-docs#196` — end-user database operations guides

This ADR intentionally lands before the final operations guides. The operator
runbooks, connection-string reference, and HA procedures should only be written
once the runtime config and Helm story exist in released code.

## Consequences

- Existing SQLite users keep a stable default path and do not need to migrate
  immediately.
- The storage interface becomes the boundary for future persistence changes.
- The eventual Postgres rollout can be documented and tested without rewriting
  application code again.
- Until `rune#234` lands, public docs must clearly state that external Postgres
  support is a planned capability rather than a released one.
