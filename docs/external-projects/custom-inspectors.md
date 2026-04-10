# Custom inspector guide

## Extension point

Implement **`InspectorFn`**:

```python
from rune_audit.sr2.inspectors import InspectContext
from rune_audit.sr2.models import InspectResult, RequirementSpec

def my_check(ctx: InspectContext, spec: RequirementSpec) -> InspectResult:
    ...
```

Return a structured **`InspectResult`** with status **`pass`**, **`fail`**, **`not_applicable`**, or **`not_implemented`** (see `rune_audit.sr2.models`).

## Registration

**`InspectorRegistry`** (`rune_audit.sr2.registry`) maps requirement ids to callables via **`register()`**.

- **`@register_inspector("SR-Q-00N")`** — decorator registers a built-in when your module is imported before **`default_registry()`** runs (rune-audit ships **`standard_inspectors`** for this pattern).
- **`default_registry()`** — builds a fresh registry, imports **`rune_audit.sr2.standard_inspectors`**, and applies all decorator-registered callables.
- **`run_verification(..., registry=...)`** — library callers can pass a fully custom **`InspectorRegistry`** instance (wraps the same **`run_all(..., registry=...)`** path). The **`rune-audit sr2 verify`** CLI still uses the default registry only (no CLI flag yet).

Forks and downstream packages can register via decorator in an importable module, or construct a registry in Python and call **`run_verification`** from their own entry point.

## Rules of thumb

- One callable **per requirement id** you own; keep id strings aligned with **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)**.
- Prefer **pure** checks (read files under `ctx.root`, no network) for CI reproducibility.
- Document evidence in your PR when adding a new inspector in a fork or upstream contribution.

## Related

- [Inspector library](inspector-library.md)
- **rune-docs#228** — pluggable inspector registry (registry API + engine wiring; CLI plugins remain follow-on).
