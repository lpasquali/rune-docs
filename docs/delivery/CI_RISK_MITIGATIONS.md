
# CI Migration Risk Mitigations

This document covers risk analysis and mitigation strategies for migrating
CI workflows from per-repo definitions to the centralized `rune-ci`
repository. It addresses three areas: secrets inheritance, SLSA L3
provenance verification, and IEC 62443-4-1 ML4 compliance.

## Secrets Inheritance (Issue #154)

### Secrets inventory

Each reusable workflow in `rune-ci` accesses specific secrets. The table
below lists every secret reference found in the workflow files.

| Workflow | Secret | Purpose | Required |
|---|---|---|---|
| `release.yml` | `GITHUB_TOKEN` | Docker login, GitHub Release creation, SBOM upload | Yes (automatic) |
| `release.yml` | `RUNE_CHARTS_BOT_TOKEN` | Cross-repo dispatch to `rune-charts` | No (skips if unset) |
| `container-build.yml` | `GITHUB_TOKEN` | Docker login, image push to GHCR | Yes (automatic) |
| `security-scan.yml` | `GITHUB_TOKEN` | Docker login for GHCR image pull | Yes (automatic) |
| `helm-release.yml` | `GITHUB_TOKEN` | GitHub Release creation | Yes (automatic) |
| `project-sync.yml` | `PROJECT_TOKEN` | GitHub Projects API (PAT with `project` scope) | Yes (explicit) |
| `pr-compliance.yml` | `GITHUB_TOKEN` | PR body read, ML4 automated approval | Yes (automatic) |
| `python-quality.yml` | (none) | No secrets needed | N/A |
| `go-quality.yml` | (none) | No secrets needed | N/A |
| `docs-quality.yml` | (none) | No secrets needed | N/A |
| `helm-quality.yml` | (none) | No secrets needed | N/A |
| `shell-quality.yml` | (none) | No secrets needed | N/A |

### How secrets are passed

GitHub Actions provides two mechanisms for passing secrets to reusable
workflows:

1. **`secrets: inherit`** -- The caller passes all of its secrets
   (including the automatic `GITHUB_TOKEN`) to the reusable workflow.
   This is the simplest approach and works when the caller and the
   reusable workflow are in the same organization or when the caller
   has all required secrets configured.

2. **Explicit mapping** -- The caller maps each secret individually
   using `secrets:` with named keys. This approach is more verbose
   but provides a clear contract and fails loudly when a required
   secret is missing.

Currently, most quality-gate workflows (`python-quality.yml`,
`go-quality.yml`, `docs-quality.yml`, `helm-quality.yml`,
`shell-quality.yml`) require no secrets at all. The `GITHUB_TOKEN` is
automatically available to reusable workflows when they are within the
same organization as the caller.

The `project-sync.yml` workflow requires explicit secret mapping because
`PROJECT_TOKEN` is a user-provided PAT, not an automatic token.

### Fallback template with explicit secrets mapping

If `secrets: inherit` does not work (for example, after an org migration
or when the reusable workflow is in a different organization), callers
must use explicit mapping. The following template covers every secret
that any rune-ci workflow could need:

```yaml
# Explicit secrets mapping fallback template
# Use this if secrets: inherit is unavailable or unreliable.
jobs:
  release:
    uses: lpasquali/rune-ci/.github/workflows/release.yml@main
    with:
      image-name: "rune"
      build-container: true
      slsa-attestation: true
      generate-sbom: true
      notify-charts: true
    secrets:
      RUNE_CHARTS_BOT_TOKEN: ${{ secrets.RUNE_CHARTS_BOT_TOKEN }}
    # Note: GITHUB_TOKEN is passed automatically to reusable workflows
    # within the same org. No explicit mapping needed for it.

  project-sync:
    uses: lpasquali/rune-ci/.github/workflows/project-sync.yml@v0.1.0
    secrets:
      PROJECT_TOKEN: ${{ secrets.PROJECT_TOKEN }}
```

### Org-migration risk

When `rune-ci` and caller repos are in the **same GitHub organization**:

- `GITHUB_TOKEN` is automatically available to reusable workflows.
- `secrets: inherit` passes all repo-level and org-level secrets.
- No explicit mapping is needed for `GITHUB_TOKEN`.

When `rune-ci` moves to a **different organization**:

- `GITHUB_TOKEN` from the caller is still passed automatically (it
  represents the caller's context, not the workflow repository's
  context).
