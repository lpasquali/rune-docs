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

**`InspectorRegistry`** (`rune_audit.sr2.registry`) maps requirement ids to callables via **`register()`**. Today **`run_all()`** always uses **`default_registry()`** internally, so the stock **`rune-audit sr2 verify`** CLI does not yet accept an injected registry. Custom inspectors require either:

- extending rune-audit (fork or PR) to register callables on the default registry at import time, or  
- waiting for **EPIC #228** / follow-on API work to pass a registry into **`run_verification`**.

Until then, treat this section as the **intended** integration pattern.

## Rules of thumb

- One callable **per requirement id** you own; keep id strings aligned with **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)**.
- Prefer **pure** checks (read files under `ctx.root`, no network) for CI reproducibility.
- Document evidence in your PR when adding a new inspector in a fork or upstream contribution.

## Related

- [Inspector library](inspector-library.md)
- Upstream **EPIC #228** — pluggable inspector registry (rune-docs / rune-audit tracking).
