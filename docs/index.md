# Welcome to Depsight

Hello and welcome! **Depsight** is a dependency analysing tool designed for the local workspace.

Built with Python, Depsight helps you inspect and understand dependencies within your development environment. It is intended exclusively for **teaching DevOps skills related to Python** — making it a focused, hands-on learning companion for students and educators alike.

Use the top menu to explore the project's development details or follow the step-by-step instructions to get started.

---

## Quick Start

This section walks you through installing Depsight, scanning a project, exporting results, and running the Docker image. If you are setting up the development environment for the first time, head over to the [Getting Started](instructions/getting-started/getting-started.md) guide.

### Install Depsight

Install from PyPI using `pip` or `uv`:

=== "pip"
    ```bash
    pip install depsight
    ```

=== "uv"
    ```bash
    uv tool install depsight
    ```

Verify the installation:

```bash
depsight --version
```

### Scan a Project

Run the `scan` command against a local project directory. Replace `<plugin>` with the package manager you want to scan (e.g. `uv`, `vsce`):

```bash
depsight <plugin> scan --project-dir /path/to/your/project
```

For example, to scan a Python project managed by `uv`:

```bash
depsight uv scan --project-dir .
```

The output is a formatted table listing every dependency with its name, version, constraint, category, and whether it is transitive.

### Export Results as CSV

Append the `--as-csv` flag to write the scan results to a CSV file in addition to the table output:

```bash
depsight uv scan --project-dir . --as-csv
```

The CSV file is saved to the Depsight data directory (`~/.depsight/data/`).

### Run with Docker

Pull and run the pre-built image from Docker Hub without installing Python or any dependencies locally:

```bash
docker run --rm depsight:latest uv scan --project-dir /depsight
```

To scan a project on the host machine, bind-mount its directory into the container:

```bash
docker run --rm -v /path/to/your/project:/project depsight:latest uv scan --project-dir /project
```
