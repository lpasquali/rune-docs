# Migration Guide

Version-to-version breaking changes in the RUNE ecosystem. Each section lists the change, the version or PR where it landed, and the before/after recipe.

!!! warning "Pre-alpha"
    RUNE is at `v0.0.0a5`. API surfaces, CLI flags, CRD fields, and env-var names are not stable. Track [CURRENT_STATE](../context/CURRENT_STATE.md) and [What's New](WHATS_NEW.md) for the current breakage cadence.

## Environment variables

### `RUNE_OLLAMA_URL` → `RUNE_BACKEND_URL`

**Landed**: [rune#173](https://github.com/lpasquali/rune/pull/173) / [#175](https://github.com/lpasquali/rune/pull/175) — April 2026.

**Reason**: backend abstraction — RUNE no longer assumes Ollama is the only backend.

**Before**:

```bash
export RUNE_OLLAMA_URL=http://localhost:11434
python -m rune run-benchmark --model llama3.1:8b --question "..."
```

**After**:

```bash
export RUNE_BACKEND_URL=http://localhost:11434
python -m rune run-benchmark --model llama3.1:8b --question "..."
```

There is **no env-var alias**; old scripts must be updated.

## CLI subcommands

### `run-ollama-instance` → `run-llm-instance`

**Landed**: [rune#172](https://github.com/lpasquali/rune/pull/172) — April 2026.

**Reason**: backend abstraction at the CLI level.

**Before**:

```bash
python -m rune run-ollama-instance --ollama-url http://...
```

**After**:

```bash
python -m rune run-llm-instance --backend-url http://... --backend-type ollama
```

## HTTP API endpoints

### `GET /v1/ollama/models` → `GET /v1/llm/models`

**Landed**: [rune#172](https://github.com/lpasquali/rune/pull/172).

**Backward compatibility**: the old path still works as a **deprecated alias**. Scripts can migrate at leisure; new code should use `/v1/llm/models`.

### `POST /v1/jobs/ollama-instance` → `POST /v1/jobs/llm-instance`

**Landed**: [rune#172](https://github.com/lpasquali/rune/pull/172).

**Backward compatibility**: deprecated alias remains functional. Payload keys changed in parallel (see next section).

### Payload keys: `ollama_url` → `backend_url`, add `backend_type`

**Landed**: [rune#173](https://github.com/lpasquali/rune/pull/173).

**Before**:

```json
{
  "ollama_url": "http://ollama:11434",
  "model": "llama3.1:8b",
  "question": "..."
}
```

**After**:

```json
{
  "backend_url": "http://ollama:11434",
  "backend_type": "ollama",
  "model": "llama3.1:8b",
  "question": "..."
}
```

The server accepts legacy keys for one minor release but logs a deprecation warning. New integrations must use the new keys.

## CRD fields (rune-operator)

### `RuneBenchmark.spec.OllamaURL` → `BackendURL`

**Landed**: [rune-operator#60](https://github.com/lpasquali/rune-operator/pull/60) — April 2026.

**Before**:

```yaml
apiVersion: bench.rune.ai/v1alpha1
kind: RuneBenchmark
spec:
  OllamaURL: http://ollama:11434
  OllamaWarmup: true
```

**After**:

```yaml
apiVersion: bench.rune.ai/v1alpha1
kind: RuneBenchmark
spec:
  BackendURL: http://ollama:11434
  BackendWarmup: true
  BackendType: ollama
```

**Path**: `kubectl convert` does not help here; apply the new CRD then re-apply `RuneBenchmark` resources with the new field names. Existing operator instances running the old CRD will error on `OllamaURL` after upgrade — ordering is: (a) upgrade chart to new CRD, (b) update all `RuneBenchmark` CRs, (c) let operator reconcile.

### New field: `BackendType`

**Landed**: [rune-operator#61](https://github.com/lpasquali/rune-operator/pull/61). Kubebuilder default is `"ollama"` so existing CRs without `backendType` continue to behave as before. Explicit values needed when selecting a non-Ollama backend.

### New field: `PollIntervalSeconds`

**Landed**: [rune-operator#62](https://github.com/lpasquali/rune-operator/pull/62). Operator now polls `GET /v1/jobs/{job_id}` until completion; no default → kubebuilder sets a sensible value. Adjust if your workloads are longer than the default polling horizon.

## Provisioning structure

### Flat `vastai: true` → nested `providers: {...}`

**Landed**: [rune#251](https://github.com/lpasquali/rune/pull/251) — April 2026.

**Reason**: provider-agnostic multi-cloud.

**Before**:

```yaml
# rune.yaml
vastai: true
max_dph: 2.50
```

**After**:

```yaml
# rune.yaml
providers:
  vastai:
    enabled: true
    max_dph: 2.50
  aws:
    enabled: false
  gcp:
    enabled: false
```

**Backward compatibility**: the flat `vastai: true` shim still works as a fallback during the pre-alpha window. Scheduled for removal in the first beta.

## Token handling

### SHA-256 hashing removed; raw tokens with `hmac.compare_digest`

**Landed**: [rune#217](https://github.com/lpasquali/rune/pull/217) — April 2026. CodeQL-driven security hardening.

**Reason**: SHA-256 pre-processing of tokens offered no security benefit and introduced silent failure modes when tokens contained whitespace.

**Before**: tokens hashed in memory, comparison on hash digest.

**After**: raw token compared with `hmac.compare_digest` (constant-time, by-byte).

**Impact**: tokens with trailing newlines or leading whitespace now fail silently instead of matching-by-accident. Trim your tokens.

## Test-socket binding

### `""` (all interfaces) → `"127.0.0.1"` (loopback)

**Landed**: [rune#217](https://github.com/lpasquali/rune/pull/217).

**Reason**: CodeQL flagged test fixtures binding to all interfaces as unnecessary exposure.

**Impact**: none for test runs; relevant only if you had custom test harnesses depending on the old bind behavior.

## Healthcheck hosts

### `0.0.0.0` → `127.0.0.1` in Docker healthchecks

**Landed**: across all Dockerfiles (listed in [SYSTEM_PROMPT §Definition of Done](../context/SYSTEM_PROMPT.md#definition-of-done-pre-pr) as "Healthchecks: prefer `127.0.0.1`").

**Reason**: `0.0.0.0` binds but doesn't probe in some container-runtime configurations; `127.0.0.1` is the reliable loopback target.

**Impact**: if you wrote custom Dockerfiles pointing healthchecks at `0.0.0.0`, migrate to `127.0.0.1`.
