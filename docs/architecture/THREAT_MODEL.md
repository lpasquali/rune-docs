# Threat Model

## API Server (`rune_bench/api_server.py`)
| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Spoofing | Unauthenticated caller impersonates legitimate client | Token-based auth on all endpoints |
| Tampering | Attacker modifies job payload in transit | HTTPS/TLS in production; input validation |
| Repudiation | No audit log of API calls | Structured request logging with timestamps |
| Information Disclosure | Error responses leak internal paths/stack traces | Sanitise error messages in production mode |
| Denial of Service | Unbounded request size causes OOM | Request size limits; rate limiting |
| Elevation of Privilege | API endpoint grants admin operations without authorisation | Role checks on destructive endpoints |

## Operator (`rune-operator`)
| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Spoofing | Malicious CRD submission by unprivileged user | Kubernetes RBAC restricts CRD writes |
| Tampering | Controller reconciles tampered CRD spec | Admission webhook validates spec fields |
| Repudiation | No audit trail for reconciliation actions | Operator logs all reconcile events |
| Information Disclosure | Operator logs expose sensitive config | Secrets redacted from structured logs |
| Denial of Service | Flood of CRD creates exhausts controller queue | Work queue depth limits |
| Elevation of Privilege | Operator service account over-privileged | Least-privilege RBAC role |

## DriverTransport Protocol
| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Spoofing | Malicious process connects to driver socket | Unix socket permissions; process ownership check |
| Tampering | JSON payload modified before driver receives it | Schema validation at driver boundary |
| Repudiation | Driver actions not auditable | All driver invocations logged with action + params hash |
| Information Disclosure | Driver output contains secrets from environment | Output scrubbing for known secret patterns |
| Denial of Service | Malformed JSON causes driver crash | Strict JSON schema validation; exception handling |
| Elevation of Privilege | Driver runs with elevated host permissions | Drivers run as non-root; capabilities dropped |

## Vast.ai Integration
| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Spoofing | Attacker uses stolen Vast.ai API token | Token stored in env var only; never in source |
| Tampering | Response from Vast.ai API is MITM-tampered | HTTPS with cert validation; response schema validation |
| Information Disclosure | API key exposed in logs | Token masked in all log output |
| Denial of Service | Runaway provisioning incurs excessive cost | Fail-closed cost estimation gate (95% confidence floor) |

## Ollama Integration
| STRIDE Category | Threat | Mitigation |
|---|---|---|
| Spoofing | Attacker points OLLAMA_HOST to malicious server | URL normalisation; warn on non-localhost targets |
| Tampering | Model response manipulated by MITM | HTTPS for remote Ollama; local-only recommended for production |
| Information Disclosure | Prompt content logged verbatim | Configurable log level; sensitive prompts redacted |
| Denial of Service | Ollama warmup blocks all other models | Warmup is intentional; document expected behaviour |