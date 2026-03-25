from __future__ import annotations

from pathlib import Path

# own imports
from depsight.core.plugins.uv.uv import UVPlugin
from depsight.core.plugins.dependency import Dependency


class TestUVPluginCollect:
    """UVPlugin.collect() test suite."""

    # ------------------------------------------------------------------
    # Full lockfile (editable block with prod + dev deps)
    # ------------------------------------------------------------------
    def test_collect_prod_deps(self, uv_project_full: Path):
        """Prod dependencies are parsed with correct metadata."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        names = {d.name for d in plugin.dependencies}
        assert "click" in names
        assert "rich" in names

    def test_collect_prod_category(self, uv_project_full: Path):
        """Runtime dependencies are classified as 'prod'."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        prod = [d for d in plugin.dependencies if d.name == "click"]
        assert len(prod) == 1
        assert prod[0].category == "prod"

    def test_collect_dev_category(self, uv_project_full: Path):
        """Dev optional-dependencies are classified as 'dev'."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        dev = [d for d in plugin.dependencies if d.name == "pytest"]
        assert len(dev) == 1
        assert dev[0].category == "dev"

    def test_collect_dev_constraint(self, uv_project_full: Path):
        """Dev dependency constraints from requires-dev are captured."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        pytest_dep = next(d for d in plugin.dependencies if d.name == "pytest")
        assert pytest_dep.constraint == ">=8.0"

    def test_collect_build_group_is_dev(self, uv_project_full: Path):
        """The 'build' dev-dependency group is classified as 'dev'."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        nuitka = next(d for d in plugin.dependencies if d.name == "nuitka")
        assert nuitka.category == "dev"
        assert nuitka.constraint == ">=2.0"

    def test_collect_docs_group_is_dev(self, uv_project_full: Path):
        """PEP 735 [dependency-groups] are always 'dev', including 'docs'."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        mkdocs = next(d for d in plugin.dependencies if d.name == "mkdocs")
        assert mkdocs.category == "dev"
        assert mkdocs.constraint == ">=1.6"

    def test_collect_versions(self, uv_project_full: Path):
        """Locked versions are captured from the lockfile."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        click_dep = next(d for d in plugin.dependencies if d.name == "click")
        assert click_dep.version == "8.3.1"

    def test_collect_constraints(self, uv_project_full: Path):
        """Version constraints from requires-dist are captured."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        click_dep = next(d for d in plugin.dependencies if d.name == "click")
        assert click_dep.constraint == ">=8.1.7"

    def test_collect_registry(self, uv_project_full: Path):
        """Registry URL is captured from the source field."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        click_dep = next(d for d in plugin.dependencies if d.name == "click")
        assert click_dep.registry is not None
        assert click_dep.registry.startswith("https://")

    def test_collect_tool_name(self, uv_project_full: Path):
        """Every dependency is tagged with the plugin name."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        assert all(d.tool_name == "uv" for d in plugin.dependencies)

    def test_collect_file_path(self, uv_project_full: Path):
        """Every dependency records the lockfile path."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        expected = str((uv_project_full / "uv.lock").resolve())
        assert all(d.file == expected for d in plugin.dependencies)

    def test_collect_returns_dependency_instances(self, uv_project_full: Path):
        """All items in the dependency list are Dependency dataclasses."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        assert all(isinstance(d, Dependency) for d in plugin.dependencies)

    # ------------------------------------------------------------------
    # Transitive dependency detection
    # ------------------------------------------------------------------
    def test_collect_direct_deps_not_transitive(self, uv_project_full: Path):
        """Direct runtime dependencies are not marked as transitive."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        click_dep = next(d for d in plugin.dependencies if d.name == "click")
        assert click_dep.is_transitive is False

    def test_collect_dev_deps_not_transitive(self, uv_project_full: Path):
        """Direct dev dependencies are not marked as transitive."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        pytest_dep = next(d for d in plugin.dependencies if d.name == "pytest")
        assert pytest_dep.is_transitive is False

    def test_collect_transitive_dep_detected(self, uv_project_full: Path):
        """Packages not declared directly are marked as transitive."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        markupsafe = next(d for d in plugin.dependencies if d.name == "markupsafe")
        assert markupsafe.is_transitive is True

    def test_collect_transitive_dep_has_version(self, uv_project_full: Path):
        """Transitive dependencies still have their version resolved."""
        plugin = UVPlugin()
        plugin.collect(uv_project_full)

        markupsafe = next(d for d in plugin.dependencies if d.name == "markupsafe")
        assert markupsafe.version == "3.0.2"

    # ------------------------------------------------------------------
    # Lockfile without editable block
    # ------------------------------------------------------------------
    def test_collect_no_editable_all_prod(self, uv_project_no_editable: Path):
        """Without an editable block every locked package defaults to 'prod'."""
        plugin = UVPlugin()
        plugin.collect(uv_project_no_editable)

        assert len(plugin.dependencies) == 2
        assert all(d.category == "prod" for d in plugin.dependencies)

    def test_collect_no_editable_not_transitive(self, uv_project_no_editable: Path):
        """Without an editable block, is_transitive defaults to False."""
        plugin = UVPlugin()
        plugin.collect(uv_project_no_editable)

        assert all(d.is_transitive is False for d in plugin.dependencies)

    def test_collect_no_editable_versions(self, uv_project_no_editable: Path):
        """Versions are still resolved when there is no editable block."""
        plugin = UVPlugin()
        plugin.collect(uv_project_no_editable)

        names_versions = {d.name: d.version for d in plugin.dependencies}
        assert names_versions["click"] == "8.3.1"
        assert names_versions["rich"] == "14.3.3"

    # ------------------------------------------------------------------
    # Empty lockfile (no packages)
    # ------------------------------------------------------------------
    def test_collect_empty_lockfile(self, uv_project_empty: Path):
        """An empty lockfile yields zero dependencies."""
        plugin = UVPlugin()
        plugin.collect(uv_project_empty)

        assert plugin.dependencies == []

    # ------------------------------------------------------------------
    # Missing lockfile
    # ------------------------------------------------------------------
    def test_collect_missing_lockfile(self, uv_project_missing: Path):
        """A project with no uv.lock yields zero dependencies."""
        plugin = UVPlugin()
        plugin.collect(uv_project_missing)

        assert plugin.dependencies == []

    # ------------------------------------------------------------------
    # Accepts string path
    # ------------------------------------------------------------------
    def test_collect_accepts_string_path(self, uv_project_full: Path):
        """``collect()`` works when called with a ``str`` path."""
        plugin = UVPlugin()
        plugin.collect(str(uv_project_full))

        assert len(plugin.dependencies) > 0
