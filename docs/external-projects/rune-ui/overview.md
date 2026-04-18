# rune-ui — standalone HTMX dashboard

`rune-ui` is the RUNE dashboard — FastAPI + Jinja2 + HTMX, **zero NPM**. It's installed as a standalone Python service that talks to **any** rune-api-compatible HTTP endpoint, so you can point it at your own aggregation service, a hosted rune-api, or a downstream fork.

## When to use standalone

- You want a **browser UI for RUNE benchmarks** without running the full stack (no Ollama, no storage, no operator required — just the UI process + something for it to query).
- You run a **fleet of rune-apis** (multi-tenant, multi-environment) and want a single dashboard pointing at each via `RUNE_API_URL`.
- You want a **reference HTMX dashboard** as a template for similar internal tools — the codebase is small, auditable, and has no JavaScript build step.

## What you get

- Dashboard routes: `/dashboard`, `/configuration`, plus benchmark-detail and chain-detail pages.
- SSE trace streaming consumption (server-side events from the backend surfaced as live chain progress).
- Configuration page surfacing API health + settings + available models.
- `/healthz` endpoint for liveness probes.
- Solarized theme pair (light / dark with `prefers-color-scheme` + localStorage override), print stylesheet (`@media print`), WCAG AAA contrast (12.6:1), focus rings.
- Mocked test suite (`respx`-backed) for the full API surface; no live backend required to run tests.

## What you give up vs full RUNE

- No server-side benchmark execution — the UI is a pure view/command layer.
- No persistence — all state lives in the backend it points at.

## Configuration

Key env vars:

| Variable | Default | Purpose |
|---|---|---|
| `RUNE_API_URL` | — | URL of the backend; **required** |
| `RUNE_API_BASE_URL` | — | Fallback env name for the same value (back-compat with earlier releases) |
| `RUNE_API_TOKEN` | — | Bearer token for backend auth |
| `RUNE_UI_HOST` / `RUNE_UI_PORT` | `127.0.0.1` / `3000` | Bind host/port |

## Next

- **[Quickstart](quickstart.md)** — run rune-ui against an existing backend in under 5 minutes.
- **[rune-ui repo](https://github.com/lpasquali/rune-ui)** — source, templates, tests.
