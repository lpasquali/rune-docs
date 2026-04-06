 
# Issue Labels

Unified label taxonomy applied across all 7 RUNE repositories. Labels are organized into namespaced groups. Every repo gets the full set — unused labels in a given repo are harmless and ensure consistency when issues move or reference cross-repo work.

 
## Type Labels

Categorize what kind of work the issue represents.

| Label | Color | Description |
|---|---|---|
| `type/bug` | `#d73a4a` | Something isn't working |
| `type/enhancement` | `#a2eeef` | New feature or improvement |
| `type/epic` | `#5319e7` | Parent issue tracking a body of work |
| `type/refactor` | `#d4c5f9` | Code restructuring with no behavior change |
| `type/documentation` | `#0075ca` | Documentation only |
| `type/question` | `#d876e3` | Needs clarification or discussion before work |

 
## Area Labels

Identify which part of the system is affected.

| Label | Color | Description |
|---|---|---|
| `area/core` | `#1d76db` | Core platform logic (orchestration, workflows, backends) |
| `area/api` | `#1d76db` | HTTP API, contracts, versioning |
| `area/agents` | `#1d76db` | Agent runners, drivers, DriverTransport |
| `area/ci-cd` | `#1d76db` | CI pipelines, quality gates, GitHub Actions |
| `area/helm` | `#1d76db` | Helm charts, Kubernetes deployment |
| `area/operator` | `#1d76db` | Kubernetes operator, CRDs, reconciler |
| `area/ui` | `#1d76db` | HTMX frontend |
| `area/docs` | `#1d76db` | Documentation content and site |
| `area/security` | `#1d76db` | Security scanning, vulnerability management, VEX |
| `area/compliance` | `#1d76db` | IEC 62443, SLSA, ML4, audit evidence |
| `area/infra` | `#1d76db` | Infrastructure, golden image, workstation, airgapped |
| `area/observability` | `#1d76db` | Metrics, logging, tracing |

 
## Priority Labels

How urgently the issue must be addressed.

| Label | Color | Description |
|---|---|---|
| `priority/p0` | `#b60205` | Critical — blocks release or creates security exposure |
| `priority/p1` | `#d93f0b` | High — must be resolved in current milestone |
| `priority/p2` | `#fbca04` | Medium — planned work, not time-sensitive |
| `priority/p3` | `#0e8a16` | Low — nice to have, backlog |

 
## Status Labels

Track workflow state for issues that need cross-functional input.

| Label | Color | Description |
|---|---|---|
| `status/blocked` | `#b60205` | Cannot proceed — dependency or decision needed |
| `status/needs-triage` | `#e4e669` | Awaiting initial assessment |
| `status/needs-legal` | `#f9d0c4` | Requires legal/licensing review before technical work can proceed |
| `status/needs-security` | `#f9d0c4` | Requires security specialist review |
| `status/needs-refinement` | `#f9d0c4` | Issue exists but needs details before an agent or human can implement |

 
## Special Labels

Project-specific labels referenced in policies.

| Label | Color | Description |
|---|---|---|
| `dep-security-patch` | `#b60205` | Fork-and-patch of a dependency to remediate a CVE (referenced in vulnerability policy) |
| `blocker` | `#b60205` | Blocks other work — link the blocked issue |
| `dependencies` | `#0366d6` | Dependency updates (Dependabot, manual bumps) |
| `testing` | `#bfd4f2` | Test infrastructure, coverage config, test fixtures |
| `good first issue` | `#7057ff` | Suitable for new contributors |
| `help wanted` | `#008672` | Community contributions welcome |

 
## Retired Labels

These labels existed on some repos but are superseded by the namespaced taxonomy above. They will be removed during sync.

| Old label | Replaced by |
|---|---|
| `bug` | `type/bug` |
| `enhancement` | `type/enhancement` |
| `epic` | `type/epic` |
| `documentation` | `type/documentation` |
| `question` | `type/question` |
| `compliance` | `area/compliance` |
| `security` | `area/security` |
| `core` | `area/core` |
| `driver` | `area/agents` |
| `python` | (removed — language is implicit from the repo) |
| `ci` | `area/ci-cd` |
| `invalid` | (removed — close the issue instead) |
| `duplicate` | (removed — close as duplicate with a link) |
| `wontfix` | (removed — close with explanation) |
| `area/scaffolding` | `area/infra` |
| `area/bootstrap` | `area/infra` |
| `area/bundling` | `area/infra` |
| `area/network` | `area/infra` |
| `area/registry` | `area/infra` |
| `area/research` | `area/core` |
| `area/integration` | `area/agents` |

 
## Label Workflow

### Legal/Licensing Issues

When a legal or licensing concern is identified (by an agent, human, or audit):

1. Create the issue with `status/needs-legal` + the relevant `area/*` label.
2. A legal specialist (human or specialized agent) reviews and adds findings to the issue.
3. Once the legal review is complete, the specialist replaces `status/needs-legal` with `status/needs-refinement` if technical work is needed, or closes the issue if no action is required.
4. A technician agent or human picks up `status/needs-refinement` issues, refines the implementation plan, and removes the status label when work begins.

### Security Issues

Same flow as legal, but using `status/needs-security`. Issues identified by the cybersecurity auditor or vulnerability scanners start here.

### dep-security-patch Workflow

Per the [Vulnerability Management Policy](VEX.md): when an unfixable CVE above the CVSS 8.8 threshold is discovered, create an issue with the `dep-security-patch` label. The issue tracks the fork-and-patch of the affected dependency.
