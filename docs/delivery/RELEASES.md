 
# RELEASES

Versioning, tagging, and artifact publishing for RUNE.

 
## 1. Synchronized Versioning

RUNE follows [Semantic Versioning](https://semver.org/). We aim to keep major and minor versions synchronized across the core components:
- `rune` (Core)
- `rune-operator`
- `rune-ui`
- `rune-charts`
- `rune-docs`

 
## 2. Release Prerequisites

A release **MUST** only be initiated after:
1.  A Pull Request has been merged into the default branch (`main` or `master`).
2.  All quality checks are **GREEN**.
3.  Metadata is updated in `pyproject.toml` or `Chart.yaml`.

 
## 3. The Tagging Workflow

Pushing a version tag (`vX.Y.Z`) triggers the automated release.

```bash
git tag -a v0.x.y -m "Release v0.x.y"
git push origin v0.x.y
```

 
## 4. Automated Artifacts

| Component | Automated Actions |
| :--- | :--- |
| **`rune`** | Publishes to **PyPI**, creates GitHub Release, and auto-tags `rune-docs`. |
| **`rune-operator`** | Builds Docker images to **GHCR**. |
| **`rune-ui`** | Builds Docker images to **GHCR**. |
| **`rune-charts`** | Packages and attaches Helm charts to GitHub Release. |
| **`rune-docs`** | Builds static site Docker image to **GHCR**. |

 
## 5. Security Gates

Every release artifact is:
- Scanned for CVEs using **Grype** and **Trivy**.
- Provenance-attested using **SLSA Level 3** (GitHub Attestations).
- Verified for license compliance.
