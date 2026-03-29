# Depsight — Claude Code Instructions

## Project Overview

**Depsight** is an extensible CLI tool for scanning and visualizing project dependencies across ecosystems (Python/uv, VS Code/vsce). It is built as a reference implementation for educational purposes.

→ For deeper context, see `README.md` and `CONTRIBUTING.md`.

---

## Stack & Tooling

| Concern        | Tool / Command                          |
|----------------|------------------------------------------|
| Runtime        | Python `>=3.12`                          |
| Build          | `uv build` (hatchling — no setuptools)  |
| Lint           | `ruff check src/ tests/`                |
| Type checking  | `mypy src/`                              |
| Tests          | `pytest tests/ -v`                       |
| CLI framework  | `rich-click`                             |
| TUI            | `Textual`                                |
| Formatting     | `Rich`                                   |

**Always prepend `from __future__ import annotations` to every module.**

---

## Verification Commands

Before considering any change complete, run in order:
```
ruff check src/ tests/
mypy src/
pytest tests/ -v
```
All three must pass with zero errors/warnings.

---

## Architecture Map

```
src/depsight/
├── cli.py                      # Entry point; command registration
├── core/
│   ├── dispatcher.py           # Routes commands; manages PluginFactory
│   └── plugins/
│       ├── __init__.py         # Clean namespace exports only
│       ├── base.py             # BasePlugin ABC, Dependency dataclass, PluginFactory
│       ├── uv/uv.py            # Parser for uv.lock (TOML)
│       └── vsce/vsce.py        # Parser for devcontainer.json extensions
├── commands/
│   └── scan.py                 # scan_handler: calls plugin.collect(), launches TUI
└── utils/                      # Constants, logging config, auto-discovery
```

---

## Plugin Contract (critical)

Every plugin lives at `src/depsight/core/plugins/<name>/<name>.py`.

1. Subclass `BasePlugin`.
2. Implement `@property name(self) -> str`.
3. Implement `collect(self, path: Path) -> None` — **must be synchronous**.
4. Populate `self.dependencies: list[Dependency]` using the `Dependency` dataclass (`@dataclass(slots=True)`).
5. Register in `pyproject.toml` under `[project.entry-points."depsight.plugins"]`.

---

## Code Conventions (non-negotiable)

- **Type aliases**: Use PEP 695 `type Alias = ...` syntax.
- **Import order**: stdlib → third-party (Rich, Click, Textual) → `# local imports` (absolute: `from depsight.core...`).
- **Paths**: `pathlib.Path` only. No `os.path`, no string concatenation for paths.
- **Output**: `rich.console` for user-facing output; `logging` for status/debug. No `print()`.
- **Logging**: `logger = logging.getLogger(__name__)`. Log during discovery and collection.
- **State**: No globals. Pass state via classes or dependency injection.
- **`__init__.py`**: Namespace exports only — no logic.
- **TUI**: All Textual widgets stay in the TUI layer. Event handlers use `async def`.
- **Docstrings**: NumPy style with `Parameters`, `Returns`, and `Raises` sections.

---

## Anti-Patterns — Never Do These

- `os.path` → use `pathlib.Path`
- `print()` → use `rich.console` or `logging`
- Global state → use dependency injection
- Logic in `__init__.py` → exports only
- `setuptools` / `setup.py` → use `hatchling`

---

## Additional Context Files

For task-specific detail, reference these with `@`:
- `@CONTRIBUTING.md` — release workflow, PR process
- `@pyproject.toml` — entry-points, dependencies, build config
- `@src/depsight/core/plugins/base.py` — BasePlugin ABC and Dependency dataclass