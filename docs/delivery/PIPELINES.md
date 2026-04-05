 
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

 
## Merge Protection

Branch protection is enforced on `main`:
- Require status checks to pass before merging.
- `Merge Gate` is a required status check.
- Fixable vulnerabilities with CVSS > 8.8 block the merge.

### Single-Maintainer ML4 Code Review Exception
To satisfy the IEC 62443-4-1 ML4 requirement for peer review (the "two-person rule") without requiring a second human:

1. **When a Human (`lpsquali`) Authors the Code**:
   - **Compensating Control**: The "second reviewer" is entirely fulfilled by the **RuneGate** automated quality pipelines. If the code deterministically passes all strict Quality Gates (100% coverage target, SAST, SCA, and formal TLA+ specs), the pipeline guarantees structural and security integrity, allowing the human to merge.

2. **When an Agent Authors the Code**:
   - **Compensating Control**: The human maintainer (`lpsquali`) acts as the mandatory "second reviewer." While the pipeline enforces security and test coverage, the human **must** review the PR for business logic, architectural intent, and edge cases before merging. The pipeline *cannot* blindly auto-approve agent-authored code.

- **AI Review Ban**: Generic, non-deterministic AI PR review bots (e.g., Copilot PR reviews) are explicitly **BANNED** from being used as formal compliance evidence, as they cannot provide guaranteed, reproducible security checks.
