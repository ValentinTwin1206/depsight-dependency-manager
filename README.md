# Depsight - Dependency Analysis Framework

## Usage

### Installation

Go to the [Releases](../../releases/latest) page of the Depsigt GitHub repository and download the `.whl` file from the latest release


#### pip

```bash
pip install depsight-<version>-py3-none-any.whl
```

#### uv

```bash
uv tool install depsight-<version>-py3-none-any.whl
```

### Getting Started

Coming soon...

## Development

### System Requirements

- **IDE with DevContainer support** — either of the following:
    - [Visual Studio Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
    - [JetBrains Gateway](https://www.jetbrains.com/remote-development/gateway/) (supports Dev Containers via the Remote Development plugin)
- **Container manager** — any one of the following:
    - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS, Windows, Linux) (**RECOMMENDED**)
    - [Docker Engine](https://docs.docker.com/engine/install/) (Linux)
    - [Podman](https://podman.io/) with the Podman Desktop or CLI

### Setup Locally

- Open Visual Studio Code at the project root directory
- When prompted, click **Reopen in Container** (or use Command Palette: `Dev Containers: Reopen in Container`)

  <img src="./images/reopen_in_container.png" alt="Logo" width="400"/>

- Wait for the containers to build and start
- Once ready, you'll have a fully configured development environment with all dependencies installed
- Open a terminal inside the DevContainer and run `depsight --help`

### Run Tests

- Open a terminal inside the DevContainer
- Activate the virtual environment:

  ```bash
  source .venv/bin/activate
  ```

- Run all tests:

  ```bash
  pytest tests/ -v
  ```

### Build Docs

- Open a terminal inside the DevContainer
- Activate the virtual environment:

  ```bash
  source .venv/bin/activate
  ```

- Serve the documentation locally with live reload:

  ```bash
  mkdocs serve
  ```

  The site will be available at `http://127.0.0.1:8000`.

- Alternatively, build the static site as a `site/` directory:

  ```bash
  mkdocs build
  ```

## Build

### Pre-release

Use this to trigger a build manually at any time without creating a release.

- Navigate to your repository on GitHub and click the **Actions** tab
- Select the **Manual Dispatch** workflow from the left sidebar
- Click **Run workflow**
- Optionally check **Upload wheel as artifact** to download the built `.whl` after the run
- Set the desired `uv_version` (defaults to `0.10.9`) and click **Run workflow**
- Once the run completes, the wheel is available under the run's **Artifacts** section (if enabled)

### Release

Use this to publish an official versioned build. The wheel is automatically attached to the GitHub Release.

- Bump the `version` field in `pyproject.toml` to the desired version (e.g. `1.2.3`)
- Commit and push the change to `main`
- Navigate to your repository on GitHub and click **Releases** → **Draft a new release**
- Create a new tag matching the version in `pyproject.toml` exactly (e.g. `1.2.3`)
- Click **Publish release**
- The **On Release** workflow triggers automatically, runs the full CI pipeline, and uploads the `.whl` to the release assets
