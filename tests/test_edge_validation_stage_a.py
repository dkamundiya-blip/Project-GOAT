"""
Project GOAT v0.6 — StageAValidator Unit Tests
"""

import numpy as np
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    ValidationLifecycleState,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_a import StageAValidator
from goat.research.edge.validation.state import ValidationStateMachine


def test_stage_a_pass_flow():
    validator = StageAValidator()
    assert validator.stage == ValidationStage.STAGE_A_DISCOVERY
    assert validator.prerequisite_stage is None

    edge = CandidateEdge(
        proposition_name="Momentum Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_a_min_sample=100, stage_a_effect_min=0.15, stage_a_alpha=0.05
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    rng = np.random.default_rng(42)
    cond = rng.normal(loc=0.5, scale=1.0, size=150)
    base = rng.normal(loc=0.0, scale=1.0, size=150)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond,
        base_arr=base,
    )

    assert res.decision == StageDecision.PASS
    assert res.reason_code == ReasonCode.PASSED
    assert len(res.evidence_ids) == 1

    # Progression check
    sm = ValidationStateMachine()
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.DISCOVERY_VALIDATION


def test_stage_a_insufficient_sample_size():
    validator = StageAValidator()
    edge = CandidateEdge(
        proposition_name="Edge Low Sample",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(policy_id="P1", stage_a_min_sample=100)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    rng = np.random.default_rng(42)
    cond = rng.normal(loc=0.5, scale=1.0, size=50)
    base = rng.normal(loc=0.0, scale=1.0, size=50)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond,
        base_arr=base,
    )

    assert res.decision == StageDecision.INSUFFICIENT_EVIDENCE
    assert res.reason_code == ReasonCode.SAMPLE_TOO_SMALL

    # Progression check: Stage B MUST be blocked
    sm = ValidationStateMachine()
    next_state = sm.handle_stage_decision(validator.stage, res.decision)
    assert next_state == ValidationLifecycleState.REJECTED


def test_stage_a_small_effect_size_failure():
    validator = StageAValidator()
    edge = CandidateEdge(
        proposition_name="Edge Small Effect",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_a_min_sample=100, stage_a_effect_min=0.50, stage_a_alpha=0.05
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    rng = np.random.default_rng(42)
    cond = rng.normal(loc=0.1, scale=1.0, size=150)
    base = rng.normal(loc=0.0, scale=1.0, size=150)

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        cond_arr=cond,
        base_arr=base,
    )

    assert res.decision == StageDecision.FAIL
    assert res.reason_code == ReasonCode.EFFECT_TOO_SMALL
