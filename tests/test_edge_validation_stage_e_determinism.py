"""
Project GOAT v0.6 — Stage E Determinism Unit Tests
"""

import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_e import StageEValidator


def test_stage_e_cross_process_determinism():
    validator = StageEValidator()

    edge = CandidateEdge(
        proposition_name="Determinism Edge E",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1", stage_e_fail_on_contradictory_inversion=True)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_d_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_D_ROBUSTNESS,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    res1 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_d_result=stage_d_res,
        baseline_effect=0.50,
        contradictory_effect=-0.30,
    )

    res2 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_d_result=stage_d_res,
        baseline_effect=0.50,
        contradictory_effect=-0.30,
    )

    assert res1.decision == res2.decision
    assert res1.reason_code == res2.reason_code
    assert res1.evidence_ids == res2.evidence_ids
