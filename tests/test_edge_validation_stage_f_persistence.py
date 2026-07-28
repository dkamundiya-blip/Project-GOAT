"""
Project GOAT v0.6 — Stage F Persistence Integration Unit Tests
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
from goat.research.edge.validation.stages.stage_f import StageFValidator


def test_stage_f_evidence_persistence_and_replay():
    repo = SQLiteEdgeRepository(":memory:")
    validator = StageFValidator()

    edge = CandidateEdge(
        proposition_name="Persistence Edge F",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    repo.save_candidate_edge(edge)

    policy = ValidationPolicy(policy_id="P1", stage_f_min_replication_pct=0.60)
    repo.save_validation_policy(policy)

    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )
    repo.save_validation_run(run)

    stage_e_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_E_FALSIFICATION,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    contexts = [
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
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

    assert len(res.evidence_ids) == 2
    for ev_id in res.evidence_ids:
        assert ev_id.startswith("EVD_")

    # Replay produces identical evidence IDs
    res_replay = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_e_result=stage_e_res,
        baseline_effect=0.50,
        context_evaluations=contexts,
    )
    assert res_replay.evidence_ids == res.evidence_ids
