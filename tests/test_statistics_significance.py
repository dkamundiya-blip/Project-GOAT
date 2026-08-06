"""
Project GOAT v0.9 — Dedicated Unit Tests for Significance Assessment Engine
"""

import pytest

from goat.statistics.significance.engine import SignificanceAssessmentEngine


@pytest.fixture
def sig_engine():
    return SignificanceAssessmentEngine()


@pytest.mark.parametrize("mean_shift", [0.0, 0.5, 2.0, 5.0])
def test_evaluate_significance_success(sig_engine: SignificanceAssessmentEngine, mean_shift: float):
    samples = [mean_shift + (i % 3) * 0.1 for i in range(100)]
    ste_id = f"STE_{int(mean_shift * 10):016X}"

    assessment = sig_engine.evaluate_significance(
        evaluation_id=ste_id,
        samples=samples,
        null_hypothesis_mean=0.0,
        alpha_threshold=0.01,
    )

    assert assessment.significance_id.startswith("SIG_")
    assert assessment.evaluation_id == ste_id
    assert 0.0 <= assessment.p_value <= 1.0
    if mean_shift >= 2.0:
        assert assessment.is_significant is True
    assert sig_engine.get_assessment(assessment.significance_id) is not None


@pytest.mark.parametrize("num_comp", [1, 5, 10, 20])
def test_bonferroni_correction(sig_engine: SignificanceAssessmentEngine, num_comp: int):
    samples = [0.2 + (i % 5) * 0.05 for i in range(50)]

    assessment = sig_engine.evaluate_significance(
        evaluation_id="STE_1234567890ABCDEF",
        samples=samples,
        correction_method="BONFERRONI",
        num_comparisons=num_comp,
    )

    assert assessment.multiple_comparison_correction == "BONFERRONI"
    assert assessment.adjusted_p_value >= assessment.p_value
