# Database HA (CloudNativePG BYO)

## Status

This page describes the **planned high-availability PostgreSQL path** for
RUNE. It is intentionally forward-looking:

- CloudNativePG is the recommended operator for HA Postgres
- RUNE's runtime integration with external PostgreSQL is **not fully released
  yet**
- Use this page for architecture and rollout planning, not as proof that HA DB
  support is already generally available

Track the remaining implementation work in:

- `rune#233` — Postgres adapter
- `rune#234` — `RUNE_DB_URL`
- `rune-charts#71` — first-party Postgres subchart
- `rune-docs#196` — final database ops guides

## When You Need HA

SQLite is enough when you have:

- one `rune-api` replica
- local development
- a small single-node or single-pod deployment
- no PITR or multi-AZ database requirement

You should plan for HA PostgreSQL when you need:

- multiple `rune-api` replicas sharing one store
- higher write concurrency than an embedded SQLite file is comfortable with
- defined RPO/RTO targets
- managed backups and point-in-time recovery
- stronger separation between application pods and persistence

## Recommended HA Path

RUNE's recommended HA database operator is **CloudNativePG (CNPG)**.

Why CNPG:

- Apache 2.0 license
- CNCF ecosystem fit
- PostgreSQL-native design
- built-in backup and recovery workflows
- avoids bundling a heavy HA operator into the default simple-install path

## Why CNPG Is Not Bundled

RUNE does **not** plan to bundle CNPG into the default deployment footprint
because:

- the simple case is still SQLite or a small Postgres install
- bundling CNPG would significantly expand the default and airgapped footprint
- many operators already have an approved HA Postgres platform

The design is therefore:

- bundle the lightweight first-party Postgres chart for simple external DB use
- document CNPG as the bring-your-own HA path

## CNPG Installation

Example installation:

```bash
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo update
helm install cnpg cloudnative-pg/cloudnative-pg \
  --namespace cnpg-system \
  --create-namespace
```

You would then create a CNPG-managed PostgreSQL cluster and expose the service
name you want RUNE to use.

## Planned RUNE Integration

Once `RUNE_DB_URL` is released, the expected integration model will be a
standard PostgreSQL connection string pointed at the CNPG primary service:

```text
postgresql://rune:${DB_PASSWORD}@rune-db-rw.rune.svc.cluster.local:5432/rune?sslmode=require
```

At the moment, this is a **target contract**, not a released runtime example.

## Backups

For HA PostgreSQL, prefer the operator-native backup path over hand-managed
container scripts.

With CNPG that generally means:

- object-store-backed base backups
- scheduled backups managed by the operator
- retention policies defined at the cluster level

## Point-In-Time Recovery

CNPG supports PITR by restoring a cluster from base backup plus WAL archives.
That is the recommended HA recovery story for RUNE once Postgres runtime support
is fully released.

Use PITR when you need:

- recovery to a known timestamp before operator error
- rollback after destructive data changes
- stronger recovery objectives than file-level SQLite restore can provide

## Practical Guidance For Today

If you need RUNE **right now** and cannot wait for the remaining Postgres work:

- run the current SQLite-backed deployment for single-pod installs
- keep backups of the SQLite volume
- do not deploy multiple `rune-api` replicas expecting shared persistence yet

If you are designing a future production rollout:

- standardize on PostgreSQL
- prefer CloudNativePG for HA in Kubernetes
- track `rune#233`, `rune#234`, and `rune-charts#71` before cutting over

## Related References

- [DATABASE.md](DATABASE.md)
- [Deployment](DEPLOYMENT.md)
- [Infrastructure](../architecture/INFRASTRUCTURE.md)
- [ADR 0006](../architecture/adrs/0006-storage-abstraction-postgres.md)
