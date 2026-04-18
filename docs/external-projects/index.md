# External projects

RUNE ships as **five independently-adoptable components**. You can take any one of them standalone — on a non-RUNE codebase, in a non-RUNE cluster, or as a library in an unrelated application — without running the rest of the RUNE stack.

## Components

| Component | When to adopt standalone | Landing page |
|---|---|---|
| **rune-audit** | Run IEC 62443-4-1 ML4 SR-2 quantitative checks on **any** codebase (not just RUNE). | [Overview](#rune-audit) below + [Quickstart](quickstart.md) |
| **rune-operator** | Kubernetes-native job scheduling against an HTTP service (your own, not necessarily rune-api). CronJob semantics + budget gate + idempotency. | [rune-operator/overview](rune-operator/overview.md) |
| **rune-ui** | Standalone HTMX dashboard pointed at **any** rune-api-compatible backend. Zero NPM. | [rune-ui/overview](rune-ui/overview.md) |
| **rune-airgapped** | Package a Kubernetes application into an offline-installable OCI bundle with SBOMs + SLSA + cosign. | [rune-airgapped/overview](rune-airgapped/overview.md) |
| **driver-sdk** | `rune_bench.drivers` as a library — protocol integration for your own agent or transport. | [driver-sdk/overview](driver-sdk/overview.md) |

## rune-audit (detail below)

Use **[rune-audit](https://github.com/lpasquali/rune-audit)** on **non-RUNE** repositories to run the same **IEC 62443-4-1 ML4 SR-2** quantitative requirement catalog (SR-Q-001 … SR-Q-036) that RUNE tracks internally.

These pages are the **adopter-facing** guide. The short upstream summary lives in the rune-audit repo as [`docs/OSS_PROJECTS.md`](https://github.com/lpasquali/rune-audit/blob/main/docs/OSS_PROJECTS.md).

## In this section

| Page | Purpose |
| --- | --- |
| [Quickstart](quickstart.md) | Install, `rune-audit init`, `sr2 verify`, multi-repo `sr2 dashboard` |
| [Configuration](configuration.md) | `.rune-audit-project.yaml` schema |
| [Inspector library](inspector-library.md) | Built-in vs stub inspectors, catalog |
| [Custom inspectors](custom-inspectors.md) | `InspectorRegistry` extension |
| [Requirement packs](requirement-packs.md) | Pack ids and SR-Q scope |
| [CI integration](ci-integration.md) | GitHub Actions, GitLab, Jenkins patterns |
| [Case study: RUNE](case-study-rune.md) | How the RUNE program consumes the same model |

## Normative requirements text

Requirement titles and evidence expectations are defined in **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)** (rune-docs). Inspectors map evidence to those SR-Q ids.

## Status

Today many SR-Q rows still return **`not_implemented`** for catalog verification (stub phase). **Stdlib** inspectors (e.g. `stdlib.python_coverage`) return **`not_applicable`** when the technology is absent. Use `rune-audit sr2 verify` without `--strict` for informational runs; add `--strict` in CI when you are ready to fail on unfinished coverage.

**Matrix dashboard:** `rune-audit sr2 dashboard` (HTML / JSON / Markdown) aggregates verification across repos listed in **`compliance-config.yaml`** — see [Quickstart §4](quickstart.md) and [rune-docs#212](https://github.com/lpasquali/rune-docs/issues/212).
