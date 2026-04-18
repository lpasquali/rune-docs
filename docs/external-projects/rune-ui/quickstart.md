# rune-ui quickstart

Run the dashboard against an existing rune-api-compatible backend in under 5 minutes.

## Prerequisites

- Python ≥ 3.12 (3.14 is the CI target).
- A reachable backend at some URL (your own rune-api, a hosted instance, or a mock).

## Install from source

```bash
git clone https://github.com/lpasquali/rune-ui.git
cd rune-ui

python3.14 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## Configure + run

```bash
export RUNE_API_URL=http://your-backend:8080
export RUNE_API_TOKEN=your-token       # optional; omit if backend is auth-disabled

python -m rune_ui                      # serves on http://127.0.0.1:3000 by default
```

Open <http://127.0.0.1:3000/dashboard> — the configuration page reports API health and available models.

## Container image

```bash
docker run --rm -d \
  -e RUNE_API_URL=http://your-backend:8080 \
  -e RUNE_API_TOKEN=your-token \
  -p 3000:3000 \
  ghcr.io/lpasquali/rune-ui:v0.0.0a0
```

(Image tag matches the repo's published version; see the [rune-ui releases page](https://github.com/lpasquali/rune-ui/releases) for current tags.)

## Health probe

```bash
curl -s http://127.0.0.1:3000/healthz
```

Returns `{"status":"ok"}` plus a `backend` field with the reachability of your configured `RUNE_API_URL`.

## Theming

Set the theme via the UI's toggle or the `localStorage` key `rune-ui-theme` (values: `light`, `dark`, `system`). The print stylesheet kicks in for any `window.print()` or PDF export.

## Running the tests

```bash
pytest
```

Uses `respx` to mock the backend — no live backend required.

## Next

- **[rune-ui README](https://github.com/lpasquali/rune-ui/blob/main/README.md)** for env var reference.
- **[Deployment §Mode 4](../../operations/DEPLOYMENT.md)** for running rune-ui via Helm alongside the rest of the stack.
