"""
Project GOAT v0.6 — Release Version Metadata Regression Test

Verifies that goat.__version__ and pyproject.toml version metadata are harmonized to "0.6.0".
"""

from __future__ import annotations

from pathlib import Path
import tomllib
import goat


def test_goat_runtime_version():
    assert goat.__version__ == "0.6.0"


def test_pyproject_package_version():
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    assert pyproject_path.exists()

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    project_version = pyproject_data.get("project", {}).get("version")
    assert project_version == "0.6.0"


def test_version_metadata_harmony():
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    project_version = pyproject_data.get("project", {}).get("version")
    assert goat.__version__ == project_version == "0.6.0"
