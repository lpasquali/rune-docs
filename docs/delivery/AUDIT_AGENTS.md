 
# Audit Agents

Detailed specifications for the legal and cybersecurity audit agents. Agents are triggered per the rules in [SYSTEM_PROMPT.md](../context/SYSTEM_PROMPT.md) and run as background tasks.

 
## Full Audit: `legal check`

Runs a comprehensive OSS licensing and legal compliance audit across all 7 repositories. The agent acts as a lawyer specializing in open-source licensing for technology companies.

**Scope:**
- License compatibility between Apache-2.0 and all dependencies (direct and transitive)
- GPL/AGPL/LGPL contamination risks (imports, bundling, distribution)
- BSL-licensed build tools — classification as build-time only vs. bundled
- NOTICE file obligations and copyright attribution
- VEX statement legal soundness
- No-bundling policy enforcement across all docs and Dockerfiles
- Patent clause implications (Apache-2.0 Section 3)
- Helm Chart.yaml and pyproject.toml license metadata
- SPDX identifier compliance
- Export control considerations for cryptographic components

**What to read:** All LICENSE and NOTICE files, dependency manifests (pyproject.toml, go.mod, requirements.txt), chains.csv Ecosystem column, CI workflows (license gates), VEX files, GOLDEN_IMAGE.md, all Dockerfiles, SECURITY.md, CODING_STANDARDS.md (no-bundling policy).

**Report severity levels:**
1. **CRITICAL** — could force license change, create legal liability, or block distribution
2. **HIGH** — violates stated policy or creates contamination risk
3. **MEDIUM** — missing attributions, unclear boundaries, documentation gaps
4. **LOW** — best practice recommendations

**Issue creation:** For each finding, open a GitHub issue in the affected repo with:
- Title: `[Legal] <short description>`
- Labels: `status/needs-legal` + `area/compliance` + appropriate `priority/*` (CRITICAL → `priority/p0`, HIGH → `priority/p1`, MEDIUM → `priority/p2`, LOW → `priority/p3`)
- Body: finding detail, evidence (file path + line), risk, and recommended remediation
- **Legal findings with license contamination risk are always `priority/p0`** regardless of other severity factors

 
## Focused Legal Checks

### `legal check:dep <package>`

Triggered when a dependency is added or bumped. Focused on a single package and its transitive tree.

**Scope:**
- Run `pip-licenses` or `go-licenses` for the specific package and its transitive dependencies
- Check each transitive dep against the blocked license list (GPL-2.0, GPL-3.0, AGPL-3.0 and their -or-later variants)
- Check for LGPL (warning tier — requires careful handling in Python packaging)
- Verify the package is declared in the appropriate manifest (not just installed in Dockerfile)
- If the package is a container base image, check all packages inside it

**Report:** PASS or FAIL. If FAIL, the agent **must not open the PR** and must report to `lpasquali`.

### `legal check:integration <agent>`

Triggered when a new agent, driver, or external tool integration is added.

**Scope:**
- Verify the agent's upstream license from its repository/website
- Check that the integration uses DriverTransport (network API only) — no imports, no bundling
- Verify the agent is classified in the correct tier in `chains.csv`
- Check that the Dockerfile does not bundle or `pip install` the agent
- If the agent is GPL/AGPL: confirm REST-only integration, add contamination warning comment to the driver file

**Report:** PASS or FAIL with specific contamination vector.

### `legal check:tool <tool>`

Triggered when a new build-time or CI tool is introduced.

**Scope:**
- Identify the tool's license (OSI-approved? BSL? Proprietary?)
- Classify: build-time only (not distributed) vs. bundled in artifacts
- If BSL or proprietary: verify it is not redistributed in any image or artifact
- Verify the tool is documented in WORKSTATION.md or GOLDEN_IMAGE.md with its license noted

**Report:** PASS (build-time only, license documented) or FAIL (bundling risk or undocumented).

 
## Full Audit: `cyber check`

