import sys

# third-party imports
import rich_click as click

from depsight.core.dispatcher import dispatch_command
from depsight.utils.constants import APP_BANNER, COLOR_DIM_ORANGE, COLOR_PEACH, SUPPORTED_PLUGINS

# rich-click styling
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 2)
click.rich_click.HEADER_TEXT = APP_BANNER
click.rich_click.STYLE_COMMAND = COLOR_DIM_ORANGE
click.rich_click.STYLE_OPTION = COLOR_DIM_ORANGE
click.rich_click.STYLE_SWITCH = COLOR_PEACH
click.rich_click.STYLE_USAGE = f"bold {COLOR_PEACH}"
click.rich_click.STYLE_USAGE_COMMAND = f"bold {COLOR_DIM_ORANGE}"
click.rich_click.STYLE_USAGE_SEPARATOR = COLOR_DIM_ORANGE
click.rich_click.STYLE_METAVAR = COLOR_PEACH
click.rich_click.STYLE_METAVAR_APPEND = COLOR_PEACH
click.rich_click.STYLE_ARGUMENT = COLOR_PEACH
click.rich_click.COMMAND_GROUPS = {
    "depsight": [{"name": "Package Managers", "commands": list(SUPPORTED_PLUGINS.keys())}]
}


@click.group()
@click.version_option(__version__, "--version", "-V", prog_name="depsight")
def main():
    """A modern TUI framework for scanning local project dependencies."""
    pass


def _register_plugin(plugin_name: str):
    """Register a plugin as a Click subgroup with its commands.

    Creates a new :func:`click.Group` attached to :func:`main` and registers
    all available sub-commands (e.g. `scan`) under it.  This function is
    called at **module import time** for every key in
    :data:`~depsight.core.registry.SUPPORTED_PLUGINS` so that the commands are
    available before Click parses the CLI arguments.

    Parameters
    ----------
    plugin_name : str
        Key in `SUPPORTED_PLUGINS` identifying the plugin (e.g. `"uv"`).
    """

    @main.group(plugin_name, help=f"Commands for the '{plugin_name}' package manager.")
    @click.pass_context
    def plugin_group(ctx):
        """Entry point for a plugin subgroup that stores the plugin name in the context."""
        ctx.ensure_object(dict)
        ctx.obj["plugin_name"] = plugin_name


    #
    # SCAN COMMAND
    # # # # # # # #
    @plugin_group.command("scan")
    @click.option(
        "--project-dir",
        type=click.Path(exists=True),
        required=True,
        help="Path to the project."
    )
    @click.option(
        "--verbose",
        is_flag=True,
        help="Enable verbose logging."
    )
    @click.option(
        "--as-csv",
        is_flag=True,
        help="Export scan results to a CSV file."
    )
    @click.pass_context
    def scan(ctx, project_dir, verbose, as_csv):
        """Scan project dependencies using the selected plugin."""
        options = {
            "plugin_name": ctx.obj["plugin_name"],
            "project_dir": project_dir,
            "verbose": verbose,
            "as_csv": as_csv,
        }
        sys.exit(dispatch_command("scan", options))


#
# PLUGIN REGISTRATION
# # # # # # # # #
for _name in SUPPORTED_PLUGINS:
    _register_plugin(_name)


if __name__ == "__main__":
    main()
