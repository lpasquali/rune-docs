# Security Training and Competency Records

IEC 62443-4-1 SM-3 requires that all personnel involved in the secure development lifecycle have documented security training and competency verification.

## Training Requirements

### Mandatory Training (All Contributors)

| Topic | Frequency | Verification |
|---|---|---|
| OWASP Top 10 (Web) | Annual | Quiz or certification |
| Secure coding practices (Python, Go) | Annual | Code review participation |
| Supply chain security (SLSA, SBOM, VEX) | Annual | Tooling proficiency demo |
| IEC 62443 awareness | At onboarding + annual | Self-assessment |
| Incident response procedures | Annual | Tabletop exercise participation |

### Role-Specific Training

| Role | Additional Training | Frequency |
|---|---|---|
| Maintainer | Threat modeling (STRIDE), Sigstore/cosign | Annual |
| CI/CD contributor | GitHub Actions security, secret management | Per-change |
| Helm chart author | Kubernetes security (PSA, RBAC, NetworkPolicy) | Annual |

## Current Training Records

### 2025-2026 Pre-Alpha Phase

| Person | Role | Training Completed | Date | Evidence |
|---|---|---|---|---|
| lpasquali | Maintainer, sole developer | OWASP Top 10, IEC 62443 awareness, SLSA L3 tooling, threat modeling (STRIDE), Sigstore/cosign | 2025-2026 (ongoing) | SDL policy authored (SM-1), risk register created (SM-5), SBOM pipeline implemented, container signing implemented |

> **Note:** During the pre-alpha solo-maintainer phase, training is self-directed and evidenced
> by the security artifacts produced. Formal third-party training certifications will be pursued
> as the team grows and the project approaches its first stable release.

## Competency Verification

Competency is verified through:

1. **Code review participation** — security-relevant PRs require review comments demonstrating understanding of the threat model.
2. **Security artifact authorship** — SDL, risk register, VEX documents, incident response plans.
3. **CI/CD pipeline design** — SAST, SCA, SBOM, container signing, and provenance attestation pipelines.
4. **Incident response exercises** — documented tabletop or live exercises.

## Training Gap Remediation

If a training gap is identified (e.g., a new technology is adopted without corresponding training):

1. The gap is logged in the [Risk Register](RISK_REGISTER.md) as a compliance risk.
2. Training is scheduled within 30 days.
3. The risk entry is updated upon completion.

## Renewal Schedule

All training records are reviewed at each milestone exit. Expired training (>12 months) blocks milestone sign-off per SM-3.
