"""
Project GOAT v0.9 — Dedicated Tests for Microstructure Public API & Exports
"""

import types
import pytest

import goat.microstructure as microstructure


def test_public_api_all_export_integrity() -> None:
    assert hasattr(microstructure, "__all__")
    expected_exports = set(microstructure.__all__)

    # Verify no missing exports
    for name in expected_exports:
        assert hasattr(microstructure, name), f"Missing exported symbol: {name}"
        item = getattr(microstructure, name)
        assert item is not None


def test_public_api_no_namespace_leakage() -> None:
    exported = set(microstructure.__all__)
    for name in dir(microstructure):
        if name.startswith("_"):
            continue
        # Skip module objects if re-imported
        val = getattr(microstructure, name)
        if isinstance(val, types.ModuleType):
            continue
        assert name in exported, f"Leaked symbol not in __all__: {name}"


@pytest.mark.parametrize("export_name", microstructure.__all__)
def test_individual_public_api_exports(export_name: str) -> None:
    obj = getattr(microstructure, export_name)
    assert obj is not None
