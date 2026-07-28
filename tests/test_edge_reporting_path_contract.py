"""
Project GOAT v0.6 — Path Validation Contract Adversarial Unit Tests

Exhaustively verifies strict regex ^[A-Za-z0-9_-]+$ path component validation and traversal rejection.
"""

from __future__ import annotations

import pytest

from goat.research.edge.reporting.exceptions import SecurityViolationError
from goat.research.edge.reporting.package_integrity import validate_path_component


@pytest.mark.parametrize(
    "invalid_path",
    [
        ".",
        "..",
        "...",
        ".hidden",
        "foo.bar",
        "foo..bar",
        "../foo",
        "..\\foo",
        "foo/bar",
        "foo\\bar",
        "C:",
        "C:\\temp",
        "/tmp/foo",
        "~",
        "%2e%2e",
        "invalid path\n",
        "invalid path ",
        "invalid path\x00",
        "",
    ],
)
def test_path_component_sanitizer_rejects_disallowed_paths(invalid_path: str):
    with pytest.raises(SecurityViolationError):
        validate_path_component("test_component", invalid_path)


@pytest.mark.parametrize(
    "valid_path",
    [
        "VAL_061DC6057ECC260E",
        "RPT_7A8B9C0D1E2F3456",
        "EVD_1234567890ABCDEF",
        "EVP_1234567890ABCDEF",
        "AUD_1234567890ABCDEF",
        "valid_identifier-123",
    ],
)
def test_path_component_sanitizer_accepts_valid_canonical_ids(valid_path: str):
    assert validate_path_component("test_component", valid_path) == valid_path
