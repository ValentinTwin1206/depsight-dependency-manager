from __future__ import annotations

# thrid-party imports
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer

# own imports
from depsight.core.plugins.dependency import Dependency


class ScanResultTableViewer(App):
    """Textual app that displays a list of dependencies in a DataTable.

    Instantiate with the dependency list collected by a plugin and
    call :meth:`run` to launch the interactive viewer::

        viewer = ScanResultTableViewer(plugin.dependencies)
        viewer.run()

    Parameters
    ----------
    result - A list of :class:`~depsight.core.dependency.Dependency` objects.
    """

    CSS_PATH = "scan_widgets.tcss"

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, result: list[Dependency]) -> None:
        """Initialize the viewer with the given dependency list."""
        super().__init__()
        self.result = result

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        """Populate the DataTable with dependency rows on mount."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Package", "Version", "Category", "Transitive", "Constraint", "Registry")
        for dep in self.result:
            table.add_row(
                dep.name,
                dep.version or "—",
                dep.category or "prod",
                "yes" if dep.is_transitive else "no",
                dep.constraint or "—",
                dep.registry or "—",
            )
