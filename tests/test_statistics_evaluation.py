"""
Project GOAT v0.9 — Dedicated Unit Tests for Statistical Evaluation Engine
"""

import pytest

from goat.statistics.core.enums import ScientificDecision
from goat.statistics.evaluation.engine import StatisticalEvaluationEngine


@pytest.fixture
def eval_engine():
    return StatisticalEvaluationEngine()


def test_evaluate_experiment_supported(eval_engine: StatisticalEvaluationEngine):
    # Positive returns with 150 samples -> SUPPORTED decision
    samples = [0.5 + (i % 5) * 0.1 for i in range(150)]
    exp_id = "EXP_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"

    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        samples=samples,
    )

    assert ev.evaluation_id.startswith("STE_")
    assert dec.decision_id.startswith("EVD_")
    assert dec.decision == ScientificDecision.SUPPORTED
    assert sig.is_significant is True
    assert exp.expected_value > 0.0


def test_evaluate_experiment_rejected(eval_engine: StatisticalEvaluationEngine):
    # Negative returns with 150 samples -> REJECTED decision
    samples = [-0.5 - (i % 5) * 0.1 for i in range(150)]
    exp_id = "EXP_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"

    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        samples=samples,
    )

    assert dec.decision == ScientificDecision.REJECTED


def test_evaluate_experiment_requires_more_data(eval_engine: StatisticalEvaluationEngine):
    # Only 15 samples (< 30) -> REQUIRES_MORE_DATA
    samples = [0.5] * 15
    exp_id = "EXP_1234567890ABCDEF"
    hyp_id = "HYP_1234567890ABCDEF"

    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id=exp_id,
        hypothesis_id=hyp_id,
        samples=samples,
    )

    assert dec.decision == ScientificDecision.REQUIRES_MORE_DATA


@pytest.mark.parametrize("invalid_exp_id", ["INVALID", "STE_1234567890ABCDEF", "HYP_1234567890ABCDEF"])
def test_evaluate_experiment_invalid_exp_prefix(eval_engine: StatisticalEvaluationEngine, invalid_exp_id: str):
    with pytest.raises(ValueError):
        eval_engine.evaluate_experiment(
            experiment_id=invalid_exp_id,
            hypothesis_id="HYP_1234567890ABCDEF",
            samples=[1.0] * 50,
        )
