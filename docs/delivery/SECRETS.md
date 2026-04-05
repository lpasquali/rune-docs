 
# SECRETS

Security scanning and credential handling for RUNE.

 
## Credential Protection

- **Secrets Management**: Do not commit secrets or API keys. Use environment variables.
- **Environment Separation**: CI/CD secrets are managed in GitHub Actions Secrets.

 
## Vulnerability Handling

- **Threshold**: CVSS > 8.8 (Critical) blocks merge and release.
- **Reporting**: Report vulnerabilities to `luca@bucaniere.us`.
- **Patch SLA**: Security vulnerabilities are addressed promptly, usually within 48 hours.
- **Exceptions**: Unfixable vulnerabilities are tracked in the **[VEX Register](VEX.md)**.

 
## Repository Policy

- Branch protection on `main` and `develop`.
- Mandatory multi-scanner analysis (Grype, Trivy, Bandit).
- Vulnerability threshold enforcement in CI.

 
## Compliance Alignment

RUNE aligns with **IEC 62443-4-1 ML4** and **SLSA Level 3** for secure development lifecycle and artifact integrity.
