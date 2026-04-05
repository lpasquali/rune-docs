# OLLAMA_REFERENCE

Quick reference for the Ollama integration module.

## Quick Start

### List available models

```python
from rune_bench.backends.ollama import OllamaModelManager

manager = OllamaModelManager.create("http://localhost:11434")
models = manager.list_available_models()
print(models)
```

### Check running models

```python
manager = OllamaModelManager.create("http://localhost:11434")
running = manager.list_running_models()
print(f"Currently running: {running}")
```

### Load a model with automatic cleanup

```python
manager = OllamaModelManager.create("http://localhost:11434")
loaded = manager.warmup_model(
    "mistral:latest",
    timeout_seconds=120,
    unload_others=True,  # Unload conflicting models
)
print(f"Ready: {loaded}")
```

## CLI Usage

### List available models on a server

```bash
python -m rune ollama-list-models --ollama-url http://localhost:11434
```

### Run benchmark with warm-up

```bash
python -m rune run-benchmark \
    --ollama-url http://localhost:11434 \
    --model mistral:latest \
    --ollama-warmup \
    --ollama-warmup-timeout 90
```

## Module Structure

- **`OllamaClient`**: Low-level HTTP transport.
- **`OllamaModelManager`**: High-level model lifecycle operations.

## Testing with Mocks

```python
from unittest.mock import Mock
from rune_bench.backends.ollama import OllamaModelManager
mock_client = Mock()
mock_client.get_available_models.return_value = ["mistral", "llama2"]

# Test with mock
manager = OllamaModelManager(client=mock_client)
assert manager.list_available_models() == ["mistral", "llama2"]
```
