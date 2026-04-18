# rune-operator — standalone CRD scheduling

`rune-operator` is a Kubernetes operator implementing the `RuneBenchmark` custom resource. Originally built to schedule benchmarks against a `rune-api` server, it can be adopted standalone whenever you need **cron-driven, budget-gated, fully-declarative job scheduling** against an HTTP service — with or without the rest of the RUNE stack.

## When to use standalone

- You want **Kubernetes-native scheduling** (CronJob-like semantics) without running the full rune-api + UI + Ollama + storage stack.
- You have an existing HTTP service that accepts JSON job submissions and you want the operator's cost-estimation gate (`/v1/finops/simulate`) + `Ready=BudgetExceeded` pattern.
- You need **idempotency keys** derived from `namespace/name/generation/scheduleTime` (operator ships this out of the box per `rune-operator#65`).
- You need **job result capture** as raw JSON in `RunRecord.Result` for downstream aggregation.

## What you get

- `RuneBenchmark` CRD at `bench.rune.ai/v1alpha1`. Fields include: `BackendURL` (service you're calling), `BackendWarmup`, `BackendType`, `Agent`, `AttestationRequired`, `Budget.maxCostUSD`, `PollIntervalSeconds`.
- Reconciler that polls `GET /v1/jobs/{job_id}` until completion; no more treating HTTP 202 as success.
- Fail-closed cost estimation via `CostEstimation` struct supporting VastAI / AWS / GCP / Azure / LocalHardware providers. `spec.budget.maxCostUSD` caps spend per job.
- Signed container images (cosign via sigstore), SLSA provenance, SBOM, VEX register integration.

## What you give up vs full RUNE

- No UI (unless you also deploy rune-ui separately).
- No persistent history beyond the `RunRecord` on each `RuneBenchmark` resource — bring your own storage if you want to keep longer-term results.
- No cross-run analytics — that's what `rune-api` aggregates over a job store.

## Next

- **[Quickstart](quickstart.md)** — install the operator + apply a `RuneBenchmark` CR against your own HTTP service.
- **[rune-operator repo](https://github.com/lpasquali/rune-operator)** — source, CRD YAML, example values.
