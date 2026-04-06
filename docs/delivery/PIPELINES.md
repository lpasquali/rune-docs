 
# PIPELINES

CI/CD workflows and automated testing for RUNE.

 
## Automated Testing

### Unit and Integration Tests

Automated tests are designed to run anywhere without creating cloud resources.
They mock Ollama and Vast.ai boundaries.

```bash
pip install -r requirements.txt
python -m pytest -q
```

Coverage is enforced at a minimum of **97%** via pytest configuration.

### Multi-Scanner Quality Gates

Every PR and merge to `main` triggers a set of quality gates:
- **SAST**: Static analysis using `bandit` and `ruff`.
- **SCA**: Dependency scanning using `safety` and `pip-audit`.
- **Container Scanning**: `Grype` and `Trivy` for Docker images.
- **SBOM**: Generation of CycloneDX SBOMs.

 
## Compliance Evidence (ML4)

RUNE aligns with **IEC 62443-4-1 ML4** and **SLSA Level 3**:
- **SLSA L3**: Build provenance attestation using GitHub Attestations.
- **IEC 62443 4-1 ML4 SM-9**: SBOM provenance attestation.
- **IEC 62443 4-1 ML4 SI-1 / SVV-1**: Mandatory SAST gates.

### Target of Evaluation (TOE)
The primary certification boundary for RUNE is **Airgapped Environments**. 
- **In-Scope**: Only Tier 1 (OSS) components that can be securely bundled and executed offline are subject to the strict 100% test coverage mandate and formal verification.
- **Out-of-Scope (Best-Effort)**: Tier 2 and Tier 3 external integrations (SaaS, external APIs, and closed-source artifacts) fall outside the strict formal certification boundary. Coverage and integration tests for these components are maintained on a **best-effort basis**, subject to available funding, API access, and community resources.

 
## Merge Protection

Branch protection is enforced on `main`:
- Require status checks to pass before merging.
- `Merge Gate` is a required status check.
- Fixable vulnerabilities with CVSS > 8.8 block the merge.
- Unfixable vulnerabilities with CVSS > 8.8 **must** be remediated by forking and patching the dependency in-house, tracked under a `dep-security-patch` issue label. Risk acceptance is **never** permitted above the threshold.
- Vulnerabilities below the threshold are targeted for closure. Risk acceptance is permitted only when no upstream fix exists, with documented justification in the [VEX Register](VEX.md).

### Single-Maintainer ML4 Code Review Exception
To satisfy the IEC 62443-4-1 ML4 requirement for peer review (the "two-person rule") without requiring a second human:
- **Compensating Control**: The "second reviewer" is entirely fulfilled by the **RuneGate** automated quality pipelines. A human maintainer (`lpsquali`) is ALWAYS the author of record. Merging a PR that has deterministically passed all strict Quality Gates (100% coverage target, SAST, SCA, SBOM, and formal TLA+ specs) satisfies the objective peer-review requirement. The pipeline guarantees structural and security integrity.
- **AI Review Ban**: Non-deterministic AI PR review tools (e.g., Copilot PR bots) are explicitly **BANNED** from being used as compliance evidence for code review, as they cannot provide guaranteed, reproducible security checks.
