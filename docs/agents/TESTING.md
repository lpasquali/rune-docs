# Testing

!!! note "Scaffold page"
    Full content tracked as a follow-up under epic [#273](https://github.com/lpasquali/rune-docs/issues/273).
    The skeleton below names the sections that will be fleshed out.

## Harness

The test surface for an agent consists of:

- Unit tests against `DriverTransport.call(...)` — one test per action verb, one test per error path.
- Unit tests against `AgentRunner.ask(...)` / `ask_async(...)` / `ask_structured(...)` — with a fake transport injected, asserting the runner maps transport responses to `AgentResult` correctly.
- Optional integration tests against a real backend — guarded behind a `--integration` pytest flag; default is skip.

## `respx` mocking pattern

For HTTP-transport agents, mock HTTP boundaries with `respx` (the pattern RUNE's own test suite uses). Example pattern for `rune_bench/agents/sre/holmes.py`:

```python
import respx
import httpx
from rune_bench.agents import get_agent

@respx.mock
def test_holmes_ask():
    respx.post("http://holmes:8080/v1/actions/ask").mock(
        return_value=httpx.Response(200, json={"job_id": "abc-123"})
    )
    respx.get("http://holmes:8080/v1/jobs/abc-123").mock(
        return_value=httpx.Response(200, json={
            "state": "done",
            "result": {"answer": "kubectl says CrashLoopBackOff", "confidence": 0.9},
        })
    )

    runner = get_agent("holmes")
    r = runner.ask("why is my pod crashing?", model="qwen3:14b-instruct",
                   backend_url="http://ollama:11434")
    assert r.answer.startswith("kubectl")
    assert r.confidence == 0.9
```

## Coverage expectations

Per [CODING_STANDARDS](../context/CODING_STANDARDS.md) §Tier Registry:

- **Tier 1**: 100% coverage target, 97% floor. Measured in `.coveragerc`. Every branch, every error path.
- **Tier 2**: best-effort. May be omitted from measurement with justification.
- **Tier 3**: excluded from coverage measurement (protocol-only; no code path to measure).

## Stub contract

Tier 1 agents that are scaffolded but not yet implemented must still be measured and tested. A test that calls the stub's entry point and asserts `pytest.raises(NotImplementedError)` is correct and sufficient:

```python
import pytest
from rune_bench.agents import get_agent

def test_my_agent_stub_contract():
    agent = get_agent("my_unimplemented_agent")
    with pytest.raises(NotImplementedError):
        agent.ask("anything", model="any")
```

This verifies the stub is importable and exposes the agent contract. Real tests replace it when the agent is implemented.

## What's NOT in scope for this page (yet)

- **Example cases** — specific test recipes per transport variant (HTTP, stdio, async, browser). Follow-up.
- **Coverage tooling setup** — `.coveragerc` authoring, `pytest-cov` flags, Tier 2 omit justification patterns. Follow-up.
- **Integration test guardrails** — when to mark tests as `@pytest.mark.integration`, how to gate them behind env-var presence, cloud-cost safety. Follow-up.

Track the expansion via [rune-docs#273](https://github.com/lpasquali/rune-docs/issues/273) child [#280](https://github.com/lpasquali/rune-docs/issues/280) follow-ups.
