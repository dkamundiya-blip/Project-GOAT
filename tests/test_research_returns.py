"""
Project GOAT v0.3 — Unit Tests for Return Series Engine
"""

import numpy as np
import pandas as pd
import pytest

from goat.research.returns import calculate_returns


def test_calculate_returns_math() -> None:
    """Test arithmetic, log, and absolute return math."""
    df = pd.DataFrame([
        {"timestamp": "2024-07-22T00:00:00Z", "close": 100.0},
        {"timestamp": "2024-07-22T00:01:00Z", "close": 105.0},
        {"timestamp": "2024-07-22T00:02:00Z", "close": 94.5},
    ])
    res = calculate_returns(df, price_col="close")

    # t=0 -> NaN
    assert np.isnan(res["ret_arithmetic"].iloc[0])

    # t=1 -> (105 - 100) / 100 = 0.05
    assert pytest.approx(res["ret_arithmetic"].iloc[1], 0.0001) == 0.05
    assert pytest.approx(res["ret_log"].iloc[1], 0.0001) == np.log(105 / 100)
    assert pytest.approx(res["ret_abs"].iloc[1], 0.0001) == 0.05

    # t=2 -> (94.5 - 105) / 105 = -0.10
    assert pytest.approx(res["ret_arithmetic"].iloc[2], 0.0001) == -0.10
    assert pytest.approx(res["ret_abs"].iloc[2], 0.0001) == 0.10


def test_calculate_returns_division_by_zero_handling() -> None:
    """Test zero and negative price protection."""
    df = pd.DataFrame([
        {"timestamp": "2024-07-22T00:00:00Z", "close": 0.0},
        {"timestamp": "2024-07-22T00:01:00Z", "close": 100.0},
    ])
    res = calculate_returns(df, price_col="close")
    assert np.isnan(res["ret_arithmetic"].iloc[1])
