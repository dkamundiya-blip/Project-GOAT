"""
Project GOAT v0.6 — Stage E Persistence Integration Unit Tests
"""

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
from goat.research.edge.validation.stages.stage_e import StageEValidator


def test_stage_e_evidence_persistence_and_replay():
    repo = SQLiteEdgeRepository(":memory:")
    validator = StageEValidator()

    edge = CandidateEdge(
        proposition_name="Persistence Edge E",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    repo.save_candidate_edge(edge)

    policy = ValidationPolicy(policy_id="P1", stage_e_fail_on_contradictory_inversion=True)
    repo.save_validation_policy(policy)

    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )
    repo.save_validation_run(run)

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
        contradictory_effect=-0.30,
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
        stage_d_result=stage_d_res,
        baseline_effect=0.50,
        contradictory_effect=-0.30,
    )
    assert res_replay.evidence_ids[0] == ev_id
