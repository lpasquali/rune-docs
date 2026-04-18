# Install — Azure (AKS)

!!! info "Content complete — validation transcript pending"
    Content drafted from Azure / Crossplane / ESO / AKS official docs (2026-04). End-to-end transcript from a real AKS cluster still needed — tracked in the [Validation transcript](#validation-transcript) section at the bottom.

## Prerequisites

- AKS cluster ≥ 1.27. Kubeconfig via `az aks get-credentials --resource-group $RG --name $CLUSTER`.
- [`helm`](https://helm.sh/docs/) ≥ 3.17.
- Azure subscription with providers registered:

  ```bash
  az provider register --namespace Microsoft.DBforPostgreSQL
  az provider register --namespace Microsoft.Storage
  az provider register --namespace Microsoft.ContainerService
  az provider register --namespace Microsoft.KeyVault
  az provider register --namespace Microsoft.Network
  ```

- [**Workload Identity**](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview) and [**OIDC Issuer**](https://learn.microsoft.com/en-us/azure/aks/cluster-configuration#oidc-issuer) enabled on the cluster. Verify:

  ```bash
  az aks show --resource-group $RG --name $CLUSTER \
    --query "oidcIssuerProfile,securityProfile.workloadIdentity" -o json
  ```

  Enable if missing:

  ```bash
  az aks update --resource-group $RG --name $CLUSTER \
    --enable-oidc-issuer --enable-workload-identity
  ```

- [**External Secrets Operator**](https://external-secrets.io/latest/provider/azure-key-vault/) installed (for Key Vault sync). Alternatively the [Azure Key Vault CSI driver](https://azure.github.io/secrets-store-csi-driver-provider-azure/) — both covered below.
- [**Application Gateway Ingress Controller (AGIC)**](https://azure.github.io/application-gateway-kubernetes-ingress/) installed as an AKS add-on.
- [**Crossplane**](https://docs.crossplane.io/latest/) installed with the Azure provider family — see [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md).

Env vars:

```bash
export SUBSCRIPTION_ID=$(az account show --query id -o tsv)
export RG=rune-rg
export LOCATION=eastus
export CLUSTER=rune-prod
export OIDC_URL=$(az aks show -g $RG -n $CLUSTER --query oidcIssuerProfile.issuerUrl -o tsv)
```

## Step 1 — Provisioning via Crossplane

### 1a. Install the Azure provider family

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata: { name: provider-family-azure }
spec:
  package: xpkg.upbound.io/upbound/provider-family-azure:v1.6.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata: { name: provider-azure-dbforpostgresql }
spec:
  package: xpkg.upbound.io/upbound/provider-azure-dbforpostgresql:v1.6.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata: { name: provider-azure-storage }
spec:
  package: xpkg.upbound.io/upbound/provider-azure-storage:v1.6.0
EOF
kubectl get providers -w
```

### 1b. ProviderConfig via Workload Identity

```bash
# Create UMI for Crossplane, grant it Contributor on the subscription
az identity create --name crossplane-azure --resource-group $RG
CROSSPLANE_CLIENT_ID=$(az identity show -g $RG -n crossplane-azure --query clientId -o tsv)
CROSSPLANE_PRINCIPAL_ID=$(az identity show -g $RG -n crossplane-azure --query principalId -o tsv)

az role assignment create --role Contributor \
  --assignee-object-id $CROSSPLANE_PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --scope /subscriptions/$SUBSCRIPTION_ID

# Federated credential: trust the crossplane K8s SA
az identity federated-credential create \
  --name crossplane-federated \
  --identity-name crossplane-azure \
  --resource-group $RG \
  --issuer $OIDC_URL \
  --subject system:serviceaccount:crossplane-system:crossplane \
  --audiences api://AzureADTokenExchange

kubectl annotate sa -n crossplane-system crossplane \
  azure.workload.identity/client-id=$CROSSPLANE_CLIENT_ID

kubectl label sa -n crossplane-system crossplane \
  azure.workload.identity/use=true
```

```yaml
apiVersion: azure.upbound.io/v1beta1
kind: ProviderConfig
metadata: { name: default }
spec:
  credentials:
    source: InjectedIdentity
  subscriptionID: $SUBSCRIPTION_ID
```

### 1c. Azure Database for PostgreSQL (Flexible Server)

```yaml
# crossplane/rune-pg.yaml
apiVersion: dbforpostgresql.azure.upbound.io/v1beta1
kind: FlexibleServer
metadata:
  name: rune-pg
spec:
  forProvider:
    location: eastus
    resourceGroupName: rune-rg
    version: "16"
    skuName: GP_Standard_D2s_v3
    storageMb: 32768
    administratorLogin: runeadmin
    administratorPasswordSecretRef:
      namespace: rune
      name: rune-pg-admin
      key: password
    backupRetentionDays: 7
    highAvailability:
      - mode: ZoneRedundant
---
apiVersion: dbforpostgresql.azure.upbound.io/v1beta1
kind: FlexibleServerDatabase
metadata: { name: rune }
spec:
  forProvider:
    serverId: /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.DBforPostgreSQL/flexibleServers/rune-pg
    charset: UTF8
    collation: "en_US.utf8"
```

### 1d. Blob Storage account + container

```yaml
apiVersion: storage.azure.upbound.io/v1beta2
kind: Account
metadata: { name: runestore }
spec:
  forProvider:
    location: eastus
    resourceGroupName: rune-rg
    accountTier: Standard
    accountReplicationType: LRS
    minTlsVersion: TLS1_2
    allowNestedItemsToBePublic: false
---
apiVersion: storage.azure.upbound.io/v1beta1
kind: Container
metadata: { name: rune-results }
spec:
  forProvider:
    storageAccountName: runestore
    containerAccessType: private
```

## Step 2 — Managed Identity + Workload Identity for `rune-api`

```bash
az identity create --name rune-api-identity --resource-group $RG
RUNE_CLIENT_ID=$(az identity show -g $RG -n rune-api-identity --query clientId -o tsv)
RUNE_PRINCIPAL_ID=$(az identity show -g $RG -n rune-api-identity --query principalId -o tsv)

# Grant Storage Blob Data Contributor on the results container
az role assignment create --role "Storage Blob Data Contributor" \
  --assignee-object-id $RUNE_PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/runestore/blobServices/default/containers/rune-results

# Federated credential
az identity federated-credential create \
  --name rune-api-federated \
  --identity-name rune-api-identity \
  --resource-group $RG \
  --issuer $OIDC_URL \
  --subject system:serviceaccount:rune:rune-api \
  --audiences api://AzureADTokenExchange
```

```yaml
# values-azure.yaml (snippet)
serviceAccount:
  create: true
  name: rune-api
  annotations:
    azure.workload.identity/client-id: $RUNE_CLIENT_ID
  labels:
    azure.workload.identity/use: "true"

podLabels:
  azure.workload.identity/use: "true"
```

## Step 3 — Azure Database for PostgreSQL — connect

The Flexible Server issues a DNS name like `rune-pg.postgres.database.azure.com`. Connection requires `sslmode=require`.

```yaml
# values-azure.yaml (continued)
rune:
  storage:
    postgresql:
      enabled: true
      host: rune-pg.postgres.database.azure.com
      port: 5432
      database: rune
      username: runeadmin
      passwordSecretRef: rune-pg-admin
      passwordKey: password
      sslmode: require
```

## Step 4 — External Secrets Operator → Key Vault

Create a Key Vault, store DB + storage secrets:

```bash
az keyvault create --name rune-kv-$RANDOM --resource-group $RG --location $LOCATION

az keyvault secret set --vault-name rune-kv --name rune-pg-admin-password --value "$PG_PASSWORD"
```

Grant ESO SA `Key Vault Secrets User` role via Workload Identity:

```bash
az identity create --name eso-identity --resource-group $RG
ESO_CLIENT_ID=$(az identity show -g $RG -n eso-identity --query clientId -o tsv)
ESO_PRINCIPAL_ID=$(az identity show -g $RG -n eso-identity --query principalId -o tsv)

az role assignment create --role "Key Vault Secrets User" \
  --assignee-object-id $ESO_PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/rune-kv

az identity federated-credential create \
  --name eso-federated \
  --identity-name eso-identity \
  --resource-group $RG \
  --issuer $OIDC_URL \
  --subject system:serviceaccount:external-secrets:external-secrets \
  --audiences api://AzureADTokenExchange

kubectl annotate sa -n external-secrets external-secrets \
  azure.workload.identity/client-id=$ESO_CLIENT_ID
```

```yaml
# eso/clustersecretstore.yaml
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: azure-keyvault
spec:
  provider:
    azurekv:
      vaultUrl: https://rune-kv.vault.azure.net
      authType: WorkloadIdentity
      serviceAccountRef:
        name: external-secrets
        namespace: external-secrets
```

```yaml
# eso/rune-pg-admin.yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata: { name: rune-pg-admin, namespace: rune }
spec:
  refreshInterval: 1h
  secretStoreRef: { kind: ClusterSecretStore, name: azure-keyvault }
  target: { name: rune-pg-admin }
  data:
    - secretKey: password
      remoteRef: { key: rune-pg-admin-password }
```

## Step 5 — Blob Storage access via Workload Identity (no S3 gateway)

RUNE's storage layer supports Azure Blob natively when `storage.azureBlob` is enabled. This **avoids the S3-compat gateway layer** (which is lossy on Blob Storage).

```yaml
# values-azure.yaml (continued)
rune:
  storage:
    azureBlob:
      enabled: true
      accountName: runestore
      container: rune-results
      authMode: workloadIdentity
    s3:
      enabled: false   # do NOT enable S3 on Azure; use native blob client
```

!!! note "If you must have S3-compat"
    Use the [Azure Blob S3 proxy](https://github.com/gaul/s3proxy) as a sidecar. It supports the subset RUNE uses (put / get / list / delete). Mark it as Tier-2 compatibility; not all S3 features survive.

## Step 6 — Application Gateway Ingress Controller

Enable AGIC as an add-on (one-time per cluster):

```bash
az aks enable-addons --resource-group $RG --name $CLUSTER \
  --addons ingress-appgw \
  --appgw-name rune-appgw --appgw-subnet-cidr "10.225.0.0/16"
```

Request a cert into Key Vault (or import existing):

```bash
az keyvault certificate create --vault-name rune-kv --name rune-cert \
  --policy "$(az keyvault certificate get-default-policy \
    | jq '.x509CertificateProperties.subject="CN=rune.example.com"')"
```

```yaml
# values-azure.yaml (continued)
ingress:
  enabled: true
  className: azure-application-gateway
  annotations:
    appgw.ingress.kubernetes.io/use-private-ip: "false"
    appgw.ingress.kubernetes.io/backend-protocol: "http"
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
    appgw.ingress.kubernetes.io/appgw-ssl-certificate: rune-cert
    appgw.ingress.kubernetes.io/health-probe-path: /healthz
  hosts:
    - host: rune.example.com
      paths:
        - path: /
          pathType: Prefix
```

Bind the Application Gateway's managed identity to Key Vault:

```bash
APPGW_IDENTITY=$(az aks show -g $RG -n $CLUSTER \
  --query addonProfiles.ingressApplicationGateway.identity.objectId -o tsv)

az keyvault set-policy --name rune-kv \
  --object-id $APPGW_IDENTITY \
  --secret-permissions get \
  --certificate-permissions get
```

## Step 7 — Chart install

```bash
helm install rune ./charts/rune \
  --namespace rune --create-namespace \
  --values values-azure.yaml \
  --wait --timeout=10m
```

## Step 8 — DNS + validate

Get the Application Gateway public IP:

```bash
APPGW_IP=$(az network public-ip show -g MC_${RG}_${CLUSTER}_${LOCATION} \
  --name rune-appgw-appgwpip --query ipAddress -o tsv)
```

Create A record `rune.example.com → $APPGW_IP` via your DNS provider.

```bash
TOKEN=$(kubectl -n rune get secret rune-api-token -o jsonpath='{.data.token}' | base64 -d)

curl -sfH "Authorization: Bearer $TOKEN" https://rune.example.com/healthz
```

## Cost estimation integration

`CostEstimation.azure` supports Azure-specific cost projections for RUNE provisioning against Azure VM / GPU SKUs. See [ADR 0002](../architecture/adrs/0002-cost-estimation.md).

## Teardown

```bash
helm uninstall rune -n rune
kubectl delete -f crossplane/rune-pg.yaml   # note deletion-protected PG flexible servers need manual prep
az aks disable-addons -g $RG -n $CLUSTER --addons ingress-appgw
az identity delete --name rune-api-identity --resource-group $RG
az keyvault delete --name rune-kv --resource-group $RG
```

## Validation transcript

!!! warning "Pending real-cluster validation"
    Populate after running this walkthrough on a real AKS cluster. Tracked in [#304](https://github.com/lpasquali/rune-docs/issues/304).

```
TODO: Paste validated transcript here.
```

## References

- [AKS Workload Identity overview](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview)
- [AGIC — Application Gateway Ingress Controller](https://azure.github.io/application-gateway-kubernetes-ingress/)
- [Azure Database for PostgreSQL — Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/overview)
- [Key Vault CSI provider](https://azure.github.io/secrets-store-csi-driver-provider-azure/)
- [External Secrets Operator — Azure Key Vault](https://external-secrets.io/latest/provider/azure-key-vault/)
- [Crossplane Azure provider](https://marketplace.upbound.io/providers/upbound/provider-family-azure)
- [ADR 0007](../architecture/adrs/0007-crossplane-infrastructure-provisioning.md)
- [External Links Catalog](../reference/EXTERNAL_LINKS.md)
