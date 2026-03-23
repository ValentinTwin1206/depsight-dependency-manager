import logging
from pathlib import Path
from typing import Callable

# third-party imports
from rich.console import Console

# own imports
from depsight.commands.scan import scan_handler
from depsight.core.plugins.factory import PluginFactory
from depsight.utils.constants import SUPPORTED_PLUGINS
from depsight.utils.logger import get_logger

# Command registry: maps command names to handler callables
COMMAND_HANDLERS: dict[str, Callable] = {
    "scan": scan_handler,
}


def run_handler(command: str, options: dict):
    """Look up the command handler by name, resolve the plugin, and dispatch.

    Uses the :data:`COMMAND_HANDLERS` registry to find the handler for
    *command* and :class:`~depsight.core.factory.PluginFactory` to instantiate
    the plugin from the plugin registry.

    Parameters
    ----------
    command - The action to perform (e.g. `"scan"`).

    options - A dict of CLI options (e.g. `plugin_name`, `project_dir`, `verbose`).
    """

    console = Console()

    # Look up handler
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        console.print(f"[bold red]Unknown command '{command}'. "
                       f"Available: {', '.join(COMMAND_HANDLERS)}[/bold red]")
        return 1

    # Destructure options
    plugin_name: str = options["plugin_name"]
    project_dir = Path(options["project_dir"]).resolve()
    verbose: bool = options.get("verbose", False)
    as_csv: bool = options.get("as_csv", False)

    # Init logger
    log_level = logging.DEBUG if verbose else logging.INFO
    logger = get_logger(command, level=log_level)

    try:
        logger.info(f"Executing command '{command}' with plugin '{plugin_name}' on project '{project_dir}'")
        logger.info(f"Supported plugins: {', '.join(SUPPORTED_PLUGINS)}")
        plugin = PluginFactory.create(plugin_name)
        logger.debug(f"Resolved plugin '{plugin_name}': {plugin}")

        # Execute public handler under '/commands/<command>/<command>.py'
        logger.info(f"Running handler for command '{command}'...")
        handler(plugin, project_dir, logger, as_csv=as_csv)

        logger.info(f"Command '{command}' executed successfully. Terminating with exit code 0.")
        return 0
    
    except Exception as exc:
        logger.warning("Execution of command %r failed", command)
        logger.error(exc)
        console.print(f"{exc!s}")
        console.print("[bold red]Terminating Depsight with exit code '1'.[/bold red]")
        return 1
