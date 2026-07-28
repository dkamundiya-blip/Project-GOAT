"""
Project GOAT v0.6 — Stage E Primitive Inversion Unit Tests
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


def test_stage_e_primitive_inversion_mapping():
    validator = StageEValidator()

    assert validator.INVERSION_MAP["greater_than"] == "less_than"
    assert validator.INVERSION_MAP["less_than"] == "greater_than"
    assert validator.INVERSION_MAP["crosses_above"] == "crosses_below"
    assert validator.INVERSION_MAP["crosses_below"] == "crosses_above"


def test_stage_e_unsupported_primitive_returns_insufficient_evidence():
    validator = StageEValidator()

    edge = CandidateEdge(
        proposition_name="Custom Primitive Edge",
        causal_primitive="custom_unknown_primitive",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1")
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

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_d_result=stage_d_res,
        baseline_effect=0.50,
    )

    assert res.decision == StageDecision.INSUFFICIENT_EVIDENCE
    assert res.reason_code == ReasonCode.SAMPLE_TOO_SMALL
