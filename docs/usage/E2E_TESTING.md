 
# End-to-End Testing — Binding Contract

!!! note "Spec v0 — scripts ship in [rune-docs#271](https://github.com/lpasquali/rune-docs/issues/271) Phase 1"
    This page is the **authoritative contract** for the Level-1 E2E path across the
    RUNE ecosystem. Phase 0 (this page + linked SYSTEM_PROMPT / DEVELOPER_GUIDE /
    WORKSTATION edits) lands first and defines the directory layout, command
    surface, and PR-body marker that the per-repo wrapper scripts (Phase 1) and
    the `rune-ci/pr-compliance.yml` content validator (Phase 2) must match. Until
    Phase 1 ships, follow the [Developer Guide Step 1/2/3 commands](DEVELOPER_GUIDE.md#definition-of-done-validation-steps)
    and assemble evidence by hand against the layout below.

This page exists because the DoD Level 1 requirement
([SYSTEM_PROMPT.md §Definition of Done](../context/SYSTEM_PROMPT.md#definition-of-done-pre-pr))
mandates three E2E modes — docker-compose, kind, and standalone CLI — but the
per-repo commands historically lived in the Developer Guide with no single
one-command entrypoint, no defined evidence bundle, and no agent-friendly
background-run recipe. PRs silently fell back to lower levels because the
friction of a full Level-1 run exceeded the 2-minute agent bash timeout.

 
## Preflight (read-only)

Before Step 7 of the SOP, confirm the tooling on your workstation matches what
`scripts/e2e.sh` expects. Run the
[Workstation Verification Checklist](../operations/WORKSTATION.md#verification-checklist)
verbatim — it reports pinned versions for `python3.14`, `docker compose`,
`kind`, `kubectl`, and `helm`. **Do not** auto-install missing tooling from an
agent context; if anything is missing, open an `area/infra` issue and continue
with whichever modes the current host supports (the `summary.md` layout below
records each mode independently so a partial run is still reviewable).

 
## Scope — which modes apply to your change

The scope table below mirrors the DoD classification from
[DEVELOPER_GUIDE.md §Definition of Done — Validation Steps](DEVELOPER_GUIDE.md#definition-of-done-validation-steps).
It does **not** invent a new classification. Misclassifying a change is a
merge blocker because the `RuneGate/Process/PR-Body-Compliance` check in
`rune-ci` validates the declared DoD level against the changed file set.

| Changed file glob | Required modes | Why |
|---|---|---|
| `rune/rune_bench/**/*.py`, `rune/rune/**/*.py` | compose + kind + cli | Runtime / API / drivers / agents |
| `rune-ui/rune_ui/**/*.py`, `rune-ui/rune_ui/templates/**` | compose + kind + cli (with UI screenshots) | UI runtime — screenshot required per SYSTEM_PROMPT §Evidence |
| `rune-charts/charts/**` | compose + kind | Helm deployment surface |
| `rune-operator/{api,controllers,internal}/**/*.go` | compose + kind + cli | Operator runtime |
| `rune-audit/rune_audit/**/*.py` | compose + kind + cli | Runtime |
| `rune-airgapped/scripts/**/*.sh` | compose (bundle smoke) | Airgapped smoke |
| `*/Dockerfile*`, `*/docker-compose.yml` | compose + kind + cli | Image surface |
| `.github/workflows/**` | none (covered by CI) | Level 2 per DoD |
| `**/tests/**`, `**/*.py` tests-only | none | Level 2 |
| `rune-docs/docs/**`, `rune-docs/mkdocs.yml` | none | Level 3 (`mkdocs build --strict`) |

If a single PR touches files across multiple rows, take the **most demanding**
row's required modes. When in doubt, run all three.

 
## One-command entrypoint contract

Every ecosystem repo that owns Level-1-applicable code ships a `scripts/e2e.sh`
wrapper implementing this contract. Phase-1 PRs add the wrappers; until they
land, the contract documents what the wrappers must produce.

### Synopsis

```text
scripts/e2e.sh --mode <compose|kind|cli|all> \
               --artifacts <dir> \
               [--keep] \
               [--timeout <seconds>]
```

### Arguments

| Flag | Values | Default | Meaning |
|---|---|---|---|
| `--mode` | `compose`, `kind`, `cli`, `all` | required | Which E2E mode to run. `all` runs each mode sequentially, halting on first failure. |
| `--artifacts` | path | `./e2e-artifacts` | Output directory for the evidence bundle. Created if missing; existing contents preserved in a sibling `e2e-artifacts.<timestamp>/` before the new run starts. |
| `--keep` | — | off | Skip teardown on failure (leave the compose stack or kind cluster up for manual inspection). Default is teardown-on-any-exit. |
| `--timeout` | seconds | `600` (cold compose) / `900` (cold kind) / `120` (cli) | Per-mode wall-clock cap. Exceeding the cap is treated as `FAIL`. |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All requested modes reached `PASS`. |
| `1` | One or more modes reached `FAIL`. |
| `2` | Pre-flight failure (missing tool, docker daemon unreachable, `kind` binary absent). No `STATUS` file written. |
| `64` | Bad usage (unknown flag, missing `--mode`). |

### Idempotency

- Running back-to-back without `--keep` is idempotent: each invocation tears
  down its own stack/cluster before exiting.
- Running back-to-back with `--keep` on the same host will refuse to start a
  second run if it detects a prior leftover stack (compose project name
  `rune-e2e`, kind cluster name `rune-e2e`). Stop the prior run or
  `--artifacts` to a different directory.

### Teardown on failure

Default is teardown on any exit (success or failure). Wrappers implement this
as a `trap` registered before the run starts. `--keep` disables the trap for
diagnostic workflows.

 
## Evidence bundle layout

The wrapper writes exactly this structure. Phase-2's
`rune-ci/.github/workflows/pr-compliance.yml` parses `summary.md`;
reviewers read the rest. Do not rename files — the marker string and the
directory names are part of the contract.

```text
e2e-artifacts/
├── summary.md              # PR-body-ready digest (see "PR-body marker" below)
├── STATUS                  # atomic file: "RUNNING" | "PASS" | "FAIL"
├── env.txt                 # tool versions: docker compose version, kind --version, python -V, git rev-parse HEAD
├── compose/
│   ├── up.log              # `docker compose up -d --build` stdout+stderr
│   ├── services.txt        # `docker compose ps` snapshot
│   ├── healthz.json        # per-service /healthz probe results
│   └── logs/
│       ├── rune-api.log
│       ├── rune-ui.log
│       ├── rune-docs.log
│       ├── ollama.log
│       └── seaweedfs.log
├── kind/
│   ├── create.log          # `kind create cluster` + image loads
│   ├── helm-install.log    # `helm install rune` + `helm install rune-operator`
│   ├── kubectl-events.txt  # `kubectl get events -A --sort-by=.lastTimestamp`
│   ├── kubectl-describe/   # `describe` for each non-Ready pod
│   └── pod-logs/           # last 500 lines from each pod
├── cli/
│   ├── help.txt            # `python -m rune --help` stdout
│   ├── run.log             # `python -m rune run-benchmark ...` stdout+stderr
│   └── exit_code           # integer
├── screenshots/            # only for rune-ui + rune-docs changes
│   ├── dashboard.png
│   ├── configuration.png
│   └── benchmark-sse.png
└── playwright-traces/      # retain-on-failure only
    └── *.zip
```

### `STATUS` — atomic contract

The wrapper writes `RUNNING` at start, then atomically renames to `PASS` or
`FAIL` at end (`echo PASS > STATUS.tmp && mv STATUS.tmp STATUS`). Consumers
(humans polling from another shell, CI scripts waiting on a background run)
can read `STATUS` without race conditions.

### `summary.md` — PR-body digest

A Markdown document beginning with the **marker comment**:

```markdown
<!-- e2e-artifacts/summary.md -->
```

The Phase-2 `pr-compliance.yml` content validator requires this marker in the
PR body followed by non-empty content for any PR with the Level-1 checkbox
ticked. Pasting `summary.md` verbatim into the PR body satisfies the check.

Expected sections (the wrapper generates these; reviewers do not edit them):

```markdown
<!-- e2e-artifacts/summary.md -->

## E2E results — <repo>@<commit-sha-short>

| Mode | Status | Duration | Log |
|---|---|---|---|
| compose | PASS | 4m21s | [compose/up.log](e2e-artifacts/compose/up.log) |
| kind    | PASS | 7m58s | [kind/helm-install.log](e2e-artifacts/kind/helm-install.log) |
| cli     | PASS | 0m47s | [cli/run.log](e2e-artifacts/cli/run.log) |

**Environment**: Python 3.14.4 · docker 29.0.1 · kind v0.27.0 · helm v3.17.0
**Commit**: `<sha>` on `<branch>`
**Host**: `<hostname>` (Linux 6.8.0)

### Compose health
- rune-api:8080/healthz → 200 (12ms)
- rune-ui:3000/healthz → 200 (8ms)
- seaweedfs:8333 → reachable
- ollama:11434/api/tags → 200

### Kind pods
- 5/5 Ready in namespace rune-test

### CLI smoke
- `python -m rune --help` → exit 0
- `python -m rune run-benchmark --model llama3.1:8b --question "..."` → exit 0

### Screenshots
- dashboard.png (1024×768)
- configuration.png (1024×768)
- benchmark-sse.png (1024×768)
```

When a mode fails, its row is `FAIL`, a `### Failure detail` section is
appended with the last 50 lines of the relevant log, and `STATUS` ends at
`FAIL`.

 
## Agent-compatible execution

The two-minute default bash timeout in Claude Code and similar agents is
shorter than a cold `docker compose up --build` (≈5–10 min) and a cold `kind
create cluster` + helm install (≈8 min). Run the wrapper as a background job
and poll `STATUS`.

### Claude Code — background tool call

```text
Bash(command="scripts/e2e.sh --mode all --artifacts ./e2e-artifacts",
     run_in_background=true,
     timeout=900000)
```

Then periodically read `e2e-artifacts/STATUS`:

```bash
cat e2e-artifacts/STATUS   # RUNNING | PASS | FAIL
```

### Plain shell — `nohup` + poll

```bash
nohup scripts/e2e.sh --mode all --artifacts ./e2e-artifacts \
  > e2e-artifacts.stdout 2> e2e-artifacts.stderr &
E2E_PID=$!

# Poll every 10 seconds, bail after 20 minutes
for _ in $(seq 1 120); do
  status=$(cat e2e-artifacts/STATUS 2>/dev/null || echo WAITING)
  [ "$status" = "PASS" ] && break
  [ "$status" = "FAIL" ] && break
  sleep 10
done
wait "$E2E_PID"
```

### Timeout expectations (reference, not a contract)

| Mode | Cold (first run on a host) | Warm (image cache + kind cluster reused with `--keep`) |
|---|---|---|
| compose | 5–10 min | 60–90 s |
| kind | 6–8 min | 2–3 min |
| cli | 30–60 s | 30–60 s |
| all (cold) | 12–18 min | — |

A wall-clock 30+ minutes without `STATUS` flipping to `PASS`/`FAIL` indicates
the run is stuck (usually docker pulls or `kind load docker-image` on
constrained bandwidth); capture `e2e-artifacts/compose/up.log` and attach it
to an `area/infra` issue rather than retrying blindly.

 
## Attaching evidence to a PR

Two artifacts ship with every Level-1 PR:

1. **`summary.md` pasted into the PR body**, replacing the
   `## Test Plan Evidence` section of the repo's
   `.github/PULL_REQUEST_TEMPLATE.md`. The marker comment
   (`<!-- e2e-artifacts/summary.md -->`) must be preserved verbatim so the
   Phase-2 content validator can find it.
2. **The binary bundle** (screenshots, playwright traces, pod logs) uploaded
   as a workflow artifact by the `e2e-verify` reusable workflow (Phase 2) or
   attached to the PR as a comment when running from a developer workstation.

### `gh pr create` recipe

```bash
# After a green scripts/e2e.sh run:
cat > /tmp/pr-body.md <<EOF
## Summary

$CHANGE_DESCRIPTION

Closes #$ISSUE
Epic: #$EPIC

## DoD Level

- [x] **Level 1 — Full Validation** (runtime, API, Helm, Dockerfile)

## Level 1 Checklist

- [x] Tested in **docker-compose mode**
- [x] Tested in **kind (Kubernetes) mode**
- [x] Tested in **standalone CLI mode**
- [x] **Breaking change audit**: API versions, persistent data, cross-component contracts
- [x] **Dependency CVE audit**: pip-audit — no new CVEs

## Audit Checks

No triggers fired.

## Acceptance Criteria Evidence

- [x] <criterion 1> [evidence: e2e-artifacts/compose/up.log]
- [x] <criterion 2> [screenshot: e2e-artifacts/screenshots/dashboard.png]

## Test Plan Evidence

$(cat e2e-artifacts/summary.md)

## Breaking Changes

None.
EOF

gh pr create --draft \
  --title "feat(runtime): <change>" \
  --body-file /tmp/pr-body.md \
  --label claude_cli
```

Use `--draft` first — flip to **Ready for Review** only after CI is green and
`STATUS=PASS` is reflected in the body.

 
## Troubleshooting

### Docker daemon permission denied

```text
Got permission denied while trying to connect to the Docker daemon socket
```

Your user is not in the `docker` group. Re-run the
[WORKSTATION.md Docker section](../operations/WORKSTATION.md#docker)
(`sudo usermod -aG docker "$USER" && newgrp docker`) and verify with
`docker ps`.

### kind can't pull the image

```text
ERROR: failed to load image: ... not found
```

Build the image locally first, then `kind load docker-image`:

```bash
docker build -t rune:e2e .
kind load docker-image rune:e2e --name rune-e2e
```

The Phase-1 wrapper does this automatically; if you are running the commands
by hand during the Phase-0-to-Phase-1 interval, follow the Developer Guide
Step 3 block.

### Compose healthcheck timing out

Prefer `127.0.0.1` in healthchecks — a healthcheck pointing at `0.0.0.0`
binds but doesn't probe, masking startup failures. See
[SYSTEM_PROMPT.md §DoD Level 1](../context/SYSTEM_PROMPT.md#definition-of-done-pre-pr)
("Healthchecks: prefer `127.0.0.1`").

### Cross-repo dependency conflicts

Symptoms: `pip install` into a combined venv surfaces `ResolutionImpossible`
between `rune` and `rune-ui`. This is expected — each repo pins its own
Python floor (`rune >=3.11`, `rune-ui >=3.12`) and the per-repo venv model in
[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#python-repositories-rune-rune-ui-rune-docs)
is the default. If you need to audit cross-repo compatibility, use the
optional [combined-venv check](../operations/WORKSTATION.md#optional-combined-venv-dependency-check).

### Kind create cluster hangs on image load

Known on constrained-bandwidth hosts pulling `kindest/node` cold. Pre-pull:

```bash
docker pull kindest/node:v1.35.0
```

Then retry `scripts/e2e.sh --mode kind`.

 
## Phase-1 / Phase-2 readiness checklist

A reviewer of this page alone — without looking at any repo's wrapper script
— should be able to predict:

- [x] The **exact directory layout** the wrapper produces (see [Evidence bundle layout](#evidence-bundle-layout)).
- [x] The **marker string** the PR-body validator matches (`<!-- e2e-artifacts/summary.md -->`).
- [x] The **command-line surface** every repo's wrapper shares (`--mode`, `--artifacts`, `--keep`, `--timeout`).

If any of those three is ambiguous to a reader, this page is incomplete —
open a rune-docs PR before any Phase-1 implementation ships.
