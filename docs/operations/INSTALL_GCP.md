# Install — GCP (GKE)

!!! note "Scaffold"
    Structure complete; cloud-specific detail needs hands-on validation.
    Follow-up: [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277).

## Prerequisites

- GKE cluster ≥ 1.27 (Standard or Autopilot). Kubeconfig via `gcloud container clusters get-credentials`.
- `helm` ≥ 3.17.
- GCP project with APIs enabled: `sqladmin.googleapis.com`, `storage.googleapis.com`, `iam.googleapis.com`.
- **Workload Identity** enabled on the cluster (the GKE equivalent of IRSA).

## Step 1 — Provisioning via Crossplane

`TODO: provider-family-gcp + Cloud SQL + GCS CRs. See follow-up.`

## Step 2 — Workload Identity for rune-api

Bind the `rune/rune-api` Kubernetes service account to a Google service account with `storage.objectAdmin` on the results bucket only.

```bash
gcloud iam service-accounts add-iam-policy-binding \
  rune-api@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[rune/rune-api]"
```

```yaml
# values.yaml snippet
serviceAccount:
  annotations:
    iam.gke.io/gcp-service-account: rune-api@PROJECT_ID.iam.gserviceaccount.com
```

`TODO: full IAM binding walkthrough.`

## Step 3 — Cloud SQL for Postgres

Use the **Cloud SQL Auth Proxy** sidecar pattern or the **Cloud SQL Connectors** (direct driver integration). Sidecar is simpler.

```yaml
# values.yaml snippet
rune:
  storage:
    postgresql:
      enabled: true
      url: "postgres://rune:$PG_PASSWORD@127.0.0.1:5432/rune"
  cloudSqlProxy:
    enabled: true
    instance: "PROJECT_ID:REGION:INSTANCE_ID"
```

`TODO: chart support for cloudSqlProxy sidecar — may need chart PR in rune-charts if not present.`

## Step 4 — GCS as S3 (HMAC keys)

GCS speaks S3 through the interoperability API; generate HMAC keys for service account auth.

```yaml
rune:
  storage:
    s3:
      enabled: true
      endpoint: https://storage.googleapis.com
      accessKey: <GCS HMAC access key>
      secretKey: <GCS HMAC secret>
      bucket: rune-results-$PROJECT_ID
```

## Step 5 — GKE ingress

Use GKE-managed certs + HTTPS load balancer via `gce` ingress class.

`TODO: managed cert + LB annotations.`

## Step 6 — Chart install + validate

Same as the [shared baseline](INSTALL.md#3-chart-install). Validate via port-forward or LB.

## Cost estimation integration

`CostEstimation.gcp` supports GCP-specific cost projections. See [ADR 0002](../architecture/adrs/0002-cost-estimation.md).

## Follow-ups tracked

- Cloud SQL Auth Proxy sidecar in rune-charts (may require chart change).
- HMAC key provisioning via External Secrets Operator.
- Managed certs + ingress-gce walkthrough.
- Validation transcript from a real GKE deployment.
