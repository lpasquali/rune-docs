# Install — Alibaba Cloud (ACK)

!!! info "Content complete — validation transcript pending"
    Content drafted from Alibaba Cloud / Crossplane community provider / ESO official docs (2026-04). End-to-end transcript from a real ACK cluster still needed — tracked in the [Validation transcript](#validation-transcript) section at the bottom.

    The Crossplane **AliCloud provider is maintained by the community** (`crossplane-contrib/provider-jet-alibabacloud`), not Upbound. It's less mature than AWS/GCP/Azure providers; expect to validate each CR before committing.

## Prerequisites

- ACK cluster ≥ 1.27 (Managed or Pro). Kubeconfig via `aliyun cs GET /k8s/$CLUSTER_ID/user_config` then merge into `~/.kube/config`.
- [`helm`](https://helm.sh/docs/) ≥ 3.17.
- Alibaba Cloud account with RAM authority for **ApsaraDB for RDS (PostgreSQL)**, **OSS**, **KMS**, **RAM**, and **ALB**.
- [**RRSA** (RAM Roles for Service Accounts)](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-rrsa-to-authorize-different-pods-to-access-different-cloud-services) enabled on the cluster. Enable once per cluster:

  ```bash
  aliyun cs POST /clusters/$CLUSTER_ID/access-control/rrsa \
    --header "Content-Type=application/json" \
    --body '{"enable_rrsa":true}'
  ```

  RRSA is Alibaba's equivalent of IRSA — it adds an OIDC issuer to the cluster and a service-account-token projector.

- [**External Secrets Operator**](https://external-secrets.io/latest/provider/alibaba/) installed (experimental provider for AliCloud KMS).
- [**Crossplane**](https://docs.crossplane.io/latest/) with the community AliCloud provider — see [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md).

Env vars:

```bash
export REGION=cn-hangzhou
export CLUSTER_ID=c1234567890abcdef
export ACCOUNT_ID=$(aliyun sts GetCallerIdentity --query AccountId --output text)
export OIDC_ARN=$(aliyun cs GET /clusters/$CLUSTER_ID | jq -r '.meta_data | fromjson | .RRSAConfig.RRSAOIDCIssuerURL')
```

## Step 1 — Provisioning via Crossplane

### 1a. Install the community provider-jet-alibabacloud

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata: { name: provider-jet-alibabacloud }
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-jet-alibabacloud:v0.9.0
EOF
kubectl get providers -w   # wait for INSTALLED and HEALTHY
```

### 1b. ProviderConfig with AK/SK (RRSA-based credentials not yet supported by the community provider)

```bash
kubectl create secret generic alicloud-creds -n crossplane-system \
  --from-literal=credentials="{\"accessKeyId\":\"$ALICLOUD_ACCESS_KEY\",\"accessKeySecret\":\"$ALICLOUD_SECRET_KEY\"}"
```

```yaml
apiVersion: alibaba.jet.crossplane.io/v1beta1
kind: ProviderConfig
metadata: { name: default }
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: alicloud-creds
      key: credentials
  region: cn-hangzhou
```

!!! note
    Once `provider-jet-alibabacloud` gains RRSA support, replace Secret-based auth with `source: InjectedIdentity`. Tracked upstream — no ETA.

### 1c. ApsaraDB RDS for PostgreSQL

```yaml
# crossplane/rune-rds.yaml
apiVersion: rds.alibaba.jet.crossplane.io/v1alpha2
kind: Instance
metadata: { name: rune-db }
spec:
  forProvider:
    region: cn-hangzhou
    engine: PostgreSQL
    engineVersion: "16.0"
    dbInstanceClass: pg.n2.2c.1m
    dbInstanceStorage: 50
    dbInstanceStorageType: cloud_essd
    securityIpList:
      - "0.0.0.0/0"   # tighten to VPC CIDR in prod
    vswitchId: vsw-xxx
    instanceNetworkType: VPC
---
apiVersion: rds.alibaba.jet.crossplane.io/v1alpha2
kind: Database
metadata: { name: rune }
spec:
  forProvider:
    instanceIdRef: { name: rune-db }
    characterSet: UTF8
---
apiVersion: rds.alibaba.jet.crossplane.io/v1alpha2
kind: Account
metadata: { name: rune }
spec:
  forProvider:
    instanceIdRef: { name: rune-db }
    accountType: Normal
    accountPasswordSecretRef:
      namespace: rune
      name: rune-db-app
      key: password
```

### 1d. OSS bucket

```yaml
apiVersion: oss.alibaba.jet.crossplane.io/v1alpha2
kind: Bucket
metadata: { name: rune-results-ACCOUNT_ID }
spec:
  forProvider:
    bucket: rune-results-ACCOUNT_ID
    acl: private
    storageClass: Standard
    serverSideEncryptionRule:
      - sseAlgorithm: AES256
```

## Step 2 — RRSA for `rune-api`

### 2a. Create a RAM role with an OIDC trust

```bash
# Policy: read/write only this OSS bucket
cat > iam/oss-policy.json <<EOF
{
  "Version": "1",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "oss:GetObject", "oss:PutObject", "oss:DeleteObject",
      "oss:ListObjects", "oss:GetBucketLocation"
    ],
    "Resource": [
      "acs:oss:*:*:rune-results-$ACCOUNT_ID",
      "acs:oss:*:*:rune-results-$ACCOUNT_ID/*"
    ]
  }]
}
EOF

aliyun ram CreatePolicy --PolicyName rune-api-oss \
  --PolicyDocument "$(cat iam/oss-policy.json)"

# Trust policy: cluster OIDC + specific SA
cat > iam/trust.json <<EOF
{
  "Version": "1",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:AssumeRole",
    "Principal": { "Federated": ["$OIDC_ARN"] },
    "Condition": {
      "StringEquals": {
        "oidc:sub": "system:serviceaccount:rune:rune-api",
        "oidc:aud": "sts.aliyuncs.com"
      }
    }
  }]
}
EOF

