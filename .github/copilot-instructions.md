# Depsight — Copilot Instructions

## Project Intent

**Depsight** is an extensible CLI tool designed for **educational and training purposes**. It serves as a reference implementation for scanning and visualizing project dependencies across ecosystems (Python/uv, VS Code/vsce).

## Stack

- **Python**: `>=3.12` — Use `from __future__ import annotations` in every module.
- **Build System**: `hatchling` (via `uv build`); strictly avoid `setuptools` or `setup.py`.
- **Lint/Format**: `ruff check src/ tests/`
- **Type Checking**: `mypy src/`
- **Testing**: `pytest tests/ -v` (Use fixtures and `pathlib.Path` for all file-based mocks).
- **CLI**: `rich-click` (Click wrapper).
- **TUI**: `Textual` (Reactive UI).
- **Formatting**: `Rich` (Console output).

## Architecture

- **depsight.cli**: Entry point; handles command registration and initial console setup.
- **depsight.core.dispatcher**: Routes CLI commands to handlers; manages the `PluginFactory`.
- **depsight.core.plugins**: Contains `BasePlugin` ABC, `Dependency` dataclass, and `PluginFactory`.
    - **uv/**: Parser for `uv.lock` (TOML).
    - **vsce/**: Parser for `devcontainer.json` extensions.
- **depsight.commands.scan**: The `scan_handler`. Triggers `plugin.collect()` and launches the Textual TUI.
- **depsight.utils**: Shared constants, logging configuration, and auto-discovery logic.

## Writing a Plugin

All plugins must reside in `src/depsight/core/plugins/<name>/<name>.py`.

1. **Subclass `BasePlugin`**:
   - Implement `@property name(self) -> str` (e.g., `"uv"`).
   - Implement `collect(self, path: Path) -> None`: Populates `self.dependencies: list[Dependency]`.
   - **Constraint**: `collect()` must remain **synchronous** to support standard CLI usage.
2. **Data Model**: Use the `Dependency` dataclass (`@dataclass(slots=True)`).
3. **Registration**: Ensure the plugin is registered in `pyproject.toml` under `[project.entry-points."depsight.plugins"]`.

## Code Conventions

- **Typing**: Use `type Alias = ...` syntax for type aliases (PEP 695).
- **Imports**: 
    1. Standard Library
    2. Third-party (Rich, Click, Textual)
    3. `# local imports` (use absolute paths: `from depsight.core...`)
- **Paths**: Use `pathlib.Path` exclusively. No string concatenation for file paths.
- **Logging**: Use `logger = logging.getLogger(__name__)`. Log significant events during discovery and collection.
- **TUI Logic**: All Textual widgets should stay in the TUI layer. Event handlers use `async def`.
- **Docstrings**: NumPy style. Include `Parameters`, `Returns`, and `Raises` sections.

## Anti-Patterns

- **No `os.path`**: Use `pathlib`.
- **No `print()`**: Use `rich.console` for output or `logging` for status.
- **No Globals**: Keep state within classes or passed via dependency injection.
- **No Logic in `__init__.py`**: Keep these files restricted to clean namespace exports.

## Release Checklist

1. Update `version` in `pyproject.toml`.
2. Update `uv` version in `.github/workflows/` and `.devcontainer/devcontainer.json`.
3. Ensure `ruff` and `mypy` pass without warnings.
4. Follow the full workflow in `CONTRIBUTING.md`.