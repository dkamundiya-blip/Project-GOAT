"""
Project GOAT v0.6 — Report Identity Unit Tests

Verifies deterministic RPT_<HEX16> calculation and wall-clock timestamp exclusion.
"""

from __future__ import annotations

import pytest

from goat.research.edge.reporting.identity import compute_report_id


def test_rpt_identity_determinism():
    rpt1 = compute_report_id(
        validation_run_id="VAL_1111",
        edge_id="EDGE_2222",
        policy_hash="PLC_3333",
        dataset_fingerprint="DS_4444",
        hypothesis_version="1234567890ab",
        evidence_payload_hashes=["EVP_AAAA", "EVP_BBBB"],
    )

    rpt2 = compute_report_id(
        validation_run_id="VAL_1111",
        edge_id="EDGE_2222",
        policy_hash="PLC_3333",
        dataset_fingerprint="DS_4444",
        hypothesis_version="1234567890ab",
        evidence_payload_hashes=["EVP_AAAA", "EVP_BBBB"],
    )

    assert rpt1 == rpt2
    assert rpt1.startswith("RPT_")
    assert len(rpt1) == 20  # "RPT_" + 16 hex chars


def test_rpt_identity_order_invariance():
    # Reverse input order of evidence payload hashes
    rpt1 = compute_report_id(
        validation_run_id="VAL_1111",
        edge_id="EDGE_2222",
        policy_hash="PLC_3333",
        dataset_fingerprint="DS_4444",
        hypothesis_version="1234567890ab",
        evidence_payload_hashes=["EVP_AAAA", "EVP_BBBB"],
    )

    rpt2 = compute_report_id(
        validation_run_id="VAL_1111",
        edge_id="EDGE_2222",
        policy_hash="PLC_3333",
        dataset_fingerprint="DS_4444",
        hypothesis_version="1234567890ab",
        evidence_payload_hashes=["EVP_BBBB", "EVP_AAAA"],
    )

    assert rpt1 == rpt2
