# RUNE Documentation

**RUNE** (Reliability Use-case Numeric Evaluator) is an **agent-neutral, backend-neutral benchmarking and compute-provisioning platform** for AI agents — so that SREs, researchers, and regulated-industry teams can compare heterogeneous agents on reproducible, cost-controlled workloads.

RUNE runs 23+ agents across five scopes (SRE, Research, Cybersecurity, Legal/Ops, Art/Creative) with pluggable LLM backends and optional cloud-GPU provisioning. No agent and no backend is privileged in code — defaults live in `rune.yaml`, never hardcoded. Cost gates are **fail-closed** (GPU provisioning rejected when `confidence_score < 0.95`; local-only workflows skip gates). Releases carry SLSA L3-style provenance and are built to an IEC 62443-4-1 **ML4** process.

Pre-alpha today (`v0.0.0a5`) — API surfaces are not stable. See [CURRENT_STATE](context/CURRENT_STATE.md) for version-to-version status until a human-readable changelog lands under [epic #273](https://github.com/lpasquali/rune-docs/issues/273) child [#283](https://github.com/lpasquali/rune-docs/issues/283).

## Start here

Pick the card that matches your goal — each links to the page you should read first.

### Evaluator

I want to try RUNE in 10 minutes.

→ **[Quickstart](usage/QUICKSTART.md)** — three parallel paths: pip-CLI (5 min), docker-compose (10 min), kind + helm (15 min).

### Operator

I want to deploy RUNE in production — on-prem or on a cloud.

→ **[Deployment](operations/DEPLOYMENT.md)** — hosting modes + per-cloud install guides (on-prem / AWS / GCP / Azure / Alibaba Cloud, landing under `operations/INSTALL_*` as part of [#277](https://github.com/lpasquali/rune-docs/issues/277)). Observability, rollback, and runbooks all live under the [Operations](#operations) section below.

### Developer

I want to build against the API or extend RUNE with a new driver, backend, or agent.

→ **[Developer Guide](usage/DEVELOPER_GUIDE.md)** + **[API Specification](usage/API_SPEC.md)** + **[Interfaces](usage/INTERFACES.md)**. For the underlying extension protocols, see [SYSTEM_PROMPT §Extension points](context/SYSTEM_PROMPT.md#extension-points-protocols).

### Agent author

I want to ship a custom agent that plugs into RUNE via the `DriverTransport` protocol.

→ **Agents SDK** (new section landing under `agents/` as part of [epic #273](https://github.com/lpasquali/rune-docs/issues/273) child [#280](https://github.com/lpasquali/rune-docs/issues/280)). Until then: read [SYSTEM_PROMPT §Extension points](context/SYSTEM_PROMPT.md#extension-points-protocols) and [CODING_STANDARDS §Agent filesystem layout](context/CODING_STANDARDS.md).

### Compliance

I need to understand RUNE's regulatory and supply-chain posture.

→ **Compliance matrix** (new section landing under `compliance/` as part of [epic #273](https://github.com/lpasquali/rune-docs/issues/273) child [#282](https://github.com/lpasquali/rune-docs/issues/282)). Until then: [Security](#security) section below, [VEX Register](delivery/VEX.md), [Audit Agents](delivery/AUDIT_AGENTS.md).

### Adopter

I want to use a RUNE component standalone (rune-audit, rune-operator, rune-ui, rune-airgapped, or the driver SDK).

→ **[External projects](external-projects/index.md)** — currently the landing for rune-audit; sibling pages for rune-operator / rune-ui / rune-airgapped / driver-sdk are landing under child [#279](https://github.com/lpasquali/rune-docs/issues/279).

## Full documentation map

For readers who prefer the full outline over persona routing:

### Context

Instructions, state, and rules for agents and humans onboarding to the codebase.

- **[SYSTEM_PROMPT](context/SYSTEM_PROMPT.md)** — core identity, mandates, SOP.
- **[CURRENT_STATE](context/CURRENT_STATE.md)** — living memory, WIP, known issues.
- **[CODING_STANDARDS](context/CODING_STANDARDS.md)** — style, coverage floors, tier layout.

### Usage

How to interact with and configure RUNE.

- **[Quickstart](usage/QUICKSTART.md)** — getting started locally.
- **[Developer Guide](usage/DEVELOPER_GUIDE.md)** — repos, env, build/test/lint, DoD validation.
- **[Guide](usage/GUIDE.md)** — end-to-end walkthrough.
- **[Agent Access Tiers](usage/TIERS.md)** — tier 1/2/3 access and cost implications.
- **[Interfaces](usage/INTERFACES.md)** — CLI commands and API endpoints.
- **[API Specification](usage/API_SPEC.md)** — REST API reference.
- **[Advanced Pipelines](usage/ADVANCED_PIPELINES.md)** — chain DAG + audit artifact views.
- **[Configuration](usage/CONFIGURATION.md)** — environment variables and `rune.yaml`.
- **[LLM Backend Reference](usage/OLLAMA_REFERENCE.md)** — backend API surface.

### External projects

Adopt RUNE components on **non-RUNE** codebases. Currently populated for rune-audit.

- **[Overview](external-projects/index.md)**, [Quickstart](external-projects/quickstart.md), [Configuration](external-projects/configuration.md), [Inspector library](external-projects/inspector-library.md), [Custom inspectors](external-projects/custom-inspectors.md), [Requirement packs](external-projects/requirement-packs.md), [CI integration](external-projects/ci-integration.md), [Case study — RUNE](external-projects/case-study-rune.md).

### Delivery

How RUNE is built, tested, and shipped.

- **[Pipelines](delivery/PIPELINES.md)**, [Shared CI Workflows](delivery/CI_SHARED_WORKFLOWS.md), [CI Migration Risk Mitigations](delivery/CI_RISK_MITIGATIONS.md), [Releases](delivery/RELEASES.md), [Secrets](delivery/SECRETS.md), [VEX Register](delivery/VEX.md), [Milestones](delivery/MILESTONES.md), [Labels](delivery/LABELS.md), [Audit Agents](delivery/AUDIT_AGENTS.md).

### Operations

How RUNE is hosted and maintained.

- **[Workstation Setup](operations/WORKSTATION.md)** — development machine provisioning.
- **[Golden Image](operations/GOLDEN_IMAGE.md)** — automated provisioning across 30+ platforms.
- **[Deployment](operations/DEPLOYMENT.md)** — hosting modes (CLI / compose / kind / k8s-prod).
- **[Database Operations](operations/DATABASE.md)** + **[Database HA](operations/DATABASE_HA.md)** — SQLite today, PostgreSQL planned.
- **[Cost Management & Reporting](operations/COST_REPORTING.md)** — Infrastructure bootstrap vs. execution spend.
- **[Observability](operations/OBSERVABILITY.md)** — metrics and logging.
- **[Runbooks](operations/RUNBOOKS.md)** — incident response checklists.
- **[Rollback Procedures](operations/ROLLBACK_PROCEDURES.md)** — version, chart, and DB rollback.
- **[Vault Integration](operations/VAULT.md)** — secret injection.

### Security

RUNE's security posture, programme, and evidence.

- **[Security Development Lifecycle](security/SDL.md)**, [Risk Assessment Methodology](security/RISK_ASSESSMENT.md), [Risk Register](security/RISK_REGISTER.md), [Penetration Testing](security/PENTEST.md), [Fuzz Testing](security/FUZZ_TESTING.md), [Incident Response](security/INCIDENT_RESPONSE.md), [Container Image Signing](security/IMAGE_SIGNING.md), [Security Training Records](security/SECURITY_TRAINING.md).

### Architecture

How RUNE is designed internally.

- **[Threat Model](architecture/THREAT_MODEL.md)**, [Security Requirements](architecture/SECURITY_REQUIREMENTS.md), [System Design](architecture/SYSTEM_DESIGN.md), [Infrastructure](architecture/INFRASTRUCTURE.md), [Formal Specs](architecture/FORMAL_SPECS.md).
- **ADRs** — [0001 API Compatibility](architecture/adrs/0001-api-compatibility.md) · [0002 Cost Estimation](architecture/adrs/0002-cost-estimation.md) · [0003 UI Design](architecture/adrs/0003-ui-design.md) · [0004 Operator Parity](architecture/adrs/0004-operator-feature-parity.md) · [0005 Advanced Cognitive Architecture](architecture/adrs/0005-advanced-cognitive-architecture.md) · [0006 Storage Abstraction and PostgreSQL](architecture/adrs/0006-storage-abstraction-postgres.md).

## Project

- **Repository**: [github.com/lpasquali/rune-docs](https://github.com/lpasquali/rune-docs) (and sibling repos `rune`, `rune-operator`, `rune-ui`, `rune-charts`, `rune-audit`, `rune-airgapped`, `rune-ci`).
- **Security disclosure**: [SECURITY.md](https://github.com/lpasquali/rune-docs/blob/main/SECURITY.md) at the repo root.
- **Contributing**: [CONTRIBUTING.md](https://github.com/lpasquali/rune-docs/blob/main/CONTRIBUTING.md) — issue and PR process, DoD levels, evidence requirements.
- **Current state snapshot**: [CURRENT_STATE](context/CURRENT_STATE.md) — the living memory is the authoritative source for what is merged, pending, and known-broken.
