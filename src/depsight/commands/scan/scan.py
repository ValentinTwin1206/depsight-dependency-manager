import logging
from pathlib import Path

# third-party imports
from rich.console import Console

# own imports
from depsight.commands.scan.scan_widgets import ScanResultTableViewer
from depsight.utils.constants import COLOR_DIM_ORANGE, COLOR_PEACH, USER_DATA_DIR

logger = logging.getLogger(__name__)


def scan_handler(plugin, project_dir: str | Path, *, as_csv: bool = False):
    """Scan a project for dependencies using the given plugin.

    Invokes :pymethod:`plugin.collect` on *project_dir* to populate
    `plugin.dependencies`, then launches the Textual viewer.

    Parameters
    ----------
    plugin - An instantiated plugin that conforms to :class:`BasePlugin`.
    
    project_dir - Absolute path to the project root to scan.

    as_csv - When `True`, export the results to a CSV file.
    """

    console = Console()

    logger.info("Starting scan in '%s' with plugin '%s'", project_dir, plugin.name)
    console.print()
    console.print(f"Scanning [{COLOR_PEACH}]{project_dir}[/{COLOR_PEACH}] using [{COLOR_DIM_ORANGE}]{plugin.name}[/{COLOR_DIM_ORANGE}]")
    console.print()

    # Collect dependencies using the plugin's collect() method
    logger.debug("Calling plugin.collect('%s')", project_dir)
    plugin.collect(project_dir)
    logger.debug("Plugin returned %d dependency(ies)", len(plugin.dependencies))

    if not plugin.dependencies:
        logger.warning("No dependencies found in '%s' — lockfile may be missing or empty", project_dir)
        console.print("[yellow]No dependencies found.[/yellow]")
        return

    # Launch Textual app to display results
    viewer = ScanResultTableViewer(plugin.dependencies)
    logger.info("Rendering table with %d dependencies", len(plugin.dependencies))
    viewer.run()

    # Optionally export results to CSV using the plugin's export() method
    if as_csv:
        csv_path = plugin.export(project_dir, USER_DATA_DIR)
        logger.info("CSV exported to '%s'", csv_path)
        console.print(f"\n[{COLOR_PEACH}]CSV exported to[/{COLOR_PEACH}] [{COLOR_DIM_ORANGE}]{csv_path}[/{COLOR_DIM_ORANGE}]")