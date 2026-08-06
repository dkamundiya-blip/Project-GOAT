"""
Project GOAT v0.9 — Dedicated Tests for Intelligence Public API Exports
"""

import types
import pytest

import goat.intelligence as intelligence


def test_public_api_all_export_integrity() -> None:
    assert hasattr(intelligence, "__all__")
    expected_exports = set(intelligence.__all__)

    for name in expected_exports:
        assert hasattr(intelligence, name), f"Missing exported symbol: {name}"
        item = getattr(intelligence, name)
        assert item is not None


def test_public_api_no_namespace_leakage() -> None:
    exported = set(intelligence.__all__)
    for name in dir(intelligence):
        if name.startswith("_"):
            continue
        val = getattr(intelligence, name)
        if isinstance(val, types.ModuleType):
            continue
        assert name in exported, f"Leaked symbol not in __all__: {name}"


@pytest.mark.parametrize("export_name", intelligence.__all__)
def test_individual_public_api_exports(export_name: str) -> None:
    obj = getattr(intelligence, export_name)
    assert obj is not None
