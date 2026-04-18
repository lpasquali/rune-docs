# Install — On-prem Kubernetes

For deployments on a Kubernetes cluster you run yourself: **Talos**, **Rancher RKE2**, **OpenShift**, or **bare-metal** (kubeadm, k3s at scale). This is the path most regulated-industry RUNE deployments take — full control over the hardware, network, and storage.

Pair this page with the [Air-gapped scenario](https://github.com/lpasquali/rune-docs/issues/278) when your cluster has no outbound internet access.

## Prerequisites

- A Kubernetes cluster ≥ 1.27 with:
  - **Storage class** (local-path for small deployments; **Longhorn** or **Ceph RBD** for HA).
  - **Ingress controller** (ingress-nginx is the reference; Traefik and HAProxy work with adjusted annotations).
  - **Cert-manager** if you want automated TLS; otherwise bring your own certs.
- `kubectl` configured to the cluster with cluster-admin for the install; runtime RBAC is narrower.
- `helm` ≥ 3.17 on your workstation.

## Step 1 — Storage class

RUNE persists:

- **PostgreSQL** data (if you use the planned PostgreSQL adapter). `RUNE_DB_URL` points at it.
- **Blob results** in an S3-compatible store (SeaweedFS is the in-chart default for on-prem; swap for MinIO or Ceph RGW for production).

```bash
# Quick smoke path: local-path provisioner
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.26/deploy/local-path-storage.yaml
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

For production, install Longhorn or Rook-Ceph. Their chart-install commands are out of scope here; follow each project's docs.

## Step 2 — PostgreSQL (optional but recommended for multi-pod)

SQLite is the **shipped default** today. For single-pod installs it works fine. For **multi-pod** or **HA** installs you want PostgreSQL via CNPG ([DATABASE_HA](DATABASE_HA.md)).

Install CNPG:

```bash
kubectl apply --server-side -f \
  https://github.com/cloudnative-pg/cloudnative-pg/releases/download/v1.24.0/cnpg-1.24.0.yaml
```

Create a RUNE-dedicated cluster:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: rune-pg
  namespace: rune
spec:
  instances: 3
  storage:
    size: 20Gi
    storageClass: longhorn
  bootstrap:
    initdb:
      database: rune
      owner: rune
      secret:
        name: rune-pg-credentials
```

```bash
kubectl apply -f rune-pg.yaml
# CNPG creates:
#   Secret: rune-pg-app (contains JDBC-style URL + raw creds)
#   Service: rune-pg-rw, rune-pg-ro
```

## Step 3 — S3-compatible object storage

For on-prem, the options are: **SeaweedFS** (embedded in rune-charts), **MinIO** (external), or **Ceph RGW** (if you already have Ceph).

SeaweedFS is the simplest — it ships as part of the `rune` chart and needs no external config. For MinIO or Ceph, configure `rune.storage.s3.endpoint` / `accessKey` / `secretKey` in values.

## Step 4 — Ingress + TLS

```yaml
# values.yaml snippet
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: rune.internal.example
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: rune-tls
      hosts:
        - rune.internal.example
```

For air-gapped or no-DNS-CA environments, use `--set tls.selfSigned=true` — the chart generates a self-signed cert; distribute the CA to clients separately.

## Step 5 — Install the chart

```bash
git clone https://github.com/lpasquali/rune-charts.git
cd rune-charts

cat > rune-values.yaml <<'EOF'
rune:
  api:
    authDisabled: false
    tokens: "platform:$(openssl rand -hex 24)"
  storage:
    postgresql:
      enabled: true
      url: "postgres://rune:$PG_PASSWORD@rune-pg-rw.rune.svc:5432/rune"
    s3:
      enabled: true
      # Leave endpoint empty to use in-chart SeaweedFS
ingress:
  enabled: true
  hosts:
    - host: rune.internal.example
EOF

kubectl create namespace rune
helm install rune ./charts/rune -n rune -f rune-values.yaml --wait --timeout=5m
helm install rune-operator ./charts/rune-operator -n rune --wait --timeout=5m
```

## Step 6 — Validate

```bash
kubectl -n rune get pods
# Expected: rune-api, rune-ui, rune-docs, ollama (or backend), seaweedfs
# All should be Ready.

TOKEN=$(kubectl -n rune get secret rune-api-tokens -o jsonpath='{.data.platform}' | base64 -d)
curl -sfH "Authorization: Bearer $TOKEN" https://rune.internal.example/healthz
```

## Variant notes

### Talos

No special steps; Talos is just Kubernetes with restricted host access. Use the standard install path above. PSA `restricted` is on by default — all RUNE charts already pass.

### Rancher RKE2

Default ingress is nginx; storage is local-path by default. Identical to the reference install. Use Rancher's UI to install CNPG if you prefer.

### OpenShift

- Use `oc` instead of `kubectl`.
- SCC: the RUNE charts run as non-root UID 10001; `restricted-v2` SCC should accept them without custom SCC. If not, grant `nonroot-v2`.
- Routes instead of Ingress: set `openshift.routes.enabled=true` in values (chart supports both; one wins based on flag).

### Bare-metal (kubeadm)

- No cloud-provider integration → no LoadBalancer. Use ingress-nginx in DaemonSet mode with `hostNetwork: true`, or MetalLB.
- Storage: Longhorn is the easiest path; NFS provisioner works for low-scale.

## Troubleshooting

See [TROUBLESHOOTING](https://github.com/lpasquali/rune-docs/issues/283) for the symptom-first index. On-prem-specific gotchas:

- **PostgreSQL not reachable from rune-api**: check NetworkPolicies (CNPG creates restrictive policies by default; the `rune` chart may need explicit egress to the `rune-pg-rw` service).
- **Longhorn volume stuck pending**: Longhorn's CSI driver needs the Kubernetes node's `iscsi_tcp` kernel module. `modprobe iscsi_tcp` or persist via `/etc/modules-load.d/`.
- **ingress-nginx 502 Bad Gateway**: the API pod's health probes haven't succeeded yet. `kubectl -n rune logs deploy/rune-api` — look for the DB connectivity line.

## Further

- [DATABASE_HA](DATABASE_HA.md) — CNPG HA topology.
- [SCENARIOS §Regulated on-prem](https://github.com/lpasquali/rune-docs/issues/278) — compliance layer.
- [Vault](VAULT.md) — secret injection instead of Kubernetes Secrets.
