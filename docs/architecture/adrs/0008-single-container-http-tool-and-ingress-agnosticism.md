# ADR 0008: Single Container-Level HTTP Tool (Caddy) and Ingress-Agnostic Charts

## Status

Accepted

## Context

RUNE container images and Helm charts have accumulated two coupling points to **nginx** that create ongoing security and portability cost:

1. **Container-level coupling (rune-docs)**. `rune-docs/Dockerfile` uses `FROM nginx:1.27.4-alpine` to serve the statically-built MkDocs site. The Alpine-based `nginx` image bundles `libxml2`, which nginx itself does not link against in this deployment (`ldd /usr/sbin/nginx` shows no `libxml2` reference). Three libxml2 CVEs (`CVE-2024-56171`, `CVE-2025-49794`, `CVE-2025-49796`) are therefore justified as "code path unreachable" in `rune-docs/.vex/permanent.openvex.json`, but each upstream libxml2 CVE requires human review and a new VEX entry. This is recurring toil rooted in a transitive dependency the workload does not use.

2. **Chart coupling hints**. `rune-charts/charts/rune/values.yaml` and `values-airgapped-prod.yaml` include commented-out examples that steer operators toward nginx-ingress (`# kubernetes.io/ingress.class: nginx`, `# className: "nginx"`). The actual `templates/ingress.yaml` is already generic `networking.k8s.io/v1`, but the default examples privilege one controller over the alternatives (Envoy / Traefik / Cilium / Gateway API).

RUNE has no in-house reason to standardise on nginx at either layer. The container-level role is narrow — static-file serving today, possibly lightweight in-container proxying later — and the ingress-level choice should belong to the cluster operator.

## Decision

### Container level — single tool: Caddy

