 
# Workstation Setup

How to provision a fresh Ubuntu 24.04 LTS machine with everything needed to develop, test, and validate the RUNE platform. This guide is written for both humans setting up their dev environment and agents that need to understand what tools are expected to be available.

For automated provisioning across 30+ platforms (Docker, Proxmox, vSphere, AWS, GCP, Azure, KubeVirt, bare metal, and more), see the [Golden Image](GOLDEN_IMAGE.md) guide. The golden image uses the same tool versions documented below, built from a single Packer template.

 
## Base System

RUNE development targets **Ubuntu 24.04 LTS** (Noble Numbat). All instructions below assume a clean install with `sudo` access.

Start by updating the package index:

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

Install common build tools that several components depend on:

```bash
sudo apt-get install -y \
  build-essential \
  curl \
  wget \
  git \
  jq \
  unzip \
  ca-certificates \
  gnupg \
  software-properties-common
```

 
## Python

The core platform (`rune`), the UI (`rune-ui`), and the documentation site (`rune-docs`) are all Python projects. The minimum supported version is **3.11** (for `rune`) and **3.12** (for `rune-ui`). CI runs on **3.14**, which is the recommended development version.

Ubuntu 24.04 ships with Python 3.12. To install 3.14 alongside it, use the deadsnakes PPA:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.14 python3.14-venv python3.14-dev
```

Verify:

```bash
python3.14 --version
```

Each repository maintains its own virtual environment. The Developer Guide covers per-repo setup, but the general pattern is:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

 
## Go

The Kubernetes operator (`rune-operator`) is written in Go. The current version is **1.25**, which is the latest stable release.

```bash
GO_VERSION=1.25.0
wget -q "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
rm "go${GO_VERSION}.linux-amd64.tar.gz"
```

Add Go to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export PATH="/usr/local/go/bin:$HOME/go/bin:$PATH"
```

Verify:

```bash
source ~/.bashrc
go version
```

Install Go development tools used by the project:

```bash
go install github.com/securego/gosec/v2/cmd/gosec@v2.22.0
go install github.com/google/go-licenses@v1.6.0
```

These provide SAST scanning (`gosec`) and license auditing (`go-licenses`) for the operator.

 
## Docker

Docker is required for building container images, running the docker-compose development stack, and executing the security scanner toolchain (Grype, Trivy, Syft all run as containers).

Install Docker Engine using the official repository:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Allow your user to run Docker without `sudo`:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

Verify:

```bash
docker --version
docker compose version
```

 
## Kubernetes Tooling

The Definition of Done requires validating changes in a local Kubernetes cluster. This needs `kubectl`, `kind`, and `helm`.

### kubectl

The project pins kubectl to the same version used in the `rune` container image. Currently **v1.35.3**.

```bash
KUBECTL_VERSION=v1.35.3
curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl
```

Verify:

```bash
kubectl version --client
```

### Kind

Kind (Kubernetes in Docker) creates local clusters for testing. The project uses it in CI via `helm/kind-action@v1.12.0`.

```bash
KIND_VERSION=v0.27.0
curl -Lo kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-amd64"
sudo install -o root -g root -m 0755 kind /usr/local/bin/kind
rm kind
```

Verify:

```bash
kind --version
```

### Helm

Helm deploys the RUNE stack into Kubernetes via the charts in `rune-charts/`.

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Verify:

```bash
helm version --short
```

 
## Security and Quality Scanners

These tools are used locally and in CI to enforce the project's vulnerability management and code quality policies.

### ShellCheck

Lints shell scripts in `rune-airgapped/`.

```bash
sudo apt-get install -y shellcheck
```

### Gitleaks

Secret scanning across all repositories. The project pins version **8.24.3**.

```bash
GITLEAKS_VERSION=8.24.3
wget -q "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
tar -xzf "gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" gitleaks
sudo install -o root -g root -m 0755 gitleaks /usr/local/bin/gitleaks
rm gitleaks "gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
```

### Container Scanners (Grype, Trivy, Syft)

These run as Docker containers, so no local binary install is needed. The project uses them via:

```bash
# SBOM generation
docker run --rm anchore/syft:v1.17.0 ...

# Vulnerability scanning
docker run --rm anchore/grype:v0.82.0 ...
docker run --rm aquasec/trivy:0.65.0 ...
```

You can optionally pull the images ahead of time to avoid download delays during development:

```bash
docker pull anchore/syft:v1.17.0
docker pull anchore/grype:v0.82.0
docker pull aquasec/trivy:0.65.0
```

 
## Python Quality Tools

These are installed inside each repo's virtual environment, but it helps to understand what they are:

| Tool | Purpose | Used by |
|---|---|---|
| `ruff` | Linter and formatter (replaces flake8/black) | rune, rune-ui |
| `mypy` | Static type checker | rune, rune-ui |
| `bandit` | Python SAST scanner | rune, rune-ui |
| `pytest` + `pytest-cov` | Test runner with coverage | rune, rune-ui |
| `pip-audit` | Dependency CVE scanner | all Python repos |
| `pymarkdownlnt` | Markdown linter | rune-docs |
| `mkdocs` + `mkdocs-material` | Documentation site builder | rune-docs |

These are declared in each repo's `requirements.txt` or `pyproject.toml` dev extras and installed as part of the per-repo virtual environment setup described in the [Developer Guide](../usage/DEVELOPER_GUIDE.md).

 
## Verification Checklist

After completing the setup, verify all tools are available:

```bash
python3.14 --version       # Python 3.14.x
go version                 # go1.25.x
docker --version           # Docker 29.x+
docker compose version     # Docker Compose v2.x+
kubectl version --client   # v1.35.3
kind --version             # kind v0.27.x
helm version --short       # v3.x
shellcheck --version       # 0.9.x+
gitleaks version           # 8.24.3
```

If any of these fail, revisit the corresponding section above. Once everything passes, proceed to the [Developer Guide](../usage/DEVELOPER_GUIDE.md) to set up the individual repositories.

### Run this before Step 7 of the SOP

The E2E contract in [E2E_TESTING.md](../usage/E2E_TESTING.md) depends on the
same tool surface as above, plus a readable Docker socket. Before starting a
Level-1 run, re-check the subset that `scripts/e2e.sh` exercises:

```bash
python3.14 --version       # Python 3.14.x
docker compose version     # Docker Compose v2.x+
docker ps > /dev/null      # current user can reach the daemon without sudo
kind --version             # kind v0.27.x
kubectl version --client   # v1.35.3
helm version --short       # v3.x
```

If any line fails, **do not** auto-install from the agent context — the
[SYSTEM_PROMPT.md Anti-Rogue rule](../context/SYSTEM_PROMPT.md#other-process-mandates)
and the risky-actions policy both prohibit opportunistic installers. Open an
`area/infra` issue, note which tool is missing, and continue the SOP with
whichever E2E modes your host supports; `e2e-artifacts/summary.md` records
each mode independently.

 
## Optional: combined-venv dependency check

The default model is **per-repo venvs** — see
[Developer Guide §Python Repositories](../usage/DEVELOPER_GUIDE.md#python-repositories-rune-rune-ui-rune-docs).
Per-repo venvs are mandatory because `rune` targets Python **>=3.11** and
`rune-ui` targets Python **>=3.12**; a single shared venv cannot satisfy both
floors simultaneously across the supported range.

Cross-repo dependency conflicts are still worth surfacing before they bite in
CI. The helper `rune/scripts/check-cross-repo-deps.sh` (shipped in Phase 1 of
[rune-docs#271](https://github.com/lpasquali/rune-docs/issues/271)) creates a
**throwaway** venv at Python 3.14, `pip install -e`s every Python repo into
it, then runs `pip check` and prints any conflicting pairs. Usage:

```bash
cd ~/Devel/rune
./scripts/check-cross-repo-deps.sh   # writes /tmp/rune-crossdep/report.txt
```

The helper is **advisory** — `pip check` failure prints the offending pair
and links to the [E2E_TESTING.md troubleshooting section](../usage/E2E_TESTING.md#cross-repo-dependency-conflicts).
It is **not** a merge gate and it does **not** replace the per-repo venvs
documented in the Developer Guide.

 
## Keeping Tools Up to Date

Tool versions are pinned in CI workflows (`.github/workflows/quality-gates.yml`) and Dockerfiles across all repositories. When a version bump happens upstream, it should be synchronized across:

1. The relevant CI workflow(s).
2. The Dockerfile(s) if applicable.
3. This document.

The Go and Python versions in particular track latest stable releases. Check the project's CI files as the authoritative source for current pinned versions.