aliyun ram CreateRole --RoleName rune-api-role \
  --AssumeRolePolicyDocument "$(cat iam/trust.json)"

aliyun ram AttachPolicyToRole --RoleName rune-api-role \
  --PolicyType Custom --PolicyName rune-api-oss
```

### 2b. Annotate the SA in Helm values

```yaml
# values-alicloud.yaml (snippet)
serviceAccount:
  create: true
  name: rune-api
  annotations:
    pod.beta1.alibabacloud.com/ram-role-name: rune-api-role
```

## Step 3 — ApsaraDB for PostgreSQL — connect

The RDS instance issues a connection string like `rm-XYZ.pg.rds.aliyuncs.com:5432`.

```yaml
# values-alicloud.yaml (continued)
rune:
  storage:
    postgresql:
      enabled: true
      host: rm-XYZ.pg.rds.aliyuncs.com
      port: 5432
      database: rune
      username: rune
      passwordSecretRef: rune-db-app
      passwordKey: password
      sslmode: require
```

## Step 4 — KMS + External Secrets Operator

### 4a. Create a KMS instance + secret

```bash
aliyun kms CreateSecret \
  --SecretName rune-db-app \
  --SecretData "$PG_PASSWORD" \
  --VersionId v1

aliyun kms CreateSecret \
  --SecretName rune-oss-hmac-access \
  --SecretData "$HMAC_ACCESS_ID" \
  --VersionId v1

aliyun kms CreateSecret \
  --SecretName rune-oss-hmac-secret \
  --SecretData "$HMAC_SECRET" \
  --VersionId v1
```

### 4b. ClusterSecretStore for ESO

```yaml
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata: { name: alicloud-kms }
spec:
  provider:
    alibaba:
      regionID: cn-hangzhou
      auth:
        rrsa:
          oidcProviderArn: $OIDC_ARN
          oidcTokenFilePath: /var/run/secrets/tokens/alicloud-token
          roleArn: acs:ram::$ACCOUNT_ID:role/external-secrets-kms
          sessionName: external-secrets
```

!!! note
    ESO's Alibaba provider is marked **experimental** at time of writing. If it misbehaves, fall back to `ack-secret-manager` (Alibaba's native operator: [ack-secret-manager docs](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-ack-secret-manager-to-retrieve-and-parse-kms-secrets-in-a-kubernetes-cluster)).

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata: { name: rune-db-app, namespace: rune }
spec:
  refreshInterval: 1h
  secretStoreRef: { kind: ClusterSecretStore, name: alicloud-kms }
  target: { name: rune-db-app }
  data:
    - secretKey: password
      remoteRef: { key: rune-db-app }
```

## Step 5 — OSS as S3

OSS speaks the S3 API with caveats: requires `SigV4`, and `pathStyle` addressing is recommended. Generate an HMAC (AK/SK equivalent) for the rune-api RAM user, store in KMS (above), and wire:

