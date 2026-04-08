 
# Developer Guide

This guide covers everything a human or agent needs to start developing on the RUNE platform: repository layout, environment setup, build/test/lint commands per repo, and how to validate changes against the Definition of Done.

 
## Repository Map

All repositories live under `~/Devel/` on the development machine.

| Directory | Language | Purpose |
|---|---|---|
| `rune/` | Python (>= 3.11, CI uses 3.14) | Core platform: CLI, orchestration, drivers, backends, API server |
| `rune-operator/` | Go (1.25) | Kubernetes operator for CRD-based job scheduling |
| `rune-ui/` | Python (>= 3.12, CI uses 3.14) | HTMX frontend (FastAPI + Jinja2, zero NPM) |
| `rune-charts/` | Helm | Kubernetes deployment charts for all components |
| `rune-docs/` | Python (MkDocs) | Documentation hub (single source of truth) |
| `rune-audit/` | YAML/Markdown | Compliance and audit evidence |
| `rune-airgapped/` | Shell (POSIX) | Air-gapped OCI bundle tooling |
| `rune-ci/` | GitHub Actions YAML | [Shared CI workflows and composite actions](../delivery/CI_SHARED_WORKFLOWS.md) |

 
## Environment Setup

If you are starting from a fresh Ubuntu 24.04 LTS machine, see the [Workstation Setup](../operations/WORKSTATION.md) guide first to install all required tooling (Python, Go, Docker, Kind, Helm, kubectl, scanners).

### Python Repositories (rune, rune-ui, rune-docs)

```bash
cd ~/Devel/rune  # or rune-ui, rune-docs

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# For rune only — install dev extras:
pip install -e ".[dev]"
```

### Go Repository (rune-operator)

```bash
cd ~/Devel/rune-operator

go mod download
# or
go mod tidy
```

Requires Go >= 1.25.

### Helm Charts (rune-charts)

```bash
# Requires: helm CLI
helm lint ./charts/rune
helm lint ./charts/rune-operator
helm lint ./charts/rune-ui
```

### Shell Scripts (rune-airgapped)

```bash
# Requires: shellcheck, yamllint
sudo apt-get install shellcheck yamllint
```

 
## Build, Test, and Lint Commands

### rune (Python)

```bash
cd ~/Devel/rune
. .venv/bin/activate

# Unit tests (97% coverage floor enforced)
pytest

# Feature tests only (no coverage enforcement)
pytest -p no:cov -o addopts='' tests/ -m "not regression" -v --tb=short

# Regression tests only
pytest -p no:cov -o addopts='' -m regression tests/ -v --tb=short

# Integration tests (requires live Ollama)
export OLLAMA_TEST_URL=http://localhost:11434
pytest -m integration

# Lint
ruff check rune rune_bench
mypy rune rune_bench

# SAST
bandit -r rune rune_bench
```

### rune-operator (Go)

```bash
cd ~/Devel/rune-operator

# Unit tests (99.5% coverage floor enforced in CI)
go test ./...

# With coverage report — use this to verify the 99.5% floor locally
go test ./... -coverprofile=coverage.out -covermode=atomic
go tool cover -func=coverage.out
# Check the "total" line — must be >= 99.5%

# Format check (must produce no output)
test -z "$(gofmt -l .)"

# Vet
go vet ./...

# SAST
gosec -fmt json -severity high ./...

# CVE scan (required before any PR that changes go.mod)
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...
```

**CRD and code generation**: The operator uses kubebuilder markers but has no Makefile or `controller-gen` wired in. After modifying `api/v1alpha1/runebenchmark_types.go`:

1. Update `api/v1alpha1/zz_generated.deepcopy.go` manually (value-type fields just need a field copy line in `DeepCopyInto`).
2. Update `config/crd/bases/bench.rune.ai_runebenchmarks.yaml` manually (add properties under `spec.properties`).
3. Copy the updated CRD YAML to `rune-charts/charts/rune-operator/crds/` so Helm distributes it.

**Test patterns**: All controller tests use `net/http/httptest` for fake API servers and `sigs.k8s.io/controller-runtime/pkg/client/fake` for fake k8s clients. Override-able function vars (`jsonMarshal`, `setupControllerWithManager`) enable failure injection. Follow the same patterns for new tests.

### rune-ui (Python)

```bash
cd ~/Devel/rune-ui
. .venv/bin/activate

# Unit tests (97% coverage floor enforced)
pytest

# Feature tests only
pytest -p no:cov -o addopts='' tests/ -m "not regression" -v --tb=short

# Lint
ruff check rune_ui
mypy rune_ui

# SAST
bandit -r rune_ui -ll
```

