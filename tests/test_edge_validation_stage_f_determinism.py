"""
Project GOAT v0.6 — Stage F Determinism Unit Tests
"""

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
from goat.research.edge.validation.stages.stage_f import StageFValidator


def test_stage_f_input_order_invariance_and_cross_process_determinism():
    validator = StageFValidator()

    edge = CandidateEdge(
        proposition_name="Determinism Edge F",
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

    contexts1 = [
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
        ("GOOGL", 0.40, 0.005, 200),
    ]

    # Reordered context input
    contexts2 = [
        ("GOOGL", 0.40, 0.005, 200),
        ("AAPL", 0.45, 0.001, 200),
        ("MSFT", 0.50, 0.002, 200),
    ]

    res1 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_e_result=stage_e_res,
        baseline_effect=0.50,
        context_evaluations=contexts1,
    )

    res2 = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_e_result=stage_e_res,
        baseline_effect=0.50,
        context_evaluations=contexts2,
    )

    assert res1.decision == res2.decision
    assert res1.reason_code == res2.reason_code
    assert res1.evidence_ids == res2.evidence_ids
