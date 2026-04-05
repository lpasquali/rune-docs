# ADR 0003: UI Design (Solarized 'Unix Guy' / Zero-NPM)

## Status
Accepted

## Context
Implement `rune-ui`, the "Face" (BFF) of the RUNE ecosystem. This component is a **thin interface** to the `rune-api`, providing a modular, observable dashboard.

## Decision
1.  **Zero NPM**: Strictly avoid JavaScript frameworks and NPM to minimize supply chain risks.
2.  **Tech Stack**: Python 3.14, FastAPI, HTMX, Jinja2.
3.  **Aesthetic**: "Modern Unix Guy" with Solarized theme and Fira Code typography.
4.  **Core Features**:
    - Modular configuration (fetched from `rune-api`).
    - Streaming log viewer via SSE/HTMX.
    - Pre-Flight Spend Alerts for projected costs.
    - S3-based report persistence.

## Consequences
- No NPM-related vulnerabilities.
- Server-driven UI (HTMX) simplifies state management.
- Limited client-side interactivity compared to SPA frameworks, but sufficient for RUNE's needs.
- Higher dependency on server-side rendering performance.
