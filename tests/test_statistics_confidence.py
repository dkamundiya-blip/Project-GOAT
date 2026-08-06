"""
Project GOAT v0.9 — Dedicated Unit Tests for Confidence Assessment Engine
"""

import pytest

from goat.statistics.confidence.engine import ConfidenceAssessmentEngine
from goat.statistics.core.enums import EvaluationConfidence


@pytest.fixture
def conf_engine():
    return ConfidenceAssessmentEngine()


@pytest.mark.parametrize("n_samples", [10, 50, 150, 600, 2500])
def test_calculate_confidence_success(conf_engine: ConfidenceAssessmentEngine, n_samples: int):
    samples = [1.0 + (i % 5) * 0.1 for i in range(n_samples)]
    ste_id = f"STE_{n_samples:016X}"

    assessment = conf_engine.calculate_confidence(
        evaluation_id=ste_id,
        samples=samples,
        confidence_level=0.95,
    )

    assert assessment.confidence_id.startswith("CON_")
    assert assessment.evaluation_id == ste_id
    assert assessment.sample_size == n_samples
    assert assessment.lower_bound <= assessment.upper_bound
    assert assessment.margin_of_error >= 0.0
    assert conf_engine.get_assessment(assessment.confidence_id) is not None


def test_calculate_confidence_empty_samples(conf_engine: ConfidenceAssessmentEngine):
    with pytest.raises(ValueError):
        conf_engine.calculate_confidence(
            evaluation_id="STE_1234567890ABCDEF",
            samples=[],
        )


@pytest.mark.parametrize(
    "n, expected_rating",
    [
        (15, EvaluationConfidence.VERY_LOW),
        (50, EvaluationConfidence.LOW),
        (250, EvaluationConfidence.MODERATE),
        (1200, EvaluationConfidence.HIGH),
        (3000, EvaluationConfidence.VERY_HIGH),
    ],
)
def test_classify_confidence_ratings(conf_engine: ConfidenceAssessmentEngine, n: int, expected_rating: EvaluationConfidence):
    rating = conf_engine.classify_confidence(sample_size=n, margin_of_error=0.01, std_dev=1.0)
    assert rating == expected_rating
