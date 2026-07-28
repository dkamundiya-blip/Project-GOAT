"""
Project GOAT v0.6 — Stage E Anti-P-Hacking Unit Tests
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
from goat.research.edge.validation.stages.stage_e import StageEValidator


def test_stage_e_cannot_select_best_inversion_or_mutate_hypothesis():
    """MANDATORY TEST: Multiple inversion search or post-hoc condition selection is prohibited."""
    validator = StageEValidator()

    edge = CandidateEdge(
        proposition_name="Anti-P-Hacking Edge E",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"period": 20},
    )
    policy = ValidationPolicy(policy_id="P1", stage_e_fail_on_contradictory_inversion=True)
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=policy.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

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

    assert res.decision == StageDecision.PASS

    # Verify baseline candidate edge parameters and primitive remained strictly untouched
    assert edge.causal_primitive == "greater_than"
    assert edge.base_condition_spec == {"period": 20}
    assert not hasattr(res, "best_inversion")
    assert not hasattr(res, "selected_inversion")
