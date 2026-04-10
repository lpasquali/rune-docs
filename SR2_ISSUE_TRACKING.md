# SR-2 Compliance Automation - Issue Tracking

**Created**: 2026-04-10  
**Status**: All issues created, work can begin

This document provides a complete index of all EPICs and issues created for SR-2 (Security Requirements Specification) compliance automation and generic OSS abstraction.

---

## Epic Overview

### EPIC #207: SR-2 Compliance Automation Infrastructure
**Priority**: P1  
**URL**: https://github.com/lpasquali/rune-docs/issues/207

Automated testing and inspection infrastructure for all 36 IEC 62443-4-1 ML4 quantitative security requirements with CI enforcement and compliance dashboard.

**Child Issues**: #210, #211, #212, #214, #215, #216, #217

### EPIC #208: Generic OSS Abstraction Layer
**Priority**: P2  
**URL**: https://github.com/lpasquali/rune-docs/issues/208

Transform rune-audit into a generic compliance tool usable by any OSS project needing IEC 62443 / SLSA / CIS compliance verification.

**Child Issues**: #227, #228, #229, #230, #231, #232

### EPIC #209: Missing Security Requirements Implementation
**Priority**: P0 (P0 issues block beta)  
**URL**: https://github.com/lpasquali/rune-docs/issues/209

Implement 9 security requirements currently marked "TO IMPLEMENT" to achieve 100% SR-2 compliance.

**Child Issues**: #218, #219, #220, #221, #222, #223, #224, #225, #226

---

## Issue Details

### EPIC 1 Child Issues (SR-2 Automation Infrastructure)

| # | Title | Priority | Area | Status |
|---|---|---|---|---|
| #210 | Create SR-2 Core Module and Data Models | P1 | compliance | Open |
| #211 | Implement 36 Requirement Inspectors | P1 | compliance | Open |
| #212 | Build Compliance Dashboard Generator | P1 | compliance | Open |
| #214 | Add CLI Commands for SR-2 Verification | P1 | compliance | Open |
| #215 | Create Test Suite with XFAIL Markers | P2 | compliance, testing | Open |
| #216 | Create Reusable CI Workflow in rune-ci | P1 | ci-cd | Open |
| #217 | Integrate SR-2 Gates into All 8 Repos | P1 | ci-cd | Open |

### EPIC 3 Child Issues (Missing Security Features)

#### P0 Issues (Blocks Beta)

| # | Title | Priority | Area | Requirement | Status |
|---|---|---|---|---|---|
| #218 | SR-Q-004: Request Body Size Limit | P0 | security | 10 MiB max | Open |
| #219 | SR-Q-005: Request Rate Limiting | P0 | security | 100 req/min per IP | Open |
| #220 | SR-Q-016: Password/Secret Minimum Length | P0 | security | 32 chars min | Open |
| #221 | SR-Q-024: Structured Audit Logging | P0 | security | JSON format | Open |

#### P1 Issues (Operational Security)

| # | Title | Priority | Area | Requirement | Status |
|---|---|---|---|---|---|
| #222 | SR-Q-008: HTTP Server Request Timeout | P1 | security | 30s timeout | Open |
| #223 | SR-Q-011: Driver Invocation Timeout | P1 | security | 180s timeout | Open |
| #224 | SR-Q-023: Audit Log Retention Policy | P1 | security | 90 days | Open |
| #225 | SR-Q-035: String Length Limits | P1 | security | Pydantic max_length | Open |

#### P2 Issues (Defense in Depth)

| # | Title | Priority | Area | Requirement | Status |
|---|---|---|---|---|---|
| #226 | SR-Q-036: Thread Pool Monitoring | P2 | observability | Load testing | Open |

### EPIC 2 Child Issues (Generic OSS Abstraction)

| # | Title | Priority | Area | Status |
|---|---|---|---|---|
| #227 | Config-Driven Project Definitions | P2 | compliance | Open |
| #228 | Pluggable Inspector Registry System | P2 | compliance | Open |
| #229 | Standard Requirement Pack Templates | P2 | compliance, docs | Open |
| #230 | Standard Inspector Library | P2 | compliance | Open |
| #231 | Generic CLI with Project Init | P2 | compliance | Open |
| #232 | Documentation for External OSS Projects | P2 | docs, compliance | Open |

---

## Implementation Order

As specified in the plan, work should proceed in this order:

1. **EPIC 1 (P1)** - SR-2 Automation Infrastructure
   - Core foundation for all compliance automation
   - Issues #210-#217
   
2. **EPIC 3 P0 Issues** - Security Critical Features (Blocks Beta)
   - Must be completed for m4 (first beta)
   - Issues #218-#221
   
3. **EPIC 3 P1 Issues** - Operational Security
   - High priority, must complete in current milestone
   - Issues #222-#225
   
4. **EPIC 2 (P2)** - Generic OSS Abstraction
   - Post-beta enhancement
   - Issues #227-#232
   
5. **EPIC 3 P2 Issue** - Thread Monitoring
   - Can defer to post-beta
   - Issue #226

---

## Statistics

- **Total EPICs**: 3
- **Total Issues**: 22
- **By Priority**:
  - P0: 4 issues (blocks beta release)
  - P1: 11 issues (must complete in milestone)
  - P2: 7 issues (post-beta enhancements)
  
- **By Repository**:
  - rune-audit: 13 issues (automation + abstraction)
  - rune: 7 issues (security features)
  - rune-operator: 2 issues (validation, limits)
  - rune-ci: 1 issue (workflow)
  - rune-charts: 1 issue (log retention)
  - rune-docs: 3 EPICs (coordination)

---

## Related Documentation

- **Quantitative Requirements**: `rune-docs/docs/architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md`
- **ML4 Evidence Report**: `IEC_62443_ML4_EVIDENCE_REPORT.md` (updated with SR-2 references)
- **Issue Templates**: `rune-docs/.github/ISSUE_TEMPLATE/`
  - `epic.yml` - Used for all 3 EPICs
  - `feature.yml` - Used for all 22 child issues

---

## Progress Tracking

To track progress on these epics:

```bash
# View all SR-2 related issues
gh issue list -R lpasquali/rune-docs --label area/compliance

# View specific EPIC
gh issue view 207 -R lpasquali/rune-docs  # EPIC 1
gh issue view 208 -R lpasquali/rune-docs  # EPIC 2
gh issue view 209 -R lpasquali/rune-docs  # EPIC 3

# View child issues
gh issue list -R lpasquali/rune-docs --search "in:body #207"  # EPIC 1 children
```

---

**Document Owner**: lpasquali  
**Last Updated**: 2026-04-10  
**Next Review**: When EPICs are completed
