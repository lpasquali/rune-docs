# Driver SDK quickstart

Build a minimal driver for a toy agent, install it as a pip package, and have it shadow the built-in registry.

## Prerequisites

- Python ≥ 3.11, `pip`.
- `rune-bench` installed (`pip install rune-bench[all]`).

## Scaffold

```bash
mkdir my-toy-agent && cd my-toy-agent
python3 -m venv .venv
. .venv/bin/activate
pip install rune-bench[all]
```

Create `pyproject.toml`:

```toml
[project]
name = "my-toy-agent"
version = "0.0.1"
dependencies = ["rune-bench"]

[project.entry-points."rune_bench.drivers"]
toy = "my_toy_agent.driver:ToyDriver"
```

Create `my_toy_agent/__init__.py` (empty) and `my_toy_agent/driver.py`:

```python
from rune_bench.drivers.base import DriverTransport

class ToyDriver(DriverTransport):
    """Echoes any question back as a fake-confident answer."""

    def call(self, action: str, params: dict) -> dict:
        if action == "ask":
            q = params.get("question", "")
            return {"answer": f"I think the answer to '{q}' is 42.", "confidence": 1.0}
        raise ValueError(f"Unknown action: {action}")
```

## Install

```bash
pip install -e .
```

## Invoke via RUNE

```bash
python -m rune run-benchmark \
  --agent toy \
  --backend-type local \
  --question "What is life?"
```

The built-in registry is lazy; your entry-point registration shadows any built-in `toy` driver (there is none by default, so yours wins cleanly).

## Registering programmatically

If you prefer runtime registration over entry points:

```python
from rune_bench.agents import register_agent
from my_toy_agent.driver import ToyDriver

register_agent("toy", ToyDriver)
```

`register_agent(...)` replaces any earlier registration under the same name.

## Testing

RUNE's own test suite uses `respx` to mock HTTP boundaries. For your driver, write a minimal test that exercises `call(...)` directly:

```python
import pytest
from my_toy_agent.driver import ToyDriver

def test_ask():
    r = ToyDriver().call("ask", {"question": "why"})
    assert r["answer"].startswith("I think")
    assert r["confidence"] == 1.0

def test_unknown_action():
    with pytest.raises(ValueError):
        ToyDriver().call("bogus", {})
```

## Next

- **[Driver SDK overview](overview.md)** for the full protocol list.
- **Agents SDK** (forthcoming under [#280](https://github.com/lpasquali/rune-docs/issues/280)) for AgentRunner, Registry, transport authoring.
- **[CODING_STANDARDS](../../context/CODING_STANDARDS.md)** for tier expectations and coverage floors.
