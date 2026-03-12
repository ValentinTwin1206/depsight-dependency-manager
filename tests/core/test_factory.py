from __future__ import annotations

import pytest

# own imports
from depsight.core.plugins.base import BasePlugin
from depsight.core.plugins.factory import PluginFactory


class TestPluginFactoryCreate:
    """PluginFactory.create() test suite."""

    def test_create_uv_plugin(self):
        """Creating the 'uv' plugin returns a valid BasePlugin instance."""
        plugin = PluginFactory.create("uv")

        assert isinstance(plugin, BasePlugin)
        assert plugin.name == "uv"
        assert hasattr(plugin, "dependencies")

    def test_create_vsce_plugin(self):
        """Creating the 'vsce' plugin returns a valid BasePlugin instance."""
        plugin = PluginFactory.create("vsce")

        assert isinstance(plugin, BasePlugin)
        assert plugin.name == "vsce"
        assert hasattr(plugin, "dependencies")

    def test_create_unknown_plugin_raises_value_error(self):
        """Requesting an unregistered plugin name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown plugin 'nonexistent'"):
            PluginFactory.create("nonexistent")

    def test_created_plugin_has_empty_dependencies(self):
        """A freshly created plugin starts with an empty dependency list."""
        plugin = PluginFactory.create("uv")
        assert plugin.dependencies == []

    def test_created_plugin_has_collect_method(self):
        """Every created plugin exposes a callable `collect` method."""
        plugin = PluginFactory.create("uv")
        assert callable(getattr(plugin, "collect", None))
