"""
Project GOAT v0.6 — StageCValidator Unit Tests
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
from goat.research.edge.validation.stages.stage_c import StageCValidator
from goat.research.edge.validation.state import ValidationStateMachine


def test_stage_c_pass_flow():
    validator = StageCValidator()
    assert validator.stage == ValidationStage.STAGE_C_TEMPORAL
    assert validator.prerequisite_stage == ValidationStage.STAGE_B_RETENTION

    edge = CandidateEdge(
        proposition_name="Momentum Edge C",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(
        policy_id="P1",
        stage_c_min_folds=5,
        stage_c_min_positive_ratio=0.70,
        stage_c_max_fold_cv=1.00,
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_b_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_B_RETENTION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # 5 stable folds with consistent positive effect
    rng = np.random.default_rng(42)
    folds = []
    for i in range(5):
        cond = rng.normal(loc=0.4, scale=1.0, size=100)
        base = rng.normal(loc=0.0, scale=1.0, size=100)
        folds.append((cond, base))

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_b_result=stage_b_res,
        discovery_effect=0.50,
        fold_observations=folds,
    )

    assert res.decision == StageDecision.PASS
    assert res.reason_code == ReasonCode.PASSED
    assert len(res.evidence_ids) == 5

    # State machine progression check
    sm = ValidationStateMachine(ValidationLifecycleState.RETENTION_VALIDATION)
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.TEMPORAL_STABILITY


def test_stage_c_prerequisite_failure_blocks_execution():
    validator = StageCValidator()
    edge = CandidateEdge(
        proposition_name="Edge Prereq Fail C",
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

    stage_b_failed_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_B_RETENTION,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.RETENTION_FAILED,
        policy_hash=policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_b_result=stage_b_failed_res,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PREREQUISITE_FAILED


def test_stage_c_insufficient_folds_returns_insufficient_evidence():
    validator = StageCValidator()
    edge = CandidateEdge(
        proposition_name="Edge Low Folds",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1", stage_c_min_folds=5)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_b_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_B_RETENTION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Only 3 folds provided (below min required 5)
    rng = np.random.default_rng(42)
    folds = [(rng.normal(0.4, 1.0, 100), rng.normal(0.0, 1.0, 100)) for _ in range(3)]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_b_result=stage_b_res,
        fold_observations=folds,
    )

    assert res.decision == StageDecision.INSUFFICIENT_EVIDENCE
    assert res.reason_code == ReasonCode.SAMPLE_TOO_SMALL


def test_stage_c_high_fold_cv_failure():
    validator = StageCValidator()
    edge = CandidateEdge(
        proposition_name="Edge High CV",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_c_min_folds=5, stage_c_min_positive_ratio=0.70, stage_c_max_fold_cv=1.00
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_b_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_B_RETENTION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Folds with extreme variance causing CV > 1.00
    rng = np.random.default_rng(42)
    folds = [
        (rng.normal(2.0, 1.0, 100), rng.normal(0.0, 1.0, 100)),
        (rng.normal(0.05, 1.0, 100), rng.normal(0.0, 1.0, 100)),
        (rng.normal(0.01, 1.0, 100), rng.normal(0.0, 1.0, 100)),
        (rng.normal(0.02, 1.0, 100), rng.normal(0.0, 1.0, 100)),
        (rng.normal(0.01, 1.0, 100), rng.normal(0.0, 1.0, 100)),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_b_result=stage_b_res,
        discovery_effect=0.50,
        fold_observations=folds,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.TEMPORAL_INSTABILITY
