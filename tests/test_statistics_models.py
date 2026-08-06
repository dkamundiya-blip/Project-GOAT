"""
Project GOAT v0.9 — Comprehensive Dedicated Unit Tests for Statistical Domain Models
"""

import pytest
from pydantic import ValidationError

from goat.statistics.core.canonical import (
    compute_canonical_sha256,
    compute_confidence_id,
    compute_decision_id,
    compute_expectancy_id,
    compute_significance_id,
    compute_statistical_evaluation_id,
    compute_summary_id,
    serialize_canonical_json,
)
from goat.statistics.core.enums import (
    EvaluationConfidence,
    EvaluationStatus,
    ScientificDecision,
)
from goat.statistics.core.models import (
    ConfidenceAssessment,
    EvaluationDecision,
    EvaluationSummary,
    ExpectancyAssessment,
    SignificanceAssessment,
    StatisticalEvaluation,
)


@pytest.mark.parametrize("status", list(EvaluationStatus))
@pytest.mark.parametrize("decision", list(ScientificDecision))
@pytest.mark.parametrize("rating", list(EvaluationConfidence))
def test_statistical_evaluation_model_instantiation(
    status: EvaluationStatus,
    decision: ScientificDecision,
    rating: EvaluationConfidence,
):
    exp_id = "EXP_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"

    ste_id, canonical_hash = compute_statistical_evaluation_id(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
    )

    eval_model = StatisticalEvaluation(
        evaluation_id=ste_id,
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        status=status,
        decision=decision,
        confidence_level=0.95,
        confidence_rating=rating,
        p_value=0.001,
        effect_size=1.2,
        expected_value=0.45,
        sample_size=500,
        evaluator="TEST_EVALUATOR",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    assert eval_model.evaluation_id == ste_id
    assert eval_model.experiment_id == exp_id
    assert eval_model.hypothesis_id == hyp_id
    assert eval_model.status == status
    assert eval_model.decision == decision
    assert eval_model.confidence_rating == rating
    assert eval_model.canonical_hash == canonical_hash


@pytest.mark.parametrize("invalid_id", ["INVALID_ID", "STE_SHORT", "123_STE", "EXP_1234567890ABCDEF"])
def test_statistical_evaluation_invalid_id_pattern(invalid_id: str):
    with pytest.raises(ValidationError):
        StatisticalEvaluation(
            evaluation_id=invalid_id,
            experiment_id="EXP_1234567890ABCDEF",
            hypothesis_id="HYP_1234567890ABCDEF",
            timestamp="2026-08-04T12:00:00Z",
        )


def test_statistical_evaluation_immutability():
    ste_id, canonical_hash = compute_statistical_evaluation_id(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
    )
    eval_model = StatisticalEvaluation(
        evaluation_id=ste_id,
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        eval_model.p_value = 0.5  # Frozen check


@pytest.mark.parametrize("rating", list(EvaluationConfidence))
def test_confidence_assessment_model(rating: EvaluationConfidence):
    ste_id = "STE_1234567890ABCDEF"
    con_id, con_hash = compute_confidence_id(
        evaluation_id=ste_id,
        confidence_level=0.95,
        margin_of_error=0.02,
    )

    conf = ConfidenceAssessment(
        confidence_id=con_id,
        evaluation_id=ste_id,
        confidence_level=0.95,
        lower_bound=0.40,
        upper_bound=0.44,
        margin_of_error=0.02,
        sample_size=1000,
        confidence_rating=rating,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=con_hash,
    )

    assert conf.confidence_id == con_id
    assert conf.confidence_rating == rating


@pytest.mark.parametrize("p_val", [0.0001, 0.005, 0.01, 0.05, 0.5])
def test_significance_assessment_model(p_val: float):
    ste_id = "STE_1234567890ABCDEF"
    sig_id, sig_hash = compute_significance_id(
        evaluation_id=ste_id,
        p_value=p_val,
        test_statistic=3.5,
    )

    sig = SignificanceAssessment(
        significance_id=sig_id,
        evaluation_id=ste_id,
        p_value=p_val,
        test_statistic=3.5,
        alpha_threshold=0.01,
        is_significant=(p_val < 0.01),
        multiple_comparison_correction="BONFERRONI",
        adjusted_p_value=min(1.0, p_val * 5),
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sig_hash,
    )

    assert sig.significance_id == sig_id
    assert sig.p_value == p_val


@pytest.mark.parametrize("exp_val", [-1.0, 0.0, 0.5, 2.5])
def test_expectancy_assessment_model(exp_val: float):
    ste_id = "STE_1234567890ABCDEF"
    exp_id, exp_hash = compute_expectancy_id(
        evaluation_id=ste_id,
        expected_value=exp_val,
        sample_size=200,
    )

    exp_model = ExpectancyAssessment(
        expectancy_id=exp_id,
        evaluation_id=ste_id,
        expected_value=exp_val,
        win_rate=0.6,
        loss_rate=0.4,
        average_gain=1.5,
        average_loss=1.0,
        profit_factor=2.25,
        sample_size=200,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=exp_hash,
    )

    assert exp_model.expectancy_id == exp_id
    assert exp_model.expected_value == exp_val


@pytest.mark.parametrize("decision", list(ScientificDecision))
def test_evaluation_decision_model(decision: ScientificDecision):
    ste_id = "STE_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"
    evd_id, evd_hash = compute_decision_id(
        evaluation_id=ste_id,
        decision=decision.value,
        hypothesis_id=hyp_id,
    )

    dec_model = EvaluationDecision(
        decision_id=evd_id,
        evaluation_id=ste_id,
        hypothesis_id=hyp_id,
        decision=decision,
        confidence_rating=EvaluationConfidence.HIGH,
        decision_rationale="Decision rationale statement for test.",
        authorizer="TEST_BOARD",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=evd_hash,
    )

    assert dec_model.decision_id == evd_id
    assert dec_model.decision == decision


@pytest.mark.parametrize("eval_count", [0, 10, 50, 100])
def test_evaluation_summary_model(eval_count: int):
    sum_id, sum_hash = compute_summary_id(
        total_evaluations=eval_count,
        total_decisions=eval_count,
        timestamp="2026-08-04T12:00:00Z",
    )

    summary = EvaluationSummary(
        summary_id=sum_id,
        total_evaluations=eval_count,
        total_decisions=eval_count,
        decision_counts={"SUPPORTED": eval_count},
        confidence_counts={"HIGH": eval_count},
        status_counts={"COMPLETED": eval_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    assert summary.summary_id == sum_id
    assert summary.total_evaluations == eval_count
