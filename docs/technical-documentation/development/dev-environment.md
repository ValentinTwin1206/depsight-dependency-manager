# Development Environment

## Overview

It is common practice to use virtual environment tools such as `venv`, `pipenv`, or `virtualenv` when running Python projects locally. They isolate project packages from the system Python and from other projects, keeping dependency versions consistent and preventing conflicts. For many projects that level of isolation is sufficient.

Depsight goes further by integrating [DevContainers](https://containers.dev/), a modern approach to virtualizing an entire development environment inside a Linux container. Instead of documenting setup steps in a README and hoping every contributor follows them correctly, a DevContainer defines and provisions the full environment as code automatically.

### Beyond Traditional Virtualization Techniques

Tools like `venv`, `pipenv`, and `virtualenv` isolate Python packages, and for many projects that is enough. DevContainers go further because they control the full operating system layer, not just Python. That makes them useful when a project depends on system tools, specific runtimes, or a development setup that should match CI. However, they might introduce some overhead, as developers need Docker or any other container manager installed and should understand the basics of working with containers. The table below shows when that extra complexity is worth it:

| Capability | venv / pipenv | DevContainer |
|-------------|:---:|:---:|
| Keep project packages separate from the system Python and other projects | ✅ | ✅ |
| Guarantee every developer uses the exact same Python interpreter version | ❌ | ✅ |
| Install OS-level libraries via `apt` (e.g. `gcc` for C extensions, `libpq` for Postgres) | ❌ | ✅ |
| Ship tools like `uv`, `ruff`, or Nuitka compiler dependencies inside the environment | ❌ | ✅ |
| Automatically install editor extensions and apply workspace settings for every developer | ❌ | ✅ |
| Run the exact same OS, Python, and toolchain locally as the CI pipeline | ❌ | ✅ |

---

### IDE Support

The [DevContainer specification](https://containers.dev/) is an open standard supported by multiple editors. VS Code supports it through the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), JetBrains IDEs connect through [Gateway](https://www.jetbrains.com/remote-development/gateway/), and the [`devcontainer` CLI](https://github.com/devcontainers/cli) enables headless usage in automation and CI pipelines.

Per-IDE configuration lives under the `customizations` key in `devcontainer.json`, so extensions and settings for different editors coexist in the same file without conflict. The `customizations` key is specific to IDEs like VS Code and JetBrains while the `devcontainer` CLI is a headless runner and ignores this section entirely. This is one of the biggest quality-of-life improvements DevContainers offer since every developer opens the project and immediately gets the right extensions, formatters, and IDE behaviour. There is no manual setup, no "works on my machine" differences.

```json
{
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",        // Python language support, IntelliSense, and debugging
                "charliermarsh.ruff",      // Fast linter and formatter — enforces code style on save
                "eamodio.gitlens"          // Inline Git blame, history, and branch comparisons
            ]
        },
        "jetbrains": {
            "plugins": [
                "com.intellij.python",     // Python language support and debugger
                "com.jetbrains.plugins.ini" // TOML / INI file support for pyproject.toml
            ]
        }
    }
}
```

!!! info "Running a Python `venv` inside the DevContainer by default"

    When the DevContainer starts, `uv sync --all-groups` runs as the `postCreateCommand` and creates a `.venv/` directory with all project dependencies. During this step, `uv` reads the project name from `pyproject.toml` (`name = "depsight"`) and writes it into `.venv/pyvenv.cfg` as `prompt = depsight`. That prompt value is what determines the `(depsight)` prefix in the shell.

    The actual activation happens through the `ms-python.python` extension listed under `customizations`. Its default setting `python.terminal.activateEnvironment` is `true`, which means it auto-detects the `.venv/` directory and injects `source .venv/bin/activate` into every new integrated terminal. So `uv sync` creates the named virtual environment, and the Python extension activates it — no manual step is needed.

---

## DevContainer Components

### Project Structure

A DevContainer is configured through a `.devcontainer/` folder at the root of the repository. The **minimum required file** is `devcontainer.json`. A `Dockerfile` is optional but recommended when the project needs system-level customizations beyond what a pre-built base image provides.

For complex post-creation routines such as configuring git hooks, installing additional tools, or running conditional setup logic, extracting the [`"postCreateCommand"`](#lifecycle-commands) into a dedicated shell script is recommended over embedding a long one-liner in `devcontainer.json`.

```
.devcontainer/
├── devcontainer.json
├── Dockerfile
└── postCreateCommand.sh
```

!!! info "Other Lifecycle Hooks"
    `postStartCommand` runs on every container start. `postAttachCommand` runs each time the IDE attaches to the running container.

---

### DevContainer Configuration

The `devcontainer.json` is the central configuration file. it instructs the IDE how to build the container image, which extensions to install, which ports to forward, and which environment variables and lifecycle commands to apply.

The `build` section points to the `Dockerfile` and passes build arguments. `${localEnv:PYTHON_VERSION:3.12}` reads `PYTHON_VERSION` from the host machine's environment — useful when a developer wants to override the version without editing the file. The value after the colon is the fallback default when the variable is not set. `containerEnv` injects environment variables into the running container, making them available to every process. `forwardPorts` maps container ports to the host so they can be accessed from a browser or tool on the developer's machine. `workspaceFolder` sets the path inside the container where the project is mounted; when omitted, the Dev Containers extension defaults to `/workspaces/<repo-name>`. The `postCreateCommand` runs with this folder as the working directory immediately after the project has been mounted:

```json
{
    "name": "Depsight DevContainer",
    "build": {
        "context": "..",
        "dockerfile": "Dockerfile",
        "args": {
            "PYTHON_VERSION": "${localEnv:PYTHON_VERSION:3.12}",
            "UV_VERSION": "${localEnv:UV_VERSION:0.10.9}"
        }
    },
    "containerEnv": {
        "APP_NAME": "DEPSIGHT",
        "DEPSIGHT_ENV": "development"
    },
    "forwardPorts": [8000],
    "portsAttributes": {
        "8000": {
            "label": "MkDocs Dev Server",
            "onAutoForward": "notify"
        }
    },
    "postCreateCommand": "uv sync --all-groups",
    "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}" //optional
}
```

#### Lifecycle Commands

The `"postCreateCommand"` runs once after the container is created and the project has been mounted into the `"workspaceFolder"`. It is typically used to install project dependencies via `uv sync --all-groups`, `npm install` etc.

Installing dependencies inside the `Dockerfile` instead would not work, since the `Dockerfile` builds the image before the project is mounted. When the Dev Containers extension mounts the workspace into `"workspaceFolder"`, it overlays that path in the container filesystem, hiding anything that was written there during the image build. Running the install in `"postCreateCommand"` ensures it happens after the mount.

---

### Container Image

The `Dockerfile` defines the content of the container image — the pre-installed system tools, users, and their permissions — while `devcontainer.json` controls how the IDE integrates with that image and which lifecycle commands to run.

When `devcontainer.json` includes a `build` block, the IDE builds the image from the Dockerfile before starting the container. Without one, DevContainers use a pre-built image directly.

Depsight's Dockerfile is intentionally minimal — it extends the [Microsoft DevContainer base image](#microsofts-devcontainer-base-images) and only adds what it doesn't already include:

```dockerfile
ARG PYTHON_VERSION="3.12"
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

ARG UV_VERSION="0.10.9"
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh \
    | UV_INSTALL_DIR=/usr/local/bin sh

ENV PYTHONUNBUFFERED=1
ENV APP_NAME=DEPSIGHT
ENV DEPSIGHT_ENV=development

EXPOSE 8000
```

---

### Microsoft's DevContainer Base Images

Microsoft publishes **purpose-built** base images at [`mcr.microsoft.com/devcontainers`](https://mcr.microsoft.com/en-us/catalog?search=devcontainers) for most common languages and stacks such as *Python*, *JavaScript*, *Rust*, etc. Unlike regular container images, these DevContainer images are built for development:

| Feature / Aspect                 | `python:3.12` | `mcr.microsoft.com/devcontainers/python:3.12` |
|----------------------------------|----------------------------------|--------------------------------------------|
| Default user                     | `root`                           | `vscode` with `sudo` access                       |
| Non-root workflow                | Manual setup required            | Ready out of the box                       |
| Preinstalled tools               | Minimal                          | Extensive        |
| Python tooling                   | `pip` only                       | `pip`, `pipx`, common dev tools            |
| Shell                            | `sh`, `bash` | `sh`, `bash`, `zsh` |
| VS Code Server                   | Requires manually creating a non-root user and using `USER` syntax   | Works out of the box; `vscode` is the default user |

---

## CI/CD Integration

The same container image used for local development can be used directly in CI, eliminating environment drift. Environment drift is the problem where builds pass locally but fail in the pipeline due to a different OS, Python version, or missing system library.

### GitHub Actions

GitHub Actions has "native" DevContainer support through the official [`devcontainers/ci`](https://github.com/devcontainers/ci) action, maintained by the same project behind the DevContainer specification. It reads the project's `devcontainer.json`, builds the container, and runs commands inside it:

```yaml
- name: Lint, test & build wheel
  uses: devcontainers/ci@v0.3
  with:
    configFile: .devcontainer/devcontainer.json
    runCmd: |
      set -e
      source .venv/bin/activate

      depsight --help                         # CLI health check
      ruff check src/ tests/                  # Linting
      mypy src/                               # Type checking
      python -m pytest tests/ -v --tb=short   # Tests
      uv build                                # Build wheel
```

### GitLab CI

GitLab has no native DevContainer support. The [`@devcontainers/cli`](https://github.com/devcontainers/cli) npm package can replicate the behaviour, but it requires ***Docker-in-Docker (DinD)*** (`docker:dind`). The setup could be a nightmare since runner privileges, TLS settings, and socket access all vary across GitLab installations and can produce hard-to-diagnose failures.

A more robust alternative is to split the work into two explicit pipeline stages. One job builds and pushes the DevContainer image, and a second job pulls and uses it directly:

```yaml
stages:
  - build
  - test

build-devcontainer:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
  script:
    - docker build -f .devcontainer/Dockerfile -t $CI_REGISTRY_IMAGE/devcontainer:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE/devcontainer:$CI_COMMIT_SHORT_SHA

test:
  stage: test
  image: $CI_REGISTRY_IMAGE/devcontainer:$CI_COMMIT_SHORT_SHA
  script:
    - source .venv/bin/activate
    - depsight --help
    - ruff check src/ tests/
    - mypy src/
    - python -m pytest tests/ -v --tb=short
    - uv build
```
