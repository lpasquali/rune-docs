# Benchmark Methodology

The "NE" in RUNE stands for **Numeric Evaluator**. This page documents **how** RUNE evaluates agents — the scoring model, scope taxonomy, tier meanings, and a worked example. The authoritative catalog files (`chains.csv`, `scopes.csv`) ship as package data inside `rune-bench`; this page is the human-readable view.

## Scoring model

Every benchmark run produces a **numeric score** plus a **`confidence_score`**. The score is aggregated per chain (a DAG of agents executed against a question), per scope (the taxonomy described below), and per tier.

- **`confidence_score`** is a fail-closed gate for cloud provisioning. Below `0.95`, `CostEstimationResponse` rejects the run; above, the run proceeds.
- **Cost Estimation Providers**: RUNE supports automated cost projection for **Vast.ai** (instance-based), **AWS** (on-demand), **GCP** (on-demand), and **Azure** (on-demand). Local hardware runs use an energy-based calculation (TDP × Rate).
- **Aggregation** is per-scope first (so an SRE benchmark isn't averaged with a Research benchmark), then per-tier (so a Tier-3 closed-SaaS agent isn't averaged with a Tier-1 OSS agent whose code path is fully measured).
- **Reproducibility** is a first-class requirement: benchmark commands are documented, seed-sensitive paths are noted, and warmup passes are deterministic.

