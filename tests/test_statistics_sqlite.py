"""
Project GOAT v0.9 — Dedicated Unit Tests for Statistical SQLite Persistence
"""

import pytest

from goat.statistics.core.canonical import (
    compute_confidence_id,
    compute_decision_id,
    compute_expectancy_id,
    compute_significance_id,
    compute_statistical_evaluation_id,
    compute_summary_id,
)
from goat.statistics.core.enums import EvaluationConfidence, EvaluationStatus, ScientificDecision
from goat.statistics.core.models import (
    ConfidenceAssessment,
    EvaluationDecision,
    EvaluationSummary,
    ExpectancyAssessment,
    SignificanceAssessment,
    StatisticalEvaluation,
)
from goat.statistics.persistence.sqlite import StatisticalPersistenceContext


@pytest.fixture
def persistence_ctx():
    ctx = StatisticalPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.mark.parametrize("idx", range(1, 15))
def test_statistical_repository_roundtrip(persistence_ctx: StatisticalPersistenceContext, idx: int):
    exp_id = f"EXP_{idx:016X}"
    hyp_id = f"HYP_{idx:016X}"
    ste_id, canonical_hash = compute_statistical_evaluation_id(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
    )

    ev = StatisticalEvaluation(
        evaluation_id=ste_id,
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        status=EvaluationStatus.COMPLETED,
        decision=ScientificDecision.SUPPORTED,
        confidence_level=0.95,
        confidence_rating=EvaluationConfidence.HIGH,
        p_value=0.001,
        effect_size=1.5,
        expected_value=0.5,
        sample_size=200,
        evaluator="EVALUATOR",
        timestamp="2026-08-04T12:00:00Z",
        tags=[f"tag_{idx}"],
        metadata={"idx": idx},
        canonical_hash=canonical_hash,
    )

    persistence_ctx.evaluations.save(ev)
    fetched = persistence_ctx.evaluations.get_by_id(ste_id)

    assert fetched is not None
    assert fetched.evaluation_id == ev.evaluation_id
    assert fetched.decision == ScientificDecision.SUPPORTED
    assert fetched.canonical_hash == ev.canonical_hash


@pytest.mark.parametrize("idx", range(1, 10))
def test_confidence_repository_roundtrip(persistence_ctx: StatisticalPersistenceContext, idx: int):
    ste_id = f"STE_{idx:016X}"
    con_id, con_hash = compute_confidence_id(
        evaluation_id=ste_id,
        confidence_level=0.95,
        margin_of_error=0.01 * idx,
    )

    conf = ConfidenceAssessment(
        confidence_id=con_id,
        evaluation_id=ste_id,
        confidence_level=0.95,
        lower_bound=0.1,
        upper_bound=0.5,
        margin_of_error=0.01 * idx,
        sample_size=100 * idx,
        confidence_rating=EvaluationConfidence.HIGH,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=con_hash,
    )

    persistence_ctx.confidence.save(conf)
    fetched = persistence_ctx.confidence.get_by_id(con_id)

    assert fetched is not None
    assert fetched.confidence_id == con_id
    assert fetched.margin_of_error == 0.01 * idx


@pytest.mark.parametrize("idx", range(1, 10))
def test_significance_repository_roundtrip(persistence_ctx: StatisticalPersistenceContext, idx: int):
    ste_id = f"STE_{idx:016X}"
    sig_id, sig_hash = compute_significance_id(
        evaluation_id=ste_id,
        p_value=0.001 * idx,
        test_statistic=3.0,
    )

    sig = SignificanceAssessment(
        significance_id=sig_id,
        evaluation_id=ste_id,
        p_value=0.001 * idx,
        test_statistic=3.0,
        alpha_threshold=0.01,
        is_significant=True,
        multiple_comparison_correction="BONFERRONI",
        adjusted_p_value=0.005 * idx,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sig_hash,
    )

    persistence_ctx.significance.save(sig)
    fetched = persistence_ctx.significance.get_by_id(sig_id)

    assert fetched is not None
    assert fetched.significance_id == sig_id
    assert fetched.is_significant is True


@pytest.mark.parametrize("idx", range(1, 10))
def test_expectancy_repository_roundtrip(persistence_ctx: StatisticalPersistenceContext, idx: int):
    ste_id = f"STE_{idx:016X}"
    exp_id, exp_hash = compute_expectancy_id(
        evaluation_id=ste_id,
        expected_value=0.2 * idx,
        sample_size=100,
    )

    exp_model = ExpectancyAssessment(
        expectancy_id=exp_id,
        evaluation_id=ste_id,
        expected_value=0.2 * idx,
        win_rate=0.6,
        loss_rate=0.4,
        average_gain=1.0,
        average_loss=0.5,
        profit_factor=3.0,
        sample_size=100,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=exp_hash,
    )

    persistence_ctx.expectancy.save(exp_model)
    fetched = persistence_ctx.expectancy.get_by_id(exp_id)

    assert fetched is not None
    assert fetched.expectancy_id == exp_id
    assert fetched.expected_value == 0.2 * idx


@pytest.mark.parametrize("idx", range(1, 10))
def test_decision_repository_roundtrip(persistence_ctx: StatisticalPersistenceContext, idx: int):
    ste_id = f"STE_{idx:016X}"
    hyp_id = f"HYP_{idx:016X}"
    evd_id, evd_hash = compute_decision_id(
        evaluation_id=ste_id,
        decision="SUPPORTED",
        hypothesis_id=hyp_id,
    )

    dec_model = EvaluationDecision(
        decision_id=evd_id,
        evaluation_id=ste_id,
        hypothesis_id=hyp_id,
        decision=ScientificDecision.SUPPORTED,
        confidence_rating=EvaluationConfidence.HIGH,
        decision_rationale=f"Rationale statement #{idx}",
        authorizer="BOARD",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=evd_hash,
    )

    persistence_ctx.decisions.save(dec_model)
    fetched = persistence_ctx.decisions.get_by_id(evd_id)

    assert fetched is not None
    assert fetched.decision_id == evd_id
    assert fetched.decision == ScientificDecision.SUPPORTED
