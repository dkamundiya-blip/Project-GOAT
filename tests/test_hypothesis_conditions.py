"""
Project GOAT v0.4 — Unit Tests for Causal Condition Evaluator
"""

import pandas as pd
import pytest

from goat.research.hypothesis.conditions import CausalConditionEvaluator


def test_condition_primitives_greater_less_between() -> None:
    """Test basic greater_than, less_than, and between condition primitives."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-07-22", periods=5, freq="1min"),
        "close": [10.0, 20.0, 30.0, 40.0, 50.0],
    })

    evaluator = CausalConditionEvaluator()

    # 1. Greater than 25
    mask_gt = evaluator.evaluate_condition(df, {"primitive": "greater_than", "feature": "close"}, {"threshold": 25.0})
    assert mask_gt.tolist() == [False, False, True, True, True]

    # 2. Less than 25
    mask_lt = evaluator.evaluate_condition(df, {"primitive": "less_than", "feature": "close"}, {"threshold": 25.0})
    assert mask_lt.tolist() == [True, True, False, False, False]

    # 3. Between 15 and 35
    mask_bet = evaluator.evaluate_condition(df, {"primitive": "between", "feature": "close"}, {"lower": 15.0, "upper": 35.0})
    assert mask_bet.tolist() == [False, True, True, False, False]
