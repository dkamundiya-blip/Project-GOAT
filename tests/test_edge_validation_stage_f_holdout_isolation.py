"""
Project GOAT v0.6 — Stage F Holdout Isolation Unit Tests
"""

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.holdout import HoldoutAccessGate
from goat.research.edge.validation.models import (
    HoldoutState,
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_f import StageFValidator


def test_stage_f_leaves_holdout_gate_sealed():
    gate = HoldoutAccessGate()
    assert gate.current_state == HoldoutState.SEALED

    validator = StageFValidator()
    edge = CandidateEdge(
        proposition_name="Holdout Isolated Edge",
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

    stage_e_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_E_FALSIFICATION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    contexts = [
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_e_result=stage_e_res,
        baseline_effect=0.50,
        context_evaluations=contexts,
    )

    assert res.decision == StageDecision.PASS
    # Confirm holdout gate state remains strictly SEALED
    assert gate.current_state == HoldoutState.SEALED
