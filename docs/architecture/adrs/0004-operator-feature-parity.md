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

## Consequences
- Requires a new minor release of the CRD (`v1alpha2` or an updated `v1alpha1`).
- Ensures the Operator adheres to the ML4 cost-safety constraints defined in the `SYSTEM_PROMPT.md`.
- Allows declarative scheduling of any Tier 1, 2, or 3 agent supported by the ecosystem.
