 
# SYSTEM_DESIGN

Mermaid.js diagrams and system boundaries for RUNE.

 
## High-Level Architecture

RUNE is a multi-layered platform for AI benchmarking and provisioning.

```mermaid
flowchart TD
    subgraph Users
        CLI["rune CLI\n(Typer + Rich)"]
        UI["rune-ui\n(FastAPI + HTMX)"]
    end

    subgraph "Control Plane (RUNE Core)"
        API["rune-api\n(ThreadingHTTPServer)"]
        STORE[("Job Store\n(SQLite)")]
        WF["Workflows\n(Orchestration)"]
    end

    subgraph "Automation"
        OP["rune-operator\n(Go / Controller-runtime)"]
        CRD[("RuneBenchmark CRD\n(Scheduled Jobs)")]
    end

    subgraph "Execution Layer"
        DRV["Drivers\n(HolmesGPT, etc.)"]
        PRV["Providers\n(Vast.ai, Ollama)"]
    end

    subgraph "Storage & Metrics"
        S3[("S3 Sink\n(SeaweedFS / AWS)")]
        MET["Metrics\n(SQLite / Memory)"]
    end

    CLI <-->|"REST API"| API
    UI <-->|"BFF / REST"| API
    OP <-->|"Reconcile"| CRD
    OP -->|"POST /v1/jobs"| API
    API <--> STORE
    API --> WF
    WF --> DRV
    WF --> PRV
    WF --> S3
    WF --> MET
```

 
## Repository Layout

- **`rune/`**: The core engine.
  - `rune/`: CLI and API entrypoints.
  - `rune_bench/`: Core business logic (Workflows, Drivers, Backends, Resources).
- **`rune-operator/`**: Kubernetes operator for declarative scheduling.
- **`rune-ui/`**: Solarized web interface (Zero-NPM, HTMX-based).
- **`rune-charts/`**: Helm charts for all components.
- **`rune-docs/`**: Centralized documentation hub (SSOT).

 
## Agent Support & Licensing Matrix

RUNE maintains a "Clean Room" policy for all agent integrations.

```mermaid
graph TD
    subgraph SupportTiers ["Support & Licensing Matrix"]
        T1["Tier 1: OSS Native\n(100% Support)"]
        T2["Tier 2: Community\n(Limited Support)"]
        T3["Tier 3: Closed SaaS/COTS\n(No Support / Protocol-only)"]
    end

    subgraph IntegrationLayer ["Integration Logic"]
        NATIVE["Bundled Code & Driver"]
        COMMUNITY["Community-Maintained Driver"]
        PROTOCOL["Decoupled Protocol ONLY"]
    end

    subgraph BundlingPolicy ["Bundling & Compliance"]
        OK["Bundled in RUNE Core"]
        NO["BANNED FROM BUNDLING"]
    end

    T1 --> NATIVE --> OK
    T2 --> COMMUNITY --> NO
    T3 --> PROTOCOL --> NO

    style OK fill:#00ff0033
    style NO fill:#ff000033
```

### Supported Agents & Scopes

| Domain | Tier 1: OSS Native (Bundled) | Tier 2: Community | Tier 3: Closed/COTS (No Bundle) |
| :--- | :--- | :--- | :--- |
| **SRE** | K8sGPT, HolmesGPT, Metoro | — | PagerDuty AI, Cleric |
| **Research** | LangGraph | — | Perplexity, Glean, Elicit, Consensus |
| **Art/Creative** | ComfyUI | Krea AI | Midjourney |
| **Cybersec** | PentestGPT, BurpGPT | — | Radiant Security, Mindgard, XBOW |
| **Legal/Ops** | Dagger, CrewAI | — | Harvey AI, Spellbook, MultiOn |
| **DevTools/Code** | OpenHands, Plandex, Sweep | — | Claude Code, Cursor, GitHub Copilot |
| **Productivity** | OpenClaw, AutoGPT | Dify | OpenAI Operator, Sierra, Decagon |

### Emerging Integration Standards

RUNE prioritizes standardized, decoupled protocols for Tier 2 and Tier 3 agents:
- **MCP (Model Context Protocol)**: Universal standard for connecting agents to data/tools.
- **A2A (Agent-to-Agent)**: Protocols for autonomous negotiation between independent agent systems.

 
## Driver Layer Design

HolmesGPT and other agents are decoupled via the `DriverTransport` protocol.

```mermaid
flowchart LR
    A["API / CLI / Operator"] -->|"Workflow"| B["HolmesDriverClient"]
    B -->|"DriverTransport"| C{Transport Mode}
    C -->|"stdio"| D["Subprocess\npython -m rune_bench.drivers.holmes"]
    C -->|"http"| E["Remote REST\n/v1/actions/ask"]
    D --> F["HolmesGPT"]
    E --> F
```

 
## Job Lifecycle (RuneBenchmark Operator)

The operator manages the lifecycle of scheduled benchmarks.

```mermaid
stateDiagram-v2
    [*] --> Scheduled: Cron Trigger
    Scheduled --> JobSubmitted: POST /v1/jobs/benchmark
    JobSubmitted --> Polling: Job ID received
    Polling --> Succeeded: API returns 'succeeded'
    Polling --> Failed: API returns 'failed'
    Succeeded --> [*]
    Failed --> [*]
```

 
## RUNE UI Interaction (HTMX/SSE)

The UI acts as a thin BFF for the RUNE API.

```mermaid
sequenceDiagram
    participant U as User
    participant UI as rune-ui (BFF)
    participant A as rune-api
    
    U->>UI: Select Model & Question
    UI->>A: POST /v1/estimates
    A-->>UI: Cost Estimate
    UI-->>U: Show Pre-Flight Modal
    U->>UI: Confirm & Run
    UI->>A: POST /v1/jobs/benchmark
    A-->>UI: Job ID (202 Accepted)
    UI-->>U: Show Job Tracker
    loop Polling Status
        UI->>A: GET /v1/jobs/{id}
        A-->>UI: Current Status
        UI-->>U: Update Tracker (HTMX)
    end
    par Log Streaming
        UI->>A: GET /v1/jobs/{id}/events
        A-->>UI: Log Chunks (SSE)
        UI-->>U: Update Log Viewer (HMAC Signed)
    end
```