### rune-charts (Helm)

```bash
cd ~/Devel/rune-charts

# Lint all charts
helm lint ./charts/rune
helm lint ./charts/rune-operator
helm lint ./charts/rune-ui

# Template render (dry run)
helm template rune ./charts/rune > /tmp/rune-rendered.yaml

# SAST
docker run --rm -v "${PWD}:/work" aquasec/trivy:0.65.0 config --severity HIGH,CRITICAL --exit-code 1 /work
```

### rune-docs (MkDocs)

```bash
cd ~/Devel/rune-docs
. .venv/bin/activate

# Build (strict mode — warnings are errors)
mkdocs build --strict

# Local preview server
mkdocs serve

# Markdown lint
pymarkdown scan README.md docs
```

### rune-airgapped (Shell)

```bash
cd ~/Devel/rune-airgapped

# Lint all scripts
shellcheck scripts/*.sh

# YAML validation
yamllint .
```

 
## Definition of Done — Validation Steps

The validation scope is **proportional to the change**. See [SYSTEM_PROMPT.md — Definition of Done](../context/SYSTEM_PROMPT.md) for the full policy. In summary:

| Level | Applies to | What to do |
|---|---|---|
| **Level 1 — Full** | Runtime code, APIs, drivers, agents, Helm, Dockerfiles | All three deployment modes + breaking change audit + CVE audit |
| **Level 2 — Test Infra** | Test config, CI workflows, coverage settings, linter configs | Full test suite + verify coverage not degraded + check side effects |
| **Level 3 — Docs** | Markdown, MkDocs config, diagrams in `rune-docs` | `mkdocs build --strict` + peer review |

When in doubt, use Level 1. Below are the concrete commands for Level 1 validation.

### Step 1: Standalone CLI Mode

```bash
cd ~/Devel/rune
. .venv/bin/activate

export RUNE_BACKEND=local
export RUNE_BACKEND_URL=http://localhost:11434

# Verify the CLI starts and responds
python -m rune --help

# Run a benchmark (adjust model/question to exercise your change)
python -m rune run-benchmark \
  --model llama3.1:8b \
  --question "Why is the cluster unhealthy?"
```

### Step 2: Docker Compose Mode

The full local stack is defined in `~/Devel/rune/docker-compose.yml`.

```bash
cd ~/Devel/rune

# Build and start the stack
docker compose up -d --build

# Services:
#   rune-api    → http://localhost:8080
#   rune-ui     → http://localhost:3000
#   rune-docs   → http://localhost:8000
#   ollama      → http://localhost:11434
#   seaweedfs   → http://localhost:8333 (S3)

# Verify health
curl -s http://localhost:8080/healthz
curl -s http://localhost:3000/healthz

# Exercise your change through the API or UI

# Tear down
docker compose down -v
```

### Step 3: Kind (Kubernetes) Mode

```bash
cd ~/Devel/rune-charts

# Create a Kind cluster
kind create cluster --name rune-test

# Install the charts
kubectl create namespace rune-test
helm install rune ./charts/rune --namespace rune-test --wait --timeout=2m
helm install rune-operator ./charts/rune-operator --namespace rune-test --wait --timeout=2m

# Verify pods are running
kubectl -n rune-test get pods

# Port-forward and test
kubectl -n rune-test port-forward svc/rune-api 8080:8080 &
curl -s http://localhost:8080/healthz

# Exercise your change

# Clean up
kind delete cluster --name rune-test
```

### Step 4: Breaking Change Audit

Before opening the PR, verify:

- **API versions**: Did you change any request/response schema? Is it additive or breaking?
- **Persistent data**: Did you change SQLite schemas or volume mount paths? Is there a migration path?
- **Cross-component contracts**: Did you change DriverTransport, AgentRunner, LLMBackend, or LLMResourceProvider protocols?
- **Helm values**: Did you add/remove/rename any values.yaml keys?

### Step 5: Dependency CVE Audit

If your change introduces or updates any dependency:

```bash
# Python repos
pip-audit

# Go repos
govulncheck ./...

# Container images
docker run --rm -v "${PWD}:/work" anchore/grype:v0.82.0 dir:/work
```

A PR that introduces a new CVE is never acceptable. Resolve it before opening the PR or report to `lpasquali` with the CVE ID, CVSS score, and reason resolution failed.

 
## Coverage Floors