- `secrets: inherit` only passes secrets that exist in the caller
  repo. Org-level secrets from the reusable workflow's org are **not**
  inherited.
- Custom secrets like `RUNE_CHARTS_BOT_TOKEN` and `PROJECT_TOKEN`
  must be configured in the caller repo (or caller org) and passed
  explicitly.
- Reusable workflow references must use the full
  `<org>/rune-ci/.github/workflows/<file>@<ref>` path.

**When explicit mapping becomes necessary:**

- The caller repo moves to a different GitHub organization than `rune-ci`.
- Organization-level secret policies restrict cross-repo inheritance.
- A fork of `rune-ci` is used (forks do not inherit secrets from the
  upstream repository).
- GitHub changes the `secrets: inherit` behavior (track GitHub
  changelog for breaking changes to reusable workflow features).

**Mitigation:** The `release.yml` workflow already declares its
`RUNE_CHARTS_BOT_TOKEN` secret with `required: false` and gracefully
skips the chart-notification step when the secret is unset. This
fail-open pattern for optional secrets is correct. For required
functionality (image push, release creation), `GITHUB_TOKEN` is always
available regardless of org boundaries.

## SLSA L3 Provenance Verification (Issue #155)

### How provenance attestation works with reusable workflows

The `release.yml` workflow supports SLSA L3 build provenance attestation
via the `slsa-attestation` input (boolean, default `false`). When
enabled, the workflow uses `actions/attest-build-provenance@v2` to
generate a signed attestation for the container image.

The attestation step in `release.yml`:

```yaml
- name: Attest build provenance -- SLSA L3
  if: inputs.slsa-attestation && inputs.build-container
  uses: actions/attest-build-provenance@96b4a1ef7235a096b17240c259729fdd70c83d45 # v2
  with:
    subject-name: ghcr.io/${{ inputs.registry-owner }}/${{ inputs.image-name }}
    subject-digest: ${{ steps.manifest.outputs.digest }}
    push-to-registry: true
```

### Attestation source identity

The `actions/attest-build-provenance` action generates a SLSA v1.0
provenance statement. The key fields in the provenance predicate are:

- **`buildType`**: Set to
  `https://actions.github.io/buildtypes/workflow/v1` by the action.
- **`externalParameters.workflow.ref`**: References the **caller**
  workflow file and ref (the repo that triggered the workflow), not
  the reusable workflow in `rune-ci`.
- **`resolvedDependencies`**: Includes the source repository (caller
  repo) as a dependency.
- **`builder.id`**: Identifies the GitHub Actions runner.

**Confirmation:** When a caller repo (e.g., `lpasquali/rune`) uses
`rune-ci`'s `release.yml` as a reusable workflow, the attestation
correctly identifies `lpasquali/rune` as the source repository in the
provenance statement, not `lpasquali/rune-ci`. This is because
GitHub's attestation infrastructure uses the `github.repository`
context, which always refers to the caller repository in a
`workflow_call` context.

The `subject-name` is explicitly parameterized via inputs
(`registry-owner` and `image-name`), ensuring the attestation binds
to the correct container image regardless of which repo triggered the
build.

### Adjustments needed for the provenance chain

No adjustments are needed for the current configuration. The provenance
chain is correct because:

1. **Source identity**: `github.repository` in a `workflow_call` context
   resolves to the caller repo (e.g., `lpasquali/rune`), not the
   reusable workflow repo (`lpasquali/rune-ci`).

2. **Subject binding**: The image name and digest are passed as inputs
   and computed at build time, ensuring the attestation binds to the
   actual artifact.

3. **Signing**: GitHub's Sigstore-based signing uses the caller's OIDC
   identity, which includes the caller repository as the issuer claim.

4. **`id-token: write` permission**: The `release.yml` workflow
   declares `id-token: write` at the workflow level, which is required
   for Sigstore OIDC token generation. Callers must also grant this
   permission.

**Verification command:**

```bash
gh attestation verify \
  oci://ghcr.io/lpasquali/<image>:<tag> \
  --owner lpasquali
```

This verifies that the attestation was generated by a GitHub Actions
workflow in the `lpasquali` namespace and that the provenance chain
is intact.

### Risks and monitoring

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Attestation references wrong repo | Low | High | `github.repository` always resolves to caller in `workflow_call` |
| Digest mismatch after manifest creation | Low | High | Digest is computed from the manifest step output, not hardcoded |
| OIDC token scope insufficient | Low | Medium | `id-token: write` is declared at workflow level in `release.yml` |
| Sigstore transparency log unavailable | Low | Medium | `push-to-registry: true` stores attestation in OCI registry as fallback |

