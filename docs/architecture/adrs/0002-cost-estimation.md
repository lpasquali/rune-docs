# ADR 0002: Cost Estimation (Pre-Flight Spend Alerts)

## Status
Proposed

## Context
As part of the `rune-ui` initiative, the `rune` core must be extended to provide cost estimation logic for all benchmarks *before* they are executed. This ensures that both the CLI and UI can provide consistent "Pre-Flight Spend Alerts."

## Decision
1.  **Unified Logic**: Centralize all cost calculation logic in the `rune_bench` core.
2.  **API Endpoint**: Implement `POST /v1/estimates` in `rune_bench/api_server.py`.
3.  **Estimation Drivers**:
    - **Cloud**: Vast.ai (current market rates), stubs for AWS/GCP/Azure.
    - **Local**: Energy consumption (TDP * rate * duration) and hardware amortization.

## Consequences
- CLI and UI can provide spend alerts before job submission.
- Consistent cost modeling across all interfaces.
- Requires maintenance of market rate queries and energy models.
