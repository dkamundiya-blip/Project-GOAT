"""
Project GOAT v0.9 — Dedicated Unit Tests for Expectancy Assessment Engine
"""

import pytest

from goat.statistics.expectancy.engine import ExpectancyAssessmentEngine


@pytest.fixture
def exp_engine():
    return ExpectancyAssessmentEngine()


@pytest.mark.parametrize("win_pct", [0.3, 0.5, 0.7, 0.9])
def test_calculate_expectancy_success(exp_engine: ExpectancyAssessmentEngine, win_pct: float):
    n = 100
    n_wins = int(n * win_pct)
    n_losses = n - n_wins

    returns = [1.5] * n_wins + [-1.0] * n_losses
    ste_id = f"STE_{int(win_pct * 100):016X}"

    assessment = exp_engine.calculate_expectancy(
        evaluation_id=ste_id,
        returns_or_gains=returns,
    )

    assert assessment.expectancy_id.startswith("EXP_")
    assert assessment.evaluation_id == ste_id
    assert assessment.sample_size == n
    assert abs(assessment.win_rate - win_pct) < 0.05
    assert assessment.average_gain == 1.5
    assert assessment.average_loss == 1.0
    assert exp_engine.get_assessment(assessment.expectancy_id) is not None


def test_calculate_expectancy_empty_returns(exp_engine: ExpectancyAssessmentEngine):
    with pytest.raises(ValueError):
        exp_engine.calculate_expectancy(
            evaluation_id="STE_1234567890ABCDEF",
            returns_or_gains=[],
        )


def test_profit_factor_calculation(exp_engine: ExpectancyAssessmentEngine):
    returns = [2.0, 3.0, -1.0, -1.0]
    assessment = exp_engine.calculate_expectancy(
        evaluation_id="STE_1234567890ABCDEF",
        returns_or_gains=returns,
    )

    # Gross gains = 5.0, Gross losses = 2.0 -> Profit factor = 2.5
    assert assessment.profit_factor == 2.5
    assert assessment.expected_value == (0.5 * 2.5) - (0.5 * 1.0)  # 0.75
