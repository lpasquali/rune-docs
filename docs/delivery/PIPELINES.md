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
