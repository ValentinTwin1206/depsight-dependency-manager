# CI/CD

## Overview

Continuous Integration and Continuous Delivery (CI/CD) automate the steps between writing code and shipping it to users. A CI pipeline typically checks out the source, runs linters, type checkers, and tests, and then builds a distributable artifact. If all checks pass, a CD pipeline publishes the artifact to a package registry, a container registry, or both. Automating these steps eliminates manual errors, enforces quality gates on every change, and ensures that the released artifact is always built from a known-good state of the codebase.

The Depsight project uses [GitHub Actions](https://docs.github.com/en/actions) for its CI/CD pipeline. GitHub Actions is a workflow automation platform built into GitHub that executes jobs in response to repository events such as pushes, pull requests, and releases. Workflows are defined as YAML files inside the `.github/workflows/` directory and run on GitHub-hosted virtual machines. A typical `.github` folder looks like this:

```
.github/
├── actions/            # composite actions shared across workflows
├── scripts/            # shell or Python scripts called from run: steps
└── workflows/
```

---

## GitHub Actions Workflows

Depsight provides three entry-point workflows that trigger the CI/CD pipeline:

- **On Pull Request** — quality gate on every PR to `main`; lints, type-checks, tests, and builds the wheel without publishing
- **On Dispatch** — manual trigger for on-demand builds; supports toolchain version selection and optional wheel artifact upload
- **On Release** — fires on a published GitHub Release; publishes the wheel to PyPI and pushes the Docker image to Docker Hub

Each responds to a different GitHub event and delegates the heavy lifting to `build.yml` via `workflow_call`. The entry points differ in how they determine version numbers, which inputs they forward, and whether they trigger a release publish.

### On Pull Request

The `on_pullrequest.yml` workflow runs automatically when a pull request is opened or updated against the `main` branch. It parses the current version from `pyproject.toml` and calls `build.yml` with `is_release: false`, which means the pipeline lints, type-checks, tests, and builds the wheel but does not publish anything. Changes to `README.md` and the `docs/` folder are excluded via `paths-ignore` so that documentation-only PRs do not trigger a full build.

```yaml
on:
  pull_request:
    branches:
      - main
    paths-ignore:
      - 'README.md'
      - 'docs/**'
```

### On Dispatch

The `on_dispatch.yml` workflow is triggered manually from the GitHub Actions UI. It exposes inputs that let the operator optionally override the Python version and the `uv` version. The Python version defaults to the value in `.python-version` if left empty. Like the pull request workflow, it calls `build.yml` with `is_release: false`, so nothing is published to PyPI or Docker Hub. This workflow is useful for testing a specific configuration or producing a pre-release wheel for local validation.

```yaml
on:
  workflow_dispatch:
    inputs:
      depsight_version:
        description: "Depsight version (must match pyproject.toml, e.g. 1.0.0)"
        required: true
        type: string
      python_version:
        description: "Python version override (leave empty to use .python-version)"
        required: false
        default: ""
        type: string
      uv_version:
        description: "uv version (e.g. 0.11.1)"
        required: false
        default: "0.11.1"
        type: string
      upload_artifact:
        description: "Upload the wheel as a workflow artifact"
        required: false
        default: false
        type: boolean
```

### On Release

The `on_release.yml` workflow fires when a GitHub Release is published. It first verifies that the release tag is [PEP 440](https://peps.python.org/pep-0440/) compliant, then calls `build.yml` with `is_release: true`. This flag enables the publish steps that upload the wheel to PyPI and push the Docker image to Docker Hub. The workflow also forwards the `PYPI_TOKEN` and `DOCKER_PAT` secrets so that the reusable workflow can authenticate with both registries.

```yaml
on:
  release:
    types: [published]
```

### Reusable Build Workflow

The `build.yml` workflow is the single source of truth for all build, test, and publish logic. It is never triggered directly by a repository event. Instead, the three entry-point workflows call it via `workflow_call`, passing the version, toolchain pins, and the `is_release` flag that controls whether artifacts are published.

```mermaid
flowchart LR
  subgraph Triggers
    PR["on_pullrequest.yml"]
    DI["on_dispatch.yml"]
    RE["on_release.yml"]
  end

  subgraph "build.yml"
    direction TB
    V["Verify version"]
    B["Lint, test & build wheel"]
    A["Upload artifact"]
    FG["Filesystem vulnerability gate\n(source + deps + secrets)"]
    D["Build Docker image"]
    IG["Container vulnerability gate\n(OS + libraries)"]
    P["Publish to PyPI"]
    PD["Push Docker image"]

    V --> B --> A
    B --> FG --> D --> IG
    IG --> P
    IG --> PD
  end

  PR -- "is_release: false" --> V
  DI -- "is_release: false" --> V
  RE -- "is_release: true" --> V
```

The workflow accepts the following inputs and secrets:

| Input / Secret      | Type      | Purpose                                              |
|----------------------|-----------|------------------------------------------------------|
| `is_release`         | boolean   | Enables PyPI and Docker Hub publish steps            |
| `uv_version`         | string    | `uv` version to install in the DevContainer          |
| `python_version`     | string    | Python version override — falls back to `.python-version` if omitted |
| `depsight_version`   | string    | Expected version (validated against `pyproject.toml`) |
| `upload_artifact`    | boolean   | Attach the wheel as a downloadable workflow artifact |
| `PYPI_TOKEN`         | secret    | API token for PyPI publishing                        |
| `DOCKER_PAT`         | secret    | Personal access token for Docker Hub                 |

---

## Build and Publish Steps

### Version Verification

Before any build work begins, the workflow compares the `depsight_version` input against the version declared in `pyproject.toml`. If they do not match, the pipeline fails immediately. This prevents accidental releases with mismatched metadata.

### Building the Wheel

The Depsight wheel is built inside the same [DevContainer](../development/dev-environment.md) that is used for local development. The `devcontainers/ci` action spins up the container image defined in `.devcontainer/devcontainer.json` on the GitHub runner, ensuring the CI environment is identical to the local development setup. Inside this container the step runs the full quality pipeline including linting, type checking, and functional tests. The package build is only executed if everything passes.

```yaml
- name: Lint, test & build wheel
  uses: devcontainers/ci@v0.3
  with:
    configFile: .devcontainer/devcontainer.json
    runCmd: |
      set -e
      source .venv/bin/activate
      ruff check src/ tests/
      mypy src/
      python -m pytest tests/ -v --tb=short
      uv build
```

### Uploading as a Workflow Artifact

When `upload_artifact` is set to `true` in the dispatch inputs, the wheel is attached to the workflow run with a 14-day retention period. This is useful for testing a pre-release build without publishing it to PyPI.

```yaml
- name: Provide wheel as workflow artifact
  if: ${{ inputs.upload_artifact }}
  uses: actions/upload-artifact@v4
  with:
    name: depsight-wheel
    path: dist/*.whl
    retention-days: 14
    if-no-files-found: error
```

### Publishing to PyPI

On release builds (`is_release: true`), the wheel is published to PyPI using `uv publish`. The `uv build` step runs inside the DevContainer, but the publish step runs directly on the bare GitHub runner where `uv` is not pre-installed. The [`astral-sh/setup-uv`](https://github.com/astral-sh/setup-uv) action installs the same `uv` version that is pinned via the `uv_version` input, keeping the toolchain consistent. The `PYPI_TOKEN` repository secret is passed to `uv publish` via the `UV_PUBLISH_TOKEN` environment variable.

```yaml
- name: Install uv
  if: ${{ inputs.is_release }}
  uses: astral-sh/setup-uv@v5
  with:
    version: ${{ inputs.uv_version }}

- name: Upload wheel to PyPI
  if: ${{ inputs.is_release }}
  env:
    UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
  run: uv publish
```

### Trivy Vulnerability Gates

Depsight ships two artifacts — a Python wheel to PyPI and a Docker image to Docker Hub. The build pipeline runs two complementary Trivy scans on **every build** (not just releases) to ensure neither artifact ships with known critical vulnerabilities.

#### Filesystem Gate

Immediately after the wheel is built, a filesystem scan (`trivy fs .`) checks the repository source for `CRITICAL` Python dependency vulnerabilities and leaked secrets. If anything is found, the pipeline fails before the Docker image is even built, let alone published. This protects PyPI consumers who install the wheel directly and never use the Docker image.

```yaml
- name: Filesystem vulnerability gate (block on CRITICAL)
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: "fs"
    scan-ref: "."
    format: "table"
    exit-code: "1"
    ignore-unfixed: true
    scanners: "vuln,secret"
    severity: "CRITICAL"
```

#### Image Gate

After the Docker image is built, an image scan checks the full container — OS packages and installed Python libraries — for `CRITICAL` vulnerabilities. If any unfixed critical CVE is found, the pipeline fails and neither the wheel nor the image is published.

```yaml
- name: Container vulnerability gate (block on CRITICAL)
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: "${{ vars.DOCKER_REPOSITORY }}:${{ inputs.depsight_version }}"
    format: "table"
    exit-code: "1"
    ignore-unfixed: true
    vuln-type: "os,library"
    scanners: "vuln"
    severity: "CRITICAL"
```

Both gates run unconditionally on every build — PRs, dispatches, and releases alike. Results are rendered as formatted tables in the workflow log. No SARIF files are written; continuous monitoring with SARIF upload is handled by the dedicated `trivy.yml` workflow (see [Security](#security) below).

### Setting Up Buildx

[Docker Buildx](https://docs.docker.com/build/buildx/) is a CLI plugin that extends `docker build` with BuildKit features such as multi-platform builds and advanced caching. The workflow initialises it on every run so the Docker image build step can execute regardless of whether this is a release.

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```

### Authenticating with Docker Hub

The workflow authenticates to Docker Hub using a username stored as a repository variable and a Personal Access Token (PAT) stored as a repository secret.

```yaml
- name: Log in to Docker Hub
  if: ${{ inputs.is_release }}
  uses: docker/login-action@v3
  with:
    username: ${{ vars.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PAT }}
```

!!! info "Docker Hub Credentials"
    `DOCKER_USERNAME` is configured as a repository **variable** and `DOCKER_PAT` as a repository **secret**. The PAT requires the **Read & Write** permission scope for the target repository on Docker Hub.

### Building the Docker Image

The Docker image is built on every workflow run — not just releases — so that build failures are caught early. The `load: true` option imports the image into the local Docker daemon without pushing it to a registry. The Python and `uv` versions are forwarded as build arguments so the image matches the versions used in the CI test environment. Two tags are applied: the exact release version and `latest`.

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build Docker image
  uses: docker/build-push-action@v6
  with:
    context: .
    load: true
    build-args: |
      PYTHON_VERSION=${{ inputs.python_version }}
      UV_VERSION=${{ inputs.uv_version }}
    tags: |
      ${{ vars.DOCKER_REPOSITORY }}:${{ inputs.depsight_version }}
      ${{ vars.DOCKER_REPOSITORY }}:latest
```

### Pushing the Docker Image

On release builds (`is_release: true`), the image is pushed to Docker Hub in a separate step after authenticating. Keeping the push separate from the build ensures that every PR and dispatch run validates the Dockerfile, while only tagged releases are published.

```yaml
- name: Push Docker image
  if: ${{ inputs.is_release }}
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    build-args: |
      PYTHON_VERSION=${{ inputs.python_version }}
      UV_VERSION=${{ inputs.uv_version }}
    tags: |
      ${{ vars.DOCKER_REPOSITORY }}:${{ inputs.depsight_version }}
      ${{ vars.DOCKER_REPOSITORY }}:latest
```

---

## Security

Depsight uses a two-layer security model: continuous vulnerability monitoring via a dedicated workflow, and blocking vulnerability gates inside the build pipeline.

### Vulnerability Monitoring

The `trivy.yml` workflow runs independently of the build pipeline. It performs two scans — a **filesystem scan** of the repository source and an **image scan** of a locally built Docker image (never pushed). Both scans always render findings as a formatted table in the Actions log. In addition, SARIF reports are generated and uploaded to the Security tab for most triggers:

| Trigger | Console output | SARIF | Uploaded to Security tab |
|---|---|---|---|
| `push` to `main` | Yes | Yes | Yes |
| `pull_request` to `main` | Yes | Yes | Yes |
| `schedule` (weekly) | Yes | Yes | Yes |
| `workflow_dispatch` on `main` | Yes | Yes | Yes |
| `workflow_dispatch` on any other branch | Yes | No | No |

The console scans run unconditionally on every trigger, giving immediate visibility in the Actions log. When SARIF output is also enabled, results are uploaded to the repository's **Security → Code scanning alerts** tab via the CodeQL upload action. Each scan uploads to a separate `category` (`trivy-filesystem` and `trivy-image`) so findings from both layers are tracked independently.

When triggered manually on a non-`main` branch, the SARIF scans and uploads are skipped. This is useful for scanning a feature branch without polluting the Security tab with in-progress work.

#### Filesystem Scan

The filesystem scan (`trivy fs .`) checks the repository source for Python dependency vulnerabilities and leaked secrets. It runs before the Docker image is built, providing fast feedback without waiting for a container build.

```yaml
- name: Trivy filesystem scan (console)
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: "fs"
    scan-ref: "."
    format: "table"
    exit-code: "0"
    ignore-unfixed: true
    scanners: "vuln,secret"
    severity: "CRITICAL,HIGH"

- name: Trivy filesystem scan (SARIF)
  if: ${{ github.event_name != 'workflow_dispatch' || github.ref == 'refs/heads/main' }}
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: "fs"
    scan-ref: "."
    format: "sarif"
    output: "trivy-fs-results.sarif"
    exit-code: "0"
    ignore-unfixed: true
    scanners: "vuln,secret"
    severity: "CRITICAL,HIGH"

- name: Upload filesystem scan results to GitHub Security tab
  if: ${{ always() && (github.event_name != 'workflow_dispatch' || github.ref == 'refs/heads/main') }}
  uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: "trivy-fs-results.sarif"
    category: "trivy-filesystem"
```

#### Image Scan

The image scan checks the full container for OS package and library vulnerabilities. It runs after the Docker image is built.

```yaml
- name: Trivy image scan (console)
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: "${{ vars.DOCKER_REPOSITORY }}:${{ github.sha }}"
    format: "table"
    exit-code: "0"
    ignore-unfixed: true
    vuln-type: "os,library"
    scanners: "vuln"
    severity: "CRITICAL,HIGH"

- name: Trivy image scan (SARIF)
  if: ${{ github.event_name != 'workflow_dispatch' || github.ref == 'refs/heads/main' }}
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: "${{ vars.DOCKER_REPOSITORY }}:${{ github.sha }}"
    format: "sarif"
    output: "trivy-image-results.sarif"
    exit-code: "0"
    ignore-unfixed: true
    vuln-type: "os,library"
    scanners: "vuln"
    severity: "CRITICAL,HIGH"

- name: Upload image scan results to GitHub Security tab
  if: ${{ always() && (github.event_name != 'workflow_dispatch' || github.ref == 'refs/heads/main') }}
  uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: "trivy-image-results.sarif"
    category: "trivy-image"
```

### Security Policy

The repository includes a `SECURITY.md` file at its root, which GitHub surfaces automatically in the **Security** tab. It documents the supported version policy and instructs reporters to use [GitHub's private vulnerability reporting](../../security/advisories/new) rather than opening a public issue. This keeps vulnerability details confidential until a patched release is available.
