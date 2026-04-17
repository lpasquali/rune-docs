# rune-airgapped quickstart

Build an offline bundle on a connected build host, transfer it, install into a disconnected cluster.

## Prerequisites

### Build host (connected)

- `bash`, `docker`, `syft`, `cosign`, `helm`.
- Network access to pull source images from `ghcr.io/lpasquali/*`.

### Target host (disconnected)

- Kubernetes ≥ 1.27, `kubectl` + `helm` + `kind` or equivalent.
- An internal OCI registry reachable from pods (can be a local `zot` or `crane registry serve`).

## Build the bundle

```bash
git clone https://github.com/lpasquali/rune-airgapped.git
cd rune-airgapped

scripts/build-bundle.sh \
  --output ./bundle \
  --version v0.0.0a5

# Outputs:
#   bundle/images/      — docker-saved OCI layouts
#   bundle/sboms/       — syft-generated SBOMs per image
#   bundle/charts/      — Helm charts tarballs
#   bundle/manifests/   — PSA + NetworkPolicies + Helmfile
#   bundle/manifest.json
#   bundle/SHA256SUMS
#   bundle/vex/         — VEX register snapshot
#   bundle/keys/        — cosign trusted public keys
```

## Transfer

Physically transfer `bundle/` to the target network (USB, network transfer across an air-gap diode, etc.). **Verify** integrity on the other side:

```bash
sha256sum --check SHA256SUMS
```

## Install (target host)

```bash
cd bundle

# 1. Verify all signatures against the shipped trusted keys (offline)
scripts/verify.sh --keys ./keys

# 2. Load images into your internal registry
scripts/load-images.sh --registry internal-registry.example:5000

# 3. Bootstrap the cluster namespaces + RBAC + NetworkPolicies
scripts/bootstrap.sh --kubeconfig /path/to/kubeconfig

# 4. Render Helm via Helmfile (all charts use internal-registry.example)
scripts/deploy.sh

# 5. Post-install checks
kubectl -n rune get pods
```

## Bundle manifest

`manifest.json` is the ground truth for what's in the bundle — image list with SHA256 digests, chart versions, SLSA attestation locations, VEX version, build environment metadata. Do not bypass this manifest; downstream audit tooling (e.g., `rune-audit`) reads it directly.

## TLS

```bash
scripts/generate-certs.sh \
  --out ./tls \
  --sans rune-api.rune.svc,rune-ui.rune.svc,rune-docs.rune.svc
```

Generated CA + leaf certs for intra-cluster TLS. `--sans` must cover every service DNS name.

## Updating

There is no online update path. To take a new release:

1. On the connected build host, rebuild with the new version tag.
2. Physically transfer.
3. Re-run verify + load-images + deploy — Helm handles the upgrade path via standard `helm upgrade`.

## Next

- **[rune-airgapped repo](https://github.com/lpasquali/rune-airgapped)** for bundle layout detail.
- **[Compliance matrix](../../compliance/MATRIX.md)** — air-gapped installs are the path for most regulated-industry scenarios.
- **[SCENARIOS §Air-gapped](../../usage/SCENARIOS.md)** — decision row.
