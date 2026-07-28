"""
Project GOAT v0.6 — Stage C Determinism Unit Tests
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
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_c import StageCValidator


def test_stage_c_cross_process_determinism():
    validator = StageCValidator()

    edge = CandidateEdge(
        proposition_name="Determinism Edge C",
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

    rng1 = np.random.default_rng(200)
    folds1 = [(rng1.normal(0.4, 1.0, 100), rng1.normal(0.0, 1.0, 100)) for _ in range(5)]

    res1 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_b_result=stage_b_res,
        discovery_effect=0.50,
        fold_observations=folds1,
    )

    rng2 = np.random.default_rng(200)
    folds2 = [(rng2.normal(0.4, 1.0, 100), rng2.normal(0.0, 1.0, 100)) for _ in range(5)]

    res2 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_b_result=stage_b_res,
        discovery_effect=0.50,
        fold_observations=folds2,
    )

    assert res1.decision == res2.decision
    assert res1.reason_code == res2.reason_code
    assert res1.evidence_ids == res2.evidence_ids
