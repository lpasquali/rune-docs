# rune-airgapped — OCI bundle tooling

`rune-airgapped` packages the complete RUNE ecosystem (images, charts, manifests, SBOMs, SLSA attestations, cosign signatures) into an **offline-installable OCI bundle**. It's usable standalone whenever you need to ship any Kubernetes application into a network-isolated environment — not just RUNE.

## When to use standalone

- **Defence, regulated manufacturing, TS/SCI** deployments where outbound internet is blocked by policy.
- **Regulated on-prem** (aligning with the [compliance matrix](https://github.com/lpasquali/rune-docs/issues/282)) where every artifact needs a signed SBOM and a Rekor-logged attestation.
- **Edge / disconnected** fleets that periodically sync from an internal mirror rather than upstream.

## What you get

- `build-bundle.sh` — pulls every RUNE image, generates SBOMs via `syft`, verifies cosign signatures, emits `manifest.json` + `SHA256SUMS`. Per `rune-airgapped#15`.
- Bootstrap script — 7 phases: verify bundle integrity → load images into internal registry (crane/zot) → apply PSA restricted manifests (RBAC, NetworkPolicies, ResourceQuotas) → render Helm via Helmfile → verify post-install.
- Self-signed TLS cert generator (`generate-certs.sh`) with SANs for internal services — per `rune-airgapped#16`.
- VEX document integration — every bundle carries the VEX register so air-gapped consumers get the same "known-false-positive CVEs" context as the online install.
- Offline cosign verification — the bundle ships trusted-public-key material; no Rekor call required at install time.

## What you give up vs online install

- **No automatic CVE refresh** — VEX and SBOM are point-in-time snapshots as of bundle build.
- **Bundle rebuild is the sole supply-chain touchpoint** — you must trust the bundle's build environment because nothing is verified online at install time.

## Next

- **[Quickstart](quickstart.md)** — build a bundle and install it into a disconnected cluster.
- **[rune-airgapped repo](https://github.com/lpasquali/rune-airgapped)** — source, manifests, reference bundle manifest.
