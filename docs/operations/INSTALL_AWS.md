# Install — AWS (EKS)

!!! note "Scaffold"
    This page has the structure, but the cloud-specific detail requires
    hands-on validation on a real EKS cluster. Flesh-out tracked as
    follow-up issue under [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277).

## Prerequisites

- EKS cluster ≥ 1.27 with `kubectl` configured via `aws eks update-kubeconfig`.
- `helm` ≥ 3.17.
- IAM role with authority to create RDS instances + S3 buckets, or opt out and bring your own.
- **IRSA** (IAM Roles for Service Accounts) enabled on the cluster — standard on EKS since 1.18.

## Step 1 — Provisioning via Crossplane

`TODO: full Crossplane AWS provider manifest — see follow-up.`

Expected: `provider-family-aws` + `provider-aws-rds` + `provider-aws-s3` installed in the cluster. Then a `DBInstance` CR for Postgres 16 and a `Bucket` CR for S3 results. CR YAML will land with the follow-up.

## Step 2 — IRSA for rune-api

Create an IAM policy granting `s3:*` on the results bucket only; attach to a role that trusts the EKS OIDC provider for the `rune/rune-api` service account.

```yaml
# values.yaml snippet
serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/rune-api-s3-role
```

`TODO: full IAM policy JSON + trust relationship example.`

## Step 3 — RDS-Postgres option

If using RDS instead of CNPG:

```yaml
# values.yaml snippet
rune:
  storage:
    postgresql:
      enabled: true
      url: "postgres://rune:$PG_PASSWORD@rune-db.cluster-xxxx.us-east-1.rds.amazonaws.com:5432/rune"
```

Store the password in **AWS Secrets Manager** and sync to Kubernetes via the AWS Secrets Manager CSI driver or External Secrets Operator. `TODO: ESO example.`

## Step 4 — ALB ingress

```yaml
# values.yaml snippet
ingress:
  enabled: true
  className: alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/xxx
```

`TODO: ACM certificate setup walkthrough + Route 53 DNS step.`

## Step 5 — Chart install

```bash
helm install rune ./charts/rune \
  --namespace rune --create-namespace \
  --values rune-aws-values.yaml \
  --wait --timeout=5m
```

## Step 6 — Validate

```bash
# Via ALB
curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/healthz
```

## Cost estimation integration

`CostEstimation.aws` supports AWS-specific cost projections for future RUNE provisioning against EC2 / GPU instances. See [ADR 0002](../architecture/adrs/0002-cost-estimation.md) and [SYSTEM_PROMPT §Cost gates](../context/SYSTEM_PROMPT.md#cost-gates-api-contracts).

## Follow-ups tracked

- Crossplane provider manifests (RDS, S3, IRSA role) — flesh out.
- External Secrets Operator example for AWS Secrets Manager — flesh out.
- ACM + Route 53 DNS step — flesh out.
- Validation transcript from a real EKS deployment — flesh out.

All tracked under [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277) follow-up issue for AWS.
