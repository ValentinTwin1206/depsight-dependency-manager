from __future__ import annotations

import json
from pathlib import Path

# own imports
from depsight.core.plugins.base import BasePlugin
from depsight.core.plugins.dependency import Dependency


class VSCEPlugin(BasePlugin):
    """Plugin for **VS Code** extensions."""

    def __init__(self) -> None:
        self.dependencies: list[Dependency] = []
        self._marketplace_url = "https://marketplace.visualstudio.com"

    @property
    def name(self) -> str:
        return "vsce"

    @property
    def dependency_files(self) -> tuple[str, ...]:
        return ("devcontainer.json",)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _load_dependency_files(project_dir: Path, filename: str) -> list[Path]:
        """Walk *project_dir* for *filename* and return all matches.

        Checks the project root first, then walks subdirectories.
        """
        found: list[Path] = []
        seen: set[Path] = set()

        root_candidate = project_dir / filename
        if root_candidate.is_file():
            resolved = root_candidate.resolve()
            found.append(resolved)
            seen.add(resolved)

        for path in project_dir.rglob(filename):
            resolved = path.resolve()
            if resolved not in seen and resolved.is_file():
                found.append(resolved)
                seen.add(resolved)

        return found

    def _parse_devcontainer_file(self, path: Path) -> list[Dependency]:
        """Parse a single `devcontainer.json` and return extension entries.

        Each extension listed under
        `customizations.vscode.extensions` becomes a dependency entry
        with `registry` pointing to the VS Code Marketplace.
        """
        try:
            raw = path.read_text(encoding="utf-8")
            # Strip single-line comments (// …) that JSONC allows.
            lines = [
                line for line in raw.splitlines()
                if not line.lstrip().startswith("//")
            ]
            data = json.loads("\n".join(lines))
        except (json.JSONDecodeError, OSError):
            return []

        if not isinstance(data, dict):
            return []

        extensions = (
            data
            .get("customizations", {})
            .get("vscode", {})
            .get("extensions", [])
        )
        if not isinstance(extensions, list):
            return []

        file_str = str(path)

        return [
            Dependency(
                name=ext_id,
                tool_name=self.name,
                registry=self._marketplace_url,
                file=file_str,
                category="dev",
            )
            for ext_id in extensions
            if isinstance(ext_id, str)
        ]

    #
    # METHODS
    # # # # # # #
    def collect(self, project_dir: str | Path) -> None:
        """Discover `devcontainer.json` files and collect VS Code extensions."""
        project_dir = Path(project_dir)
        paths = self._load_dependency_files(project_dir, self.dependency_files[0])

        results: list[Dependency] = []
        for dc_path in paths:
            results.extend(self._parse_devcontainer_file(dc_path))

        self.dependencies = results
