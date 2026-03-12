from __future__ import annotations

# own imports
from depsight.core.plugins.base import BasePlugin
from depsight.utils.constants import SUPPORTED_PLUGINS


class PluginFactory:
    """Create plugin instances by name.

    Looks up the plugin class in `SUPPORTED_PLUGINS` and returns a
    validated `BasePlugin` instance.

    Usage::

        plugin = PluginFactory.create("uv")
        deps = plugin.collect_dependencies("/path/to/project")
    """

    @staticmethod
    def create(plugin_name: str) -> BasePlugin:
        """Instantiate and return a plugin.

        Parameters
        ----------
        plugin_name - Key in `SUPPORTED_PLUGINS` (e.g. `"uv"`).

        Raises
        ------
        ValueError
            If *plugin_name* is not found in the registry.
        TypeError
            If the registered class does not conform to :class:`BasePlugin`.
        """
        plugin_cls = SUPPORTED_PLUGINS.get(plugin_name)
        if plugin_cls is None:
            raise ValueError(
                f"Unknown plugin '{plugin_name}'. "
                f"Available: {', '.join(SUPPORTED_PLUGINS)}"
            )

        plugin = plugin_cls()

        if not isinstance(plugin, BasePlugin):
            raise TypeError(
                f"Plugin '{plugin_name}' ({plugin_cls.__qualname__}) "
                "does not implement BasePlugin."
            )

        return plugin
