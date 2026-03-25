import logging
from pathlib import Path

# third-party imports
from rich.console import Console

# own imports
from depsight.core.plugins.factory import PluginFactory
from depsight.utils.constants import COMMANDS_REGISTRY
from depsight.utils.logger import setup_logging

logger = logging.getLogger(__name__)


def dispatch_command(command: str, options: dict):
    """Look up the command handler by name, resolve the plugin, and dispatch.

    Uses :func:`~depsight.utils.utils.discover_commands` to build the
    command registry and :class:`~depsight.core.factory.PluginFactory` to
    instantiate the plugin from the plugin registry.

    Parameters
    ----------
    command - The action to perform (e.g. `"scan"`).

    options - A dict of CLI options (e.g. `plugin_name`, `project_dir`, `verbose`).
    """

    console = Console()

    # Look up available command handlers
    logger.debug("Available commands: %s", list(COMMANDS_REGISTRY.keys()))

    # Look up handler
    handler = COMMANDS_REGISTRY.get(command)
    if handler is None:
        console.print(f"[bold red]Unknown command '{command}'. "
                       f"Available: {', '.join(COMMANDS_REGISTRY)}[/bold red]")
        return 1

    # Destructure options
    plugin_name: str = options["plugin_name"]
    project_dir = Path(options["project_dir"]).resolve()
    verbose: bool = options.get("verbose", False)
    as_csv: bool = options.get("as_csv", False)

    # Configure logging once for the whole application
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=log_level)

    try:
        logger.info(f"Executing command '{command}' with plugin '{plugin_name}' on project '{project_dir}'")
        plugin = PluginFactory.create(plugin_name)
        logger.debug(f"Resolved plugin '{plugin_name}': {plugin}")

        # Execute public handler under '/commands/<command>/<command>.py'
        logger.info(f"Running handler for command '{command}'...")
        handler(plugin, project_dir, as_csv=as_csv)

        logger.info(f"Command '{command}' executed successfully. Terminating with exit code 0.")
        return 0
    
    except Exception as exc:
        logger.warning("Execution of command %r failed", command)
        logger.error(exc)
        console.print(f"{exc!s}")
        console.print("[bold red]Terminating Depsight with exit code '1'.[/bold red]")
        return 1