```yaml
# values-alicloud.yaml (continued)
rune:
  storage:
    s3:
      enabled: true
      endpoint: https://oss-cn-hangzhou.aliyuncs.com
      region: cn-hangzhou
      bucket: rune-results-$ACCOUNT_ID
      accessKeySecretRef: rune-oss-hmac
      accessKeyKey: access
      secretKeySecretRef: rune-oss-hmac
      secretKeyKey: secret
      pathStyle: true
      sigVersion: v4
```

## Step 6 — ALB ingress

ACK managed ALB ingress controller provides the `alb` ingress class. Pre-create an ALB or let AGIC create one.

Get/create an SSL cert via [Alibaba Cloud Certificate Management](https://www.alibabacloud.com/product/certificate), then reference it:

```yaml
# values-alicloud.yaml (continued)
ingress:
  enabled: true
  className: alb
  annotations:
    alb.ingress.kubernetes.io/address-type: "internet"
    alb.ingress.kubernetes.io/load-balancer-spec: "slb.s2.small"
    alb.ingress.kubernetes.io/cert-id: "CERT-ID-cn-hangzhou"
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "true"
    alb.ingress.kubernetes.io/healthcheck-path: /healthz
  hosts:
    - host: rune.example.com
      paths:
        - path: /
          pathType: Prefix
```

Install the ALB ingress add-on if not already present:

```bash
aliyun cs POST /clusters/$CLUSTER_ID/components/alb-ingress-controller/install
```

## Step 7 — Chart install

```bash
helm install rune ./charts/rune \
  --namespace rune --create-namespace \
  --values values-alicloud.yaml \
  --wait --timeout=10m
```

## Step 8 — DNS + validate

Get the ALB public IP:

```bash
ALB_IP=$(kubectl -n rune get ingress rune \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

Create A record `rune.example.com → $ALB_IP` in [Alibaba Cloud DNS](https://www.alibabacloud.com/product/dns) or your DNS provider.

```bash
TOKEN=$(kubectl -n rune get secret rune-api-token -o jsonpath='{.data.token}' | base64 -d)
curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/healthz
```

## Cost estimation integration

**`CostEstimation.alicloud` is not yet defined** in RUNE's cost contracts (today: `vastai`, `aws`, `gcp`, `azure`, `localhardware`). File as a `rune` follow-up to add it before declaring the ACK install production-ready. Placeholder contract shape:

```python
# rune_bench/resources/alicloud.py (planned)
class AliCloudCostEstimator(CostEstimator):
    """
    Uses aliyun.pricing GetPrice / DescribePrice for ECS + GPU SKUs.
    Returns CostEstimationResponse with confidence_score and per-hour projections.
    """
```

Tracking: [`rune-docs#305`](https://github.com/lpasquali/rune-docs/issues/305) (this issue) + follow-up issue in `rune` for the driver.

## Teardown

```bash
helm uninstall rune -n rune
kubectl delete -f crossplane/rune-rds.yaml
aliyun ram DetachPolicyFromRole --RoleName rune-api-role \
  --PolicyType Custom --PolicyName rune-api-oss
aliyun ram DeleteRole --RoleName rune-api-role
aliyun ram DeletePolicy --PolicyName rune-api-oss
```

## Validation transcript

!!! warning "Pending real-cluster validation"
    Populate after running this walkthrough on a real ACK cluster. Tracked in [#305](https://github.com/lpasquali/rune-docs/issues/305).

```
TODO: Paste validated transcript here.
```

## References

- [ACK — managed Kubernetes overview](https://www.alibabacloud.com/help/en/ack/)
- [RRSA — RAM Roles for Service Accounts](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-rrsa-to-authorize-different-pods-to-access-different-cloud-services)
- [ApsaraDB RDS PostgreSQL](https://www.alibabacloud.com/help/en/rds/apsaradb-rds-for-postgresql)
- [OSS — S3 compatibility](https://www.alibabacloud.com/help/en/oss/developer-reference/use-amazon-s3-sdks-to-access-oss)
- [ALB Ingress Controller](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/alb-ingresses)
- [Key Management Service (KMS)](https://www.alibabacloud.com/product/kms)
- [ack-secret-manager](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-ack-secret-manager-to-retrieve-and-parse-kms-secrets-in-a-kubernetes-cluster)
- [Crossplane contrib — provider-jet-alibabacloud](https://github.com/crossplane-contrib/provider-jet-alibabacloud)
- [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md)
- [External Links Catalog](../reference/EXTERNAL_LINKS.md)
