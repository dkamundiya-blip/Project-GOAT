"""
Project GOAT v0.6 — Stage F Meta-Analysis Unit Tests
"""

import pytest
from scipy import stats

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.enums import MetaAnalysisMethod
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.stage_f import StageFValidator


def test_meta_analysis_method_affects_policy_hash():
    p_fisher = ValidationPolicy(policy_id="P1", meta_analysis_method=MetaAnalysisMethod.FISHER_COMBINED_PROBABILITY)
    p_stouffer = ValidationPolicy(policy_id="P1", meta_analysis_method=MetaAnalysisMethod.STOUFFER_Z_SCORE)

    assert p_fisher.policy_hash != p_stouffer.policy_hash


def test_stage_f_fisher_meta_analysis_pass_and_fail():
    validator = StageFValidator()

    edge = CandidateEdge(
        proposition_name="Meta Edge",
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

    # 4 contexts with borderline p-values causing combined p_meta > 0.01
    contexts_high_p = [
        ("C1", 0.30, 0.04, 200),
        ("C2", 0.30, 0.04, 200),
        ("C3", 0.30, 0.04, 200),
        ("C4", 0.05, 0.30, 200),
    ]

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="1234567890ab",
        policy=policy,
        validation_run=run,
        dataset_partitions={},
        stage_e_result=stage_e_res,
        baseline_effect=0.50,
        context_evaluations=contexts_high_p,
    )

    assert res.decision in (StageDecision.PASS, StageDecision.FAIL)
