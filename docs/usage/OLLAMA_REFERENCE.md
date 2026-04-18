 
# LLM Backend Reference

Quick reference for the LLM backend integration layer. RUNE supports pluggable backends via the `LLMBackend` protocol. The default backend is [Ollama](https://ollama.com/) ([API reference](https://github.com/ollama/ollama/blob/main/docs/api.md)). See the [External Links Catalog](../reference/EXTERNAL_LINKS.md) for all backend, agent, and provider docs.

 
## Quick Start (Generic API)

### List available models

```python
from rune_bench.backends import get_backend

backend = get_backend("ollama", "http://localhost:11434")
models = backend.list_models()
print(models)
```

### Check running models

```python
backend = get_backend("ollama", "http://localhost:11434")
running = backend.list_running_models()
print(f"Currently running: {running}")
```

### Warm up a model

```python
backend = get_backend("ollama", "http://localhost:11434")
loaded = backend.warmup("mistral:latest", timeout_seconds=120)
print(f"Ready: {loaded}")
```

### Get model capabilities

```python
backend = get_backend("ollama", "http://localhost:11434")
normalized = backend.normalize_model_name("mistral:latest")
caps = backend.get_model_capabilities(normalized)
print(f"Context window: {caps.context_window}, Max tokens: {caps.max_output_tokens}")
```

 
## CLI Usage

### List available models on a server

```bash
python -m rune llm-list-models --backend-url http://localhost:11434 --backend-type ollama
```

### Run benchmark with warm-up

```bash
python -m rune run-benchmark \
    --backend-url http://localhost:11434 \
    --model mistral:latest \
    --backend-warmup \
    --backend-warmup-timeout 90
```

 
## Ollama-Specific Module

For direct access to Ollama-specific features, the `OllamaBackend` facade and lower-level `OllamaClient`/`OllamaModelManager` are still available:

```python
from rune_bench.backends.ollama import OllamaClient, OllamaModelManager

# Low-level client
client = OllamaClient("http://localhost:11434")
models = client.get_available_models()

# High-level manager
manager = OllamaModelManager.create("http://localhost:11434")
manager.warmup_model("mistral:latest", timeout_seconds=120, unload_others=True)
```

 
## Architecture

- **`LLMBackend`** (Protocol): `rune_bench/backends/base.py` — 6 methods: `base_url`, `get_model_capabilities`, `list_models`, `list_running_models`, `normalize_model_name`, `warmup`.
- **`get_backend(type, url)`**: Factory in `rune_bench/backends/__init__.py` — resolves backend by type.
- **`OllamaBackend`**: `rune_bench/backends/ollama.py` — implements `LLMBackend` for Ollama.
- **`OllamaClient`**: Low-level HTTP transport for Ollama API.
- **`OllamaModelManager`**: High-level model lifecycle operations.

 
## Testing with Mocks

```python
from unittest.mock import MagicMock
from rune_bench.backends.base import ModelCapabilities

fake_backend = MagicMock()
fake_backend.normalize_model_name.return_value = "mistral:latest"
fake_backend.get_model_capabilities.return_value = ModelCapabilities(
    model_name="mistral:latest",
    context_window=32768,
    max_output_tokens=4096,
)

# Patch get_backend to return the fake
# monkeypatch.setattr("rune_bench.backends.get_backend", lambda *a, **kw: fake_backend)
```
