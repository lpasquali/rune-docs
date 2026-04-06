 
# VEX Register — Vulnerability Exception Tracking

 
## Vulnerability Management Policy

The project aims to **close all known vulnerabilities**, not just those above the threshold. The CVSS 8.8 gate is a merge blocker, not a goal.

| Severity | Upstream fix exists | Action |
|---|---|---|
| Any | Yes | Fix immediately — no exceptions |
| Above threshold (CVSS > 8.8) | No | **Fork and patch** the dependency in-house. Track under `dep-security-patch` issue label. Never risk-accept above threshold. |
| Below threshold (CVSS <= 8.8) | No | Risk acceptance permitted with documented justification (see entry format below). Re-evaluate on Patch SLA date. |

 
## Exception Entry Format

Each risk-accepted entry requires:
- CVE ID and CVSS score
- Affected package and version
- Justification for acceptance (exploit path not applicable, mitigating control, etc.)
- Patch SLA (target date for re-evaluation)
- Approver

 
## Active exceptions

| CVE ID | CVSS | Package | Justification | Patch SLA | Approver |
|--------|------|---------|---------------|-----------|----------|
| _None_ | — | — | — | — | — |

 
## Closed exceptions

_None._
