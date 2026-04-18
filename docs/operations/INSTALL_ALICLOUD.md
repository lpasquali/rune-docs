# Install — Alibaba Cloud (ACK)

!!! note "Scaffold"
    Structure complete; cloud-specific detail needs hands-on validation.
    Follow-up: [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277).

## Prerequisites

- ACK cluster ≥ 1.27. Kubeconfig via `aliyun cs GET /k8s/$CLUSTER_ID/user_config`.
- `helm` ≥ 3.17.
- Alibaba Cloud account with RAM authority for ApsaraDB for PostgreSQL + OSS.
- **RAM Roles for Service Accounts (RRSA)** enabled on the cluster — the Alibaba equivalent of IRSA.

## Step 1 — Provisioning via Crossplane

`TODO: provider-jet-alibabacloud (community) + ApsaraDB RDS + OSS CRs. Crossplane AliCloud provider is less mature than AWS/GCP/Azure — validate before committing.`

## Step 2 — RRSA for rune-api

```bash
# Create RAM role trusted by the cluster's OIDC provider
aliyun ram CreateRole --RoleName rune-api-role --AssumeRolePolicyDocument '...'
aliyun ram AttachPolicyToRole --RoleName rune-api-role --PolicyType Custom --PolicyName rune-api-oss
```

```yaml
serviceAccount:
  annotations:
    pod.beta1.alibabacloud.com/ram-role-name: rune-api-role
```

`TODO: full RRSA walkthrough + OIDC provider setup on the ACK cluster.`

## Step 3 — ApsaraDB for PostgreSQL

```yaml
rune:
  storage:
    postgresql:
      enabled: true
      url: "postgres://rune:$PG_PASSWORD@rm-xxx.pg.rds.aliyuncs.com:5432/rune"
```

Password in **Key Management Service** (KMS) + External Secrets Operator sync. `TODO: KMS + ESO example.`

## Step 4 — OSS (Object Storage Service)

OSS has S3-compatible API with specific caveats (signing version, virtual-hosted style).

```yaml
rune:
  storage:
    s3:
      enabled: true
      endpoint: https://oss-cn-hangzhou.aliyuncs.com
      accessKey: $ALI_ACCESS_KEY
      secretKey: $ALI_SECRET_KEY
      bucket: rune-results
      # AWS SigV4 required:
      region: cn-hangzhou
```

`TODO: exact S3-compat flags; validate on a real bucket.`

## Step 5 — SLB ingress

Alibaba SLB (Server Load Balancer) via `alb` ingress class (ALB v2 managed by the cluster's add-on).

`TODO: ALB annotations + cert hosting on ACM (Alibaba's cert manager).`

## Step 6 — Chart install + validate

Same as the [shared baseline](INSTALL.md#3-chart-install).

## Cost estimation integration

`CostEstimation.alicloud` **is not yet defined** in RUNE's cost contracts (today: `vastai`, `aws`, `gcp`, `azure`, `localhardware`). File as a `rune` follow-up to add it before declaring the ACK install production-ready.

## Follow-ups tracked

- Crossplane AliCloud provider validation (less mature than others).
- RRSA + OIDC provider walkthrough.
- ApsaraDB for PostgreSQL + KMS integration.
- OSS S3 compatibility validation.
- SLB ingress + ACM cert walkthrough.
- `CostEstimation.alicloud` driver in `rune`.
- Validation transcript from a real ACK deployment.

All tracked under [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277) AliCloud follow-up.
