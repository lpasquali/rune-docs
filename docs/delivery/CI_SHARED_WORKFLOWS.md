
# CI Shared Workflows (rune-ci)

The [`rune-ci`](https://github.com/lpasquali/rune-ci) repository centralizes
reusable GitHub Actions workflows and composite actions for the entire RUNE
platform. Consumer repos call these shared workflows with thin callers
(typically 15-20 lines each), eliminating duplication across 8 repositories.

## Repository Structure

```text
rune-ci/
  .github/workflows/          # Reusable workflows (workflow_call)
    python-quality.yml         # Coverage + lint + SAST + license
    go-quality.yml             # Go test + fmt + vet + gosec + license
    security-scan.yml          # Gitleaks + optional SBOM scan
    container-build.yml        # Multi-arch Docker build (amd64 + arm64)
    release.yml                # Tag verify + build + manifest + GH Release
    helm-release.yml           # Helm chart packaging + GH Release
    helm-quality.yml           # helm lint + trivy config scan
    docs-quality.yml           # mkdocs build --strict + pymarkdown
    shell-quality.yml          # ShellCheck + YAMLLint
    pr-compliance.yml          # PR body validation + merge gate + ML4
    project-sync.yml           # Project board automation
    quality-gates.yml          # CI for CI (actionlint + yamllint)
  actions/                     # Composite actions
    gitleaks-scan/             # Secret scanning
    sbom-scan/                 # SBOM generation + CVE scanning
    license-check/             # License compliance (Python + Go)
    docker-setup/              # Docker login + buildx + cache metadata
  scripts/
    merge_gate.py              # Merge gate evaluator
```

## Reusable Workflows

### python-quality.yml

Python test coverage, linting (ruff), SAST (bandit), and license compliance.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `"3.12"` | Python version |
| `coverage-threshold` | number | `97` | Minimum coverage percentage |
| `requirements-file` | string | `"requirements.txt"` | Pip requirements file |
| `source-dir` | string | `"."` | Source directory for coverage |

### go-quality.yml

Go test coverage, formatting, vetting, static analysis (gosec), and license
compliance.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `go-version` | string | `"1.24"` | Go version |
| `coverage-threshold` | number | `80` | Minimum coverage percentage |

### security-scan.yml

Gitleaks secret scanning with optional SBOM + CVE scanning.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `gitleaks-version` | string | `"8.24.3"` | Gitleaks version |
| `run-sbom` | boolean | `false` | Enable SBOM + CVE scan |
| `image` | string | `""` | Container image for SBOM scan |

### container-build.yml

Multi-arch Docker image build (amd64 + arm64) with registry caching.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `image-name` | string | required | Image name |
| `registry-owner` | string | `"lpasquali"` | Registry owner |
| `dockerfile` | string | `"./Dockerfile"` | Dockerfile path |

### release.yml

Tag verification, multi-arch Docker build, manifest creation, GitHub Release,
optional SBOM generation, SLSA L3 attestation, and rune-charts notification.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `image-name` | string | `""` | Image name (required if `build-container` is true) |
| `registry-owner` | string | `"lpasquali"` | Registry owner |
| `dockerfile` | string | `"./Dockerfile"` | Dockerfile path |
| `build-container` | boolean | `true` | Build and publish container image |
| `notify-charts` | boolean | `false` | Send dispatch to rune-charts |
| `generate-sbom` | boolean | `false` | Generate CycloneDX SBOM |
| `slsa-attestation` | boolean | `false` | Generate SLSA L3 attestation |

| Secret | Required | Description |
|--------|----------|-------------|
| `RUNE_CHARTS_BOT_TOKEN` | No | PAT for cross-repo dispatch |

### helm-release.yml

Helm chart packaging and GitHub Release creation.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `charts-dir` | string | `"charts"` | Directory containing chart subdirectories |

### helm-quality.yml

Helm lint and Trivy configuration scanning.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `charts-dir` | string | `"charts"` | Directory containing chart subdirectories |

### docs-quality.yml

MkDocs strict build and pymarkdown linting.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `"3.12"` | Python version |
| `requirements-file` | string | `"requirements.txt"` | Pip requirements file |

### shell-quality.yml

ShellCheck and YAMLLint for shell scripts and YAML files.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `script-dirs` | string | `"scripts"` | Space-separated script directories |
| `script-glob` | string | `"*.sh"` | Glob pattern for shell scripts |

### pr-compliance.yml

PR body structure validation, merge gate aggregation, and ML4 automated
approval.

No configurable inputs. The workflow validates PR body sections (issue
reference, DoD level, Acceptance Criteria Evidence, Audit Checks, Breaking
Changes) and auto-approves after all gates pass.

### project-sync.yml

Automated project board synchronization. Sets Status (Todo/In progress/Done)
and Agent Lane (Claude/Gemini/Copilot/Human) based on issue/PR events and
labels.

| Secret | Required | Description |
|--------|----------|-------------|
| `PROJECT_TOKEN` | Yes | PAT with `project` scope |

## Composite Actions

### gitleaks-scan

Secret scanning using Gitleaks. Supports both PR (range-based) and push event
scanning.

### sbom-scan

SBOM generation with Syft, CVE scanning with Grype and Trivy, and policy
enforcement against a configurable CVSS threshold. Supports VEX suppression.

### license-check

License compliance checking for Python (pip-licenses) and Go (go-licenses)
ecosystems. Configurable blocklist and package-level exceptions.

### docker-setup

Docker login to GHCR, buildx setup, and cache metadata computation. Outputs
`full-image`, `cache-from`, and `cache-to` for use with `docker/build-push-action`.

## Versioning and Pinning

Consumer repos pin to a tagged version:

```yaml
uses: lpasquali/rune-ci/.github/workflows/release.yml@v0.1.0
```

The current version is **v0.1.0**. Tags are updated in-place during pre-1.0
development. After 1.0, tags will follow strict semver with immutable releases.

All third-party actions within rune-ci are SHA-pinned for supply chain security
(SLSA L3 compliance).

## Onboarding a New Repository

1. **Quality gates** -- copy `project-sync-caller-template.yml` to
   `.github/workflows/project-sync.yml` in the new repo.

2. **Create a quality-gates.yml** caller that invokes the appropriate shared
   workflows (python-quality, go-quality, security-scan, etc.) based on the
   repo's tech stack.

3. **Create a release.yml** caller that invokes `release.yml` (for container
   repos) or `helm-release.yml` (for Helm repos), or uses
   `build-container: false` (for non-container repos like rune-audit).

4. **Set secrets** at the org or repo level:
   - `PROJECT_TOKEN` -- PAT with `project` scope (required for project-sync)
   - `RUNE_CHARTS_BOT_TOKEN` -- PAT for cross-repo dispatch (only if
     `notify-charts: true`)

5. **Add the repo** to the project board and verify sync works by opening a
   test issue.

## Consumer Repo Examples

### Container repo with charts notification (rune, rune-ui)

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]
jobs:
  release:
    uses: lpasquali/rune-ci/.github/workflows/release.yml@v0.1.0
    with:
      image-name: "rune"
      notify-charts: true
    secrets:
      RUNE_CHARTS_BOT_TOKEN: ${{ secrets.RUNE_CHARTS_BOT_TOKEN }}
```

### Container repo with SBOM and SLSA (rune-docs)

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]
jobs:
  release:
    uses: lpasquali/rune-ci/.github/workflows/release.yml@v0.1.0
    with:
      image-name: "rune-docs"
      generate-sbom: true
      slsa-attestation: true
```

### Non-container repo (rune-audit)

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]
jobs:
  release:
    uses: lpasquali/rune-ci/.github/workflows/release.yml@v0.1.0
    with:
      build-container: false
```

### Helm repo (rune-charts)

```yaml
# .github/workflows/release.yml
name: Release Charts
on:
  push:
    tags: ["v*"]
jobs:
  release:
    uses: lpasquali/rune-ci/.github/workflows/helm-release.yml@v0.1.0
    with:
      charts-dir: "charts"
```
