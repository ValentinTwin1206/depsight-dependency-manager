from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, runtime_checkable

# own imports
from deply.core.dependency import Dependency

@runtime_checkable
class BasePlugin(Protocol):
    """Contract for deply plugins.

    Any class that satisfies this protocol can be registered as a plugin,
    either as a built-in or via the ``deply.plugins`` entry-point group.

    Attributes
    ----------
    name:
        Human-readable identifier for the plugin (e.g. ``"uv"``).
    """


    def __init__(self) -> None:
        self.dependencies: list[Dependency] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the canonical name of the package manager."""

    def collect(self, path: str) -> list[tuple[str, str]]:
        """Return a list of `(package_name, version)` tuples found at *path*."""
        ...
