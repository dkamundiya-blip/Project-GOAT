"""
Project GOAT v0.6 — StageDValidator Unit Tests
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
from goat.research.edge.validation.stages.stage_d import StageDValidator
from goat.research.edge.validation.state import ValidationStateMachine


def test_stage_d_pass_flow():
    validator = StageDValidator()
    assert validator.stage == ValidationStage.STAGE_D_ROBUSTNESS
    assert validator.prerequisite_stage == ValidationStage.STAGE_C_TEMPORAL

    edge = CandidateEdge(
        proposition_name="Momentum Edge D",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_d_min_stable_ratio=0.65, stage_d_max_allowed_drop=0.60
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_c_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_C_TEMPORAL,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # 4 perturbations evaluated around baseline effect 0.50 (all stable, small drops)
    evals = [
        ({"period": 16}, 0.45),
        ({"period": 20}, 0.50),
        ({"period": 24}, 0.42),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_c_result=stage_c_res,
        baseline_effect=0.50,
        perturbation_evaluations=evals,
    )

    assert res.decision == StageDecision.PASS
    assert res.reason_code == ReasonCode.PASSED
    assert len(res.evidence_ids) == 3

    # State machine progression check
    sm = ValidationStateMachine(ValidationLifecycleState.TEMPORAL_STABILITY)
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.PARAMETER_ROBUSTNESS


def test_stage_d_prerequisite_failure_blocks_execution():
    validator = StageDValidator()
    edge = CandidateEdge(
        proposition_name="Edge Prereq Fail D",
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

    stage_c_failed_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_C_TEMPORAL,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.TEMPORAL_INSTABILITY,
        policy_hash=policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_c_result=stage_c_failed_res,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PREREQUISITE_FAILED


def test_stage_d_low_stable_ratio_failure():
    validator = StageDValidator()
    edge = CandidateEdge(
        proposition_name="Edge Fragile",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1", stage_d_min_stable_ratio=0.65)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_c_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_C_TEMPORAL,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # 3 out of 4 perturbations flip direction -> stable ratio = 0.25 < 0.65
    evals = [
        ({"p": 1}, 0.50),
        ({"p": 2}, -0.30),
        ({"p": 3}, -0.20),
        ({"p": 4}, -0.40),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_c_result=stage_c_res,
        baseline_effect=0.50,
        perturbation_evaluations=evals,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PARAMETER_INSTABILITY


def test_stage_d_excessive_effect_drop_failure():
    validator = StageDValidator()
    edge = CandidateEdge(
        proposition_name="Edge High Drop",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_d_min_stable_ratio=0.65, stage_d_max_allowed_drop=0.60
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_c_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_C_TEMPORAL,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Baseline effect = 1.0. Perturbation effect = 0.20 -> Drop = (1.0 - 0.2) / 1.0 = 0.80 > 0.60
    evals = [
        ({"p": 1}, 1.00),
        ({"p": 2}, 0.20),
        ({"p": 3}, 0.90),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_c_result=stage_c_res,
        baseline_effect=1.00,
        perturbation_evaluations=evals,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PARAMETER_INSTABILITY
