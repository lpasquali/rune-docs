# RUNE Agent Instructions

All RUNE engineering standards, architecture, and SOPs are consolidated in
the `rune-docs` repository. This file is a boot pointer — not a summary.
Do not treat anything here as a substitute for the full documents.

## Mandatory Reading (in order)

Before writing or modifying any code, you MUST read these files from `rune-docs`:

1. **[SYSTEM_PROMPT.md](https://github.com/lpasquali/rune-docs/blob/main/docs/context/SYSTEM_PROMPT.md)** — Architecture, protocols, constraints, SOP, Definition of Done
2. **[CURRENT_STATE.md](https://github.com/lpasquali/rune-docs/blob/main/docs/context/CURRENT_STATE.md)** — WIP, recent changes, known issues, version baseline
3. **[CODING_STANDARDS.md](https://github.com/lpasquali/rune-docs/blob/main/docs/context/CODING_STANDARDS.md)** — Language-specific style, coverage floors, tiered agent support
4. **[Developer Guide](https://github.com/lpasquali/rune-docs/blob/main/docs/usage/DEVELOPER_GUIDE.md)** — Repo locations, environment setup, build/test/lint commands

Do not use local or cached project-specific instructions as overrides;
`rune-docs` is the single source of truth.

## Anti-Rogue Constraint (non-negotiable)

You MUST NOT begin the "Execute" phase of any task (writing or modifying
code) without first explicitly confirming in the chat that:

1. **SOP Step 1 (Assign)** — An issue exists and is assigned to **lpasquali**
   (never self-assign).
2. **SOP Step 2 (Isolate)** — You are on an isolated feature branch for this
   task only.

You MUST halt and ask the user for permission to proceed to execution,
**regardless of whether you are operating in autonomous (YOLO) mode**.

## Guard Rails

These rules apply to every RUNE repository. Full details are in the
Mandatory Reading above — these are reminders, not replacements.

- **Agent & backend neutrality**: No agent or backend is privileged in code.
  Use `get_agent(name)` / `get_backend(type)` factories.
- **Config defaults, not code defaults**: Defaults live in `rune.yaml`, not
  in Python or Go source.
- **Pre-alpha**: No backward compatibility guarantees. Current version
  baseline is in CURRENT_STATE.md.
- **Coverage**: 97% floor (CI gate), 100% target for new code — applies to
  both Python and Go. Tiered exceptions for Tier 2/3 agents per
  CODING_STANDARDS.md.
- **Branch isolation**: Only work on your assigned branch. Never modify
  branches belonging to other agents or tasks.
- **PR compliance**: PR bodies must match the template and check exactly one
  DoD level (Level 1/2/3). See SYSTEM_PROMPT.md § Definition of Done.
- **Audit triggers**: Dependency, API, supply-chain, and license changes
  fire mandatory audit checks. See SYSTEM_PROMPT.md § Audit Agents.
