from __future__ import annotations

from pathlib import Path

# own imports
from deply.core.plugins.vsce.vsce import VSCEPlugin
from deply.core.plugins.dependency import Dependency


class TestVSCEPluginCollect:
    """VSCEPlugin.collect() test suite."""

    # ------------------------------------------------------------------
    # Valid devcontainer.json with extensions
    # ------------------------------------------------------------------
    def test_collect_finds_extensions(self, vsc_project_valid: Path):
        """All listed extensions are collected."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        names = [d.name for d in plugin.dependencies]
        assert "ms-python.python" in names
        assert "ms-python.vscode-pylance" in names
        assert "charliermarsh.ruff" in names

    def test_collect_extension_count(self, vsc_project_valid: Path):
        """The correct number of extensions is collected."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        assert len(plugin.dependencies) == 3

    def test_collect_category_is_dev(self, vsc_project_valid: Path):
        """VS Code extensions are classified as 'dev'."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        assert all(d.category == "dev" for d in plugin.dependencies)

    def test_collect_tool_name(self, vsc_project_valid: Path):
        """Every dependency is tagged with the plugin name."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        assert all(d.tool_name == "vsce" for d in plugin.dependencies)

    def test_collect_registry(self, vsc_project_valid: Path):
        """Registry points to the VS Code Marketplace."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        assert all(
            d.registry == "https://marketplace.visualstudio.com"
            for d in plugin.dependencies
        )

    def test_collect_file_path(self, vsc_project_valid: Path):
        """Every dependency records the devcontainer.json path."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        expected = str((vsc_project_valid / ".devcontainer" / "devcontainer.json").resolve())
        assert all(d.file == expected for d in plugin.dependencies)

    def test_collect_returns_dependency_instances(self, vsc_project_valid: Path):
        """All items in the dependency list are Dependency dataclasses."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_valid)

        assert all(isinstance(d, Dependency) for d in plugin.dependencies)

    # ------------------------------------------------------------------
    # devcontainer.json without extensions key
    # ------------------------------------------------------------------
    def test_collect_no_extensions_key(self, vsc_project_no_extensions: Path):
        """A devcontainer.json without extensions yields zero dependencies."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_no_extensions)

        assert plugin.dependencies == []

    # ------------------------------------------------------------------
    # Invalid JSON
    # ------------------------------------------------------------------
    def test_collect_invalid_json(self, vsc_project_invalid_json: Path):
        """Malformed JSON is handled gracefully (no crash, empty list)."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_invalid_json)

        assert plugin.dependencies == []

    # ------------------------------------------------------------------
    # Missing devcontainer.json
    # ------------------------------------------------------------------
    def test_collect_missing_devcontainer(self, vsc_project_missing: Path):
        """A project with no devcontainer.json yields zero dependencies."""
        plugin = VSCEPlugin()
        plugin.collect(vsc_project_missing)

        assert plugin.dependencies == []

    # ------------------------------------------------------------------
    # Accepts string path
    # ------------------------------------------------------------------
    def test_collect_accepts_string_path(self, vsc_project_valid: Path):
        """`collect()` works when called with a `str` path."""
        plugin = VSCEPlugin()
        plugin.collect(str(vsc_project_valid))

        assert len(plugin.dependencies) == 3