**RUNE container images SHALL NOT include nginx.** The single container-level HTTP tool is **[Caddy](https://caddyserver.com)**, consumed as the official `caddy:2-alpine` base image.

Rationale:

- **Memory safety.** Caddy is written in Go. The entire class of nginx C-level memory-corruption CVEs (buffer overflow, use-after-free, OOB read in DNS resolver / HTTP/3 / SSL client-hello handling) becomes non-applicable.
- **Supply-chain hygiene.** `caddy:2-alpine` does not include `libxml2`. The three libxml2 VEX entries in `rune-docs/.vex/permanent.openvex.json` stop being necessary and are deleted by the Dockerfile migration (rune-docs#297).
- **Role fit.** Caddy serves static sites and reverse-proxies behind a declarative Caddyfile / JSON config — a match for both the current role (serving MkDocs output) and plausible future in-container roles (sidecar proxies, TLS termination when a workload is not fronted by a k8s Service).
- **Default-secure.** Modern TLS, HSTS, automatic HTTPS via ACME are on by default; no extra hardening step is required in environments where in-container TLS is appropriate.
- **Size parity.** `caddy:2-alpine` is in the same ballpark (~45 MB) as `nginx:1.27.4-alpine`; no material image-size regression.

The **only** exemption is `rune/tests/test_k8sgpt_driver.py`, which uses the string `"nginx:nonexistent"` as a **test fixture** simulating a broken Pod image for the k8sgpt driver. This is test data, not a RUNE container, and is explicitly excluded from the CI regression lint (rune-ci#41) by path.

### Ingress level — charts are platform-agnostic

**RUNE Helm charts SHALL be ingress-agnostic.** Concretely:

1. Charts expose only the generic contract: `ingress.enabled`, `ingress.className`, `ingress.annotations`, `ingress.hosts`, `ingress.tls`. No controller-specific fields.
2. `ingress.className: ""` (the default) means "use the cluster's default IngressClass" — the one marked `ingressclass.kubernetes.io/is-default-class: "true"`. This is documented inline in every `values*.yaml`.
3. Example comments in values files use **neutral placeholders** (e.g. `# className: "traefik" | "envoy" | "cilium" | "istio"`). nginx is never suggested as the preferred choice.
4. Charts **MUST NOT** declare `ingress-nginx` as a Helm dependency (`Chart.yaml` or otherwise).
5. Charts **MUST NOT** emit `nginx.ingress.kubernetes.io/*` annotations in default values.
6. An opt-in Gateway API template (`gateway.networking.k8s.io/v1 HTTPRoute`) gated by `gatewayApi.enabled: false` is permitted as a **non-default** path for clusters that prefer Gateway API over Ingress (rune-charts#99).
7. `rune-ci` (#41) runs a regression lint that hard-fails any PR across the 8 RUNE repos that reintroduces `FROM nginx*`, `nginx.ingress.kubernetes.io/*`, an `ingress-nginx` chart dependency, or `kubernetes.io/ingress.class: nginx` outside documentation files.

The choice of ingress controller in any given deployment remains the **cluster operator's** responsibility. RUNE does not ship, recommend, or assume one.

### Out of scope

- **Service mesh layer.** Envoy, Linkerd2-proxy, Cilium Service Mesh, Istio sidecars — not a container-level concern and unaffected by this ADR.
- **Edge / CDN tier.** Any external-facing proxy in front of the cluster remains the operator's choice.
- **Switching k8s ingress controllers** in any existing deployment. This ADR changes chart defaults and example text, not running deployments.

## Alternatives Considered

| Alternative | Role fit | Why rejected for the container-level slot |
|---|---|---|
| **Envoy** (C++) | Ingress / mesh | Overkill for static serving; xDS config complexity far exceeds the role; C++ memory-safety is engineering discipline, not language-level. Remains the right choice at the **ingress** layer (opt-in via `ingress.className`). |
| **Cloudflare Pingora** (Rust) | Edge / high-throughput proxy | Memory-safe and excellent at the edge, but each use case requires Rust integration code; there is no drop-in static-serve path equivalent to Caddy's `file_server`. Better suited to public-edge deployments, which are out of scope for in-cluster RUNE images. |
| **Traefik** (Go) | Ingress controller | Memory-safe but designed as an ingress controller with provider auto-discovery, not as an in-container static server. Remains a valid choice at the ingress layer. |
| **HAProxy** (C) | L4 / L7 load balancer | Narrower than nginx and has a cleaner per-capability CVE record, but no native static-content serving. Wrong role. |
| **Distroless + tiny Go static-server binary** | Static serving only | Smaller attack surface than any of the above, but single-role: would require a second tool the moment any container needs reverse-proxying. Violates the "one solution at container level" goal stated in the epic. |
| **Keep nginx, accept the libxml2 VEX burden** | Status quo | Recurring maintenance cost; each libxml2 CVE forces a VEX update; the underlying coupling (C language, transitive `libxml2` in the base) does not improve over time. |

## Consequences

- **rune-docs image**: base becomes `caddy:2-alpine`; a minimal `Caddyfile` serves `/usr/share/caddy` with a standard static-site security-header set. Image size within ±10% of the previous nginx image.
- **VEX**: three libxml2 entries removed; future libxml2 CVEs do not require a rune-docs VEX response.
- **Airgapped bundle**: `INFRA_IMAGES` ships `caddy:2-alpine` instead of `nginx:1.27.4-alpine`; `architecture.md` tree diagram updated.
- **Charts**: values-file comments switch to neutral examples; existing template behavior is unchanged. Users relying on the cluster's default IngressClass see no difference.
- **CI**: a regression lint in `rune-ci` prevents reintroduction of any of the forbidden patterns.
- **Documentation**: `CURRENT_STATE.md` records the migration at epic closure.
- **Ops**: operators gain no new required knobs; charts keep the existing `ingress.className` field and default to platform.
- **Future in-container HTTP roles** (sidecars, TLS termination) have a designated tool (Caddy) and config shape (Caddyfile).

### Non-consequences (what does *not* change)

- Ingress controller choice in any running cluster.
- Mesh / sidecar posture.
- External CDN / edge configuration.
- Any user-visible URL, path, or behavior of the MkDocs site.

## Related References

- Epic [rune-docs#295](https://github.com/lpasquali/rune-docs/issues/295) — Eliminate nginx from RUNE container images; enforce ingress-agnostic charts
- [rune-docs#297](https://github.com/lpasquali/rune-docs/issues/297) — Dockerfile migration + VEX cleanup
- [rune-airgapped#86](https://github.com/lpasquali/rune-airgapped/issues/86) — Bundle base image swap
- [rune-charts#98](https://github.com/lpasquali/rune-charts/issues/98) — Values cleanup + `className` semantics
- [rune-charts#99](https://github.com/lpasquali/rune-charts/issues/99) — Optional Gateway API template
- [rune-ci#41](https://github.com/lpasquali/rune-ci/issues/41) — Regression lint
- ADR 0006: Storage abstraction and external PostgreSQL (related pattern: charts consume platform-provided primitives via a stable contract)
- Caddy documentation: <https://caddyserver.com/docs/>
- Gateway API: <https://gateway-api.sigs.k8s.io/>
