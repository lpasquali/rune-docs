# rune-docs

Standalone documentation repository for the RUNE platform.

## Purpose

This repository isolates RUNE documentation from application and operator source code so it can be:

- versioned independently
- published as a MkDocs static site
# rune-docs

Standalone documentation repository for the RUNE platform.

## Purpose

This repository isolates documentation from application, operator, and chart source code so it can be:

- versioned independently
- published as a MkDocs site
- shipped as a container image
- protected by dedicated CI, security, and quality gates

## Contents

- `docs/` — source Markdown for the documentation site
- `mkdocs.yml` — MkDocs navigation and theme configuration
- `Dockerfile` — containerized docs build and runtime image
- `.github/workflows/` — CI and quality/security gates for docs

## Included Documentation

- [Docs index](docs/INDEX.md)
- [Architecture](docs/architecture.md)
- [API compatibility plan](docs/API_COMPATIBILITY_PLAN.md)
- [Ollama quick reference](docs/OLLAMA_QUICK_REFERENCE.md)
- [Compliance targets](docs/compliance-targets.md)

## Local Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

## Local Container Build

```bash
docker build -t rune-docs:local .
docker run --rm -p 18080:80 rune-docs:local
```

## Security and Compliance

See [SECURITY.md](SECURITY.md).
See [docs/compliance-targets.md](docs/compliance-targets.md) for the explicitly declared repository targets.