Runs a comprehensive cybersecurity compliance audit against IEC 62443-4-1 ML4 and SLSA Level 3. The agent acts as a CISO consultant for critical infrastructure.

**Scope:**
- IEC 62443-4-1 practice areas: SM (Security Management), SR (Security Requirements), SD (Secure by Design), SI (Secure Implementation), SVV (Security Verification & Validation), DM (Defect Management), SUM (Security Update Management)
- SLSA Level 3: source integrity, build integrity, provenance, verification
- Supply chain security: SBOM, dependency pinning, container signing
- Incident response: disclosure, response plan, communication, recovery
- Access control: branch protection, secrets management, API auth
- Compensating controls: solo-developer peer review exception assessment
- Risk assessment: methodology, threat models, residual risk tracking

**What to read:** All docs in `rune-docs/docs/`, SECURITY.md, VEX files, CI workflows (`quality-gates.yml`), API_SPEC.md, all ADRs, FORMAL_SPECS.md.

**Report severity levels:**
1. **NON-CONFORMANCE** — requirement not met for claimed compliance level
2. **OBSERVATION** — meets minimum but has weaknesses
3. **OPPORTUNITY FOR IMPROVEMENT** — best practice enhancement
4. **CONFORMANCE** — properly handled (document for audit evidence)

**Issue creation:** For each NON-CONFORMANCE and OBSERVATION, open a GitHub issue in `rune-docs` (for policy/documentation gaps) or the affected repo (for implementation gaps) with:
- Title: `[Security] <IEC/SLSA reference>: <short description>`
- Labels: `status/needs-security` + `area/security` or `area/compliance` + appropriate `priority/*` (NON-CONFORMANCE → `priority/p0` or `priority/p1`, OBSERVATION → `priority/p2`)
- Body: IEC/SLSA reference, finding, evidence (file + line), risk, and recommended remediation

 
## Focused Cyber Checks

### `cyber check:dep <package>`

Triggered alongside `legal check:dep` when a dependency changes.

**Scope:**
- Run `pip-audit`, `safety`, or `govulncheck` against the updated dependency set
- Check if the new/bumped package introduces any known CVE
- Check if the new version drops support for any security fix present in the old version
- Verify the dependency is pinned appropriately (not floating on `>=` for security-critical packages)

**Report:** PASS or FAIL. If FAIL, the agent **must not open the PR** — resolve or report per the vulnerability management policy.

### `cyber check:api`

Triggered when API endpoints, auth mechanisms, Helm values, or CRD schemas change.

**Scope:**
- Review authentication changes: are tokens still hashed? Is auth bypass (`RUNE_API_AUTH_DISABLED`) confined to dev mode?
- Review authorization changes: is tenant scoping preserved? Is RBAC for HolmesGPT still read-only?
- Review schema changes: are new fields additive (backward compatible) or breaking?
- Check for OWASP API Top 10 risks in the change (injection, broken auth, excessive data exposure)

**Report:** Findings per OWASP/IEC reference with severity.

### `cyber check:supply-chain`

Triggered when CI workflows, Dockerfiles, or build infrastructure change.

**Scope:**
- Verify SLSA provenance chain is intact (attestation still runs, covers image digest)
- Check GitHub Actions are pinned by SHA (not just major version)
- Verify SBOM generation still runs on the modified pipeline
- Check for new secret access patterns or permission escalations in workflows
- Verify Gitleaks still scans the modified paths
- If Dockerfile changed: verify multi-stage build still isolates build tools from runtime

**Report:** SLSA L3 conformance status per requirement.

### `cyber check:vex`

Triggered when VEX statements are added or modified.

**Scope:**
- Verify each VEX justification is technically defensible (not generic "unused component" for active components)
- Check that `not_affected` status is supported by specific technical evidence (module not compiled, feature not enabled, code path not reachable)
- Verify affected packages match actual image contents
- Cross-reference CVSS scores against the project's threshold policy

**Report:** Per-statement assessment — DEFENSIBLE or NEEDS REVISION with specific technical gap.
