"""
Project GOAT v0.6 — StageFValidator Unit Tests
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
from goat.research.edge.validation.stages.stage_f import StageFValidator
from goat.research.edge.validation.state import ValidationStateMachine


def test_stage_f_pass_flow():
    validator = StageFValidator()
    assert validator.stage == ValidationStage.STAGE_F_REPLICATION
    assert validator.prerequisite_stage == ValidationStage.STAGE_E_FALSIFICATION

    edge = CandidateEdge(
        proposition_name="Momentum Edge F",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_f_min_replication_pct=0.60, stage_f_meta_alpha=0.01
    )
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

    # 5 contexts: 4 successful replications (80% > 60%), combined p-meta < 0.01
    contexts = [
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
        ("GOOGL", 0.40, 0.005, 200),
        ("AMZN", 0.35, 0.010, 200),
        ("TSLA", 0.05, 0.400, 200),
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
    assert res.reason_code == ReasonCode.PASSED
    assert len(res.evidence_ids) == 5

    # State machine progression check
    sm = ValidationStateMachine(ValidationLifecycleState.FALSIFICATION)
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.CONFIRMATORY_READY


def test_stage_f_prerequisite_failure_blocks_execution():
    validator = StageFValidator()
    edge = CandidateEdge(
        proposition_name="Edge Prereq Fail F",
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

    stage_e_failed_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_E_FALSIFICATION,
        decision=StageDecision.FAIL,
        reason_code=ReasonCode.FALSIFICATION_FAILED,
        policy_hash=policy.policy_hash,
    )

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_e_result=stage_e_failed_res,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.PREREQUISITE_FAILED


def test_stage_f_low_replication_ratio_failure():
    validator = StageFValidator()
    edge = CandidateEdge(
        proposition_name="Edge Low Replication",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1", stage_f_min_replication_pct=0.60)
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

    # Only 1 of 5 contexts succeeds (20% < 60%)
    contexts = [
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.05, 0.300, 200),
        ("GOOGL", -0.20, 0.400, 200),
        ("AMZN", 0.02, 0.800, 200),
        ("TSLA", 0.01, 0.900, 200),
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

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.REPLICATION_FAILED
