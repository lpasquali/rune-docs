# Example: end-to-end agent package

!!! note "Scaffold page"
    Full worked example tracked as a follow-up under epic [#273](https://github.com/lpasquali/rune-docs/issues/273).
    A short pointer version lives in [Driver SDK quickstart](https://github.com/lpasquali/rune-docs/issues/279)
    today; the full narrative with a realistic domain agent and all
    five transport variants is pending.

## What this page will cover

1. **Pick a domain** — a realistic agent scenario (e.g., a custom SRE agent that wraps a proprietary incident-triage backend).
2. **Scaffold the package** — `pyproject.toml`, directory layout, `[project.entry-points."rune_bench.agents"]`.
3. **Implement the `DriverTransport`** — choice of transport (HTTP shown first, variations noted).
4. **Implement the `AgentRunner`** — map transport responses to `AgentResult`.
5. **Register via entry point** — `pip install -e .` and observe `list_agents()` output.
6. **Catalog row** — add a `chains.csv` entry (or register outside the catalog for private use).
7. **Run against RUNE** — `python -m rune run-benchmark --agent my_agent ...`.
8. **Test suite** — `respx`-mocked unit tests per the [Testing](TESTING.md) pattern.
9. **Ship** — package version, release, PyPI publish (or internal registry).

## Pointer: quickstart today

The [Driver SDK quickstart](https://github.com/lpasquali/rune-docs/issues/279) already walks through a minimal toy-agent end-to-end. It's shorter than the worked example planned here, but it's reproducible today and exercises the same API surface.

## Track progress

Follow-up issue under [#280](https://github.com/lpasquali/rune-docs/issues/280) will expand this scaffold into the full narrative. If you need this page urgently for an integration you're doing today, comment on that issue.
