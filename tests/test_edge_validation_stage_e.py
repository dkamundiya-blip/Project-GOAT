"""
Project GOAT v0.6 — StageEValidator Unit Tests
"""

import numpy as np
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationLifecycleState,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_e import StageEValidator
from goat.research.edge.validation.state import ValidationStateMachine


def test_stage_e_pass_flow_positive_baseline():
    validator = StageEValidator()
    assert validator.stage == ValidationStage.STAGE_E_FALSIFICATION
    assert validator.prerequisite_stage == ValidationStage.STAGE_D_ROBUSTNESS

    edge = CandidateEdge(
        proposition_name="Momentum Edge E",
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

    # Positive baseline (+0.50), contradictory effect is negative (-0.30) -> PASS
    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_d_result=stage_d_res,
        baseline_effect=0.50,
        contradictory_effect=-0.30,
    )

    assert res.decision == StageDecision.PASS
    assert res.reason_code == ReasonCode.PASSED

    # State machine progression check
    sm = ValidationStateMachine(ValidationLifecycleState.PARAMETER_ROBUSTNESS)
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.FALSIFICATION


def test_stage_e_fail_positive_baseline_positive_contradictory():
    """Positive baseline (+0.50) + materially positive contradictory effect (+0.40) -> FAIL."""
    validator = StageEValidator()
    edge = CandidateEdge(
        proposition_name="Edge Contradictory Same Dir",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_e_fail_on_contradictory_inversion=True, stage_a_effect_min=0.15
    )
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
        contradictory_effect=0.40,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.FALSIFICATION_FAILED


def test_stage_e_negative_baseline_negative_contradictory_fails():
    """Negative baseline (-0.50) + materially negative contradictory effect (-0.40) -> FAIL."""
    validator = StageEValidator()
    edge = CandidateEdge(
        proposition_name="Edge Neg Baseline",
        causal_primitive="less_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_e_fail_on_contradictory_inversion=True, stage_a_effect_min=0.15
    )
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
        baseline_effect=-0.50,
        contradictory_effect=-0.40,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.FALSIFICATION_FAILED


def test_stage_e_prerequisite_failure_blocks_execution():
    validator = StageEValidator()
    edge = CandidateEdge(
        proposition_name="Edge Prereq Fail E",
        causal_primitive="greater_than",
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

    stage_d_failed_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_D_ROBUSTNESS,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.PARAMETER_INSTABILITY,
        policy_hash=policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_d_result=stage_d_failed_res,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PREREQUISITE_FAILED
