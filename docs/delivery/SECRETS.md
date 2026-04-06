 
# SECRETS

Security scanning and credential handling for RUNE.

 
## Credential Protection

- **Secrets Management**: Do not commit secrets or API keys. Use environment variables.
- **Environment Separation**: CI/CD secrets are managed in GitHub Actions Secrets.

 
## Vulnerability Handling

- **Goal**: Close all known vulnerabilities, not just those above the threshold. The CVSS 8.8 gate is a merge blocker, not the target.
- **Threshold**: CVSS > 8.8 blocks merge and release.
- **Remediation (fixable)**: Apply the upstream fix immediately — no exceptions regardless of severity.
- **Remediation (unfixable, above threshold)**: Fork and patch the dependency in-house. Track under `dep-security-patch` issue label. Risk acceptance is **never** permitted above the threshold.
- **Remediation (unfixable, below threshold)**: Risk acceptance permitted with documented justification in the **[VEX Register](VEX.md)**. Re-evaluate on Patch SLA date.
- **Reporting**: Report vulnerabilities to `luca@bucaniere.us`.
- **Patch SLA**: Security vulnerabilities are addressed promptly, usually within 48 hours.

 
## Repository Policy

- Branch protection on `main` and `develop`.
- Mandatory multi-scanner analysis (Grype, Trivy, Bandit).
- Vulnerability threshold enforcement in CI.

 
## Compliance Alignment

RUNE aligns with **IEC 62443-4-1 ML4** and **SLSA Level 3** for secure development lifecycle and artifact integrity.
