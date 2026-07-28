"""
Project GOAT v0.6 — Validation Models Unit Tests
"""

import pytest

from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationLifecycleState,
    ValidationStage,
)


def test_stage_result_creation_and_immutability():
    res = StageResult(
        validation_run_id="VAL_1234567890abcdef",
        edge_id="EDGE_1234567890abcdef",
        stage=ValidationStage.STAGE_A_DISCOVERY,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        evidence_ids=("EVD_111", "EVD_222"),
        policy_hash="PLC_1234567890abcdef",
        explanation="Discovery significance test passed",
    )

    assert res.validation_run_id == "VAL_1234567890abcdef"
    assert res.decision == StageDecision.PASS
    assert res.evidence_ids == ("EVD_111", "EVD_222")

    # Immutability check
    with pytest.raises(Exception):
        res.decision = StageDecision.FAIL


def test_stage_result_non_empty_validation():
    with pytest.raises(ValueError):
        StageResult(
            validation_run_id="",
            edge_id="EDGE_1234567890abcdef",
            stage=ValidationStage.STAGE_A_DISCOVERY,
            decision=StageDecision.PASS,
            reason_code=ReasonCode.PASSED,
            policy_hash="PLC_1234567890abcdef",
        )
