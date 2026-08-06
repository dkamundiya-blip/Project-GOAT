"""
Project GOAT v0.7 — Step 5.7 Statistical Validation Subsystem Test Suite
"""

from __future__ import annotations

import pytest

from goat.validation.evidence import ValidationEvidence, compute_evidence_id
from goat.validation.statistics import (
    StatisticalCalculator,
    ValidationScores,
    compute_agreement_score,
    compute_confidence_score,
    compute_evidence_score,
    compute_overall_confidence,
    compute_reproducibility_score,
    compute_robustness_score,
    compute_stability_score,
    compute_validation_score,
)


@pytest.mark.parametrize("total,validated,max_evd,expected", [
    (0, 0, 20, 0.0),
    (10, 0, 20, 0.0),
    (10, 10, 20, 0.5),
    (20, 20, 20, 1.0),
    (30, 30, 20, 1.0),
    (5, 5, 20, 0.25),
])
def test_confidence_score_parametrized(total: int, validated: int, max_evd: int, expected: float):
    """Verify confidence score calculation via parametrization."""
    assert compute_confidence_score(total, validated, max_evidence=max_evd) == expected


@pytest.mark.parametrize("total_w,max_w,expected", [
    (0.0, 20.0, 0.0),
    (10.0, 20.0, 0.5),
    (20.0, 20.0, 1.0),
    (30.0, 20.0, 1.0),
    (5.0, 20.0, 0.25),
])
def test_evidence_score_parametrized(total_w: float, max_w: float, expected: float):
    """Verify evidence score calculation via parametrization."""
    assert compute_evidence_score(total_w, max_weight=max_w) == expected


@pytest.mark.parametrize("supp,contra,expected", [
    (0, 0, 0.0),
    (5, 0, 1.0),
    (0, 5, 0.0),
    (3, 1, 0.75),
    (5, 5, 0.5),
    (9, 1, 0.9),
])
def test_agreement_score_parametrized(supp: int, contra: int, expected: float):
    """Verify agreement score calculation via parametrization."""
    assert compute_agreement_score(supp, contra) == expected


@pytest.mark.parametrize("reps,min_reps,expected", [
    (0, 3, 0.0),
    (1, 3, 0.333333),
    (2, 3, 0.666667),
    (3, 3, 1.0),
    (5, 3, 1.0),
])
def test_reproducibility_score_parametrized(reps: int, min_reps: int, expected: float):
    """Verify reproducibility score calculation via parametrization."""
    assert compute_reproducibility_score(reps, min_replications=min_reps) == expected


@pytest.mark.parametrize("contexts,min_c,expected", [
    (0, 4, 0.0),
    (2, 4, 0.5),
    (4, 4, 1.0),
    (6, 4, 1.0),
])
def test_robustness_score_parametrized(contexts: int, min_c: int, expected: float):
    """Verify robustness score calculation via parametrization."""
    assert compute_robustness_score(contexts, min_contexts=min_c) == expected


@pytest.mark.parametrize("cons,total,expected", [
    (0, 0, 0.0),
    (8, 10, 0.8),
    (10, 10, 1.0),
    (5, 10, 0.5),
])
def test_stability_score_parametrized(cons: int, total: int, expected: float):
    """Verify stability score calculation via parametrization."""
    assert compute_stability_score(cons, total) == expected


@pytest.mark.parametrize("passed,total,expected", [
    (0, 5, 0.0),
    (3, 5, 0.6),
    (5, 5, 1.0),
    (4, 5, 0.8),
])
def test_validation_score_parametrized(passed: int, total: int, expected: float):
    """Verify validation threshold pass score via parametrization."""
    assert compute_validation_score(passed, total) == expected


def test_overall_confidence_weighted_sum():
    """Verify weighted linear combination for overall scientific confidence."""
    score = compute_overall_confidence(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    assert score == 1.0

    score_zero = compute_overall_confidence(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert score_zero == 0.0


def test_statistical_calculator_orchestration():
    """Verify StatisticalCalculator calculates all 8 scores deterministically."""
    calculator = StatisticalCalculator()

    eid1, eh1 = compute_evidence_id("VRN_1", "EXP_1", "experiment", "2026-01-01T00:00:00Z")
    eid2, eh2 = compute_evidence_id("VRN_1", "EXP_2", "experiment", "2026-01-01T00:01:00Z")

    e1 = ValidationEvidence(evidence_id=eid1, evidence_hash=eh1, confidence=0.9, weight=2.0, supports_hypothesis=True, timestamp="2026-01-01T00:00:00Z")
    e2 = ValidationEvidence(evidence_id=eid2, evidence_hash=eh2, confidence=0.8, weight=2.0, supports_hypothesis=True, timestamp="2026-01-01T00:01:00Z")

    evidence_list = [e1, e2]
    summary = {
        "overall": {
            "total_count": 2,
            "supporting_count": 2,
            "contradicting_count": 0,
            "total_weight": 4.0,
            "weighted_confidence": 0.85,
        }
    }

    scores = calculator.calculate_all_scores(
        evidence_list=evidence_list,
        evidence_summary=summary,
        replication_count=3,
        cross_context_count=3,
        consistent_periods=5,
        total_periods=5,
    )

    assert isinstance(scores, ValidationScores)
    assert scores.agreement_score == 1.0
