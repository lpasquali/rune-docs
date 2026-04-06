 
# Milestones

 
## What is a Milestone

A milestone is a named delivery gate that groups related issues and PRs toward a measurable project goal. Milestones are time-boxed or scope-boxed and represent a coherent increment of platform capability.

 
## Milestone Structure

Each milestone must define:

| Field | Description |
|---|---|
| **Name** | Short identifier (e.g., `m0-bootstrap`, `m1-core-backends`) |
| **Goal** | One-sentence description of what "done" means |
| **Scope** | List of repos and components affected |
| **Entry criteria** | Prerequisites from prior milestones or external dependencies |
| **Exit criteria** | Concrete, testable conditions that close the milestone |
| **DoD compliance** | All PRs within the milestone must satisfy the Definition of Done (docker-compose, kind, standalone CLI validation + breaking change audit) |

 
## Milestone and Documentation Channels

Development work flows through two parallel channels:

- **Feature milestones** — time-boxed or scope-boxed delivery gates for platform capability.
- **Documentation expedite channel** — docs PRs run independently of milestones and are never gated by them (see [SYSTEM_PROMPT.md](../context/SYSTEM_PROMPT.md)).

Both channels share the same CI quality gates. Feature milestones reference docs but do not block them.

 
## Epics as Swim Lanes

RUNE does not use a traditional agile board with swim lanes. Instead, **epics serve as swim lanes** — each epic represents a parallel stream of work that can be tracked, prioritized, and staffed independently.

### Every issue must belong to an epic

No orphan issues. This is enforced by the issue templates: the "Parent Epic" field is required. If no epic exists for the work you're about to do, create the epic first.

This gives us:

| Agile concept | RUNE equivalent |
|---|---|
| Swim lane | Epic (`type/epic` label) |
| Story / task | Issue (bug, feature, or other type) |
| Sprint | Milestone (time-boxed or scope-boxed) |
| Board | GitHub Issues filtered by epic |
| Progress | Epic checklist (checked child issues / total) |

### Epic hierarchy

```
Milestone (m1-core-backends)
├── Epic: Agent Driver Framework (#54)
│   ├── Issue: driver: HolmesGPT (#60)
│   ├── Issue: driver: K8sGPT (#61)
│   └── Issue: driver: Cleric (#62) [blocked]
├── Epic: ML4 Compliance Tooling (#121)
│   ├── Issue: Strict .coveragerc (#123)
│   ├── Issue: Remove security gate bypasses (#122)
│   └── Issue: SAST exclusions (#125)
└── Epic: Operator Feature Parity (#31)
    └── Issue: ADR 0004 implementation
```

### Cross-repo epics

An epic can span multiple repos. The epic lives in whichever repo owns the primary work stream. Child issues in other repos link back to the epic with a cross-repo reference (e.g., `lpasquali/rune-docs#20`).

### Viewing progress

Filter issues by epic to see a swim lane's progress:

```bash
# All open issues in epic #121
gh issue list -R lpasquali/rune --label type/epic --search "in:body #121"

# Or simply open the epic issue — the checklist shows progress
gh issue view 121 -R lpasquali/rune
```

 
## Release Roadmap

| Milestone | Target | Significance |
|---|---|---|
| **m4** | First beta | Feature-complete enough for external testers. Not production-ready. |
| **m10+** | First stable release | Production-ready, fully compliant and prepared for certification (IEC 62443 ML4, SLSA L3). |

Agents and developers must not assume a stable release is imminent. Current version is `0.0.0a2`. The path to stable is long and intentional — compliance, security, and quality gates will not be rushed.

**Stability decisions require approval from both the copyright owner and project maintainers.** No agent or automated process may promote a release to beta or stable. Agents may recommend readiness based on exit criteria, but the decision to cut a beta or declare stability is a human judgment call — made by maintainer consensus with the copyright owner holding final authority.

 
## Milestone Lifecycle

1. **Proposed** — Goal and scope drafted; not yet committed.
2. **Active** — Work is in progress; issues and PRs are tagged.
3. **Blocked** — External dependency or decision needed; document the blocker.
4. **Closed** — All exit criteria met; `CURRENT_STATE.md` updated.

 
## Documentation Channel

Documentation changes run on a **parallel expedited channel** independent of feature milestones. See [SYSTEM_PROMPT.md — Documentation Expedite Channel](../context/SYSTEM_PROMPT.md) for the policy.

Rationale: `rune-docs` is the single source of truth for all agents. Blocking docs behind feature milestones means agents operate on stale information, which compounds errors across the entire platform.
