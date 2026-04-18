# Install — Azure (AKS)

!!! note "Scaffold"
    Structure complete; cloud-specific detail needs hands-on validation.
    Follow-up: [rune-docs#277](https://github.com/lpasquali/rune-docs/issues/277).

## Prerequisites

- AKS cluster ≥ 1.27. Kubeconfig via `az aks get-credentials`.
- `helm` ≥ 3.17.
- Azure subscription with providers registered: `Microsoft.DBforPostgreSQL`, `Microsoft.Storage`, `Microsoft.ContainerService`.
- **Workload Identity** for AKS enabled (the Azure equivalent of IRSA).

## Step 1 — Provisioning via Crossplane

`TODO: provider-family-azure + Azure Database for PostgreSQL + Blob Storage CRs.`

## Step 2 — Managed Identity for rune-api

```bash
az identity create --name rune-api-identity --resource-group rune-rg
az identity federated-credential create \
  --name rune-api-federated \
  --identity-name rune-api-identity \
  --resource-group rune-rg \
  --issuer $OIDC_URL \
  --subject system:serviceaccount:rune:rune-api
```

```yaml
serviceAccount:
  annotations:
    azure.workload.identity/client-id: $CLIENT_ID
  labels:
    azure.workload.identity/use: "true"
```

`TODO: full Managed Identity walkthrough.`

## Step 3 — Azure Database for PostgreSQL

```yaml
rune:
  storage:
    postgresql:
      enabled: true
      url: "postgres://rune@runepg:$PG_PASSWORD@runepg.postgres.database.azure.com:5432/rune?sslmode=require"
```

Password via Azure Key Vault + CSI driver or External Secrets Operator. `TODO: AKV + CSI example.`

## Step 4 — Azure Blob Storage

Blob Storage speaks S3 via the Azure Blob-S3 gateway or via the **azcopy** tool. For programmatic S3, use **Azurite** in dev or a compatibility gateway in prod. Alternative: use a third-party S3 interface layer.

`TODO: concrete path — azurite dev, something-else prod.`

## Step 5 — Application Gateway ingress

```yaml
ingress:
  enabled: true
  className: azure-application-gateway
```

`TODO: AGIC add-on installation + Key Vault cert sync.`

## Step 6 — Chart install + validate

Same as the [shared baseline](INSTALL.md#3-chart-install).

## Cost estimation integration

`CostEstimation.azure` supports Azure-specific cost projections.

## Follow-ups tracked

- Managed Identity + Workload Identity walkthrough.
- Azure Database for PostgreSQL + AKV + CSI.
- S3-compatible path for Blob Storage.
- Application Gateway Ingress Controller (AGIC) walkthrough.
- Validation transcript from a real AKS deployment.
