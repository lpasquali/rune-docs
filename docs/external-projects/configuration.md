# Configuration reference

## Project file: `.rune-audit-project.yaml`

The on-disk schema is defined in **rune-audit** as `AuditProjectFile` in `rune_audit.sr2.project_config` (Pydantic). It describes **which repositories** belong to a logical project for future multi-repo scans.

### Schema (v1)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `version` | int | yes | Must be `1` today. |
| `name` | string | no | Human label (default `unnamed-project`). |
| `repos` | list | no | Named repos to include. |

Each **repo** entry:

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Short id (e.g. `app`). |
| `path` | string | Relative path from the project file (often `.`). |
| `url` | string | Optional remote URL (metadata). |

### Example

```yaml
# rune-audit external project definition (SR-2 / EPIC #227)
version: 1
name: my-oss-project
repos:
  - name: app
    path: .
```

### CLI

- **Generate**: `rune-audit sr2 init [-o path]`
- **Validate**: `rune-audit sr2 config-validate .rune-audit-project.yaml`

## Environment variables

rune-audit historically uses the **`RUNE_AUDIT_*`** prefix for service configuration. For SR-2 CLI-only usage you typically need no extra env vars beyond Python/PATH.

See rune-audit `README` and `rune_audit` package for collector-specific variables when you enable non-SR2 commands.

## Related documentation

- [Quickstart](quickstart.md)
- [CI integration](ci-integration.md)
