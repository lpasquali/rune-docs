# Troubleshooting

Symptom-first FAQ. Match your symptom, read the diagnosis, apply the fix. For issues not listed here, [CURRENT_STATE §Known Issues](../context/CURRENT_STATE.md) is the authoritative list of unresolved gotchas.

## `/v1/estimates` returns 404

**Symptom**: calling the estimates endpoint from the docker-compose stack returns HTTP 404.

**Diagnosis**: `rune-api` auth is enabled by default. Without a valid token, routes that require auth return 404 (not 401, to avoid leaking existence).

**Fix**: either disable auth for local dev (`RUNE_API_AUTH_DISABLED=1`, or `--set rune.api.authDisabled=true` via Helm) or wire proper tokens (`--set rune.api.tokens="myteam:$(openssl rand -hex 24)"`). In production, **never** disable auth.

## `ModuleNotFoundError: No module named 'StringIO'` when running `pymarkdown`

**Symptom**: `pymarkdown scan README.md docs` exits with Python-2-era `StringIO` import error.

**Diagnosis**: two packages both register a top-level `pymarkdown` module — the unrelated Python-2-era `pymarkdown==0.1.4` (unused experimental package) and the actual `pymarkdownlnt==0.9.36` (the CI linter). The first shadows the second.

**Fix**: `pip uninstall -y pymarkdown` in your local `.venv`. `requirements.txt` pins only `pymarkdownlnt`; CI is unaffected. The canonical command is `pymarkdownlnt scan README.md docs`, not `pymarkdown scan`.

## Docker daemon permission denied

**Symptom**: `docker compose up` or `docker ps` fails with `Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock`.

**Diagnosis**: your user is not in the `docker` group.

**Fix**: `sudo usermod -aG docker "$USER"` then `newgrp docker` (or log out and back in). Verify with `docker ps`. See [WORKSTATION §Docker](../operations/WORKSTATION.md#docker).

## `kind create cluster` hangs pulling `kindest/node`

**Symptom**: `kind create cluster --name ...` stalls on the "Ensuring node image" step for minutes with no progress.

**Diagnosis**: constrained bandwidth pulling the `kindest/node:vX.Y.Z` image cold.

**Fix**: pre-pull the image before running kind:

```bash
docker pull kindest/node:v1.35.0
```

Then retry. The `scripts/e2e.sh` wrapper (landing via [rune-docs#271](https://github.com/lpasquali/rune-docs/issues/271) Phase 1) automates this.

## `SQLite database is locked` on long-running benchmarks

**Symptom**: long-running benchmarks eventually fail with `database is locked` errors.

**Diagnosis**: SQLite is the default job store. Under concurrent writes from multiple pods, lock contention leads to timeouts. This is a known limitation — see [DATABASE_HA](../operations/DATABASE_HA.md) and [ADR 0006](../architecture/adrs/0006-storage-abstraction-postgres.md).

**Fix**: for single-pod deployments, increase `RUNE_API_DB_BUSY_TIMEOUT`. For multi-pod deployments, migrate to external PostgreSQL — the path is documented in [DATABASE_HA](../operations/DATABASE_HA.md) and the adapter ships via the optional `[pg]` extra per `rune#258`.

## Vast.ai instance created but not torn down

**Symptom**: you ran `rune run-benchmark --vastai` and the benchmark finished, but the Vast.ai dashboard shows a running instance charging you hourly.

**Diagnosis**: teardown is a separate step. If the benchmark CLI was killed (Ctrl-C or SIGKILL) before teardown executed, the instance persists.

**Fix**: either use `--vastai-stop-instance` on the `run-benchmark` invocation (teardown on normal exit), or manually kill the instance via the Vast.ai dashboard or `vastai destroy instance <id>`. Per [CURRENT_STATE §Known Issues](../context/CURRENT_STATE.md): "Manual Vast.ai instance creation/destruction can incur costs and requires careful validation."

## `mkdocs build --strict` fails with broken-link warning

**Symptom**: `python -m mkdocs build --strict` exits 1 with `WARNING -  Doc file 'X' contains a link 'Y', but the target is not found among documentation files.`

**Diagnosis**: you referenced a page that doesn't exist (typo, or forward-reference to a page landing in a sibling PR).

**Fix**: either create the missing page, correct the link, or use an absolute GitHub URL instead of a relative markdown link (which does not go through mkdocs link-checking). For sibling-PR forward-references, link to the tracking GitHub issue rather than the future page path.

## `mkdocs build --strict` flags orphan pages

**Symptom**: build log contains `INFO -  The following pages exist in the docs directory, but are not included in the "nav" configuration:` followed by page paths.

**Diagnosis**: a Markdown file exists under `docs/` but has no `mkdocs.yml` nav entry.

**Fix**: either add a nav entry in `mkdocs.yml` or delete/move the orphan file. Note: `--strict` treats this as INFO, not WARNING — the build still exits 0. It's a health signal, not a gate.

## Benchmark fails with `agent required` RuntimeError

**Symptom**: `python -m rune run-benchmark ...` fails with `RuntimeError: agent required` even though you're just testing.

**Diagnosis**: `agent` is a required field after the Holmes decoupling (`rune#163`). There is no default agent in code — the default lives in `rune.yaml` (if present).

**Fix**: either pass `--agent <name>` on the CLI, or run `rune init` to generate a starter `rune.yaml` with a default agent. See [CONFIGURATION](CONFIGURATION.md) for the `rune.yaml` precedence chain.

## `RUNE_OLLAMA_URL not set` on new CLI invocations

**Symptom**: old scripts or CI jobs setting `RUNE_OLLAMA_URL` fail with the CLI not picking it up.

**Diagnosis**: `RUNE_OLLAMA_URL` was renamed to `RUNE_BACKEND_URL` in [rune#173](https://github.com/lpasquali/rune/pull/173) / [#175](https://github.com/lpasquali/rune/pull/175). Subcommands like `run-llm-instance` were renamed to `run-llm-instance` in [#172](https://github.com/lpasquali/rune/pull/172).

**Fix**: update your scripts per [MIGRATION](MIGRATION.md). Deprecated API aliases (`/v1/llm/models`, `/v1/jobs/llm-instance`) still work at the HTTP layer but CLI env-vars do not have aliases.

## Tokens not comparing correctly

**Symptom**: API returns 401/403 even when you pass a token that should match.

**Diagnosis**: tokens are compared with `hmac.compare_digest` (constant-time, by-byte) since [rune#217](https://github.com/lpasquali/rune/pull/217). A trailing newline or leading whitespace in the token will break equality silently.

**Fix**: trim the token. The SHA-256 hashing that used to pre-process tokens was removed in the same PR — pass the raw token.
