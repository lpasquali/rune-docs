# Quickstart (about five minutes)

Goal: install **rune-audit**, create a project definition, and run **one** SR-2 verification pass on a repository.

## Prerequisites

- Python **3.12+** (3.14 used in shared CI workflows).
- A git checkout of the **target** repository (your OSS app, not necessarily RUNE).

## 1. Install rune-audit

From a virtualenv:

```bash
python -m pip install "git+https://github.com/lpasquali/rune-audit.git@main"
# or: pip install ./rune-audit   # when developing from a local clone
```

Confirm:

```bash
rune-audit --version
```

## 2. Create a project file

At the **root of the repo you want to audit**:

```bash
cd /path/to/your/repo
rune-audit sr2 init -o .rune-audit-project.yaml
```

This writes a starter file (see [Configuration](configuration.md)). Validate it:

```bash
rune-audit sr2 config-validate .rune-audit-project.yaml
```

## 3. Run verification

Non-strict (typical while inspectors are still stubs):

```bash
rune-audit sr2 verify .
```

Strict CI gate (fails with exit code **2** if any inspector is still `not_implemented`):

```bash
rune-audit sr2 verify . --strict
```

Optional filters and output:

```bash
rune-audit sr2 verify . --priority P0
rune-audit sr2 verify . --json
rune-audit sr2 gaps --priority P0
```

## 4. Next steps

- Add a reusable workflow: [CI integration](ci-integration.md).
- Register real checks: [Custom inspectors](custom-inspectors.md).
- Read the SR-Q catalog: [Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md).
