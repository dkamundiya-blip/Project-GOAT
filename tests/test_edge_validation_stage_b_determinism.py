"""
Project GOAT v0.6 — Stage B Determinism Unit Tests
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
from goat.research.edge.validation.stages.stage_b import StageBValidator


def test_stage_b_cross_process_determinism():
    validator = StageBValidator()

    edge = CandidateEdge(
        proposition_name="Determinism Edge B",
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

    rng1 = np.random.default_rng(100)
    val_cond1 = rng1.normal(loc=0.4, scale=1.0, size=150)
    val_base1 = rng1.normal(loc=0.0, scale=1.0, size=150)

    res1 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_a_result=stage_a_res,
        discovery_effect=0.50,
        val_cond_arr=val_cond1,
        val_base_arr=val_base1,
    )

    rng2 = np.random.default_rng(100)
    val_cond2 = rng2.normal(loc=0.4, scale=1.0, size=150)
    val_base2 = rng2.normal(loc=0.0, scale=1.0, size=150)

    res2 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_a_result=stage_a_res,
        discovery_effect=0.50,
        val_cond_arr=val_cond2,
        val_base_arr=val_base2,
    )

    assert res1.decision == res2.decision
    assert res1.reason_code == res2.reason_code
    assert res1.evidence_ids == res2.evidence_ids
