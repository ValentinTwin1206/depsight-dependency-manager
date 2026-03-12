import logging
from pathlib import Path
from typing import Callable

# third-party imports
from rich.console import Console

# own imports
from depsight.core.plugins.factory import PluginFactory
from depsight.utils.constants import SUPPORTED_PLUGINS
from depsight.utils.logger import get_logger


def run_handler(command: str, handler: Callable, options: dict):
    """Resolve a plugin by name and execute the requested command.

    Uses :class:`~depsight.core.factory.PluginFactory` to instantiate the plugin
    from the registry and dispatches the given `command` via the provided
    `handler` callable.

    Parameters
    ----------
    command - The action to perform (e.g. `"scan"`).

    handler - A callable that implements the command logic.

    options - A dict of CLI options (e.g. `plugin_name`, `project_dir`, `verbose`).
    """

    console = Console()

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
