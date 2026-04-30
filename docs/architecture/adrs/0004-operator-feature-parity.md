# ADR 0004: Operator Feature Parity

## Status
Proposed

## Context
The current `rune-operator` CRD (`RuneBenchmark`) is missing key fields required to achieve full feature parity with the `rune` core engine. Specifically, it lacks:
1. **Agent Routing (`Agent`)**: The ability to specify which agent to run (currently locked to HolmesGPT).
2. **Cost Safety (`Pre-Flight Estimates`)**: The reconciliation loop submits jobs without checking the fail-closed cost estimation gates.
3. **Attestations (`AttestationRequired`)**: The ability to demand SLSA L3 signed provenance from the core engine.

## Decision
To bring the Operator up to the state of the art defined by the platform's API:
1. Update `api/v1alpha1/runebenchmark_types.go` to include `Agent string` and `AttestationRequired bool`.
2. Modify `controllers/runebenchmark_controller.go` to explicitly issue a `POST /v1/estimates` call and halt reconciliation if the confidence score is `< 0.95`.

### Scope of the estimates pre-flight gate

The `POST /v1/estimates` call must be issued **only for workflows that involve cloud cost** — specifically when `spec.VastAI` is `true`. For local-only workflows (`VastAI: false`), the estimates call is skipped because there is no cloud cost to gate. This avoids creating a hard dependency on the estimates endpoint for zero-cost jobs.

### Field mapping: CRD spec to CostEstimationRequest

| CRD field (`RuneBenchmarkSpec`) | Estimates field (`CostEstimationRequest`) | Notes |
|---|---|---|
| `VastAI` | `vastai` | Direct mapping |
| `MinDPH` | `min_dph` | Direct mapping |
| `MaxDPH` | `max_dph` | Direct mapping |
| `Model` | `model` | Direct mapping |
| `TimeoutSeconds` | `estimated_duration_seconds` | Use `TimeoutSeconds` as the duration estimate; default `3600` if unset |

AWS, GCP, Azure, and local hardware fields should be set to their zero-value defaults (the operator does not currently support these providers).

### Field semantics

- **`Agent string`**: Added to `RuneBenchmarkSpec`. Used only by the `agentic-agent` workflow — inserted into `buildPayload()` for that case. Defaults to `"holmes"` if empty (matching the core API default). The `benchmark` and `llm-instance` workflows ignore this field.
- **`AttestationRequired bool`**: Added to `RuneBenchmarkSpec`. Used by the `benchmark` workflow — forwarded as `attestation_required` in `buildPayload()`. The `agentic-agent` and `llm-instance` workflows ignore this field.

### CRD regeneration

The operator uses kubebuilder markers but has **no Makefile or `controller-gen` toolchain wired in**. After modifying `runebenchmark_types.go`:

1. **DeepCopy** (`zz_generated.deepcopy.go`): `Agent` (string) and `AttestationRequired` (bool) are value types — no pointer handling needed. Update the `DeepCopyInto` method for `RuneBenchmarkSpec` manually by adding the two field copies.
2. **CRD YAML** (`config/crd/bases/bench.rune.ai_runebenchmarks.yaml`): Add the two new properties under `spec.properties` manually.
3. **Helm CRD distribution**: Copy the updated CRD YAML to `rune-charts/charts/rune-operator/crds/` (create the directory if needed). Helm applies CRDs before templates automatically.

### Sample CR update

Update `config/samples/bench_v1alpha1_runebenchmark.yaml` with:
```yaml
spec:
  agent: "holmes"                 # Optional: defaults to "holmes" for agentic-agent workflow
  attestationRequired: false      # Optional: require SLSA L3 attestation for benchmark workflow
```

## Consequences
- Requires updating the CRD structure within the existing `v1alpha1` API version. Avoid bumping the API version (e.g., to `v1alpha2`) unless it becomes a hard blocker, to minimize disruption to existing users.
- Ensures the Operator adheres to the ML4 cost-safety constraints defined in the `SYSTEM_PROMPT.md`.
- Allows declarative scheduling of any Tier 1, 2, or 3 agent supported by the ecosystem.
- Helm chart for `rune-operator` gains a `crds/` directory, enabling CRD distribution via Helm for the first time.
