# Database Operations

## Status

**Current release status:** RUNE ships with **SQLite** as the supported runtime
store today.

External PostgreSQL support is an accepted direction and parts of the storage
refactor are already merged, but the Postgres adapter, runtime selection, Helm
subchart, and migration CLI are **not all released yet**. This page therefore
documents both:

- what is **supported now**
- what is the **planned operational model** once the remaining work lands

Track implementation status in
[ADR 0006](../architecture/adrs/0006-storage-abstraction-postgres.md).

## Decision Matrix

| Deployment shape | Recommended store | Status today | Why |
|---|---|---|---|
| Local development | SQLite | Supported | Lowest friction, no extra service |
| Single-pod Kubernetes | SQLite | Supported | Embedded persistence is sufficient |
| Simple airgapped install | SQLite | Supported | Fewer moving parts and smaller bundle |
| Multi-pod `rune-api` deployment | PostgreSQL | Planned | Shared network database for multiple replicas |
| Audit-heavy / compliance-focused production | PostgreSQL | Planned | Centralized persistence and cleaner separation from app pods |
| HA / multi-AZ / PITR requirements | PostgreSQL + CNPG | Planned | SQLite is not the right HA substrate |

## Current Supported Configuration

Today the supported persistence knob is:

- `RUNE_API_DB_PATH=.rune-api/jobs.db`

That points `rune-api` at the embedded SQLite file used by the current runtime.

Example:

```bash
export RUNE_API_DB_PATH=/var/lib/rune/jobs.db
python -m rune.api
```

## Planned URL-Based Storage Selection

The storage layer is moving toward URL-based backend selection behind the same
storage interface. The planned runtime variable is `RUNE_DB_URL`, but it is
**not yet the released public contract**.

### Planned SQLite URL forms

```text
sqlite:///:memory:
sqlite:///var/lib/rune/jobs.db
```

### Planned PostgreSQL URL forms

```text
postgresql://rune:secret@postgres.rune.svc.cluster.local:5432/rune
postgresql://rune:${DB_PASSWORD}@db.example.internal:5432/rune?sslmode=require
```

Use these as target formats for rollout planning only until `rune#234` lands.

## Migrations Framework

The hand-rolled migration framework is already part of the storage layer.

### How it works

- Ordered `.sql` files are applied in lexicographic order
- Applied versions are tracked in `schema_version`
- Migrations run inside explicit transactions
- Re-running pending migrations is designed to be idempotent
- Legacy SQLite databases without `schema_version` are bootstrapped by
  pre-seeding known migration versions

This keeps the persistence layer simple and auditable without pulling in
SQLAlchemy/Alembic.

## Backup and Restore

### SQLite

SQLite is the only store you should operate in production today.

Backup:

```bash
sqlite3 /var/lib/rune/jobs.db ".backup '/var/backups/rune/jobs-$(date +%F).db'"
```

Restore:

```bash
cp /var/backups/rune/jobs-2026-04-09.db /var/lib/rune/jobs.db
```

Operational notes:

- Stop `rune-api` or ensure the file is copied atomically during your backup
  procedure.
- Back up the persistent volume, not just the container filesystem.

### PostgreSQL (planned support)

Once the Postgres adapter is released, the normal backup primitives will be:

- logical backups with `pg_dump`
- replica/base backups with `pg_basebackup`
- operator-managed snapshots when using CloudNativePG

Those flows are intentionally not described as current RUNE runtime procedures
yet, because the runtime integration is still blocked on `rune#233` and
`rune#234`.

## Migration Path: Embedded SQLite to PostgreSQL

The planned graduation path is:

1. Run the SQLite-backed deployment until your scaling or compliance needs
   require a shared external store.
2. Provision PostgreSQL via the first-party `rune-charts` subchart or your own
   managed service.
3. Run the planned `rune db migrate-to-postgres` command.
4. Switch runtime configuration to the Postgres URL and restart `rune-api`.

The migration CLI itself is still open as `rune#235`.

## Licensing and Supply-Chain Rationale

| Option | Decision | Rationale |
|---|---|---|
| PostgreSQL upstream | Approved | PostgreSQL License |
| `docker.io/library/postgres:17-alpine` | Approved | Official image, minimal and well-understood supply chain |
| `psycopg[binary]` / `psycopg[pure]` | Approved | Apache 2.0 wrapper around `libpq` |
| First-party `rune-charts/charts/postgres` | Approved | Avoids third-party chart dependency |
| CloudNativePG | Approved as BYO | Apache 2.0 HA path; not bundled |
| Bitnami PostgreSQL chart | Rejected | Supply-chain and maintenance concerns after the Broadcom/Tanzu shift |
| StackGres | Rejected | AGPLv3 |
| Bundled MariaDB / MySQL server | Rejected | GPL server bundling concerns |
| CockroachDB | Rejected | BUSL on current releases |

If any exception is ever required, document it in the
[VEX Register](../delivery/VEX.md) and in the relevant ADR or issue before
changing the dependency set.

## High Availability

For the planned HA path, see [DATABASE_HA.md](DATABASE_HA.md).

## Related References

- [Configuration](../usage/CONFIGURATION.md)
- [Developer Guide](../usage/DEVELOPER_GUIDE.md)
- [Deployment](DEPLOYMENT.md)
- [ADR 0006](../architecture/adrs/0006-storage-abstraction-postgres.md)
