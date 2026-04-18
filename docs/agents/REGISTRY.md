# Registry

The registry lets your custom agent shadow built-ins by name. RUNE's registry is lazy — built-in agents are imported via `importlib.import_module` only when their name is requested — which means a custom registration inserted before any code calls `get_agent("holmes")` will take precedence without any import-order gymnastics.

Source: `rune_bench/agents/registry.py`.

## Surface

```python
from rune_bench.agents import register_agent, get_agent, list_agents

def register_agent(name: str, factory: type[AgentRunner] | callable) -> None: ...
def get_agent(name: str) -> AgentRunner: ...
def list_agents() -> list[str]: ...
```

## Shadowing built-ins

```python
from rune_bench.agents import register_agent
from my_custom.holmes import MyCustomHolmes

# Before any get_agent("holmes") call:
register_agent("holmes", MyCustomHolmes)
```

After this line, `get_agent("holmes")` returns `MyCustomHolmes`. The built-in `rune_bench.agents.sre.holmes:HolmesGPT` is never imported.

**Ordering matters**: if some earlier code path already did `get_agent("holmes")`, the built-in has been instantiated (and possibly cached). Register before first use. For tests, use a fixture that runs `register_agent` in `conftest.py`.

## Registration via entry points

The recommended distribution path for a custom agent is a pip package with an entry point:

```toml
# pyproject.toml
[project.entry-points."rune_bench.agents"]
my_agent = "my_pkg.agent:MyAgent"
```

RUNE scans entry points on first call to `list_agents()` or `get_agent()` and calls `register_agent(name, factory)` for each. Entry-point registrations happen **before** any built-in import — this is the cleanest way to ship a shadow.

## Lazy importlib

Built-in registrations are declared in `rune_bench/agents/registry.py` as `(name, "rune_bench.agents.sre.holmes:HolmesGPT")` tuples. `get_agent(name)` resolves via `importlib.import_module(module)` + `getattr(module, class_name)`. This means:

- Importing `rune_bench` does not pull in every agent's dependencies.
- A Tier 3 agent whose SDK isn't installed doesn't crash `rune_bench` on import.
- Custom shadows preempt the import entirely — the shadowed built-in is never loaded.

## Missing config → RuntimeError

When `get_agent(name)` instantiates an agent whose constructor requires env vars or config (e.g., `RUNE_HOLMES_DRIVER_URL`), missing values produce `RuntimeError` with a message naming the specific missing variable. Callers should surface the error to the user with its message preserved.

## Listing

```python
from rune_bench.agents import list_agents
print(list_agents())  # ['holmes', 'k8sgpt', 'pagerduty', ...]
```

Returns all names registered at the time of the call (built-ins + custom). The order reflects registration order: built-ins as declared in `registry.py`, followed by any custom shadows and fresh registrations.

## Common patterns

### Replace a built-in with a hardened fork

```python
register_agent("holmes", MyHardenedHolmes)
```

### Register a new Tier 1 OSS agent you want upstreamed

Open a PR against `rune` that adds the driver under `rune_bench/agents/<scope>/<name>.py` + a row in `chains.csv`. That's the long-term path; until it merges, use `register_agent(...)` in your own deployment.

### Register a Tier 3 closed-SaaS stub with no working driver yet

```python
from rune_bench.agents.base import AgentRunner, AgentResult

class SierraStub(AgentRunner):
    def ask(self, *a, **kw):
        raise NotImplementedError("Sierra has no public API; stub-only.")

    async def ask_async(self, *a, **kw):
        raise NotImplementedError("Sierra has no public API; stub-only.")

    def ask_structured(self, *a, **kw):
        raise NotImplementedError("Sierra has no public API; stub-only.")

register_agent("sierra", SierraStub)
```

Stubs are legitimate: they make the catalog complete and let tooling detect which Tier 3 agents are callable versus placeholder.

## Further

- [AgentRunner](AGENT_RUNNER.md) — protocol contract for what `register_agent` accepts.
- [DriverTransport](DRIVER_TRANSPORT.md) — the wire layer.
- [Driver SDK quickstart](https://github.com/lpasquali/rune-docs/issues/279) — end-to-end package-and-ship.
