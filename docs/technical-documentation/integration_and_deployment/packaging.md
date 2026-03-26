# Packaging

## Overview

The most common way to distribute Python projects is as a **wheel** (`.whl`), a pre-built binary that installs without a build step. A wheel is well suited for developer tools and libraries, but it requires Python and a package manager like `pip` or `uv` to already be present on the target machine. This makes it a poor fit for distributing to end users who are not developers, for shipping to locked-down environments where installing runtimes is restricted, or for desktop applications where a one-click install experience is expected. For those cases, [PyInstaller](https://pyinstaller.org/) and [Nuitka](https://nuitka.net/) produce self-contained executables from a Python project, removing the runtime dependency for the end user. The trade-off is a more complex build environment and toolchain compared to a simple `uv build`.

Depsight is a developer tool designed for learning purposes and does not target any production environment. It is shipped as a wheel and published to [PyPI](https://pypi.org), the standard distribution channel for packages installed via `pip` or `uv`.

---

## Python Wheels

### Wheel Contents

A wheel (`.whl`) is a ZIP archive with a standardised layout. It contains the source code, package metadata, and entry-point declarations — everything an installer needs to place the package into a Python environment without running arbitrary build code.

```
depsight-0.1.0-py3-none-any.whl
├── depsight/
│   ├── __init__.py
│   ├── cli.py
│   ├── commands/...
│   ├── core/...
│   └── utils/...
└── depsight-0.1.0.dist-info/
    ├── METADATA          # Package name, version, dependencies
    ├── entry_points.txt  # CLI + plugin entry points
    └── RECORD            # File checksums
```

The `entry_points.txt` file registers the CLI command and the plugin system. See [CLI Architecture](../development/cli-architecture.md) for details on how entry points wire the plugin registry together.

### Build System

#### uv

According to [Python Project Configuration Nowadays](../development/project-overview.md#python-project-configuration-nowadays), [PEP 517](https://peps.python.org/pep-0517/) generally defined a standard interface between build frontends and build backends. A build frontend is the tool the developer runs (e.g `uv build`, `python -m build`) and is responsible for orchestrating the build process. A build backend is the library that does the actual work of compiling metadata and assembling the wheel; it is declared in the `[build-system]` table in `pyproject.toml` and invoked by the frontend. 

The latest version of Depsight uses `uv` as its build backend, which has provided a stable, PEP 517-compliant build backend since version `v0.7.19`. In the current `pyproject.toml` configuration, that backend is declared through the separate `uv_build` package. `uv_build` is shipped with the installation of `uv`, but it is not user-facing; `uv build` remains the command intended for normal use:

```toml
[build-system]
requires = ["uv_build>=0.11.1,<0.12"]
build-backend = "uv_build"
```

Running the build produces two output files in `dist/`:

=== "uv"
    ```bash
    uv build
    ```

=== "build"
    ```bash
    python -m build
    ```

This will generate a `*.whl` (binary distribution) and a `*.tar.gz` (source distribution) in the local `dist/` directory:

```
dist/
├── depsight-1.0.0-py3-none-any.whl
└── depsight-1.0.0.tar.gz
```

The generated `.whl` can be directly used to install Depsight locally:

=== "pip"
    ```bash
    pip install dist/depsight-1.0.0-py3-none-any.whl
    ```

=== "uv"
    ```bash
    uv pip install dist/depsight-1.0.0-py3-none-any.whl
    ```

#### Alternatives

##### Setuptools

**[Setuptools](https://setuptools.pypa.io/)** is probably the most widely adopted Python build backend. It has the broadest ecosystem compatibility, works well with older packaging workflows, and remains a sensible default when maximum tooling interoperability matters more than using uv's native backend. Older versions of Depsight used `setuptools.build_meta` before the project switched to uv's build backend.

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

##### Hatchling

**[Hatchling](https://hatch.pypa.io/latest/backend/)** is a modern alternative that reads all metadata directly from `pyproject.toml` with no additional configuration files. It is faster, stricter about standards compliance, and produces reproducible builds by default. Switching is a one-line change:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Publishing to PyPI

[PyPI](https://pypi.org) (the Python Package Index) is the official package registry for Python. It is the registry that `pip install depsight` and `uv tool install depsight` query by default. Every package on PyPI is identified by its `"name"` and `"version"` as declared in `pyproject.toml`. Once uploaded, the wheel is immediately available at `https://pypi.org/project/depsight/` and installable by anyone.

![Depsight on PyPI](../../images/depsight_pypi.png)

!!! info "PyPI Account and API Token"
    Uploading a package requires an account and an API token. The token is scoped either to the entire account or to a single project, and is passed as a secret during publishing.