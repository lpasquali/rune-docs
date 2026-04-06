 
# CODING_STANDARDS

 
## Specific Stylistic Rules

- **Python**: Use `black` and `ruff`. Follow PEP 8.
- **Go**: Use `gofmt` and `staticcheck`.
- **Typing**: Use type hints in Python.
- **Testing**:
  - **97% is the absolute floor** (CI gate); however, **100% coverage is the expected target** for all new code if achievable.
  - **TOE Exception (Airgapped)**: Components outside the formal Target of Evaluation (Tier 2/3 SaaS, external APIs) are exempt from the strict 100% coverage mandate. These are tested on a **best-effort basis**.
  - **Coverage measurement scope**: Only Tier 2/3 agents are excluded from measurement via `.coveragerc` `[report] omit`. Tier 1 agents must always be measured. **Warning**: if you change coverage omit rules to include previously-excluded code, verify that sufficient tests exist for the newly-measured code first. Adding code to measurement without corresponding tests will drop the project below the 97% floor and break CI. Audit test coverage before changing `.coveragerc`.
  - **Stub coverage**: Tier 1 agents that are stubs (`raise NotImplementedError`) must still be measured and tested. A test that calls the stub's entry point and asserts `pytest.raises(NotImplementedError)` is the correct and sufficient test for an unimplemented agent. This is not "cheating" — it verifies the stub contract and ensures the module is importable. Real implementation tests replace stub tests when the agent is implemented.
  - **CI/CD Script Exception**: Simple automation/pipeline scripts (e.g., in a `scripts/` directory) using only standard library primitives are exempt from unit test coverage. However, they **MUST** be extracted into `.py` files to guarantee they are scanned by SAST (Bandit) and Linters (Ruff/MyPy). Inline YAML scripts are **BANNED**.
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
  - **Tier Registry**: The authoritative agent-to-tier mapping is in `rune_bench/catalog/defaults/chains.csv` (the `Tier` column). This file is the single source of truth for which agents belong to which tier. Coverage and testing obligations follow directly from this classification:
    - **Tier 1**: OSS, fully testable, 100% coverage target, included in `.coveragerc` measurement.
    - **Tier 2**: Partial API access or freemium, best-effort coverage, may be omitted from measurement with justification.
    - **Tier 3**: Closed SaaS or no public API, protocol-only integration via `DriverTransport`, excluded from coverage measurement.
  - **Agent filesystem layout**: Agents live under `rune_bench/agents/` grouped by domain directory. The mapping from `chains.csv` `Scope` column to directory is:

    | Scope (chains.csv) | Directory |
    |---|---|
    | SRE | `rune_bench/agents/sre/` |
    | Research | `rune_bench/agents/research/` |
    | Art/Creative | `rune_bench/agents/art/` |
    | Cybersec | `rune_bench/agents/cybersec/` |
    | Legal/Ops | `rune_bench/agents/legal/` and `rune_bench/agents/ops/` |

    Agent filenames follow the pattern `<agentname_lowercase>.py`. Where the filename differs from the agent name in `chains.csv`, the mapping is:

    | Agent Name (chains.csv) | File | Rule applied |
    |---|---|---|
    | HolmesGPT | `holmes.py` | Shortened |
    | Radiant Security | `radiant.py` | First word only |
    | Perplexity Pro | `perplexity.py` | First word only |
    | PagerDuty AI | `pagerduty.py` | Strip suffix, merge |
    | Krea AI | `krea.py` | First word only |
    | Harvey AI | `harvey.py` | First word only |
    | Spellbook | `spellbook.py` | Direct lowercase |
    | LangGraph | `langgraph.py` | Direct lowercase |
    | BurpGPT | `burpgpt.py` | Direct lowercase |

    All other agents use direct lowercase with no spaces (e.g., K8sGPT → `k8sgpt.py`, PentestGPT → `pentestgpt.py`, CrewAI → `crewai.py`, ComfyUI → `comfyui.py`). When in doubt, check the filesystem under `rune_bench/agents/`.
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
