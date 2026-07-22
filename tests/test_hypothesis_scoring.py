"""
Project GOAT v0.4 — Unit Tests for EdgeScore Normalization & Evidence Discipline

Tests Amendment Requirements A–F:
A. Negligible effect + large N cannot drive EdgeScore to max via q-value reduction.
B. Extremely small q-values saturate statistical-evidence component.
C. Metric-specific effect normalization is deterministic.
D. Changing effect_size_method explicitly changes normalization scale.
E. Statistically significant but practically negligible effect receives weak-effect classification.
F. EdgeScore remains bounded between 0 and 100 under all inputs.
"""

import numpy as np

from goat.research.hypothesis.scoring import (
    calculate_edge_score,
    is_practically_weak_effect,
    normalize_effect_magnitude,
)


def test_amendment_a_negligible_effect_large_n_bounded() -> None:
    """Amendment A: Huge N with tiny q-value cannot drive EdgeScore to max if effect is negligible."""
    # Negligible effect d = 0.01, but huge sample size giving tiny q-value (1e-15)
    score_huge_n = calculate_edge_score(
        effect_size=0.01,
        q_value=1e-15,
        effect_method="cohens_d",
        sample_size=100000,
    )

    # Statistical score saturates at 25, but effect magnitude score is tiny (~0.31)
    # Total EdgeScore MUST NOT be near maximum (100)
    assert score_huge_n["total_edge_score"] < 65.0
    assert score_huge_n["effect_magnitude_score"] < 1.0


def test_amendment_b_qvalue_saturation() -> None:
    """Amendment B: Extremely small q-values saturate the statistical-evidence component."""
    score_q1 = calculate_edge_score(effect_size=0.5, q_value=0.0001, effect_method="cohens_d")
    score_q2 = calculate_edge_score(effect_size=0.5, q_value=1e-12, effect_method="cohens_d")

    # Both achieve maximum statistical confidence score (25.0) due to saturation
    assert score_q1["statistical_confidence_score"] == 25.0
    assert score_q2["statistical_confidence_score"] == 25.0


def test_amendment_c_and_d_metric_specific_effect_normalization() -> None:
    """Amendment C & D: Metric-specific effect normalization is deterministic and changes scale explicitly."""
    # Cohen's d = 0.8 is benchmark "large" -> 25.0 pts
    s_cohen = normalize_effect_magnitude(0.8, method="cohens_d")
    assert s_cohen == 25.0

    # Rank-biserial r = 0.5 is benchmark "large" -> 25.0 pts
    s_rank = normalize_effect_magnitude(0.5, method="rank_biserial")
    assert s_rank == 25.0

    # Changing method explicitly changes normalization output for same input value
    s_cohen_val = normalize_effect_magnitude(0.5, method="cohens_d")
    s_rank_val = normalize_effect_magnitude(0.5, method="rank_biserial")

    assert s_cohen_val != s_rank_val
    assert s_cohen_val == (0.5 / 0.8) * 25.0
    assert s_rank_val == 25.0


def test_amendment_e_practically_weak_effect_classification() -> None:
    """Amendment E: Negligible effect receives STATISTICALLY_SUPPORTED_BUT_PRACTICALLY_WEAK status."""
    assert is_practically_weak_effect(0.05, method="cohens_d") is True
    assert is_practically_weak_effect(0.50, method="cohens_d") is False
    assert is_practically_weak_effect(0.01, method="prop_diff") is True


def test_amendment_f_edge_score_bounded_0_to_100() -> None:
    """Amendment F: EdgeScore remains strictly bounded between 0 and 100 under extreme inputs."""
    score_max = calculate_edge_score(
        effect_size=10.0,
        q_value=0.0,
        effect_method="cohens_d",
        sample_size=10000,
    )
    score_min = calculate_edge_score(
        effect_size=-0.0,
        q_value=1.0,
        effect_method="cohens_d",
        sample_size=0,
        dependence_overlap_risk=True,
    )

    assert 0.0 <= score_max["total_edge_score"] <= 100.0
    assert 0.0 <= score_min["total_edge_score"] <= 100.0
