# Security Requirements

| ID | Description | Source Threat | Priority | Verification Method | Acceptance Criteria |
|---|---|---|---|---|---|
| SR-001 | The API server MUST authenticate all requests using a token with minimum 256-bit entropy | STRIDE/Spoofing — API | P0 | Integration test: unauthenticated request returns HTTP 401 | CI test passes |
| SR-002 | All API request bodies MUST be validated against a defined schema before processing | STRIDE/Tampering — API | P0 | Unit test: malformed body returns HTTP 400 | CI test passes |
| SR-003 | Error responses from the API server MUST NOT include internal stack traces in production mode | STRIDE/InfoDisc — API | P1 | Manual: trigger error in prod config; verify response body | No traceback in response |
| SR-004 | The DriverTransport protocol MUST validate all incoming JSON payloads against a defined schema | STRIDE/Tampering — Driver | P0 | Unit test: invalid payload raises `ValidationError` | CI test passes |
| SR-005 | Drivers MUST run as non-root with all unnecessary Linux capabilities dropped | STRIDE/EoP — Driver | P0 | Container inspection: `USER` != root; `--cap-drop ALL` | CI scan passes |
| SR-006 | The Vast.ai API token MUST be stored in an environment variable and MUST NOT appear in logs | STRIDE/InfoDisc — Vast.ai | P0 | Log scrub test: token pattern not present in captured logs | CI test passes |
| SR-007 | Cost estimation MUST fail closed: if confidence < 95%, GPU provisioning MUST be rejected | STRIDE/DoS — Vast.ai | P0 | Unit test: low-confidence estimate raises `CostGateError` | CI test passes |
| SR-008 | All container images MUST be signed with `cosign` using keyless Sigstore/OIDC signing | SLSA L3 — supply chain | P1 | `cosign verify <image>` succeeds in CI post-push | CI step passes |
| SR-009 | All GitHub Actions MUST be pinned to full SHA digests, not mutable version tags | SLSA L3 — supply chain | P1 | `grep -r "@v" .github/` returns zero matches | CI grep step |
| SR-010 | SBOMs MUST be attached as GitHub Release assets and retained for the lifetime of the release | NIST SP 800-218 PS.3 | P1 | Release asset list includes `sbom.json` after tag push | Manual release check |