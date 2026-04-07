## Summary

Configure MkDocs to show all documentation for all released versions and protected/active branches using `mike`. The `pages.yml` workflow has been updated to trigger on branch pushes and tag pushes, cleaning up any stale branches from the `gh-pages` deployment before deploying the current version. 

Additionally, this PR fully airgaps the `rune-docs` MkDocs deployment by disabling remote Google Fonts and serving them locally alongside the required `htmx.min.js` script. It also unifies the theme between `rune-docs` and `rune-ui` by applying the exact same Solarized CSS aesthetic and porting over the full 7-mode theme switcher logic.

Closes #87

## DoD Level

- [ ] **Level 1 — Full Validation** (runtime, API, Helm, Dockerfile)
- [ ] **Level 2 — Test Infrastructure** (test config, CI, coverage, linter)
- [x] **Level 3 — Documentation** (Markdown, MkDocs, diagrams)

## Level 1 Checklist

- [ ] Tested in **docker-compose mode**
- [ ] Tested in **kind (Kubernetes) mode**
- [ ] Tested in **standalone CLI mode**
- [ ] **Breaking change audit**: API versions, persistent data, cross-component contracts
- [ ] **Dependency CVE audit** (if deps changed): `pip-audit` / `govulncheck` / `grype` — no new CVEs

## Level 2 Checklist

- [ ] Full test suite passes
- [ ] Coverage not degraded (at or above floor)
- [ ] No unintended CI side effects

## Level 3 Checklist

- [x] `mkdocs build --strict` passes
- [x] `pymarkdown scan README.md docs` passes

## Audit Checks

| Check | Result | Evidence |
|---|---|---|
| `legal check:dep mike` | PASS | BSD 3-Clause |
| `legal check:dep htmx` | PASS | 0BSD |
| `legal check:dep OpenDyslexic` | PASS | OFL |
| `legal check:dep FiraCode` | PASS | OFL |

## Acceptance Criteria Evidence

- [x] Versioned documentation via `mike` configured — Implemented in `pages.yml` and `mkdocs.yml`
- [x] Stale branches cleaned up before compiling — Bash script implemented in `pages.yml`
- [x] Fully airgapped (`font: false` in mkdocs, local scripts) — Verified in mkdocs config and static folders
- [x] Unified Solarized Theme with 7 modes — Implemented via `theme-overrides.css` and `docs/overrides/main.html`

## Test Plan Evidence

- [x] `mkdocs build --strict` passes

## Breaking Changes

None.

## Notes for Reviewer

The obsolete `deploy-pages.yml` workflow has been deleted to consolidate deployment under `pages.yml`.
