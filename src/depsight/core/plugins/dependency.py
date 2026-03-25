"""Data structures shared by all package managers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

type packageType = Literal["dev", "prod"]


@dataclass(slots=True)
class Dependency:
    """Single dependency discovered by a package manager.

    Every concrete :class:`BasePkgManager` populates a list of these
    so that the rest of the application can rely on a single,
    well-defined schema instead of ad-hoc dicts.

    Attributes
    ----------
    name - Package or extension identifier.

    version - Resolved / locked version (`None` when unknown).

    constraint - Version specifier from the manifest (`None` when absent).

    tool_name - Name of the plugin / tool.

    registry - URL of the package registry (`None` when not applicable).

    file - Absolute path to the file this dependency was read from.

    category - Dependency classification: `"dev"` or `"prod"`.

    is_transitive - Whether this dependency is a transitive (indirect) dependency.
    """

    name: str
    version: str | None = None
    constraint: str | None = None
    tool_name: str | None = None
    registry: str | None = None
    file: str | None = None
    category: packageType = "prod"
    is_transitive: bool = False
