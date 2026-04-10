# Case study: RUNE program usage

RUNE itself is a **multi-repo program** (`rune`, `rune-ui`, `rune-operator`, `rune-charts`, `rune-docs`, `rune-audit`, `rune-airgapped`, `rune-ci`). The same **SR-2 quantitative model** applies both **inside** RUNE and to **external** OSS adopters.

## Documentation

- **Normative SR-Q text**: **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)** (this site).
- **Operational audit agents** (legal/cyber narrative checks): **[Audit Agents](../delivery/AUDIT_AGENTS.md)**.
- **Machine catalog**: implemented in **rune-audit** `rune_audit.sr2.catalog`.

## Engineering workflow

1. **rune-audit** ships the **`sr2`** Typer group (`verify`, `init`, `gaps`, `dashboard`, `config-validate`).
2. **rune-ci** exposes **`sr2-compliance.yml`** so every consumer repo can call one workflow.
3. **rune-docs** (this section) documents adoption for third parties; **rune-audit** keeps a one-page **[OSS_PROJECTS](https://github.com/lpasquali/rune-audit/blob/main/docs/OSS_PROJECTS.md)** pointer.

## Stub phase transparency

During early rollout, most inspectors return **`not_implemented`**. RUNE uses **non-strict** verification in informational jobs and reserves **strict** gates for repositories that have committed to full automation coverage.

## Related epics

- **rune-docs#208** — Generic OSS abstraction layer (parent of **#232**).
- **rune-audit** issues **#211+** — concrete inspector implementations.
