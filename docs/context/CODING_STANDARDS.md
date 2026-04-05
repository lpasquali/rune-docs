# CODING_STANDARDS

## Specific Stylistic Rules

- **Python**: Use `black` and `ruff`. Follow PEP 8.
- **Go**: Use `gofmt` and `staticcheck`.
- **Typing**: Use type hints in Python.
- **Testing**:
  - **97% is the absolute floor** (CI gate); however, **100% coverage is the expected target** for all new code if achievable.
  - **No "Cheating"**: Coverage must be earned through meaningful tests, including edge cases and error paths. Do not use excessive "happy path" mocking or `pragma: no cover` to artificially inflate scores.
  - Unit tests should be safe/offline (mock boundaries).
  - Manual tests (e.g., cloud resource creation) must be explicitly marked or handled separately.
- **Documentation**:
  - Keep `rune-docs` as the single source of truth.
  - All public APIs and CLI commands must be documented.

- **Visual Documentation**:
  - **Mermaid.js Only**: Use Mermaid.js for all architectural diagrams.
  - **No Binaries**: BANNED: PNG, JPG, or other binary formats.

- **Agent Support & Licensing**:
  - **Tiered Support Matrix**: Support is graded by licensing: Tier 1 (OSS, 100% Support) to Tier 3 (Closed SaaS, Protocol-only/No Support).
  - **No-Bundling Policy**: BANNED: Bundling any non-compatible COTS (Commercial Off-The-Shelf) binaries, proprietary code, or licensed artifacts.
  - **Clean Room Integration**: Closed-source agents must be integrated via the decoupled `DriverTransport` layer; the RUNE codebase must remain 100% free of proprietary "black box" code.

- **State Integrity (SSOT)**:
  - **Single Source of Truth**: All project-specific state, WIP, bugs, and "living memory" must reside in `rune-docs/docs/context/CURRENT_STATE.md`.
  - **No External State**: BANNED: Gists, external notes, or project-specific facts stored in an agent's global memory. 
  - **Global Memory Usage**: Use `save_memory` ONLY for global user preferences (e.g., identity, hardware facts, stylistic defaults). Never use it for project-level state.
  - **Atomic Persistence**: Every task must end with an update to `CURRENT_STATE.md` if the system state has evolved.
- **Structure**:
  - Prefer thin entrypoints; keep business logic in `rune_bench/`.
  - Use protocols/interfaces for pluggable components (e.g., `DriverTransport`).
- **Security**:
  - Do not commit secrets or API keys.
  - Use environment variables for sensitive configuration.
  - All PRs require review and passing CI gates.
