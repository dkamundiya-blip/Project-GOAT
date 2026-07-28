"""
Project GOAT v0.6 — Package Security & Path Sanitization Unit Tests

Verifies strict path component sanitization and containment protection against path traversal attacks.
"""

from __future__ import annotations

import tempfile
import pytest

from goat.research.edge.reporting import (
    SecurityViolationError,
    validate_path_component,
)


def test_path_component_sanitizer_rejects_malicious_inputs():
    # Path traversal attempts
    with pytest.raises(SecurityViolationError):
        validate_path_component("run_id", "../../../etc/passwd")

    with pytest.raises(SecurityViolationError):
        validate_path_component("report_id", "..\\win.ini")

    # Slashes and backslashes
    with pytest.raises(SecurityViolationError):
        validate_path_component("run_id", "val/run")

    with pytest.raises(SecurityViolationError):
        validate_path_component("run_id", "val\\run")

    # Whitespace and special symbols
    with pytest.raises(SecurityViolationError):
        validate_path_component("run_id", "val run")

    with pytest.raises(SecurityViolationError):
        validate_path_component("run_id", "val$run")


def test_path_component_sanitizer_accepts_valid_identifiers():
    assert validate_path_component("run_id", "VAL_061DC6057ECC260E") == "VAL_061DC6057ECC260E"
    assert validate_path_component("report_id", "RPT_7A8B9C0D1E2F3456") == "RPT_7A8B9C0D1E2F3456"
    assert validate_path_component("key", "valid-key_123") == "valid-key_123"
