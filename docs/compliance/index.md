# Compliance Posture

Compliance-officer-oriented landing for RUNE. This section is a **hub** — the detailed evidence lives under [Security](../security/SDL.md), [Delivery VEX](../delivery/VEX.md), and [Audit Agents](../delivery/AUDIT_AGENTS.md). Come here for the one-page view; follow the links for the work underneath.

!!! warning "Pre-alpha, not certified"
    RUNE is at `v0.0.0a5` (pre-alpha). **Nothing on these pages is a
    certification.** We document which controls are met today and which
    are gaps; no external conformance body has issued an attestation.
    Applicability statements are honest: "Not certified; here is what is
    met; here are the gaps."

## What you'll find here

| Page | What it covers |
|---|---|
| **[Matrix](MATRIX.md)** | ML4 / IEC 62443-4-1 control status, SLSA level per repo, VEX summary, FedRAMP / SOC 2 / ISO 27001 / HIPAA applicability statements, dependency-scanner cadence. |

## How to escalate

- **Audit questions** (request for evidence, control walkthrough): open a GitHub issue with `priority/p1` + `area/compliance` labels in `rune-docs`, or contact the maintainer directly.
- **CVE / security disclosure**: **do not** use public issues. See [SECURITY.md](https://github.com/lpasquali/rune-docs/blob/main/SECURITY.md).
- **License concerns** (dependency licensing, redistribution): `legal check:dep` workflow triggers in the repo where the change lands; see [Audit Agents](../delivery/AUDIT_AGENTS.md).

## Reading order

1. **[Matrix](MATRIX.md)** — 2-minute overview.
2. **[SDL](../security/SDL.md)** — SDL/SM/SVV/DM/SUM detail.
3. **[VEX Register](../delivery/VEX.md)** — per-CVE exploitability statements.
4. **[Audit Agents](../delivery/AUDIT_AGENTS.md)** — when legal/cyber checks run in CI.
