# Compliance Matrix

!!! warning "Pre-alpha, no external certification"
    This page is a **self-declaration** of the state of controls in the
    RUNE codebase and process. No external conformance body has audited
    any of this. Where we write "Met", we mean: a control is documented,
    implemented, and has evidence in the repo. Where we write "Gap", we
    mean: the control is relevant but not fully met today.

## ML4 / IEC 62443-4-1 — process maturity

[IEC 62443-4-1](https://webstore.iec.ch/publication/33615) *Security for industrial automation and control systems — Part 4-1: Product security development life-cycle requirements*, Maturity Level 4. Nine practice areas map to sections across `docs/security/` and the CI workflow set.

| Practice | Status | Evidence |
|---|---|---|
| SM — Security Management | **Met** | [Security Training Records](../security/SECURITY_TRAINING.md); label-driven ownership fence in [SYSTEM_PROMPT §Ownership](../context/SYSTEM_PROMPT.md#ownership-labels-and-board-mandatory). |
| SDL — Security Development Lifecycle | **Met** | [SDL.md](../security/SDL.md) documents the SDL policy; enforced via PR template + `pr-body-check`. |
| SVV — Security Verification & Validation | **Met** | [Penetration Testing](../security/PENTEST.md), [Fuzz Testing](../security/FUZZ_TESTING.md). CI runs Bandit / gosec / Trivy / Grype / CodeQL on every PR. |
| DM — Defect Management | **Met** | [Incident Response](../security/INCIDENT_RESPONSE.md). CVE handling workflow: [VEX Register](../delivery/VEX.md) + [dep-security-patch](../delivery/LABELS.md) label. |
| SUM — Security Update Management | **Met** | [Rollback Procedures](../operations/ROLLBACK_PROCEDURES.md) covers Helm, image, DB, PyPI, airgapped. Dependency cadence below. |
| SG — Security Guidelines | **Partial** | Deployment security guidance in [WORKSTATION](../operations/WORKSTATION.md), [Vault Integration](../operations/VAULT.md); missing: customer-facing hardening guide (tracked follow-up). |
| Risk Assessment | **Met** | [Risk Assessment Methodology](../security/RISK_ASSESSMENT.md) + [Risk Register](../security/RISK_REGISTER.md) (15 entries). |
| Threat Modeling | **Met** | [Threat Model](../architecture/THREAT_MODEL.md) + [Security Requirements](../architecture/SECURITY_REQUIREMENTS.md). |
| Container Image Signing | **Met** | [Image Signing](../security/IMAGE_SIGNING.md) — cosign via sigstore; release workflow signs all pushed images. |

**Gap note**: these statuses reflect **documentation + implementation completeness**. They are **not** audited conformance; an external 62443-4-1 assessor has never reviewed the repo.

## SLSA — supply-chain provenance

[SLSA](https://slsa.dev) Levels for Software Artifacts. RUNE's release workflow emits SLSA L3-style provenance (signed, non-falsifiable, build-service-generated). Per-repo status:

| Repo | Level | Evidence |
|---|---|---|
| `rune-audit` | **L3 (confirmed)** | [PR #62 release workflow](https://github.com/lpasquali/rune-audit/pull/62) — SBOM + SLSA provenance + PyPI OIDC publishing. Per [CURRENT_STATE 2026-04-07](../context/CURRENT_STATE.md). |
| `rune` | **Measurement pending** | Release workflow present; formal SLSA L3 verification not yet run. |
| `rune-operator` | **Measurement pending** | Same as above. |
| `rune-ui` | **Measurement pending** | Same as above. |
| `rune-charts` | **Measurement pending** | Helm charts sign via cosign; SLSA provenance for charts is a separate workstream. |
| `rune-docs` | **N/A** | Documentation site; no binary artifacts. |
| `rune-airgapped` | **Measurement pending** | Bundle includes SLSA attestations for every packaged image ([CURRENT_STATE 2026-04-07](../context/CURRENT_STATE.md) — "Compliance Artifacts #11"). |

**Gap note**: "Measurement pending" means the workflow infrastructure exists and is expected to pass L3 verification, but a clean-room external verification has not been performed. Treat every non-`rune-audit` entry as unverified until independently measured.

## VEX — per-CVE exploitability

See the authoritative [VEX Register](../delivery/VEX.md). Summary posture:

- All declared VEX statements carry a specific technical justification (not blanket "not affected").
- Three nginx CVE entries currently carry strengthened VEX with specific libxml2 module analysis and `ldd` verification (`rune-docs#34`).
- Per the SYSTEM_PROMPT vulnerability policy: risk acceptance only for CVSS < 8.8 with no fix available. Above threshold with no upstream fix → fork/patch + `dep-security-patch` label.

## Applicability statements

None of these are certifications. Each is a candid read of which controls are already met versus which would require additional work.

### FedRAMP Moderate

**Not certified.** No ATO (Authority to Operate) exists.

- **Controls likely met**: SC-7 (boundary protection), SC-13 (crypto with FIPS-validated modules — needs validation), AC-2 (account management), AU-2 (audit events), CA-7 (continuous monitoring via CI).
- **Gaps**: FedRAMP-specific documentation (SSP, POA&M), 3PAO assessment, specific control tailoring for Moderate baseline, FISMA-aligned incident response procedures.

### SOC 2 Type II

**Not certified.** No auditor engagement.

- **Trust Services Criteria likely met**: Security (CC1-CC9 via SDL + VEX + CI gates), Availability (rollback procedures, runbooks), Processing Integrity (fail-closed cost gates, deterministic benchmark scoring).
- **Gaps**: Formal SOC 2 Type II audit (minimum 6-month observation period), Confidentiality-specific controls beyond Apache-2.0 IP boundaries, Privacy controls (not in-scope today).

### ISO 27001

**Not certified.** No certification body engagement.

- **Annex A controls likely met**: A.5 (information security policies — [SDL](../security/SDL.md)), A.8 (asset management — [Risk Register](../security/RISK_REGISTER.md)), A.12 (operations security — [Runbooks](../operations/RUNBOOKS.md)), A.14 (system acquisition/development — [PR workflow](../context/SYSTEM_PROMPT.md) + CI gates).
- **Gaps**: Statement of Applicability document, internal audit program, management review process, certification audit with accredited body.

### HIPAA

**Not applicable** by default — RUNE doesn't process PHI (Protected Health Information). If a downstream deployment handles PHI, additional controls apply: BAA with subprocessors, audit log retention (6 years), specific encryption-at-rest requirements, breach notification workflows. None of these are pre-configured in RUNE charts today.

## Dependency hygiene

Scanner cadence and outputs:

| Scanner | Scope | Cadence | Evidence |
|---|---|---|---|
| `pip-audit` | Python deps (rune, rune-ui, rune-docs, rune-audit) | Every PR + weekly | `.github/workflows/quality-gates.yml` per repo |
| `govulncheck` | Go deps (rune-operator) | Every PR | `.github/workflows/quality-gates.yml` |
| `grype` | Container images | Every image build | Output in SBOM + CVE job |
| `trivy` | Helm charts (config scan) | `rune-charts` PRs | `trivy config --severity HIGH,CRITICAL` |
| `gitleaks` | Secret scanning | All repos, every PR | Pinned `v8.24.3` |
| `CodeQL` | Static analysis | All Python repos | Standalone workflow per repo |
| `bandit` | Python SAST | rune, rune-ui, rune-audit | `.github/workflows/quality-gates.yml` |
| `gosec` | Go SAST | rune-operator | `gosec -fmt json -severity high ./...` |

**Policy**: a PR that introduces a new CVE is never acceptable. Fix, replace, fork-patch, or escalate to `lpasquali` — see [SYSTEM_PROMPT §Vulnerabilities](../context/SYSTEM_PROMPT.md#core-constraints).

**VEX workflow**: false positives and genuinely-unexploitable CVEs land in [delivery/VEX.md](../delivery/VEX.md) with a specific technical justification. Blanket "not affected" statements are rejected.

## Further reading

- [Security Development Lifecycle](../security/SDL.md) — full SDL policy.
- [Risk Register](../security/RISK_REGISTER.md) — 15 open risks.
- [Container Image Signing](../security/IMAGE_SIGNING.md) — cosign + sigstore detail.
- [Audit Agents](../delivery/AUDIT_AGENTS.md) — `legal check:*` and `cyber check:*` trigger tables.
