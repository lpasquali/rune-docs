# Install — GCP (GKE)

!!! info "Content complete — validation transcript pending"
    Content drafted from GCP / Crossplane / ESO / Cloud SQL Auth Proxy official docs (2026-04). End-to-end transcript from a real GKE cluster still needed — tracked in the [Validation transcript](#validation-transcript) section at the bottom.

## Prerequisites

- GKE cluster ≥ 1.27 (Standard or Autopilot). Kubeconfig via `gcloud container clusters get-credentials $CLUSTER --region $REGION`.
- [`helm`](https://helm.sh/docs/) ≥ 3.17.
- GCP project with APIs enabled:

  ```bash
  gcloud services enable \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    iam.googleapis.com \
    container.googleapis.com \
    iamcredentials.googleapis.com
  ```

- [**Workload Identity**](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity) enabled on the cluster (the GKE equivalent of IRSA). For Autopilot this is on by default; for Standard, enable it with `--workload-pool=$PROJECT_ID.svc.id.goog`.
- [**External Secrets Operator**](https://external-secrets.io/latest/provider/google-secrets-manager/) installed (for Secret Manager sync).
- [**Crossplane**](https://docs.crossplane.io/latest/) installed with the GCP provider family — see [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md).

Set env vars:

```bash
export PROJECT_ID=my-rune-project
export REGION=us-central1
export CLUSTER=rune-prod
```

## Step 1 — Provisioning via Crossplane

### 1a. Install the GCP provider family

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-family-gcp
spec:
  package: xpkg.upbound.io/upbound/provider-family-gcp:v1.12.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp-sql
spec:
  package: xpkg.upbound.io/upbound/provider-gcp-sql:v1.12.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp-storage
spec:
  package: xpkg.upbound.io/upbound/provider-gcp-storage:v1.12.0
EOF
kubectl get providers -w
```

### 1b. ProviderConfig with Workload Identity

Create a Google service account with necessary permissions (`roles/cloudsql.admin`, `roles/storage.admin`, `roles/iam.serviceAccountAdmin`), then bind the Crossplane controller SA to it:

```bash
gcloud iam service-accounts create crossplane-gcp --project=$PROJECT_ID

# Grant roles
for role in roles/cloudsql.admin roles/storage.admin roles/iam.serviceAccountAdmin; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:crossplane-gcp@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "$role"
done

# Bind the K8s SA to the GSA
gcloud iam service-accounts add-iam-policy-binding \
  crossplane-gcp@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[crossplane-system/crossplane]"

# Annotate the controller SA
kubectl annotate serviceaccount -n crossplane-system crossplane \
  iam.gke.io/gcp-service-account=crossplane-gcp@$PROJECT_ID.iam.gserviceaccount.com
```

```yaml
kind: ProviderConfig
apiVersion: gcp.upbound.io/v1beta1
metadata:
  name: default
spec:
  projectID: $PROJECT_ID
  credentials:
    source: InjectedIdentity
```

### 1c. Cloud SQL for PostgreSQL instance

```yaml
# crossplane/rune-sql.yaml
apiVersion: sql.gcp.upbound.io/v1beta2
kind: DatabaseInstance
metadata:
  name: rune-db
spec:
  forProvider:
    region: us-central1
    databaseVersion: POSTGRES_16
    rootPasswordSecretRef:
      namespace: rune
      name: rune-db-master
      key: password
    settings:
      - tier: db-g1-small
        availabilityType: ZONAL
        diskSize: 20
        diskType: PD_SSD
        backupConfiguration:
          - enabled: true
            pointInTimeRecoveryEnabled: true
        ipConfiguration:
          - ipv4Enabled: false
            privateNetwork: projects/$PROJECT_ID/global/networks/default
        databaseFlags:
          - name: max_connections
            value: "200"
    deletionProtection: true
---
apiVersion: sql.gcp.upbound.io/v1beta1
kind: Database
metadata:
  name: rune
spec:
  forProvider:
    instance: rune-db
    project: $PROJECT_ID
---
apiVersion: sql.gcp.upbound.io/v1beta1
kind: User
metadata:
  name: rune
spec:
  forProvider:
    instance: rune-db
    passwordSecretRef:
      namespace: rune
      name: rune-db-app
      key: password
    project: $PROJECT_ID
```

### 1d. GCS bucket + HMAC keys

```yaml
# crossplane/rune-gcs.yaml
apiVersion: storage.gcp.upbound.io/v1beta1
kind: Bucket
metadata:
  name: rune-results-PROJECT_ID
spec:
  forProvider:
    location: US
    storageClass: STANDARD
    uniformBucketLevelAccess: true
    versioning:
      - enabled: true
```

Create an HMAC key for S3-compat access:

```bash
gcloud iam service-accounts create rune-gcs \
  --display-name="RUNE GCS S3-compat access"

gcloud storage buckets add-iam-policy-binding gs://rune-results-$PROJECT_ID \
  --member="serviceAccount:rune-gcs@$PROJECT_ID.iam.gserviceaccount.com" \
  --role=roles/storage.objectAdmin

gcloud storage hmac create \
  rune-gcs@$PROJECT_ID.iam.gserviceaccount.com \
  --project $PROJECT_ID \
  --format=json > hmac.json

# Store in Secret Manager:
ACCESS_ID=$(jq -r '.metadata.accessId' hmac.json)
SECRET=$(jq -r '.secret' hmac.json)
gcloud secrets create rune-gcs-hmac-access \
  --data-file=<(echo -n "$ACCESS_ID") --project $PROJECT_ID
gcloud secrets create rune-gcs-hmac-secret \
  --data-file=<(echo -n "$SECRET") --project $PROJECT_ID
```

## Step 2 — Workload Identity for `rune-api`

```bash
gcloud iam service-accounts create rune-api --project=$PROJECT_ID

gcloud storage buckets add-iam-policy-binding gs://rune-results-$PROJECT_ID \
  --member="serviceAccount:rune-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role=roles/storage.objectAdmin

# Bind K8s SA → GSA
gcloud iam service-accounts add-iam-policy-binding \
  rune-api@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[rune/rune-api]"
```

```yaml
# values-gcp.yaml (snippet)
serviceAccount:
  create: true
  name: rune-api
  annotations:
    iam.gke.io/gcp-service-account: rune-api@$PROJECT_ID.iam.gserviceaccount.com
```

## Step 3 — Cloud SQL Auth Proxy sidecar

The recommended pattern on GKE. Chart support lands in `rune-charts` via `values.sidecars.cloudSqlProxy`:

```yaml
# values-gcp.yaml (continued)
rune:
  storage:
    postgresql:
      enabled: true
      # app connects to the sidecar on localhost
      hostSecretRef: ""
      host: "127.0.0.1"
      port: 5432
      username: rune
      passwordSecretRef: rune-db-app
      passwordKey: password
      database: rune
      sslmode: disable   # proxy handles TLS to Cloud SQL

sidecars:
  cloudSqlProxy:
    enabled: true
    image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.14.0
    instance: "$PROJECT_ID:$REGION:rune-db"
    port: 5432
    extraArgs:
      - "--private-ip"
      - "--structured-logs"
```

!!! note "Follow-up"
    If the chart doesn't yet expose `sidecars.cloudSqlProxy`, file a chart PR against `rune-charts` — it's a pod-spec addition under the `rune-api` deployment. Until then, use a Helm post-renderer or edit the rendered manifest.

## Step 4 — External Secrets Operator → Secret Manager

```yaml
# eso/clustersecretstore.yaml
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: gcp-secret-manager
spec:
  provider:
    gcpsm:
      projectID: $PROJECT_ID
      auth:
        workloadIdentity:
          clusterLocation: $REGION
          clusterName: $CLUSTER
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

```yaml
# eso/rune-secrets.yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: rune-db-app
  namespace: rune
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: gcp-secret-manager
  target:
    name: rune-db-app
  data:
    - secretKey: password
      remoteRef:
        key: rune-db-app-password
---
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: rune-s3
  namespace: rune
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: gcp-secret-manager
  target:
    name: rune-s3
  data:
    - secretKey: accessKey
      remoteRef: {key: rune-gcs-hmac-access}
    - secretKey: secretKey
      remoteRef: {key: rune-gcs-hmac-secret}
```

## Step 5 — GCS as S3 (HMAC keys)

GCS speaks S3 via the [interoperability API](https://cloud.google.com/storage/docs/interoperability):

```yaml
# values-gcp.yaml (continued)
rune:
  storage:
    s3:
      enabled: true
      endpoint: https://storage.googleapis.com
      accessKeySecretRef: rune-s3
      accessKeyKey: accessKey
      secretKeySecretRef: rune-s3
      secretKeyKey: secretKey
      bucket: rune-results-$PROJECT_ID
      pathStyle: true   # GCS doesn't support virtual-hosted
```

## Step 6 — Managed-cert + `gce` ingress

Reserve a global static IP:

```bash
gcloud compute addresses create rune-ip --global
gcloud compute addresses describe rune-ip --global --format='value(address)'
```

Create an A record in your DNS provider pointing `rune.example.com` at that IP.

```yaml
# values-gcp.yaml (continued)
ingress:
  enabled: true
  className: gce
  annotations:
    kubernetes.io/ingress.global-static-ip-name: "rune-ip"
    networking.gke.io/managed-certificates: "rune-cert"
    kubernetes.io/ingress.class: "gce"
  hosts:
    - host: rune.example.com
      paths:
        - path: /
          pathType: Prefix

# Separate ManagedCertificate CR
extraObjects:
  - apiVersion: networking.gke.io/v1
    kind: ManagedCertificate
    metadata:
      name: rune-cert
    spec:
      domains:
        - rune.example.com
```

## Step 7 — Chart install

```bash
helm install rune ./charts/rune \
  --namespace rune --create-namespace \
  --values values-gcp.yaml \
  --wait --timeout=10m
```

Wait for the ingress IP to provision (can take 5-15 min for ManagedCertificate):

```bash
kubectl -n rune get ingress rune -w
kubectl get managedcertificate rune-cert -n rune -w  # wait for Active
```

## Step 8 — Validate

```bash
TOKEN=$(kubectl -n rune get secret rune-api-token -o jsonpath='{.data.token}' | base64 -d)

curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/healthz
# Expected: {"status":"ok","version":"0.0.0aN"}

curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/v1/llm/models | jq
```

## Cost estimation integration

`CostEstimation.gcp` supports GCP-specific cost projections. See [ADR 0002](../architecture/adrs/0002-cost-estimation.md).

## Teardown

```bash
helm uninstall rune -n rune
kubectl delete -f crossplane/rune-sql.yaml -f crossplane/rune-gcs.yaml
# Cloud SQL deletion-protected; disable first:
#   kubectl patch databaseinstance rune-db --type=merge \
#     -p '{"spec":{"forProvider":{"settings":[{"deletionProtection":false}]}}}'
gcloud compute addresses delete rune-ip --global --quiet
```

## Validation transcript

!!! warning "Pending real-cluster validation"
    Populate after running this walkthrough on a real GKE cluster. Tracked in [#303](https://github.com/lpasquali/rune-docs/issues/303).

```
TODO: Paste validated transcript here.
```

## References

- [GKE Workload Identity](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity)
- [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy)
- [GCS interoperability (S3-compat)](https://cloud.google.com/storage/docs/interoperability)
- [Google-managed SSL certs on GKE](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs)
- [External Secrets Operator — Google Secret Manager](https://external-secrets.io/latest/provider/google-secrets-manager/)
- [Crossplane GCP provider](https://marketplace.upbound.io/providers/upbound/provider-family-gcp)
- [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md)
- [External Links Catalog](../reference/EXTERNAL_LINKS.md)
