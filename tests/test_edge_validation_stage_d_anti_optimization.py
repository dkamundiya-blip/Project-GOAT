"""
Project GOAT v0.6 — Stage D Anti-Optimization Unit Tests
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
from goat.research.edge.validation.stages.stage_d import StageDValidator


def test_stage_d_stronger_perturbation_never_replaces_baseline():
    """MANDATORY TEST: A perturbation producing a stronger effect MUST NOT replace baseline parameters."""
    validator = StageDValidator()

    edge = CandidateEdge(
        proposition_name="Anti-Optimization Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(
        policy_id="P1", stage_d_min_stable_ratio=0.65, stage_d_max_allowed_drop=0.60
    )
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    stage_c_res = StageResult(
        validation_run_id=run.validation_run_id,
        edge_id=edge.edge_id,
        stage=ValidationStage.STAGE_C_TEMPORAL,
        decision=StageDecision.PASS,
        reason_code=ReasonCode.PASSED,
        policy_hash=policy.policy_hash,
    )

    # Baseline effect = 0.40. Perturbation with period=24 yields 0.90 (much stronger)!
    evals = [
        ({"period": 16}, 0.35),
        ({"period": 20}, 0.40),
        ({"period": 24}, 0.90),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_c_result=stage_c_res,
        baseline_effect=0.40,
        perturbation_evaluations=evals,
    )

    assert res.decision == StageDecision.PASS

    # Verify baseline candidate edge parameters remained strictly untouched
    assert edge.base_condition_spec == {"period": 20}
    assert not hasattr(res, "best_parameter")
    assert not hasattr(res, "argmax")
