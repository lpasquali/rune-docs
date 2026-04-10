# External projects (rune-audit)

Use **[rune-audit](https://github.com/lpasquali/rune-audit)** on **non-RUNE** repositories to run the same **IEC 62443-4-1 ML4 SR-2** quantitative requirement catalog (SR-Q-001 … SR-Q-036) that RUNE tracks internally.

These pages are the **adopter-facing** guide. The short upstream summary lives in the rune-audit repo as [`docs/OSS_PROJECTS.md`](https://github.com/lpasquali/rune-audit/blob/main/docs/OSS_PROJECTS.md).

## In this section

| Page | Purpose |
| --- | --- |
| [Quickstart](quickstart.md) | Install, init project file, first `sr2 verify` |
| [Configuration](configuration.md) | `.rune-audit-project.yaml` schema |
| [Inspector library](inspector-library.md) | Built-in vs stub inspectors, catalog |
| [Custom inspectors](custom-inspectors.md) | `InspectorRegistry` extension |
| [Requirement packs](requirement-packs.md) | Pack ids and SR-Q scope |
| [CI integration](ci-integration.md) | GitHub Actions, GitLab, Jenkins patterns |
| [Case study: RUNE](case-study-rune.md) | How the RUNE program consumes the same model |

## Normative requirements text

Requirement titles and evidence expectations are defined in **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)** (rune-docs). Inspectors map evidence to those SR-Q ids.

## Status

Today many inspectors still return **`not_implemented`** (stub phase). Use `rune-audit sr2 verify` without `--strict` for informational runs; add `--strict` in CI when you are ready to fail on unfinished coverage.
