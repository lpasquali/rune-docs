 
# QUICKSTART

Getting the software running locally.

 
## Installation

RUNE is a Python-based platform. The core package can be installed with optional extras.

```bash
pip install rune-bench                  # core only
pip install rune-bench[holmes]          # + holmesgpt + supabase
pip install rune-bench[all]             # + all optional extras (holmesgpt, vastai-sdk)
```

 
## Running Your First Benchmark

The simplest way to run a benchmark is using existing Ollama server mode:

```bash
 
# Set your existing Ollama server URL

export RUNE_OLLAMA_URL=http://localhost:11434

 
# Run a benchmark with a specific model and question

python -m rune run-benchmark \
  --model llama3.1:8b \
  --question "Why is the cluster unhealthy?"
```

 
## Running with Vast.ai Provisioning

To provision a GPU instance on Vast.ai:

```bash
export VAST_API_KEY=...

python -m rune run-benchmark \
  --vastai \
  --question "What is the status of the deployment?"
```

 
## Docker Quickstart

```bash
 
# Build image

docker build -t ai-benchmark-rune .

 
# Run existing server mode

docker run -it --rm \
  ai-benchmark-rune run-ollama-instance \
  --ollama-url http://host.docker.internal:11434
```

 
## Local Development Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run tests: `pytest`.
