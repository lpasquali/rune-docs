# Rollback Procedures

IEC 62443-4-1 SUM-4 requires documented rollback procedures for all deployment artifacts.

## Kubernetes Deployments (Helm)

### Chart Rollback

```bash
# List release history
helm history rune -n rune

# Rollback to previous revision
helm rollback rune <revision> -n rune

# Verify rollback
kubectl get pods -n rune -w
helm status rune -n rune
```

### Operator Rollback

```bash
helm rollback rune-operator <revision> -n rune-system
kubectl get pods -n rune-system -w
```

### UI Rollback

```bash
helm rollback rune-ui <revision> -n rune
```

## Container Image Rollback

If a new image introduces a regression:

```bash
# Pin to previous known-good tag
helm upgrade rune rune/rune \
  --set image.tag=v0.0.0a4 \
  -n rune

# Verify pods are running the correct image
kubectl get pods -n rune -o jsonpath='{.items[*].spec.containers[*].image}'
```

## Database Schema Rollback

RUNE uses SQLite for job persistence. The database file is stored in a persistent volume.

### Pre-upgrade Backup

Before any upgrade that modifies the SQLite schema:

```bash
# Backup the database
kubectl exec -n rune deploy/rune-api -- cp /data/jobs.db /data/jobs.db.bak

# Verify backup
kubectl exec -n rune deploy/rune-api -- ls -la /data/jobs.db.bak
```

### Restore from Backup

```bash
kubectl exec -n rune deploy/rune-api -- cp /data/jobs.db.bak /data/jobs.db
kubectl rollout restart deploy/rune-api -n rune
```

## Release Rollback (PyPI)

PyPI does not support true rollback — only yanking. If a bad release is published:

1. Yank the bad version: `twine yank rune-bench==<bad-version>`
2. Users can pin to the previous version: `pip install rune-bench==<good-version>`

## Air-Gapped Environment Rollback

See [rune-airgapped upgrade/rollback scripts](https://github.com/lpasquali/rune-airgapped) (Issue #13).

For air-gapped clusters:

1. Keep the previous OCI bundle tarball on the bootstrap node.
2. Re-run `bootstrap.sh` with the previous bundle.
3. Helm releases are rolled back automatically when the previous chart versions are applied.

## Emergency Shutdown

If a rollback is insufficient and the system must be stopped immediately:

```bash
# Suspend all scheduled benchmarks
kubectl patch runebenchmark --all -n rune --type merge -p '{"spec":{"suspend":true}}'

# Scale down all RUNE workloads
kubectl scale deploy --all -n rune --replicas=0
kubectl scale deploy --all -n rune-system --replicas=0
```

## Verification After Rollback

After any rollback, run the health check script:

```bash
./scripts/health-check.sh --namespace rune
```

Confirm:
- All pods are Running with zero recent restarts
- `/healthz` endpoints return `200 OK`
- Job history is intact (no data loss)
- Scheduled benchmarks resume correctly (if unsuspended)
