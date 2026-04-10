# Inspector library reference

## Catalog

All **36** SR-Q requirements (**SR-Q-001** … **SR-Q-036**) are enumerated in rune-audit:

- **Code**: `rune_audit.sr2.catalog.iter_requirements()`
- **Priorities**: P0 / P1 / P2 aligned with **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)**

Use:

```bash
rune-audit sr2 verify . --priority P0
```

to scope runs while you incrementally implement inspectors.

## Default registry

`rune_audit.sr2.registry.default_registry()` returns an **`InspectorRegistry`** that maps requirement ids to callables. Until custom registrations exist, unknown ids resolve to **`stub_inspector`**, which yields **`not_implemented`** with a short detail string.

## Standard inspectors

Module **`rune_audit.sr2.standard_inspectors`** is the home for **built-in** checks as they land (see open issues in **rune-audit** for implementation status). The engine invokes the registry for each `RequirementSpec` from the catalog.

## CLI introspection

```bash
rune-audit sr2 gaps              # list not_implemented
rune-audit sr2 dashboard --format md
rune-audit sr2 verify . --json   # full machine-readable report
```

## Further reading

- [Custom inspectors](custom-inspectors.md)
- [Requirement packs](requirement-packs.md)
