# Depsight — Copilot Instructions

## Stack

- **Python** `>=3.12` — use `from __future__ import annotations` in every module
- **Build**: `uv_build` (not setuptools); build with `uv build`
- **Lint**: `ruff check src/ tests/`
- **Types**: `mypy src/`
- **Tests**: `pytest tests/ -v`
- **CLI**: `rich-click` (Click wrapper); **TUI**: Textual; **output**: Rich

## Architecture

```
depsight.cli          — entry point; registers plugin commands at import time
depsight.core.dispatcher  — routes CLI commands → handlers, instantiates plugins via PluginFactory
depsight.core.plugins — BasePlugin ABC, Dependency dataclass, PluginFactory
  └─ uv/             — parses uv.lock (TOML)
  └─ vsce/           — parses devcontainer.json extensions
depsight.commands.scan — scan_handler: calls plugin.collect(), launches Textual TUI
depsight.utils        — constants, logging, plugin/command auto-discovery
```

## Writing a Plugin

Every plugin lives at `src/depsight/core/plugins/<name>/<name>.py`:

1. Subclass `BasePlugin` and implement:
   - `@property name(self) -> str` — canonical key (e.g. `"uv"`)
   - `collect(self, path: str | Path) -> None` — populate `self.dependencies: list[Dependency]`
2. Register in `pyproject.toml` under `[project.entry-points."depsight.plugins"]`

`Dependency` is a `@dataclass(slots=True)` — see `src/depsight/core/plugins/dependency.py`.

## Code Conventions

- `from __future__ import annotations` at the top of every module
- Import order: stdlib → third-party → `# own imports`
- `pathlib.Path` over string paths
- `type X = ...` alias syntax (Python 3.12+)
- Logging: `logging.getLogger(__name__)` per module
- Textual CSS in `.tcss` files alongside the widget module
- Docstrings: NumPy style with `Parameters` / `Returns` / `Raises` and dash separators

## Release Checklist

Before tagging a release, update `versions.env` if the Python or uv version has changed.
See `README.md` → **Build → Release** for the full workflow.