Design reference: [SYSTEM_PROMPT §Cost gates](../context/SYSTEM_PROMPT.md#cost-gates-api-contracts), [ADR 0002: Cost Estimation](../architecture/adrs/0002-cost-estimation.md).

## Scope taxonomy

Agents are classified by **scope** — the problem domain they're designed for. This determines which question set a benchmark exercises and which agents are comparable.

| Scope | Representative question | Representative agents (see `chains.csv`) |
|---|---|---|
| **SRE** | "Why is my Pod in CrashLoopBackOff?" | K8sGPT (T1), HolmesGPT (T1), PagerDuty AI (T3), Metoro (T2), Cleric (T2) |
| **Research** | "Efficacy of Drug X for Condition Y?" | Perplexity Pro (T3), Glean (T3), Elicit (T2), LangGraph (T1), Consensus (T2) |
| **Art/Creative** | "Consistent character in 5 scenes?" | Midjourney (T3), ComfyUI (T2), Krea AI (T3) |
| **Cybersec** | "Perform grey-box pentest on app?" | PentestGPT (T1), Radiant Security (T3), Mindgard (T3), BurpGPT (T2), XBOW (T3) |
| **Legal/Ops** | "Review 50-page NDA for clauses?" | Harvey AI (T3), Spellbook (T3), MultiOn (T2), Dagger (T1), CrewAI (T1), Browser-Use (T3) |

Scope-to-directory mapping lives in [CODING_STANDARDS §Agent filesystem layout](../context/CODING_STANDARDS.md). Filename conventions (lower-case, first-word-only, special-cases listed) are authoritative.

## Tier meanings

Sourced verbatim from [CODING_STANDARDS §Tier Registry](../context/CODING_STANDARDS.md). See also [Agent Access Tiers](TIERS.md) for the reader-facing tier page (filename rename to `TIERS.md` pending).

- **Tier 1** — OSS, fully testable, 100% coverage target, included in `.coveragerc` measurement.
- **Tier 2** — Partial API access or freemium, best-effort coverage, may be omitted from measurement with justification.
- **Tier 3** — Closed SaaS or no public API, protocol-only integration via `DriverTransport`, excluded from coverage measurement.

**Consumer implications**: you can run any Tier-1 agent end-to-end with full code-path inspection. Tier-2 agents work via their public API with best-effort integration. Tier-3 agents return via the `DriverTransport` protocol; RUNE cannot see inside them. Scores across tiers are comparable for a given question set but the confidence bounds differ.

## Catalog surface

`rune_bench/catalog/defaults/chains.csv` and `scopes.csv` ship as package data inside the `rune-bench` Python package. At runtime:

```python
from importlib.resources import files
from rune_bench.catalog import defaults
import csv

chains_path = files(defaults) / "chains.csv"
with chains_path.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["Scope"], row["Agent Name"], row["Tier"], row["Rating"])
```

The CSV is the source of truth. When this documentation page drifts from the CSV, the CSV wins. Run the `rune catalog ls` command (or its equivalent) to see the live state.

Columns in `chains.csv`: `Scope`, `Rank`, `Agent Name`, `Tier` (1/2/3), `Rating` (agent-specific competence estimate), `Agentic Capability`, three representative question/action pairs (`Q1`/`Q2`/`Q3`), `GitHub/Docs Link`, `Ecosystem`, `Ollama Model (2026)` (recommended model when the agent runs against Ollama).

## Sample: SRE scope, K8sGPT vs HolmesGPT

Worked example. Uses two Tier-1 OSS agents so the entire code path is measurable.

!!! note "Pre-alpha output"
    The output structure shown below reflects `v0.0.0a5` behavior. The
    shape of `AgentResult` is expected to evolve before beta. Treat the
    example as illustrative, not a stable contract.

### Invocation (Ollama)

```bash
export RUNE_BACKEND_URL=http://localhost:11434

python -m rune run-benchmark \
  --scope SRE \
  --chain "k8sgpt,holmesgpt" \
  --model qwen3:14b-instruct \
  --question "Why is my Pod in CrashLoopBackOff?"
```

### Invocation (AWS Bedrock)

```bash
export RUNE_BACKEND_TYPE=bedrock
export RUNE_BACKEND_REGION=us-east-1

python -m rune run-benchmark \
  --scope SRE \
  --chain "holmesgpt" \
  --model anthropic.claude-3-5-sonnet \
  --question "Audit this namespace for security issues"
```

### What happens

1. **Agent resolution**. `get_agent("k8sgpt")` and `get_agent("holmesgpt")` resolve from the built-in registry (both Tier 1; fully measurable). Missing required config → `RuntimeError` with an env hint.
2. **Cost gate**. Local backend → gate skipped (no provisioning). If the backend were `vastai`, `CostEstimationRequest` would fire with `confidence_score` check.
3. **Warmup**. Deterministic warmup on the `qwen3:14b-instruct` model to eliminate cold-start variance.
4. **Q1 execution**. K8sGPT runs its standard-Q1 action ("Scans logs/events and provides a human-readable fix"). HolmesGPT runs its standard-Q1 action ("Runs kubectl commands to fetch logs and traces autonomously").
5. **Scoring**. Per-agent `AgentResult` is scored against the scope's reference rubric; aggregated into a benchmark score + confidence.

### Expected output shape

```json
{
  "benchmark_id": "...",
  "scope": "SRE",
  "question": "Why is my Pod in CrashLoopBackOff?",
  "chain": ["k8sgpt", "holmesgpt"],
  "confidence_score": 0.98,
  "per_agent": [
    {
      "agent": "k8sgpt",
      "tier": 1,
      "score": 4.5,
      "duration_s": 12.3,
      "result_excerpt": "...scanned events, found ImagePullBackOff on container ..."
    },
    {
      "agent": "holmesgpt",
      "tier": 1,
      "score": 4.3,
      "duration_s": 34.7,
      "result_excerpt": "...ran kubectl get events --all-namespaces | kubectl describe pod ..."
    }
  ],
  "aggregate_score": 4.4,
  "notes": ["Warmup took 2.1s", "Both agents used qwen3:14b-instruct"]
}
```

### Interpretation

- Both agents scored high (4.3, 4.5) on this Q1-class question. K8sGPT's Rating (5.0 in `chains.csv`) is borne out; HolmesGPT (Rating 4.5) matches expectation.
- The confidence is `0.98` because the run was local, deterministic, and the model was warmed.
- Reproducing this benchmark with the same seed + model + question should yield scores within a narrow band; scoring variance is bounded by the backend's temperature/sampling configuration.

## Reproducibility

- **Commands**: record the exact CLI + env vars. Example above is reproducible verbatim once Ollama is pulling `qwen3:14b-instruct`.
- **Backend**: state the backend URL and model. Different backends can give different scores for the same prompt.
- **Seed**: if the backend supports deterministic sampling, declare the seed. Today, Ollama's determinism depends on model + sampler configuration.
- **Cost**: for non-local runs, record the `CostEstimationResponse` (`projected_cost_usd`, `cost_high_usd`, `confidence_score`) alongside the benchmark output.
- **Warmup**: a cold run and a warmed run will differ. The warmup pass is documented in [CURRENT_STATE §Conventions](../context/CURRENT_STATE.md) and in the `backend_warmup: true` config key.

## Further reading

- [Agent Access Tiers](TIERS.md) — Tier 1/2/3 access and licensing detail.
- [External projects](../external-projects/index.md) — adopt RUNE components standalone.
- [ADR 0005: Advanced Cognitive Architecture](../architecture/adrs/0005-advanced-cognitive-architecture.md) — design for chain execution.
- [API Specification](API_SPEC.md) — REST interface to benchmarks.
