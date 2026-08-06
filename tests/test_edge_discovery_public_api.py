"""
Project GOAT v0.9 — Dedicated Tests for Edge Discovery Public API Exports
"""

import types
import pytest

import goat.edge_discovery as edge_discovery


def test_public_api_all_export_integrity() -> None:
    assert hasattr(edge_discovery, "__all__")
    expected_exports = set(edge_discovery.__all__)

    for name in expected_exports:
        assert hasattr(edge_discovery, name), f"Missing exported symbol: {name}"
        item = getattr(edge_discovery, name)
        assert item is not None


def test_public_api_no_namespace_leakage() -> None:
    exported = set(edge_discovery.__all__)
    for name in dir(edge_discovery):
        if name.startswith("_"):
            continue
        val = getattr(edge_discovery, name)
        if isinstance(val, types.ModuleType):
            continue
        assert name in exported, f"Leaked symbol not in __all__: {name}"


@pytest.mark.parametrize("export_name", edge_discovery.__all__)
def test_individual_public_api_exports(export_name: str) -> None:
    obj = getattr(edge_discovery, export_name)
    assert obj is not None
