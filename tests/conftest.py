from __future__ import annotations

import shutil
from pathlib import Path

import pytest

#
# GLOBALS
# # # # # # # #
FIXTURES_DIR = Path(__file__).parent / "fixtures"


#
# UV-PLUGIN
# # # # # # # #
@pytest.fixture()
def uv_project_full(tmp_path: Path) -> Path:
    """Fake project with a full `uv.lock` (editable block + dev deps)."""
    shutil.copy(FIXTURES_DIR / "uv_lock_full.toml", tmp_path / "uv.lock")
    return tmp_path


@pytest.fixture()
def uv_project_no_editable(tmp_path: Path) -> Path:
    """Fake project whose `uv.lock` has no editable block."""
    shutil.copy(FIXTURES_DIR / "uv_lock_no_editable.toml", tmp_path / "uv.lock")
    return tmp_path


@pytest.fixture()
def uv_project_empty(tmp_path: Path) -> Path:
    """Fake project whose `uv.lock` has no packages at all."""
    shutil.copy(FIXTURES_DIR / "uv_lock_empty.toml", tmp_path / "uv.lock")
    return tmp_path


@pytest.fixture()
def uv_project_missing(tmp_path: Path) -> Path:
    """Fake project with **no** `uv.lock` file."""
    return tmp_path


#
# VSC-PLUGIN
# # # # # # # #
@pytest.fixture()
def vsc_project_valid(tmp_path: Path) -> Path:
    """Fake project with a valid `devcontainer.json` containing extensions."""
    dc_dir = tmp_path / ".devcontainer"
    dc_dir.mkdir()
    shutil.copy(FIXTURES_DIR / "devcontainer_valid.json", dc_dir / "devcontainer.json")
    return tmp_path


@pytest.fixture()
def vsc_project_no_extensions(tmp_path: Path) -> Path:
    """Fake project whose `devcontainer.json` has no extensions key."""
    dc_dir = tmp_path / ".devcontainer"
    dc_dir.mkdir()
    shutil.copy(FIXTURES_DIR / "devcontainer_no_extensions.json", dc_dir / "devcontainer.json")
    return tmp_path


@pytest.fixture()
def vsc_project_invalid_json(tmp_path: Path) -> Path:
    """Fake project with a malformed `devcontainer.json`."""
    dc_dir = tmp_path / ".devcontainer"
    dc_dir.mkdir()
    shutil.copy(FIXTURES_DIR / "devcontainer_invalid.json", dc_dir / "devcontainer.json")
    return tmp_path


@pytest.fixture()
def vsc_project_missing(tmp_path: Path) -> Path:
    """Fake project with **no** `devcontainer.json` at all."""
    return tmp_path
