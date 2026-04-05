 
# Vault Integration

The operator chart supports **optional** HashiCorp Vault integration via the Vault Agent Injector (sidecar) pattern. This is an opt-in feature; the default deployment uses standard Kubernetes Secrets.

 
## Architecture

```
Pod
├── manager (rune-operator)          ← reads token from projected volume
└── vault-agent (sidecar, injected)  ← fetches secret from Vault, writes to shared tmpfs
```

 
## Prerequisites

1. [Vault Agent Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector) installed.
2. A Kubernetes Auth method configured in Vault.
3. A Vault policy that allows reading the secret.

 
## Helm values

```yaml
vault:
  enabled: true
  address: "https://vault.example.com:8200"
  role: "rune-operator"
  secretPath: "secret/data/rune/api-token"
```

 
## Troubleshooting

```bash
 
# Check Vault Agent sidecar logs.

kubectl logs -n <namespace> deploy/rune-operator -c vault-agent

 
# Verify the projected secret volume is populated.

kubectl exec -n <namespace> deploy/rune-operator -c manager -- cat /vault/secrets/token
```
