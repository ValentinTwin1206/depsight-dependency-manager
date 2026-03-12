"""Rich renderables for the *scan* command output."""

from __future__ import annotations

from rich import box
from rich.table import Table
from rich.text import Text

from depsight.core.plugins.dependency import Dependency
from depsight.utils.constants import COLOR_DIM_ORANGE, COLOR_PEACH


class ScanResultTableViewer:
    """Rich renderable that displays a list of dependencies as a styled table.

    Instantiate with the dependency list collected by a plugin and
    print it with any :class:`rich.console.Console`::

        viewer = ScanResultTableViewer(plugin.dependencies)
        console.print(viewer)

    Parameters
    ----------
    result - A list of :class:`~depsight.core.dependency.Dependency` objects.
    """

    def __init__(self, result: list[Dependency]) -> None:
        """Initialize the viewer with the given dependency list."""

        self.result = result
        self.category_styles: dict[str, str] = {
            "prod": f"bold {COLOR_PEACH}",
            "dev": f"bold {COLOR_DIM_ORANGE}",
        }

    def _styled_category(self, category: str) -> Text:
        """Return a :class:`Text` with the category styled per the color map."""
        style = self.category_styles.get(category, f"bold {COLOR_PEACH}")
        return Text(category, style=style)

    def __rich__(self) -> Table:
        """Build and return the styled :class:`rich.table.Table`."""
        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style=COLOR_DIM_ORANGE,
            header_style=f"bold {COLOR_DIM_ORANGE}",
            pad_edge=True,
            expand=False,
        )

        # Define heading rows and column styles
        table.add_column("Package", min_width=14)
        table.add_column("Version", justify="right", min_width=8)
        table.add_column("Category", justify="center", min_width=8)
        table.add_column("Constraint", justify="center")
        table.add_column("Registry", max_width=30, no_wrap=True)

        # Append a row for each dependency in the result list
        for dep in self.result:
            table.add_row(
                dep.name,
                dep.version or "—",
                self._styled_category(dep.category or "prod"),
                dep.constraint or "—",
                dep.registry or "—",
            )

        return table

    # Convenience so the object is directly printable
    __rich_console__ = None  # let Rich fall back to __rich__
