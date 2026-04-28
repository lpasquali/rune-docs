# Security Hardening Guide

This guide details the security controls built into the RUNE air-gapped deployment and how customers can apply their own replaceable security policies to harden the environment further.

## Pod Security Admission (PSA)

RUNE namespaces are labeled to enforce the `restricted` Pod Security Admission (PSA) profile by default. This ensures:
- Containers cannot run as root.
- Containers drop all privileges (`ALL` capabilities).
- The root filesystem is mounted as read-only.
- Privilege escalation is disabled.

### Customer-Replaceable Policies

Customers who use external policy engines (e.g., OPA Gatekeeper, Kyverno, or Kubewarden) can replace or augment the default PSA labels. To do this, provide a custom `values.yaml` file during deployment:

```yaml
global:
  podSecurityLabels:
    enforce: "baseline"  # Or your organization's preferred level
    warn: "baseline"
```

## Network Policies

The bootstrap script applies a default-deny NetworkPolicy across all RUNE namespaces (`rune`, `rune-system`, `rune-registry`). Explicit allow rules are created only for required traffic (e.g., DNS, registry pulling, operator to API communication).

### Extending Network Policies

Customers can inject their own NetworkPolicies to enforce stricter network segmentation (e.g., locking down egress to specific IP blocks for an external PostgreSQL database or S3 endpoint).

1. Place your custom NetworkPolicy manifests in a directory (e.g., `/custom/netpols/`).
2. Apply them post-deployment or integrate them into a GitOps flow.
3. If your CNI requires specific labels for DNS or egress to external endpoints, add them via the Helm values overlay.

## Certificate Management (TLS)

RUNE requires TLS for production deployments. By default, it supports bringing your own Certificates via Kubernetes Secrets.

### Enforcing Strict TLS

1. Ensure `global.tls.enabled: true` is set in your values.
2. Provide your own trusted CA certificates for the in-cluster registry and all services.
3. Use a tool like cert-manager if you need automated certificate rotation within the air-gapped environment.

## RBAC and Service Accounts

RUNE uses dedicated Service Accounts for the API, the UI, and the Operator. The Operator runs with the minimum required privileges to reconcile its Custom Resource Definitions (CRDs).

### Auditing RBAC

Customers should periodically audit the Roles and ClusterRoles applied to RUNE components. You can view the applied permissions:

```bash
kubectl get rolebindings,clusterrolebindings -A | grep rune
```

If your organization requires stricter namespace isolation, ensure the Operator is only granted permissions within the `rune` and `rune-system` namespaces, and adjust the values accordingly.

## VEX and SBOM Validation

RUNE air-gapped bundles include Vulnerability Exploitability eXchange (VEX) documents and Software Bill of Materials (SBOM) for all components.

- **VEX Documents**: Located in the bundle under `/compliance/vex/`.
- **SBOMs**: Located in `/compliance/sbom/`.

Customers can ingest these documents into their internal vulnerability management systems (e.g., Dependency-Track or DefectDojo) to validate the security posture of the RUNE deployment against their organizational policies.