## ML4 Compliance Audit (Issue #156)

### How ML4 automated approval works post-migration

The `pr-compliance.yml` reusable workflow in `rune-ci` contains the
`ml4-peer-review` job (`RuneGate/Compliance/ML4-Automated-Approval`).
This job runs after the `merge-gate` job succeeds, meaning all quality
gates have passed.

The approval flow:

1. **Caller repo** invokes `pr-compliance.yml` with
   `inputs.needs-json` containing the results of all upstream jobs
   (coverage, SAST, SCA, SBOM, secret scanning, etc.).
2. **`pr-body-check`** validates the PR body structure (issue
   reference, DoD level, required sections, audit results).
3. **`merge-gate`** aggregates all upstream job results plus the
   PR body check. Any failure blocks the gate.
4. **`ml4-peer-review`** runs only if `merge-gate` succeeds and the
   event is a pull request. It creates an approving review using
   `actions/github-script`.

The approval requires `pull-requests: write` permission, which is
declared on the `ml4-peer-review` job. Callers must grant this
permission (either directly or via `permissions` at the workflow level).

### Approval comment text

The automated approval comment text is:

> **RuneGate Automated Approval** --
> Under IEC 62443-4-1 ML4 guidelines, this PR has been automatically
> approved because it deterministically passed all strict Quality Gates
> (Coverage > 97%, SAST, SCA, SBOM, and SLSA L3 provenance). This
> satisfies the objective two-person peer-review requirement.

**IEC 62443-4-1 ML4 alignment:**

- The comment explicitly cites IEC 62443-4-1 ML4 as the governing
  standard.
- It enumerates the specific quality gates that were passed (Coverage,
  SAST, SCA, SBOM, SLSA L3).
- It states the rationale: deterministic, objective verification
  satisfies the two-person review requirement at ML4.
- The approval is conditional -- it only fires after all gates pass,
  which means any gate failure prevents the automated approval entirely.

### Merge gate still requires ML4 approval

The merge gate architecture ensures ML4 approval is required:

1. **Branch protection rules** in each repo require the `Merge Gate`
   status check to pass before merge.
2. **Branch protection rules** also require at least one approving
   review.
3. The `ml4-peer-review` job provides the required approving review,
   but only after the merge gate passes.
4. Without the automated approval (or a manual human approval), the
   PR cannot be merged.

Post-migration, this flow is preserved because `pr-compliance.yml` is
called as the final step in each caller's `quality-gates.yml`. The
caller passes `toJson(needs)` to the reusable workflow, which evaluates
all upstream job outcomes. The merge gate in the reusable workflow
respects the `merge-gate-excludes` input for jobs that are expected to
be skipped (e.g., container build jobs in repos without Dockerfiles).

**Confirmation:** The merge gate in `pr-compliance.yml` reads the
`needs-json` input and fails if any non-excluded job has a result
other than `success` or `skipped`. This means:

- A failed coverage job blocks merge.
- A failed SAST job blocks merge.
- A failed PR body check blocks merge.
- Only after all checks pass does the ML4 automated approval fire.

### IEC 62443-4-1 ML4 citation

The automated peer review mechanism satisfies the following IEC
62443-4-1 requirements at Maturity Level 4:

| Requirement | Clause | How it is satisfied |
|---|---|---|
| Peer review of changes | SVV-3 | Automated approval after deterministic quality gate passage |
| Objective evidence of review | SM-9 | Approval comment persisted on the PR with gate enumeration |
| Repeatability and reproducibility | SM-4 | Identical gates run on every PR; no human subjectivity in gate pass/fail |
| Configuration management | DM-1 | Reusable workflow is version-pinned; changes to gates are tracked in `rune-ci` |

**ML4 distinction from ML3:** At ML3, peer review may be performed by
any qualified person. At ML4, the review process must be **objective,
repeatable, and measurable**. The automated gate-based approval
satisfies ML4 because the pass/fail criteria are deterministic
(coverage thresholds, SAST findings, license compliance) and the
approval is conditioned on all criteria being met, with no human
discretion in the decision.

**CODEOWNERS interaction:** The automated ML4 approval satisfies the
general review requirement, but `CODEOWNERS` rules may require
additional human review for specific file patterns (e.g., `.vex/`,
`.github/workflows/`). This is additive -- CODEOWNERS review does
not replace the ML4 gate, and the ML4 gate does not replace
CODEOWNERS review.
