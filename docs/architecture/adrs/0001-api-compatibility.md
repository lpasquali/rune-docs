 
# ADR 0001: RUNE Client/Server Compatibility

 
## Status

Accepted

 
## Context

Goal: keep the current CLI UX unchanged while enabling a cloud-native API backend suitable for Kubernetes Operators and CRDs.

 
## Decision

1.  **Stable Contracts**: Use request/response dataclasses as stable contracts for each operation.
2.  **Pluggable Backends**: Implement a `Backend` protocol with `LocalBackend` (in-process) and `HttpBackend` (remote).
3.  **Opt-in HTTP Mode**: CLI defaults to local but can switch to HTTP via environment or flag.
4.  **Async Job Model**: Remote operations are async (submit + poll) to handle long-running provisioning.

 
## Consequences

- CLI remains consistent for users.
- Server implementation can evolve independently.
- Overhead of HTTP calls is added when in `http` mode.
- Requires job persistence (SQLite) on the server.
