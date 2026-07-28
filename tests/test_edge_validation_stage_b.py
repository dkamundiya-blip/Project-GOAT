"""
Project GOAT v0.6 — StageBValidator Unit Tests
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
from goat.research.edge.validation.stages.stage_b import StageBValidator
from goat.research.edge.validation.state import ValidationStateMachine


def test_stage_b_pass_flow():
    validator = StageBValidator()
    assert validator.stage == ValidationStage.STAGE_B_RETENTION
    assert validator.prerequisite_stage == ValidationStage.STAGE_A_DISCOVERY

    edge = CandidateEdge(
        proposition_name="Momentum Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1", stage_b_min_retention_ratio=0.50)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_a_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_A_DISCOVERY,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    rng = np.random.default_rng(42)
    val_cond = rng.normal(loc=0.4, scale=1.0, size=150)
    val_base = rng.normal(loc=0.0, scale=1.0, size=150)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_a_result=stage_a_res,
        discovery_effect=0.50,
        val_cond_arr=val_cond,
        val_base_arr=val_base,
    )

    assert res.decision == StageDecision.PASS
    assert res.reason_code == ReasonCode.PASSED

    # State machine progression check
    sm = ValidationStateMachine(ValidationLifecycleState.DISCOVERY_VALIDATION)
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.RETENTION_VALIDATION


def test_stage_b_prerequisite_failure_blocks_execution():
    validator = StageBValidator()
    edge = CandidateEdge(
        proposition_name="Edge Prereq Fail",
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

    stage_a_failed_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_A_DISCOVERY,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.EFFECT_TOO_SMALL,
        policy_hash=policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_a_result=stage_a_failed_res,
        discovery_effect=0.50,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PREREQUISITE_FAILED


def test_stage_b_direction_reversed_failure():
    validator = StageBValidator()
    edge = CandidateEdge(
        proposition_name="Edge Reversed",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1", stage_b_min_retention_ratio=0.50)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_a_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_A_DISCOVERY,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Positive discovery (+0.50), but negative validation (-0.40)
    rng = np.random.default_rng(42)
    val_cond = rng.normal(loc=-0.4, scale=1.0, size=150)
    val_base = rng.normal(loc=0.0, scale=1.0, size=150)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_a_result=stage_a_res,
        discovery_effect=0.50,
        val_cond_arr=val_cond,
        val_base_arr=val_base,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.DIRECTION_REVERSED


def test_stage_b_retention_ratio_below_threshold_failure():
    validator = StageBValidator()
    edge = CandidateEdge(
        proposition_name="Edge Low Retention",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1", stage_b_min_retention_ratio=0.50)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_a_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_A_DISCOVERY,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Discovery effect = 1.0, but validation effect = 0.20 (Retention ratio = 0.20 < 0.50)
    rng = np.random.default_rng(42)
    val_cond = rng.normal(loc=0.2, scale=1.0, size=150)
    val_base = rng.normal(loc=0.0, scale=1.0, size=150)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_a_result=stage_a_res,
        discovery_effect=1.00,
        val_cond_arr=val_cond,
        val_base_arr=val_base,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.RETENTION_FAILED