| Repo | Floor | Enforced by |
|---|---|---|
| rune | 97% | `pytest.ini` `--cov-fail-under=97` |
| rune-operator | 99.5% | CI Python script; locally check `go tool cover -func=coverage.out` total line |
| rune-ui | 97% | `pyproject.toml` `--cov-fail-under=97` |

Target is always 100%. The floor is the hard gate.

 
## Secret Scanning

All repos run `gitleaks` in CI. Never commit secrets, API keys, or tokens. Use environment variables (see [Configuration](CONFIGURATION.md)).

 
## CI Workflows

Every repo follows the same CI pattern in `.github/workflows/quality-gates.yml`:

1. **Path-change detection** — only runs relevant jobs based on changed files.
2. **Coverage** — hard floor per repo.
3. **Linting** — language-specific (ruff/mypy, gofmt/govet, helm lint, pymarkdown, shellcheck).
4. **SAST** — bandit (Python), gosec (Go), trivy config (Helm).
5. **Container build** — if Dockerfile changed.
6. **SBOM + CVE scan** — Syft, Grype, Trivy on built images.
7. **Secret scan** — gitleaks.
8. **Merge Gate** — aggregates all jobs; required status check for merge.

No repo has a Makefile or Taskfile. All automation lives in GitHub Actions.

 
## GitHub Process Enforcement

The project enforces its development process through GitHub mechanisms — not through trust. Humans and agents follow the same rules because CI rejects PRs that skip steps.

### Issue Templates

All repos use structured issue templates (`.github/ISSUE_TEMPLATE/`). Blank issues are disabled. Every issue must declare:
- **Priority** (p0–p3)
- **Area** label
- **DoD level** (for feature requests)
- **Acceptance criteria** with required audit check placeholders
- **Test plan evidence** requirements

### PR Template

Every PR auto-populates from `.github/PULL_REQUEST_TEMPLATE.md` with mandatory sections:

1. **Issue reference** — must link to an issue (`Closes #NNN`)
2. **DoD level** — must check exactly one (Level 1, 2, or 3)
3. **Level-specific checklist** — the appropriate checklist for the declared level
4. **Audit checks table** — must report PASS/FAIL for each triggered check, or state "No triggers fired"
5. **Acceptance criteria evidence** — each criterion must be ticked with evidence attached
6. **Test plan evidence** — screenshots, logs, diffs as required by the issue
7. **Breaking changes** — must be declared or explicitly "None"

### CI Enforcement (`pr-body-check`)

The `RuneGate/Process/PR-Body-Compliance` CI job validates the PR body before merge is allowed:

- Rejects PRs with no issue reference
- Rejects PRs with no DoD level checked
- Rejects PRs with missing Acceptance Criteria or Audit Checks sections
- Rejects PRs with any `FAIL` audit result in the table
- Rejects PRs with missing Breaking Changes section

This job is part of the Merge Gate — if it fails, the PR cannot be merged.

### CODEOWNERS

`.github/CODEOWNERS` requires review from `@lpasquali` for changes to sensitive paths (`.vex/`, `.github/workflows/`). Even if the automated ML4 peer review approves the PR, CODEOWNERS can require an additional human review for specific file patterns.

 
## Adding Documentation Pages (rune-docs)

When creating a new page in `rune-docs`:

1. **Create the Markdown file** under `docs/` in the appropriate subdirectory:
   - `docs/usage/` — user-facing guides, references, quickstarts
   - `docs/operations/` — deployment, observability, runbooks, workstation
   - `docs/delivery/` — CI/CD, releases, secrets, compliance
   - `docs/architecture/` — design docs, formal specs, ADRs
   - `docs/context/` — system prompt, current state, coding standards (rarely add new files here)

2. **Add a nav entry** in `mkdocs.yml` under the appropriate section. Without a nav entry, the page is orphaned and `mkdocs build --strict` may warn.

3. **Validate**:
   ```bash
   cd ~/Devel/rune-docs
   . .venv/bin/activate
   mkdocs build --strict       # Must pass with no warnings
   pymarkdown scan README.md docs  # Markdown lint
   mkdocs serve                # Preview at http://localhost:8000
   ```

4. **Cross-reference the SSOT**: If the page presents data that also lives in a canonical source (e.g., `chains.csv` for agent tiers), link to the source and note that it is authoritative. Do not duplicate data without linking.

5. **DoD Level 3** applies: `mkdocs build --strict` + peer review. No deployment-mode validation needed.
