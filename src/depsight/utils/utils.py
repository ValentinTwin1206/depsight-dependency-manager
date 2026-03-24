from __future__ import annotations

import importlib
import importlib.metadata
import os

from pathlib import Path


def resolve_user_dir(app_name: str, *, dev_mode: bool) -> Path:
    """Return the user-level base directory for Depsight.

    Parameters
    ----------
    app_name - Application name (used to build `~/.{app_name}`).
    
    dev_mode - If `True`, return the repository root directory.

    Returns
    -------
    Path
        The resolved user-level directory path.
    """
    if dev_mode:
        return Path(__file__).resolve().parents[3] / f".{app_name}"
    return Path.home() / f".{app_name}"


def resolve_output_dir(default: Path) -> Path:
    """Return the output directory for exported files.

    Uses the `DEPSIGHT_OUTPUT_DIR` environment variable when set,
    otherwise falls back to *default*.

    Parameters
    ----------
    default - The fallback directory derived from DEPSIGHT_HOME.

    Returns
    -------
    Path
        The resolved output directory path.
    """
    env_value = os.getenv("DEPSIGHT_OUTPUT_DIR")
    if env_value:
        return Path(env_value)
    return default


def discover_plugins(app_name: str) -> dict:
    """Build the full plugin registry from entry points.

    All plugins (built-in and third-party) are discovered via the
    `<app_name>.plugins` entry-point group declared in `pyproject.toml`.

    Parameters
    ----------
    app_name - Application name used to look up the entry-point group (e.g. `"depsight"`).

    Returns
    -------
    dict[str, type]
        A mapping of plugin name → plugin class.
    """
    registry: dict[str, type] = {}

    # discover plugins via entry points
    entry_points = importlib.metadata.entry_points(group=f"{app_name}.plugins")
    for ep in entry_points:
        try:
            plugin_cls = ep.load()
            registry[ep.name] = plugin_cls
        except Exception:
            raise SystemExit(f"Failed to load plugin '{ep.name}'.")

    return registry