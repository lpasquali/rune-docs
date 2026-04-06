# Security Policy

We take the security of `rune` very seriously.

## Supported Versions

Currently, only the main branch (`master` or `main`) and the latest tagged release are actively supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| v1.x    | :white_check_mark: |
| < v1.0  | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within `rune`, please do **not** open a public issue.

Instead, please send an e-mail to **[luca@bucaniere.us]**.

All security vulnerabilities will be promptly addressed. We will try to get back to you within 48 hours to acknowledge the report and briefly detail how and when we plan to address it.

Once the vulnerability is resolved, a security advisory will be published, and you will be credited for the discovery if you so choose.

## Mandatory Merge Protection

The repository must enforce branch protection on target branches (`main`, `develop`) so pull requests cannot be merged when checks fail.

Required policy:

- Require status checks to pass before merging.
- Mark `Merge Gate` as a required status check.
- Do not allow bypassing required checks for regular contributors.

Security policy gate in CI:

- SBOM is generated and scanned by multiple scanners.
- If any fixable vulnerability has CVSS score > 8.8, CI fails and PR merge is blocked.
- Because `Merge Gate` is required, PR merge is blocked when CVSS > 8.8 is detected.

## Vulnerability Remediation Policy

The project aims to **close all known vulnerabilities**, not just those above the CVSS 8.8 threshold.

| Scenario | Action |
|---|---|
| Upstream fix exists (any severity) | Apply fix immediately — no exceptions |
| No upstream fix, CVSS > 8.8 | Fork and patch the dependency in-house. Track under `dep-security-patch` issue label. Risk acceptance is never permitted above the threshold. |
| No upstream fix, CVSS <= 8.8 | Risk acceptance permitted with documented justification in the [VEX Register](docs/delivery/VEX.md). Re-evaluate on Patch SLA date. |
