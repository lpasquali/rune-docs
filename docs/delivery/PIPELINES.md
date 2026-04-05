 
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
- **Compensating Control**: The "second reviewer" is entirely fulfilled by the **RuneGate** automated quality pipelines. A human maintainer (`lpsquali`) is ALWAYS the author of record. Merging a PR that has deterministically passed all strict Quality Gates (100% coverage target, SAST, SCA, SBOM, and formal TLA+ specs) satisfies the objective peer-review requirement. The pipeline guarantees structural and security integrity.
- **AI Review Ban**: Non-deterministic AI PR review tools (e.g., Copilot PR bots) are explicitly **BANNED** from being used as compliance evidence for code review, as they cannot provide guaranteed, reproducible security checks.
