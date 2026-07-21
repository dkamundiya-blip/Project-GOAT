"""
Project GOAT v0.3 — Unit Tests for Look-Ahead Leakage Detection

Tests Amendment Requirement A:
- Modifying observations after timestamp t does NOT change causal features at or before t.
"""

import numpy as np
import pandas as pd
import pytest

from goat.research.events import ImpulseCharacterization
from goat.research.returns import calculate_returns
from goat.research.stats import calculate_range_stats


def test_lookahead_leakage_returns_invariance() -> None:
    """Amendment A: Modifying future prices after timestamp t leaves past returns unchanged."""
    dates = pd.date_range("2024-07-22", periods=10, freq="1min")
    prices_orig = [100.0, 102.0, 101.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0]
    prices_mutated = [100.0, 102.0, 101.0, 103.0, 104.0, 999.0, 0.01, 500.0, 1.0, 2.0]  # Rows 5..9 mutated

    df_orig = pd.DataFrame({"timestamp": dates, "close": prices_orig})
    df_mutated = pd.DataFrame({"timestamp": dates, "close": prices_mutated})

    res_orig = calculate_returns(df_orig, price_col="close")
    res_mutated = calculate_returns(df_mutated, price_col="close")

    # Features at rows 0..4 MUST be identical despite future mutations in rows 5..9
    pd.testing.assert_series_equal(
        res_orig["ret_arithmetic"].iloc[:5],
        res_mutated["ret_arithmetic"].iloc[:5],
        check_names=False,
    )


def test_lookahead_leakage_impulse_detection_invariance() -> None:
    """Amendment A: Modifying future rows does not change impulse detection at past timestamp t."""
    dates = pd.date_range("2024-07-22", periods=40, freq="1min")
    prices1 = [100.0] * 20 + [120.0] + [100.0] * 19
    prices2 = [100.0] * 20 + [120.0] + [500.0] * 19  # Future rows mutated

    df1 = pd.DataFrame({"timestamp": dates, "close": prices1})
    df2 = pd.DataFrame({"timestamp": dates, "close": prices2})

    detector = ImpulseCharacterization(std_threshold=1.5, lookback_window=10)

    # Calculate impulse mask for both DataFrames
    imp1 = detector.detect_impulses(df1)
    imp2 = detector.detect_impulses(df2)

    # Impulse detected at index 20 must be present and identical in magnitude in both datasets
    assert 20 in imp1.index
    assert 20 in imp2.index
    assert imp1.loc[20, "impulse_magnitude"] == imp2.loc[20, "impulse_magnitude"]
