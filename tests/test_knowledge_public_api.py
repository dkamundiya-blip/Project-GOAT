"""
Project GOAT v0.9 — Dedicated Tests for Knowledge Public API Exports
"""

import types
import pytest

import goat.knowledge as knowledge


def test_public_api_all_export_integrity() -> None:
    assert hasattr(knowledge, "__all__")
    expected_exports = set(knowledge.__all__)

    for name in expected_exports:
        assert hasattr(knowledge, name), f"Missing exported symbol: {name}"
        item = getattr(knowledge, name)
        assert item is not None


def test_public_api_no_namespace_leakage() -> None:
    exported = set(knowledge.__all__)
    for name in dir(knowledge):
        if name.startswith("_"):
            continue
        val = getattr(knowledge, name)
        if isinstance(val, types.ModuleType):
            continue
        assert name in exported, f"Leaked symbol not in __all__: {name}"


@pytest.mark.parametrize("export_name", knowledge.__all__)
def test_individual_public_api_exports(export_name: str) -> None:
    obj = getattr(knowledge, export_name)
    assert obj is not None
