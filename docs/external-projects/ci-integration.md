# CI integration examples

## GitHub Actions (reusable workflow)

The **rune-ci** repository publishes **`sr2-compliance.yml`**, a **`workflow_call`** job that:

1. Checks out your repository.
2. Checks out **lpasquali/rune-audit** at a configurable ref.
3. Installs rune-audit with pip.
4. Runs **`rune-audit sr2 verify .`** with optional **`--strict`**.

**Caller example** (in `.github/workflows/sr2.yml`):

```yaml
name: SR-2
on:
  push:
    branches: [main]
  pull_request:

jobs:
  compliance:
    uses: lpasquali/rune-ci/.github/workflows/sr2-compliance.yml@main
    with:
      strict: false
      rune-audit-ref: main
```

Set **`strict: true`** when every SR-Q inspector you care about is implemented and must block merges.

Inputs (see workflow source for the authoritative list):

- **`python-version`** — default `3.14`
- **`strict`** — maps to `sr2 verify --strict`
- **`rune-audit-ref`** — branch/tag/SHA of rune-audit to install

## GitLab CI

```yaml
stages: [compliance]

sr2-verify:
  stage: compliance
  image: python:3.14-bookworm
  script:
    - git clone --depth 1 https://github.com/lpasquali/rune-audit.git /tmp/rune-audit
    - python -m pip install /tmp/rune-audit
    - rune-audit sr2 verify .
```

Add **`--strict`** to the last line when ready.

## Jenkins (declarative sketch)

```groovy
stage('SR-2') {
  steps {
    sh '''
      python -m pip install "git+https://github.com/lpasquali/rune-audit.git@main"
      rune-audit sr2 verify .
    '''
  }
}
```

## Secrets and provenance

SR-2 **verify** is designed to run on **checked-out source** without cloud credentials. Keep tokens out of the verification step; use separate jobs for publish/deploy.

## See also

- [Quickstart](quickstart.md)
- [CI_SHARED_WORKFLOWS.md](../delivery/CI_SHARED_WORKFLOWS.md) — how RUNE wires reusable workflows.
