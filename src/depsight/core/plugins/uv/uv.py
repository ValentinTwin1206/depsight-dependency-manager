import tomllib

from pathlib import Path

# own imports
from depsight.core.plugins.base import BasePlugin
from depsight.core.plugins.dependency import Dependency, packageType


class UVPlugin(BasePlugin):
    """Plugin for **uv**."""

    def __init__(self) -> None:
        self.dependencies: list[Dependency] = []

    @property
    def name(self) -> str:
        return "uv"

    @property
    def dependency_files(self) -> tuple[str, ...]:
        return ("uv.lock",)

    @staticmethod
    def _load_dependency_files(project_dir: Path, filename: str) -> tuple[dict, Path] | None:
        """Walk *project_dir* for *filename*, parse the first match as TOML.

        Checks the project root first, then walks subdirectories.
        Returns the parsed data and the resolved file path, or
        `None` if no matching file is found.
        """
        root_candidate = project_dir / filename
        if root_candidate.is_file():
            with root_candidate.open("rb") as f:
                return tomllib.load(f), root_candidate.resolve()

        for path in project_dir.rglob(filename):
            if path.is_file():
                with path.open("rb") as f:
                    return tomllib.load(f), path.resolve()

        return None

    #
    # METHODS
    # # # # # # #
    def collect(self, project_dir: str | Path) -> None:
        """Parses `uv.lock` and populate `self.dependencies`.

        Reads the lockfile via :mod:`tomllib`, extracts every locked
        package with its version and registry source, then classifies
        each dependency as *prod* or *dev* based on the
        editable project block.
        """
        project_dir = Path(project_dir)
        result = self._load_dependency_files(
            project_dir, self.dependency_files[0],
        )
        if result is None:
            self.dependencies = []
            return

        data, lockfile_path = result
        lockfile_str = str(lockfile_path)

        packages: list[dict] = data.get("package", [])

        # Build name → version and name → registry lookups
        locked: dict[str, str] = {}
        sources: dict[str, str] = {}
        project_block: dict | None = None

        for pkg in packages:
            pkg_name = pkg.get("name", "")
            pkg_version = pkg.get("version", "")

            if pkg_name and pkg_version:
                locked[pkg_name] = pkg_version

            registry = pkg.get("source", {}).get("registry")
            if pkg_name and registry:
                sources[pkg_name] = registry  # PyPI URL or private index

            if "editable" in pkg.get("source", {}):
                project_block = pkg

        # No editable block → every locked package counts as runtime
        if project_block is None:
            self.dependencies = [
                Dependency(
                    name=n,
                    version=v,
                    tool_name=self.name,
                    registry=sources.get(n),
                    file=lockfile_str,
                )
                for n, v in sorted(locked.items())
            ]
            return

        # Parse runtime deps
        runtime_names = [
            dep["name"] for dep in project_block.get("dependencies", [])
        ]

        # Classify non-runtime groups.
        # Both optional-dependencies and dev-dependencies are non-prod → "dev".

        non_runtime_names: set[str] = set()

        # [project.optional-dependencies]  →  uv.lock optional-dependencies
        for _group, deps in project_block.get("optional-dependencies", {}).items():
            non_runtime_names.update(dep["name"] for dep in deps)

        # PEP 735 [dependency-groups]  →  uv.lock dev-dependencies
        for _group, deps in project_block.get("dev-dependencies", {}).items():
            non_runtime_names.update(dep["name"] for dep in deps)

        # Parse version constraints from metadata.requires-dist
        metadata = project_block.get("metadata", {})
        constraints: dict[str, str] = {
            entry["name"]: entry["specifier"]
            for entry in metadata.get("requires-dist", [])
            if "specifier" in entry
        }

        # Parse version constraints from metadata.requires-dev
        for _group, entries in metadata.get("requires-dev", {}).items():
            for entry in entries:
                if "specifier" in entry:
                    constraints[entry["name"]] = entry["specifier"]

        # Build category lookup: prod for runtime, dev for everything else
        category_map: dict[str, packageType] = {}
        for dep_name in runtime_names:
            category_map[dep_name] = "prod"

        for dep_name in non_runtime_names:
            category_map.setdefault(dep_name, "dev")

        # Build structured dependency list
        self.dependencies = [
            Dependency(
                name=dep_name,
                version=locked.get(dep_name),
                constraint=constraints.get(dep_name),
                tool_name=self.name,
                registry=sources.get(dep_name),
                file=lockfile_str,
                category=category_map.get(dep_name, "prod"),
            )
            for dep_name in sorted(category_map)
        ]
