"""
Project GOAT v0.6 — Engine Holdout Hard Boundary Unit Tests

Verifies strict architectural separation between pre-confirmatory (A-F) execution and Stage G holdout access.
"""

from __future__ import annotations

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.engine import MultiStageValidationEngine
from goat.research.edge.validation.exceptions import ValidationStateError
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import ReasonCode, StageDecision, StageResult, ValidationStage


def test_stage_g_cannot_execute_if_stage_f_did_not_pass():
    engine = MultiStageValidationEngine()
    edge = CandidateEdge(
        proposition_name="Holdout Boundary Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )
    gate = HoldoutAccessGate()

    stage_f_fail = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_F_REPLICATION,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.REPLICATION_FAILED,
        policy_hash=policy.policy_hash,
    )

    with pytest.raises(ValidationStateError) as excinfo:
        engine.execute_confirmatory(
            candidate_edge=edge,
            hypothesis_version="1234567890ab",
            policy=policy,
            validation_run=run,
            dataset_partitions={},
            stage_f_result=stage_f_fail,
            holdout_gate=gate,
        )
    assert "Cannot execute Stage G" in str(excinfo.value)
    assert gate.bytes_read == 0
