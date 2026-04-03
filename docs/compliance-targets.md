# Compliance Targets

This document is the single source of truth for the security and compliance posture that `rune` is currently designed to support.

It distinguishes between:

- **Primary explicit targets**: standards or control frameworks directly referenced by repository policy or CI.
- **Supporting security frameworks**: practices that inform implementation and evidence, but are not yet declared as formal certification targets.
- **Not yet declared targets**: standards that may be relevant later, but are not currently claimed by this repository.

## Primary Explicit Targets

### SLSA Level 3

`rune` is explicitly aiming for **SLSA Level 3-style supply-chain provenance evidence** for build artifacts.

Current evidence in the repo:

- provenance attestation permissions in .github/workflows/quality-gates.yml
- SBOM provenance attestation step labeled **SLSA L3** in .github/workflows/quality-gates.yml

Practical meaning for this project:

- signed or attested build provenance for generated artifacts
- CI-backed artifact traceability
- stronger supply-chain integrity controls around build outputs

### IEC 62443-4-1

`rune` is also explicitly aligning parts of its secure development lifecycle evidence with **IEC 62443-4-1** secure development practices.

Current evidence in the repo:

- SBOM provenance step labeled **IEC 62443 4-1 ML4 SM-9** in .github/workflows/quality-gates.yml
- SAST gate labeled **IEC 62443 4-1 ML4 SI-1 / SVV-1** in .github/workflows/quality-gates.yml

Practical meaning for this project:

- secure build/release evidence
- static analysis enforcement
- vulnerability handling and verification as part of the SDLC

### Enforced Repository Security Policy

In addition to named frameworks, `rune` explicitly enforces repository-level security controls documented in SECURITY.md.

Current required controls include:

- mandatory branch protection on key branches
- required passing merge gates before merge
- SBOM generation and multi-scanner analysis
- vulnerability threshold enforcement in CI

These are project policy requirements even where they do not map 1:1 to a public certification badge.

## Supporting Security Frameworks and Practices

These are not currently declared as formal certification targets in-repo, but the implementation direction is compatible with them.

### NIST SSDF / Secure SDLC Practices

The repository demonstrates several SSDF-style practices, including:

- automated SAST
- dependency and license scanning
- SBOM generation
- merge protection and required checks
- provenance-oriented release controls

This means SSDF is a useful internal design lens, even if not yet declared as an official target.

### General Software Supply-Chain Security

The current CI/CD posture also supports broader supply-chain security expectations through:

- pinned dependencies where practical
- artifact traceability
- SBOM generation and retention
- scanner aggregation and severity gating

## Not Yet Declared as Formal Targets

The repository does **not currently explicitly claim** any of the following as active compliance objectives:

- SOC 2
- ISO 27001
- FedRAMP
- PCI DSS
- HIPAA
- GDPR certification-style conformance
- CIS Benchmarks as a formal target set

These may still matter to downstream deployments or customers, but they are **not presently documented here as the repository's formal compliance targets**.

## Current Positioning Summary

If someone asks what `rune` is aiming for today, the most accurate short answer is:

> `rune` is currently oriented toward **secure software supply-chain evidence and secure SDLC controls**, with explicit emphasis on **SLSA Level 3 provenance-style attestation** and **IEC 62443-4-1-aligned development security evidence**, backed by mandatory CI security gates.

## Maintenance Rule

If new standards are adopted, this file should be updated first, and any workflow labels, README claims, and security-policy text should then be kept consistent with it.
