# AgentRunner

The agent-level protocol that sits above `DriverTransport`. `AgentRunner` gives every RUNE agent a uniform call surface: `ask` (sync), `ask_async` (async), and `ask_structured` (multi-modal — text + images + structured data).

Source: `rune_bench/agents/base.py` in [the rune repo](https://github.com/lpasquali/rune/blob/main/rune_bench/agents/base.py). Defined as a `typing.Protocol`.

## Signature

```python
from typing import Protocol

class AgentRunner(Protocol):
    def ask(
        self,
        question: str,
        model: str,
        backend_url: str | None = None,
        backend_type: str = "ollama",
    ) -> "AgentResult":
        ...

    async def ask_async(
        self,
        question: str,
        model: str,
        backend_url: str | None = None,
        backend_type: str = "ollama",
    ) -> "AgentResult":
        ...

    def ask_structured(
        self,
        question: str,
        model: str,
        backend_url: str | None = None,
        backend_type: str = "ollama",
    ) -> "AgentResult":
        ...
```

All three take the same parameters; `ask_structured` is expected to populate the `images` / `structured` fields of `AgentResult` where applicable.

## Dataclasses

### `AgentConfig`

Configuration passed to a runner at construction time. Driver-specific; the base fields:

```python
@dataclass
class AgentConfig:
    name: str                       # agent name, matches registry key
    transport: DriverTransport      # injected; never instantiated inside AgentRunner
    tier: int                       # 1, 2, or 3
    extra: dict | None = None       # driver-specific kwargs
```

The runner does **not** instantiate its own transport — it receives one. This keeps drivers mockable (hand in a fake transport during tests).

### `AgentResult`

The uniform response shape:

```python
@dataclass
class AgentResult:
    answer: str                     # required — human-readable response
    confidence: float               # 0.0–1.0; not the same as confidence_score for cost gates
    images: list[bytes] | None = None       # populated by ask_structured
    structured: dict | None = None          # populated by ask_structured
    raw: dict | None = None                 # pass-through of the driver's raw response
    duration_s: float | None = None         # set by the runner, not the driver
```

Always non-null: `answer`, `confidence`. The rest are optional.

## Minimal implementation

```python
from rune_bench.agents.base import AgentRunner, AgentConfig, AgentResult
from rune_bench.drivers.base import DriverTransport

class MyAgent(AgentRunner):
    def __init__(self, config: AgentConfig):
        self._tx = config.transport

    def ask(self, question, model, backend_url=None, backend_type="ollama"):
        r = self._tx.call("ask", {
            "question": question,
            "model": model,
            "backend_url": backend_url,
            "backend_type": backend_type,
        })
        return AgentResult(
            answer=r["answer"],
            confidence=r.get("confidence", 0.5),
            raw=r,
        )

    async def ask_async(self, question, model, backend_url=None, backend_type="ollama"):
        # default: call sync in a thread if no async transport is available
        import asyncio
        return await asyncio.to_thread(self.ask, question, model, backend_url, backend_type)

    def ask_structured(self, question, model, backend_url=None, backend_type="ollama"):
        # if your agent supports structured output, populate images/structured here
        return self.ask(question, model, backend_url, backend_type)
```

The `typing.Protocol` is structural: you **don't** need to subclass `AgentRunner` explicitly. Duck-typing is sufficient. Subclassing adds clarity for contributors and is recommended but not required.

## Backend parameters

Every `AgentRunner.ask(...)` takes `backend_url` + `backend_type`. The runner can use these to:

- Select the correct `LLMBackend` via `get_backend(backend_type)`.
- Override the default model resolution (e.g., strip LiteLLM `ollama/` prefix via `normalize_model_name`).
- Resolve provisioning via `LLMResourceProvider` when needed.

Agents that **don't** care about backend parameters (e.g., a Tier 3 closed SaaS that uses its own hidden backend) should accept and ignore them gracefully.

## Error conventions

- **Missing required config** → `RuntimeError` with an env-var hint: `"RUNE_MYAGENT_DRIVER_URL is required for MyAgent"`.
- **Transport failure** → let the `DriverTransport.call(...)` `RuntimeError` propagate; don't swallow it.
- **Agent-specific failure mode** → `RuntimeError` with a clear message. Avoid generic exceptions.

## Further

- [Registry](REGISTRY.md) — wire your `AgentRunner` into the catalog.
- [DriverTransport](DRIVER_TRANSPORT.md) — the wire-level layer underneath.
- [CODING_STANDARDS §Agent filesystem layout](../context/CODING_STANDARDS.md) — where your agent file lives by scope.
