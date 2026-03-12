from __future__ import annotations

import csv
from abc import abstractmethod
from dataclasses import fields
from pathlib import Path
from typing import Protocol, runtime_checkable

# own imports
from depsight.core.plugins.dependency import Dependency

@runtime_checkable
class BasePlugin(Protocol):
    """Contract for depsight plugins.

    Any class that satisfies this protocol can be registered as a plugin,
    either as a built-in or via the `depsight.plugins` entry-point group.

    Attributes
    ----------
    name:
        Human-readable identifier for the plugin (e.g. `"uv"`).
    """

    dependencies: list[Dependency]

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the canonical name of the package manager."""

    def collect(self, path: str | Path) -> None:
        """Populate *self.dependencies* from files found at *path*."""
        ...

    def export(self, project_dir: str | Path, output_dir: str | Path) -> Path:
        """Export *self.dependencies* to a CSV file.

        The file is named `<plugin_name>_<project_dir_name>.csv`.

        Parameters
        ----------
        project_dir - The project root whose basename is used in the filename.

        output_dir - Directory where the CSV file will be written.

        Returns
        -------
        Path
            Absolute path to the created CSV file.
        """
        project_name = Path(project_dir).resolve().name
        dest = Path(output_dir)

        dest.mkdir(parents=True, exist_ok=True)
        csv_path = dest / f"{self.name}_{project_name}.csv"

        header = [f.name for f in fields(Dependency)]
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            for dep in self.dependencies:
                writer.writerow(getattr(dep, col) for col in header)

        return csv_path
