# Project Overview

## Overview

Setting up a Python project has changed significantly over the past two decades. What once required a fragmented mix of configuration files has since converged on a single standard with `pyproject.toml`. Alongside this consolidation, a new generation of developer tools has emerged that takes full advantage of the modern standard. Tools like [uv](https://docs.astral.sh/uv/) and [Ruff](https://docs.astral.sh/ruff/) enable a scalable and streamlined project setup with minimal configuration overhead.

Depsight embraces this modern stack. Metadata, dependencies, build system configuration, and tool settings all live in a single `pyproject.toml`, and `uv` manages the full dependency lifecycle from installation to publishing.

---

## Project Configuration

### Python Project Configuration in the Past

In 1998, `distutils` introduced `setup.py`, an imperative Python script that served as the build entry point for a project. Package metadata such as the `name`, `version`, and `description` were declared as function arguments inside executable code. A `requires` keyword existed for declaring dependencies, but it was purely informational metadata. No tool ever used it to download or install packages automatically; developers had to find, download, and install each dependency by hand.

=== "`setup.py`"
    ```python
    from distutils.core import setup

    setup(
        name="my-package",
        version="1.0.0",
        description="A sample package",
        requires=[
            "lxml (>=0.9)",
        ],
    )
    ```

Around 2004, `setuptools` extended `setup.py` with automatic package discovery and replaced the inert `requires` with `install_requires`, which actually caused dependencies to be resolved and installed. Metadata, however, remained executable Python code. Consequently, any tool had to run the file just to read the package name or version, which was both a security risk and a barrier to static tooling.

=== "`setup.py`"
    ```python
    from setuptools import setup, find_packages

    setup(
        name="my-package",
        version="2.0.0",
        description="A sample package",
        packages=find_packages(),
        install_requires=[
            "lxml>=1.0",
        ],
    )
    ```

In 2008, `pip` was released and introduced `requirements.txt` as a convention for pinning exact dependency versions alongside the existing `setup.py`. Some teams also started maintaining a separate `requirements-dev.txt` for development tools like test runners and linters, which meant keeping multiple files in sync manually.

=== "`setup.py`"

    ```python
    from setuptools import setup, find_packages

    setup(
        name="my-package",
        version="3.0.0",
        description="A sample package",
        packages=find_packages(),
        install_requires=[
            "lxml>=1.0",
        ],
    )
    ```

=== "`requirements.txt`"

    ```text
    lxml==1.3.6
    ```

=== "`requirements-dev.txt`"

    ```text
    pytest==2.3.5
    ```

In late 2016, `setuptools 30.3` introduced full support for declarative metadata in `setup.cfg`, moving all package metadata out of executable Python code and into a static configuration file. Runtime dependencies could be declared under `[options] install_requires`, and development extras under `[options.extras_require]`, installable via `pip install -e ".[dev]"`.

However, the entries under `install_requires` and `extras_require`only expressed loose constraints and did not pin exact versions. A separate `requirements.txt` (and `requirements-dev.txt`) was therefore still maintained alongside `setup.cfg` to lock exact versions for reproducible installs. And despite all of this, `setup.py` was still required because `pip` internally depended on it. Consequently, removing it would cause installs to fail entirely:

=== "`pip`"

    ```
    $ pip install -e .
    Obtaining file:///{PATH_TO_PROJECT_ROOT}/my-package
    ERROR: file:///{PATH_TO_PROJECT_ROOT}/my-package does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.
    ```

=== "`uv`"

    ```
    $ uv sync
    error: No `pyproject.toml` found in current directory or any parent directory
    ```

Projects therefore had to keep `setup.cfg`, `setup.py`, `requirements.txt`, and `requirements-dev.txt` in sync manually.

=== "`setup.cfg`"

    ```ini
    [metadata]
    name = my-package
    version = 4.0.0
    description = A sample package

    [options]
    packages = find:
    install_requires =
        lxml>=3.0

    [options.extras_require]
    dev =
        pytest>=3.2
    ```

=== "`setup.py`"

    ```python
    from setuptools import setup
    setup()
    ```

=== "`requirements.txt`"

    ```text
    lxml==3.6.4
    ```

=== "`requirements-dev.txt`"

    ```text
    pytest==3.2.3
    ```

### Python Project Configuration Nowadays

#### Single Source of True

In 2016 the fragmentation of project configuration across several files ended, since [PEP 517](https://peps.python.org/pep-0517/) and [PEP 518](https://peps.python.org/pep-0518/) introduced `pyproject.toml` as a standard home for build system metadata. [PEP 621](https://peps.python.org/pep-0621/) completed the picture in 2020 by standardising the `[project]` table for package metadata.

The `[project]` table consolidates everything that used to live across `setup.py` and `setup.cfg`. It declares the package name, version, description, and a `dependencies` list that serves as the canonical declaration of runtime requirements, replacing `requirements.txt`. The `[build-system]` table specifies the backend responsible for assembling the project into a distributable artifact. The `[dependency-groups]` table takes care of development and documentation tooling separately from runtime requirements, replacing scattered `requirements-dev.txt` files with a structured, first-class concept inside the same file. Finally, `[tool.*]` sections configure linters, formatters, and test runners directly in `pyproject.toml`, removing the need for separate files such as `.flake8` or `pytest.ini`.

#### Project Orchestration

With `pyproject.toml` as a stable foundation, the Python ecosystem now has the same capability as other languages (e.g. `npm`, `cargo`, `go mod`) to orchestrate the entire project lifecycle around a single central configuration file.

Tools such as [Poetry](https://python-poetry.org/) and [uv](https://docs.astral.sh/uv/) expose a unified interface covering project initialization (`uv init` / `poetry new`), dependency management (`uv add` / `poetry add`), environment synchronization (`uv sync`), building (`uv build` / `poetry build`), and publishing (`uv publish` / `poetry publish`). Both tools scaffold a PEP 621-compliant `pyproject.toml` from a single command and support various flags to customise the output layout, Python version, or build backend:

=== "`uv`"

    ```bash
    uv init my-package --build-backend "uv"
    ```

=== "`poetry`"

    ```bash
    poetry new my-package
    ```

Both tools provide an `add` command to register packages as part of the project, either as runtime dependencies or scoped to a named group via `--group <name>`:

=== "`uv`"

    ```bash
    cd my-package
    uv add lxml
    uv add --group dev ruff pytest
    uv add --group docs mkdocs mkdocs-material
    ```

=== "`poetry`"

    ```bash
    cd my-package
    poetry add lxml
    poetry add --group dev ruff pytest
    poetry add --group docs mkdocs mkdocs-material
    ```

Both tools update `pyproject.toml` and their respective lockfile on every `add` call. With `uv`, each invocation also immediately installs the package into a `.venv` in the project root, keeping the virtual environment continuously in sync. The resulting `pyproject.toml` only differs in the `[build-system]` table:

=== "`uv`"

    ```
    my-package/
    ├── .git/
    ├── .gitignore
    ├── .python-version
    ├── .venv
    ├── README.md
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
    ```

    ```toml
    [project]
    name = "my-package"
    version = "0.1.0"
    description = "Add your description here"
    readme = "README.md"
    authors = [
        { name = "{GIT_USER}", email = "{GIT_MAIL}" }
    ]
    requires-python = ">=3.12"
    dependencies = [
        "lxml>=6.0.2",
    ]

    [project.scripts]
    hello-world = "hello_world:main"

    [build-system]
    requires = ["uv_build>=0.11.1,<0.12.0"]
    build-backend = "uv_build"

    [dependency-groups]
    dev = [
        "pytest>=9.0.2",
        "ruff>=0.15.8",
    ]
    docs = [
        "mkdocs>=1.6.1",
        "mkdocs-material>=9.7.6",
    ]
    ```

=== "`poetry`"

    ```
    my-package/
    ├── README.md
    ├── poetry.lock
    ├── pyproject.toml
    ├── src/
    │   └── my_package/
    │       └── __init__.py
    └── tests/
        └── __init__.py
    ```

    ```toml
    [project]
    name = "my-package"
    version = "0.1.0"
    description = ""
    authors = [
        { name = "{GIT_USER}", email = "{GIT_MAIL}" }
    ]
    readme = "README.md"
    requires-python = ">=3.12"
    dependencies = [
        "lxml (>=6.0.2,<7.0.0)"
    ]

    [tool.poetry]
    packages = [{include = "my_package", from = "src"}]

    [build-system]
    requires = ["poetry-core>=2.0.0,<3.0.0"]
    build-backend = "poetry.core.masonry.api"

    [dependency-groups]
    dev = [
        "ruff (>=0.15.8,<0.16.0)",
        "pytest (>=9.0.2,<10.0.0)"
    ]
    docs = [
        "mkdocs (>=1.6.1,<2.0.0)",
        "mkdocs-material (>=9.7.6,<10.0.0)"
    ]
    ```

---

## Development Tools

### Build Management

Build management is the process of packaging Python source code into [distributable artifacts](./../integration_and_deployment/distribution.md#python-wheels). [PEP 517](https://peps.python.org/pep-0517/) defined a standard interface between build frontends and build backends. A build frontend is the tool the developer runs (e.g. `uv build`, `python -m build`) and orchestrates the build process. A build backend is the library that does the actual work of compiling metadata and assembling the wheel; it is declared in the `[build-system]` table in `pyproject.toml` and invoked by the frontend.

Depsight uses `uv_build` as its build backend, which has been a stable, PEP 517-compliant backend since uv `v0.7.19`. `uv_build` is shipped with `uv` but is not user-facing; `uv build` remains the command for normal use. The backend is declared in `pyproject.toml`:

```toml
[build-system]
requires = ["uv_build>=0.11.1,<0.12"]
build-backend = "uv_build"
```

#### Alternatives

The most widely adopted alternative is [Setuptools](https://pypi.org/project/setuptools/), which offers the broadest ecosystem compatibility and is a sensible default when tooling interoperability matters most. [Hatchling](https://pypi.org/project/hatchling/) is a modern option that reads all metadata directly from `pyproject.toml`, enforces standards compliance more strictly, and produces reproducible builds by default.

### Dependency Management

Dependency management is the process of declaring which third-party packages a project needs, resolving compatible versions, and installing them reproducibly across environments. As already introduced in [Project Orchestation](#project-orchestration), centralizing all dependency declarations in `pyproject.toml` significantly streamlines this process.

Depsight uses [**uv**](https://docs.astral.sh/uv/) as its package manager, a Rust-based tool that resolves and installs packages significantly faster than `pip` or any other Python dependency manager through parallel downloads and a shared global cache.

```mermaid
xychart-beta
    title "Install time in seconds (lower is better)"
    x-axis ["pip", "pip-tools", "conda", "poetry", "uv"]
    y-axis "Seconds" 0 --> 130
    bar [45, 40, 120, 25, 3]
```

#### Install Dependencies

To install the direct and transitive dependencies declared in `pyproject.toml`, use `uv sync` during local development. In CI/CD, use `uv sync --locked` instead so the build installs exactly what is pinned in the committed `uv.lock` and fails immediately if the lockfile is out of sync with `pyproject.toml`.

=== "Local Development"

    ```bash
    uv sync
    ```

=== "CI/CD"

    ```bash
    uv sync --locked
    ```

On a clean checkout, `uv sync` resolves the dependency graph, creates `uv.lock`, and sets up the `.venv`. On subsequent local runs, it updates both to match the current state of `pyproject.toml`. In CI/CD, `uv sync --locked` installs directly from the committed lockfile and aborts if that lockfile was not regenerated after a dependency change.

| Command                       | Effect                                                                                     |
|-------------------------------|--------------------------------------------------------------------------------------------|
| `uv sync`                     | Installs all project dependencies                         |
| `uv sync --group <group>`     | Also installs the dependencies declared in the named `<group>`                             |
| `uv sync --locked`            | Installs from `uv.lock` and fails if the lockfile is not up to date with `pyproject.toml`  |
| `uv sync --frozen`            | Installs from `uv.lock` as-is, without checking whether it matches `pyproject.toml`        |
| `uv pip list`                 | Lists the packages currently installed in the active environment                            |
| `uv lock --upgrade`           | Re-resolves the entire dependency graph and writes a new `uv.lock`                         |

#### Updating Dependencies

##### New Upstream Release, Constraint Unchanged

Consider a project that declares `click>=8.1.7` in `pyproject.toml`. When `uv sync` first runs, it resolves `click` to version `8.1.7`, pins it in `uv.lock`, and the lockfile is committed to version control. Later, `click 8.2.0` and `8.3.1` are published upstream. If the constraint in `pyproject.toml` stays unchanged, the newer release is not picked up automatically.

The constraint still reads `click>=8.1.7` and the lockfile already pins `8.1.7`, which satisfies it. Running `uv sync` installs `8.1.7` again because `uv` never upgrades a locked version on its own. To pick up the latest release, run `uv lock --upgrade-package click` followed by `uv sync`. This re-resolves only `click` (and its transitive dependencies), updates `uv.lock` to `8.3.1`, and installs the new version. To upgrade every package at once, run `uv lock --upgrade` instead.

```mermaid
flowchart LR
    A["uv.lock pins<br>click 8.1.7"] -->|uv sync| B["Installs click 8.1.7<br>(lockfile unchanged)"]
    A -->|uv lock --upgrade-package click| C["uv.lock updated to<br>click 8.3.1"]
    C -->|uv sync| D["Installs click 8.3.1"]
```

##### Constraint Changed

A developer changes the constraint from `click>=8.1.7` to `click>=8.2.0`. The locked version `8.1.7` no longer satisfies the new lower bound, so `uv sync` automatically re-resolves the dependency graph, updates `uv.lock` to `8.3.1`, and installs it. No separate `uv lock` step is needed.

```mermaid
flowchart LR
    A["pyproject.toml<br>click ≥8.2.0"] -->|uv sync| B["uv.lock updated to<br>click 8.3.1"]
    B --> C["Installs click 8.3.1"]
```

#### Lockfile

A lockfile is a machine-generated snapshot of the fully resolved dependency graph. It pins exact versions, records download URLs with cryptographic hashes, and captures transitive dependencies. Committing it to version control ensures that every developer, CI run, and production build installs bit-for-bit identical packages without re-running the resolver. Until recently, each tool generated its own proprietary format (e.g. `poetry.lock`, `Pipfile.lock`, `uv.lock`) making lockfiles non-portable. [PEP 751](https://peps.python.org/pep-0751/) addresses this by introducing `pylock.toml`, a standardised, tool-agnostic format for the Python ecosystem.

As described in [Install Dependencies](#install-dependencies), `uv sync` locks both direct and transitive dependencies into `uv.lock` for reproducible installs. Since uv `v0.7.0`, `uv export --format pylock.toml` can convert it into the standardised format. The excerpt below shows entries for `click` and its transitive dependency `colorama`, including the pinned version, source registry, SHA-256 hashes for the source distribution and wheel, and a platform-conditional dependency via an environment marker:

```toml
[[package]]
name = "click"
version = "8.3.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/.../click-8.3.1.tar.gz", hash = "sha256:12ff478..." }
wheels = [
    { url = "https://files.pythonhosted.org/.../click-8.3.1-py3-none-any.whl", hash = "sha256:981153a..." },
]

# transitive dependency of click (Windows only)
[[package]]
name = "colorama"
version = "0.4.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/.../colorama-0.4.6.tar.gz", hash = "sha256:08695f5..." }
wheels = [
    { url = "https://files.pythonhosted.org/.../colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d999..." },
]
```

---

### Testing

Testing is the practice of executing code in a controlled way to verify that it behaves as intended and to catch regressions when the codebase changes. In Python, tests are usually written as regular Python functions that assert on expected behavior, which keeps the feedback loop simple and accessible. The ecosystem is centered around tools such as `pytest`, which handle discovery, fixtures, parametrization, and failure reporting.

Automated tests verify that the code behaves as expected and catch regressions before they reach other developers or production. Without a test runner, verifying correctness means manually re-running the application after every change — which does not scale and is error-prone. Depsight uses [pytest](https://docs.pytest.org/). A basic test looks like this:

```python
# tests/test_math.py
def add(a: int, b: int) -> int:
    return a + b

def test_add() -> None:
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

Running `python -m pytest tests/` discovers and executes all `test_*` functions automatically.

---

### Code Quality Tools

#### Linter and Formatter

Linters and formatters improve source code quality before the program is ever run. In Python, this is especially valuable because the language emphasizes readability and has many style and correctness conventions that benefit from automatic enforcement. Modern Python tooling often combines import sorting, formatting, and static rule checking into a small number of fast commands that can run locally and in CI.

Depsight uses [Ruff](https://docs.astral.sh/ruff/) as its linter and formatter. Ruff is implemented in Rust and represents a modern consolidation of the Python tooling ecosystem. It is a full replacement of `flake8`, `isort`, and `black` in a single binary while being significantly faster than any of them. Rather than maintaining separate configuration files like `.flake8` or `tox.ini`, Ruff reads all its settings from `pyproject.toml` under `[tool.ruff]`, keeping the entire project configuration in one place. Running `ruff check` on the following code

```python
import os  # unused import
import sys

x=1+2      # missing whitespace around operator
print(x)
```

produces:

```
error[F401]: `os` imported but unused
error[E225]: missing whitespace around operator
```

Both issues are caught before the code is ever run or reviewed.

#### Type Checker

Type checking verifies that values are used consistently with their declared types, such as ensuring that a function expecting a `str` is not given an `int`. Python remains dynamically typed at runtime, but its type hint system has grown into a major part of modern development because it allows tools to analyze code statically before execution. In practice, Python type checkers improve refactoring safety, editor support, and API clarity, especially in larger projects and plugin-based architectures.

Depsight uses [mypy](https://mypy.readthedocs.io/) as its static type checker. Python is dynamically typed by default, which means type errors only surface at runtime. mypy analyses the code without running it and catches type mismatches, missing attributes, and incorrect function signatures before they can become runtime failures. It replaces the need for a standalone `mypy.ini` configuration file by reading its settings from `pyproject.toml` under `[tool.mypy]`. For a project like Depsight that exposes a plugin API, type annotations enforced by mypy also serve as living documentatio. Callers know exactly what a function expects and returns without having to read the implementation. Running `mypy` on the following code:

```python
def greet(name: str) -> str:
    return "Hello, " + name

result: int = greet("world")  # assigned to int, but greet returns str
print(result.upper())         # int has no upper() — runtime crash waiting to happen
```

produces:

```
error: Incompatible types in assignment (expression has type "str", variable has type "int")
```
