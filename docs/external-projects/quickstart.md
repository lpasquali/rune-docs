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

## 2. Bootstrap config

At the **root of the repo you want to audit**:

```bash
cd /path/to/your/repo
rune-audit init -y --org my-org --repos core --no-project-file
# or interactive: rune-audit init
```

This writes **`compliance-config.yaml`** (and optionally **`.rune-audit-project.yaml`**). Validate the project file if you use it:

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

## 4. Multi-repo matrix dashboard (optional)

From a **parent directory** that contains sibling clones named like your **`compliance-config.yaml`** `project.repos` entries:

```bash
cd ~/Devel
rune-audit sr2 dashboard --base-path . --format html -o sr2-dashboard.html
rune-audit sr2 dashboard --base-path . --format json -o sr2-dashboard.json
rune-audit sr2 dashboard --single-repo --format md
```

Use **`--previous sr2-dashboard.json`** on a second run to emit a **trend delta** in HTML/JSON output. See [rune-docs#212](https://github.com/lpasquali/rune-docs/issues/212).

## 5. Next steps

- Add a reusable workflow: [CI integration](ci-integration.md).
- Register real checks: [Custom inspectors](custom-inspectors.md).
- Read the SR-Q catalog: [Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md).
