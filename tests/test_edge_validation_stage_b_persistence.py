"""
Project GOAT v0.6 — Stage B Persistence Integration Unit Tests
"""

import numpy as np
import pytest

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_b import StageBValidator


def test_stage_b_evidence_persistence_and_replay():
    repo = SQLiteEdgeRepository(":memory:")
    validator = StageBValidator()

    edge = CandidateEdge(
        proposition_name="Persistence Edge B",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    repo.save_candidate_edge(edge)

    policy = ValidationPolicy(policy_id="P1", stage_b_min_retention_ratio=0.50)
    repo.save_validation_policy(policy)

    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )
    repo.save_validation_run(run)

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

    ev_id = res.evidence_ids[0]
    assert ev_id.startswith("EVD_")

    # Replay produces identical evidence ID
    res_replay = validator.evaluate(
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
    assert res_replay.evidence_ids[0] == ev_id
