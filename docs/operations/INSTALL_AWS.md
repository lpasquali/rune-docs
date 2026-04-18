# Install — AWS (EKS)

!!! info "Content complete — validation transcript pending"
    Content drafted from AWS / Crossplane / ESO / AWS Load Balancer Controller official docs (2026-04). End-to-end transcript from a real EKS cluster still needed — tracked in the [Validation transcript](#validation-transcript) section at the bottom.

## Prerequisites

- EKS cluster ≥ 1.27 with `kubectl` configured via `aws eks update-kubeconfig --region $REGION --name $CLUSTER`.
- [`helm`](https://helm.sh/docs/) ≥ 3.17.
- AWS account with a role authorised to create RDS instances, S3 buckets, IAM roles/policies, ACM certificates, and Route 53 records — or opt out and bring your own.
- [**IRSA**](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html) (IAM Roles for Service Accounts) enabled on the cluster — standard on EKS since 1.18. Verify with `aws iam list-open-id-connect-providers`.
- [**AWS Load Balancer Controller**](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/) installed (for ALB ingress).
- [**External Secrets Operator**](https://external-secrets.io/latest/) installed (for AWS Secrets Manager sync) — one-time cluster add-on.
- [**Crossplane**](https://docs.crossplane.io/latest/) installed with the AWS provider family — see [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md).

Set these env vars once (used throughout):

```bash
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export CLUSTER=rune-prod
export OIDC_ID=$(aws eks describe-cluster --name $CLUSTER \
  --query 'cluster.identity.oidc.issuer' --output text | sed 's|.*/||')
```

## Step 1 — Provisioning via Crossplane

### 1a. Install the AWS provider family

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-family-aws
spec:
  package: xpkg.upbound.io/upbound/provider-family-aws:v1.21.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-rds
spec:
  package: xpkg.upbound.io/upbound/provider-aws-rds:v1.21.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v1.21.0
EOF
```

Wait for `HEALTHY`:

```bash
kubectl get providers -w
```

### 1b. Configure AWS credentials for Crossplane

Using IRSA on the Crossplane controller pod (recommended), or an AWS credentials Secret. The Upbound provider supports both; IRSA is preferred.

```bash
# Secret-based (simpler; use this only in non-prod):
kubectl create secret generic aws-creds -n crossplane-system \
  --from-literal=creds="[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY"

kubectl apply -f - <<EOF
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-creds
      key: creds
EOF
```

### 1c. RDS PostgreSQL instance

```yaml
# crossplane/rune-rds.yaml
apiVersion: rds.aws.upbound.io/v1beta2
kind: Instance
metadata:
  name: rune-db
spec:
  forProvider:
    region: us-east-1
    engine: postgres
    engineVersion: "16.3"
    instanceClass: db.t3.medium
    allocatedStorage: 50
    storageType: gp3
    storageEncrypted: true
    dbName: rune
    username: rune
    passwordSecretRef:
      namespace: rune
      name: rune-db-master
      key: password
    publiclyAccessible: false
    vpcSecurityGroupIdSelector:
      matchLabels:
        role: rune-db
    dbSubnetGroupName: rune-db-subnets
    backupRetentionPeriod: 7
    skipFinalSnapshot: false
    finalSnapshotIdentifier: rune-db-final
  writeConnectionSecretToRef:
    namespace: rune
    name: rune-db-connection
```

### 1d. S3 bucket for benchmark results

```yaml
# crossplane/rune-s3.yaml
apiVersion: s3.aws.upbound.io/v1beta2
kind: Bucket
metadata:
  name: rune-results-ACCOUNT_ID
spec:
  forProvider:
    region: us-east-1
    objectLockEnabled: false
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: BucketPublicAccessBlock
metadata:
  name: rune-results-ACCOUNT_ID
spec:
  forProvider:
    region: us-east-1
    bucketRef:
      name: rune-results-ACCOUNT_ID
    blockPublicAcls: true
    blockPublicPolicy: true
    ignorePublicAcls: true
    restrictPublicBuckets: true
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: BucketServerSideEncryptionConfiguration
metadata:
  name: rune-results-ACCOUNT_ID
spec:
  forProvider:
    region: us-east-1
    bucketRef:
      name: rune-results-ACCOUNT_ID
    rule:
      - applyServerSideEncryptionByDefault:
          - sseAlgorithm: AES256
        bucketKeyEnabled: true
```

Apply and verify:

```bash
kubectl apply -f crossplane/rune-rds.yaml -f crossplane/rune-s3.yaml
kubectl get instance.rds.aws.upbound.io -w  # wait for READY=True
kubectl get bucket.s3.aws.upbound.io -w
```

## Step 2 — IRSA for `rune-api`

### 2a. IAM policy — least-privilege to the results bucket only

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RuneResultsReadWrite",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::rune-results-ACCOUNT_ID",
        "arn:aws:s3:::rune-results-ACCOUNT_ID/*"
      ]
    }
  ]
}
```

Create the policy:

```bash
aws iam create-policy --policy-name rune-api-s3 \
  --policy-document file://iam/rune-api-s3.json
```

### 2b. Trust policy — only the `rune/rune-api` SA can assume

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/OIDC_ID"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.us-east-1.amazonaws.com/id/OIDC_ID:sub": "system:serviceaccount:rune:rune-api",
          "oidc.eks.us-east-1.amazonaws.com/id/OIDC_ID:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

Create the role:

```bash
aws iam create-role --role-name rune-api-s3-role \
  --assume-role-policy-document file://iam/trust.json

aws iam attach-role-policy --role-name rune-api-s3-role \
  --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/rune-api-s3
```

### 2c. Annotate the SA in Helm values

```yaml
# values-aws.yaml
serviceAccount:
  create: true
  name: rune-api
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/rune-api-s3-role
```

## Step 3 — External Secrets Operator → AWS Secrets Manager

### 3a. ClusterSecretStore pointing at Secrets Manager

```yaml
# eso/clustersecretstore.yaml
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

The `external-secrets` ServiceAccount needs its own IRSA role with `secretsmanager:GetSecretValue` on the RUNE secrets. ESO documents this in [AWS provider auth](https://external-secrets.io/latest/provider/aws-secrets-manager/).

### 3b. ExternalSecret — sync the DB password

```yaml
# eso/rune-db-secret.yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: rune-db-master
  namespace: rune
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: rune-db-master
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: rune/prod/db-master
        property: password
```

ESO will populate `rune-db-master` Secret in the `rune` namespace from Secrets Manager key `rune/prod/db-master`.

### 3c. RDS connection URL in Helm values

Crossplane writes `rune-db-connection` Secret with host/port/username. Rune API consumes both the connection Secret (host/port) and the ESO-synced password Secret:

```yaml
# values-aws.yaml (continued)
rune:
  storage:
    postgresql:
      enabled: true
      # chart expands this to a full URL at runtime
      hostSecretRef: rune-db-connection
      hostKey: endpoint
      portKey: port
      usernameKey: username
      passwordSecretRef: rune-db-master
      passwordKey: password
      database: rune
      sslmode: require
```

## Step 4 — ACM certificate + Route 53 DNS

### 4a. Request a public certificate for the RUNE domain

```bash
CERT_ARN=$(aws acm request-certificate \
  --domain-name rune.example.com \
  --validation-method DNS \
  --region us-east-1 \
  --query CertificateArn --output text)
```

ACM emits a DNS validation record you must add to Route 53:

```bash
aws acm describe-certificate --certificate-arn $CERT_ARN \
  --query 'Certificate.DomainValidationOptions[].ResourceRecord' \
  --output table
```

Create the Route 53 validation record (manual one-time):

```bash
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID \
  --change-batch file://route53/acm-validation.json
```

Wait for `Status: ISSUED` via `aws acm describe-certificate`.

### 4b. Route 53 A-record pointing at the ALB

After Step 5 creates the ALB, get its DNS name via `kubectl -n rune get ingress rune -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'`, then create an alias A-record:

```json
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "rune.example.com.",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z35SXDOTRQ7X7K",
        "DNSName": "$ALB_HOSTNAME",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
```

(The `Z35SXDOTRQ7X7K` is the fixed ALB hosted-zone ID for `us-east-1`; get yours from [AWS ELB regional endpoints](https://docs.aws.amazon.com/general/latest/gr/elb.html).)

## Step 5 — ALB ingress

```yaml
# values-aws.yaml (continued)
ingress:
  enabled: true
  className: alb
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID
    alb.ingress.kubernetes.io/healthcheck-path: /healthz
    alb.ingress.kubernetes.io/load-balancer-attributes: access_logs.s3.enabled=true,access_logs.s3.bucket=rune-alb-logs
  hosts:
    - host: rune.example.com
      paths:
        - path: /
          pathType: Prefix
```

## Step 6 — Chart install

```bash
helm install rune ./charts/rune \
  --namespace rune --create-namespace \
  --values values-aws.yaml \
  --wait --timeout=5m
```

Sanity-check:

```bash
kubectl -n rune get pods                     # all Running
kubectl -n rune get externalsecrets          # SyncedStatus=Ready
kubectl -n rune get ingress rune             # ADDRESS populated
```

## Step 7 — Validate

```bash
TOKEN=$(kubectl -n rune get secret rune-api-token -o jsonpath='{.data.token}' | base64 -d)

# Via ALB
curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/healthz
# Expected: {"status":"ok","version":"0.0.0aN"}

curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/v1/llm/models | jq
# Expected: list of backends registered

# End-to-end: run a small benchmark
curl -sfH "Authorization: Bearer $TOKEN" -X POST \
  -H 'Content-Type: application/json' \
  -d '{"agent":"holmes","backend_type":"ollama","question":"Test"}' \
  https://rune.example.com/v1/benchmark/run
```

## Cost estimation integration

`CostEstimation.aws` supports AWS-specific cost projections for future RUNE provisioning against EC2 / GPU instances. See [ADR 0002](../architecture/adrs/0002-cost-estimation.md) and [SYSTEM_PROMPT §Cost gates](../context/SYSTEM_PROMPT.md#cost-gates-api-contracts).

## Teardown

```bash
helm uninstall rune -n rune
kubectl delete -f crossplane/rune-rds.yaml -f crossplane/rune-s3.yaml
# RDS final snapshot is kept per skipFinalSnapshot:false
aws iam detach-role-policy --role-name rune-api-s3-role \
  --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/rune-api-s3
aws iam delete-role --role-name rune-api-s3-role
aws iam delete-policy --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/rune-api-s3
aws acm delete-certificate --certificate-arn $CERT_ARN
```

## Validation transcript

!!! warning "Pending real-cluster validation"
    This section is intentionally empty until the walkthrough above is run on a real EKS cluster. Paste the transcript here, with timings and relevant output for each step. Tracked in [#302](https://github.com/lpasquali/rune-docs/issues/302).

```
TODO: Paste validated transcript here, e.g.
$ kubectl get instance.rds.aws.upbound.io
NAME      READY   SYNCED   EXTERNAL-NAME    AGE
rune-db   True    True     rune-db          8m
...
```

## References

- [EKS user guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)
- [External Secrets Operator — AWS Secrets Manager provider](https://external-secrets.io/latest/provider/aws-secrets-manager/)
- [Crossplane AWS provider](https://marketplace.upbound.io/providers/upbound/provider-family-aws)
- [ADR 0007 — Crossplane infrastructure provisioning](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md)
- [External Links Catalog](../reference/EXTERNAL_LINKS.md) — canonical URLs
