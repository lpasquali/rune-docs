# rune-operator quickstart

Install the operator into your cluster and apply a `RuneBenchmark` custom resource that points at **your** HTTP service (not necessarily rune-api).

## Prerequisites

- Kubernetes cluster ≥ 1.27 with `kubectl` configured.
- Helm ≥ 3.17.
- An HTTP service accepting JSON `POST` job submissions and exposing `GET /v1/jobs/{job_id}` for polling. If your service mimics rune-api's contract, no further changes are needed; otherwise adjust the operator's endpoint paths via chart values.

## Install

```bash
# Add and install via the rune-charts repo
git clone https://github.com/lpasquali/rune-charts.git
cd rune-charts

kubectl create namespace rune-operator
helm install rune-operator ./charts/rune-operator \
  --namespace rune-operator \
  --wait --timeout=3m

# CRDs ship in-chart at charts/rune-operator/crds/
kubectl get crd runebenchmarks.bench.rune.ai
```

## Apply a `RuneBenchmark`

```yaml
apiVersion: bench.rune.ai/v1alpha1
kind: RuneBenchmark
metadata:
  name: example-nightly
  namespace: default
spec:
  agent: custom-downstream-agent
  backendURL: http://my-service.default.svc:8080
  backendType: http
  backendWarmup: false
  pollIntervalSeconds: 30
  schedule: "0 2 * * *"    # 02:00 nightly
  budget:
    maxCostUSD: "1.50"
```

```bash
kubectl apply -f example-nightly.yaml
kubectl get runebenchmark example-nightly -o yaml
```

Watch reconciliation:

```bash
kubectl -n rune-operator logs -l app.kubernetes.io/name=rune-operator -f
```

## Budget gate in action

When `spec.budget.maxCostUSD` is set, the operator calls `GET /v1/finops/simulate` on your backend before submitting the job. If the backend returns `cost_high_usd` (preferred) or `projected_cost_usd` above the cap, the operator sets `Ready=False` with reason `BudgetExceeded` and does **not** submit.

## Idempotency

Each scheduled run produces an `Idempotency-Key: <namespace>/<name>/<generation>/<scheduleTime>` header on the submission. Your backend can use this to deduplicate retries safely.

## Next

- Full CRD reference: [rune-operator/api/v1alpha1/runebenchmark_types.go](https://github.com/lpasquali/rune-operator/blob/main/api/v1alpha1/runebenchmark_types.go).
- Helm values surface: [rune-charts/charts/rune-operator/values.yaml](https://github.com/lpasquali/rune-charts/blob/main/charts/rune-operator/values.yaml).
- Migration from older CRDs (`OllamaURL` → `BackendURL`): see [MIGRATION](../../usage/MIGRATION.md).
