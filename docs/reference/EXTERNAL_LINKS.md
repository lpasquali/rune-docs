# External Links & Official Documentation

Canonical catalog of official documentation and specification URLs for every standard RUNE complies with and every third-party tool or platform component RUNE uses. Both humans reading the docs and agents consulting them should start here when they need an authoritative upstream URL.

Each row contains the full URL as bare text so that automated tooling (grep, `awk`, LLM extraction) can lift URLs without parsing markdown link syntax. The same URLs appear as hyperlinks for one-click navigation.

Contents:

- [1. Compliance Standards & Specifications](#1-compliance-standards-specifications)
- [2. Security & Compliance Tools](#2-security-compliance-tools)
- [3. Development Tools](#3-development-tools)
- [4. Platform & Infrastructure](#4-platform-infrastructure)
- [5. RUNE Repositories](#5-rune-repositories)
- [Freshness & updates](#freshness-updates)

---

## 1. Compliance Standards & Specifications

RUNE claims alignment with — or targets compliance against — the following standards. Links point to the official source of each spec; paywalled standards also include a free overview URL.

| Name | Version | Official URL | Notes |
|---|---|---|---|
| IEC 62443-4-1 (Secure product development lifecycle) | 2018 | <https://webstore.iec.ch/publication/33615> | Paywalled (IEC Webstore) |
| IEC 62443 series — ISA overview | — | <https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards> | Free overview of the full series |
| SLSA — Supply-chain Levels for Software Artifacts | v1.0 | <https://slsa.dev/spec/v1.0/> | RUNE targets Level 3 |
| SLSA — project site | — | <https://slsa.dev/> | Landing + tooling |
| SLSA Provenance predicate | v1 | <https://slsa.dev/spec/v1.0/provenance> | Build attestation format |
| OWASP Top 10 | 2021 | <https://owasp.org/www-project-top-ten/> | Web application risks |
| OWASP Web Security Testing Guide | v4.2 | <https://owasp.org/www-project-web-security-testing-guide/> | Pentest methodology |
| OWASP API Security Top 10 | 2023 | <https://owasp.org/www-project-api-security/> | API risk categories |
| NIST SP 800-61r2 — Computer Security Incident Handling Guide | rev 2 | <https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final> | Incident response baseline |
| NIST SP 800-30r1 — Guide for Conducting Risk Assessments | rev 1 | <https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final> | Risk assessment methodology |
| NIST Cybersecurity Framework | 2.0 | <https://www.nist.gov/cyberframework> | Core governance reference |
| Microsoft STRIDE threat-modelling taxonomy | — | <https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats> | Threat categories |
| PTES — Penetration Testing Execution Standard | — | <http://www.pentest-standard.org/> | Pentest execution stages |
| SPDX — Software Package Data Exchange | 2.3 | <https://spdx.dev/> | SBOM format |
| SPDX License List | — | <https://spdx.org/licenses/> | License identifiers used in SPDX headers |
| Semantic Versioning | 2.0.0 | <https://semver.org/> | Release versioning rules |
| in-toto attestation framework | v1 | <https://in-toto.io/> | Provenance foundation |
| CVSS — Common Vulnerability Scoring System | 3.1 | <https://www.first.org/cvss/v3-1/specification-document> | CVE severity scoring |
| CycloneDX SBOM | 1.5 | <https://cyclonedx.org/specification/overview/> | Alternative SBOM format |
| Conventional Commits | 1.0.0 | <https://www.conventionalcommits.org/en/v1.0.0/> | Commit message format |
| Keep a Changelog | 1.1.0 | <https://keepachangelog.com/en/1.1.0/> | Changelog format |

## 2. Security & Compliance Tools

Tools invoked by RUNE CI, security workflows, or compliance evidence collection.

| Tool | Docs URL | Use in RUNE |
|---|---|---|
| Sigstore | <https://docs.sigstore.dev/> | Signing infrastructure |
| cosign | <https://docs.sigstore.dev/cosign/overview/> | Container image signing |
| Rekor | <https://docs.sigstore.dev/logging/overview/> | Transparency log |
| Fulcio | <https://docs.sigstore.dev/certificate_authority/overview/> | Keyless signing CA |
| gitleaks | <https://github.com/gitleaks/gitleaks> | Secret scanning (CI) |
| Trivy | <https://trivy.dev/> | Container CVE + config scan |
| Grype | <https://github.com/anchore/grype> | Container CVE scan |
| Syft | <https://github.com/anchore/syft> | SBOM generation |
| pip-audit | <https://pypi.org/project/pip-audit/> | Python CVE audit |
| pip-licenses | <https://pypi.org/project/pip-licenses/> | Python license check |
| govulncheck | <https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck> | Go CVE audit |
| go-licenses | <https://github.com/google/go-licenses> | Go license check |
| Bandit | <https://bandit.readthedocs.io/> | Python SAST |
| gosec | <https://github.com/securego/gosec> | Go SAST |
| CodeQL | <https://codeql.github.com/docs/> | Static analysis (CI) |
| Dependabot | <https://docs.github.com/en/code-security/dependabot> | Dependency updates |
| TLA+ Tools | <https://lamport.azurewebsites.net/tla/tools.html> | Formal specs |
| TLA+ Toolbox | <https://lamport.azurewebsites.net/tla/toolbox.html> | Model checker UI |
| VS Code TLA+ extension | <https://marketplace.visualstudio.com/items?itemName=alygin.vscode-tlaplus> | Editor support |
| tpm2-tools | <https://tpm2-tools.readthedocs.io/> | TPM attestation |
| OpenSSF Scorecard | <https://scorecard.dev/> | Supply-chain security grading |

## 3. Development Tools

Per-language and per-format tooling used across RUNE repositories.

### Python

| Tool | Docs URL | Use in RUNE |
|---|---|---|
| Python Language Reference | <https://docs.python.org/3/> | Language reference (3.14) |
| black | <https://black.readthedocs.io/> | Formatter |
| ruff | <https://docs.astral.sh/ruff/> | Linter |
| mypy | <https://mypy.readthedocs.io/> | Type checker |
| pytest | <https://docs.pytest.org/> | Test runner |
| pytest-cov | <https://pytest-cov.readthedocs.io/> | Coverage plugin |
| coverage.py | <https://coverage.readthedocs.io/> | Coverage engine |
| respx | <https://lundberg.github.io/respx/> | httpx mocking |
| Hypothesis | <https://hypothesis.readthedocs.io/> | Property-based / fuzz testing |
| httpx | <https://www.python-httpx.org/> | HTTP client |
| Typer | <https://typer.tiangolo.com/> | CLI framework |
| Pydantic | <https://docs.pydantic.dev/> | Data validation |
| FastAPI | <https://fastapi.tiangolo.com/> | API framework (rune-ui) |
| Jinja2 | <https://jinja.palletsprojects.com/> | Templating (rune-ui) |

### Go

| Tool | Docs URL | Use in RUNE |
|---|---|---|
| Go Language | <https://go.dev/doc/> | Language reference (1.25) |
| gofmt | <https://pkg.go.dev/cmd/gofmt> | Formatter |
| go vet | <https://pkg.go.dev/cmd/vet> | Correctness checks |
| staticcheck | <https://staticcheck.dev/> | Static analysis |
| Go native fuzzing | <https://go.dev/doc/security/fuzz/> | Fuzz testing |
| Kubebuilder | <https://book.kubebuilder.io/> | Operator scaffolding |
| controller-runtime | <https://pkg.go.dev/sigs.k8s.io/controller-runtime> | Operator framework |

### Docs / Markdown / Shell / YAML

| Tool | Docs URL | Use in RUNE |
|---|---|---|
| MkDocs | <https://www.mkdocs.org/> | Docs site builder |
| MkDocs Material | <https://squidfunk.github.io/mkdocs-material/> | Docs theme |
| mike | <https://github.com/jimporter/mike> | MkDocs version manager |
| PyMarkdown | <https://github.com/jackdewinter/pymarkdown> | Markdown linter |
| Mermaid.js | <https://mermaid.js.org/> | Diagrams (only diagram format allowed) |
| shellcheck | <https://www.shellcheck.net/> | Shell linter |
| yamllint | <https://yamllint.readthedocs.io/> | YAML linter |

## 4. Platform & Infrastructure

Runtime components, LLM backends, agents, and infrastructure that RUNE integrates with.

### LLM backends and agents

| Component | Docs URL | Use in RUNE |
|---|---|---|
| Ollama | <https://ollama.com/> | Default local LLM backend |
| Ollama API reference | <https://github.com/ollama/ollama/blob/main/docs/api.md> | HTTP API |
| LiteLLM | <https://docs.litellm.ai/> | Multi-provider router |
| HolmesGPT | <https://github.com/robusta-dev/holmesgpt> | SRE diagnostics agent |
| LangGraph | <https://langchain-ai.github.io/langgraph/> | Multi-agent orchestration |
| CrewAI | <https://docs.crewai.com/> | Agent framework |
| Model Context Protocol (MCP) | <https://modelcontextprotocol.io/> | Agent context protocol |
| A2A Protocol | <https://a2aproject.github.io/A2A/> | Agent-to-agent interop |
| InvokeAI | <https://invoke-ai.github.io/InvokeAI/> | Art/creative agent |
| ComfyUI | <https://docs.comfy.org/> | Art/creative agent |

### Compute & provisioning

| Component | Docs URL | Use in RUNE |
|---|---|---|
| Vast.ai | <https://vast.ai/docs/> | GPU provisioning resource |
| Crossplane | <https://docs.crossplane.io/latest/> | Infrastructure provisioning (ADR 0007) |

### Kubernetes & deployment

| Component | Docs URL | Use in RUNE |
|---|---|---|
| Kubernetes | <https://kubernetes.io/docs/> | Orchestration platform |
| kubectl | <https://kubernetes.io/docs/reference/kubectl/> | K8s CLI |
| Helm | <https://helm.sh/docs/> | Package manager |
| kind | <https://kind.sigs.k8s.io/> | Local K8s (CI + dev) |
| Pod Security Admission | <https://kubernetes.io/docs/concepts/security/pod-security-admission/> | PSA restricted baseline |
| Gateway API Inference Extension | <https://gateway-api-inference-extension.sigs.k8s.io/> | Planned `k8s-inference` backend |
| CloudNativePG | <https://cloudnative-pg.io/> | PostgreSQL operator (ADR 0006) |
| CloudNativePG Helm charts | <https://cloudnative-pg.github.io/charts> | CNPG distribution |

### Secrets & storage

| Component | Docs URL | Use in RUNE |
|---|---|---|
| HashiCorp Vault | <https://developer.hashicorp.com/vault/docs> | Secrets management |
| Vault Agent Injector | <https://developer.hashicorp.com/vault/docs/platform/k8s/injector> | K8s secret injection |
| SeaweedFS | <https://github.com/seaweedfs/seaweedfs> | S3-compatible object store (local dev) |
| SQLite | <https://www.sqlite.org/docs.html> | Default embedded store |
| PostgreSQL | <https://www.postgresql.org/docs/> | Scale-out store target (ADR 0006) |

### Container & CI/CD

| Component | Docs URL | Use in RUNE |
|---|---|---|
| Docker | <https://docs.docker.com/> | Container runtime |
| Docker Compose | <https://docs.docker.com/compose/> | Local stack |
| OCI Image Spec | <https://github.com/opencontainers/image-spec> | Image format |
| GitHub Actions | <https://docs.github.com/en/actions> | CI/CD platform |
| GitHub Actions build-type attestation | <https://actions.github.io/buildtypes/workflow/v1> | SLSA builder reference |
| crane | <https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane.md> | Registry CLI (airgapped) |
| zot registry | <https://zotregistry.dev/> | Airgapped OCI registry |
| Helmfile | <https://helmfile.readthedocs.io/> | Multi-chart orchestration |
| Cilium | <https://docs.cilium.io/> | CNI (airgapped) |

## 5. RUNE Repositories

GitHub repositories that make up the RUNE platform. All under the [`lpasquali`](https://github.com/lpasquali) user.

| Repo | URL | Purpose |
|---|---|---|
| rune | <https://github.com/lpasquali/rune> | Core Python platform (CLI, API, drivers, backends) |
| rune-operator | <https://github.com/lpasquali/rune-operator> | Kubernetes operator (Go) |
| rune-ui | <https://github.com/lpasquali/rune-ui> | HTMX frontend |
| rune-charts | <https://github.com/lpasquali/rune-charts> | Helm charts |
| rune-docs | <https://github.com/lpasquali/rune-docs> | This documentation hub |
| rune-audit | <https://github.com/lpasquali/rune-audit> | Compliance & audit evidence service |
| rune-airgapped | <https://github.com/lpasquali/rune-airgapped> | Air-gapped OCI bundle tooling |
| rune-ci | <https://github.com/lpasquali/rune-ci> | Shared GitHub Actions workflows |

## Freshness & updates

- Add a row here whenever rune-docs introduces a new external dependency, tool, or compliance claim.
- If an upstream URL moves, update it here first and then grep the docs for any stale inline references to fix.
- For paywalled standards (IEC), link to the official webstore entry and, when available, a free overview page.
- Version columns should reflect the version RUNE currently targets or cites, not simply the latest upstream release.
