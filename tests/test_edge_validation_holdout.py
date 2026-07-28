"""
Project GOAT v0.6 — HoldoutAccessGate Unit Tests
"""

import pytest

from goat.research.edge.validation.exceptions import HoldoutAccessError
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import HoldoutState


def test_holdout_access_gate_sealed_rejection():
    gate = HoldoutAccessGate()
    assert gate.current_state == HoldoutState.SEALED

    # Access without authorization must be rejected
    with pytest.raises(HoldoutAccessError) as exc_info:
        gate.access_holdout(lambda: "synthetic_data")
    assert "SEALED" in str(exc_info.value)


def test_holdout_access_gate_full_lifecycle():
    gate = HoldoutAccessGate()

    # Pre-register confirmatory audit identity
    audit_id = gate.authorize_access(
        edge_id="EDGE_1234567890abcdef",
        hypothesis_version="1234567890ab",
        policy_hash="PLC_1234567890abcdef",
        dataset_fingerprint="ds_fp_123",
        holdout_partition_identity="holdout_v1",
        validation_run_id="VAL_1234567890abcdef",
    )

    assert audit_id.startswith("AUD_")
    assert gate.current_state == HoldoutState.AUTHORIZED

    # Re-authorization attempt must be rejected
    with pytest.raises(HoldoutAccessError):
        gate.authorize_access(
            edge_id="EDGE_1234567890abcdef",
            hypothesis_version="1234567890ab",
            policy_hash="PLC_1234567890abcdef",
            dataset_fingerprint="ds_fp_123",
            holdout_partition_identity="holdout_v1",
            validation_run_id="VAL_1234567890abcdef",
        )

    # Access synthetic data (Zero real files opened)
    mock_data = gate.access_holdout(lambda: {"rows": 100})
    assert mock_data == {"rows": 100}
    assert gate.current_state == HoldoutState.CONSUMED

    # Re-access after CONSUMED must be strictly rejected
    with pytest.raises(HoldoutAccessError) as exc_info:
        gate.access_holdout(lambda: "synthetic_data")
    assert "CONSUMED" in str(exc_info.value)
