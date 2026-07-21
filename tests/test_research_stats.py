"""
Project GOAT v0.3 — Unit Tests for Statistical Fingerprinting
"""

import numpy as np
import pandas as pd

from goat.research.stats import (
    calculate_distribution_stats,
    calculate_range_stats,
    calculate_run_lengths,
    calculate_serial_dependence,
)


def test_calculate_distribution_stats() -> None:
    """Test distribution statistics calculation."""
    arr = np.array([0.01, -0.02, 0.03, 0.01, -0.01, 0.02, -0.03, 0.01])
    stats = calculate_distribution_stats(arr)

    assert stats["count"] == 8.0
    assert "mean" in stats
    assert "std" in stats
    assert "skewness" in stats
    assert "kurtosis" in stats
    assert "q50" in stats


def test_calculate_serial_dependence() -> None:
    """Test autocorrelation calculation across lags."""
    arr = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1], dtype=float)
    deps = calculate_serial_dependence(arr, lags=[1, 2])

    assert "autocorr_lag_1" in deps
    # Strong negative autocorrelation at lag 1 for alternating series
    assert deps["autocorr_lag_1"] < 0.0
    # Positive autocorrelation at lag 2
    assert deps["autocorr_lag_2"] > 0.0


def test_calculate_run_lengths() -> None:
    """Test positive and negative run-length analysis and zero return handling."""
    # Sequence: 3 positive, 1 zero (breaks run), 2 negative
    arr = np.array([0.01, 0.02, 0.01, 0.0, -0.01, -0.02], dtype=float)
    runs = calculate_run_lengths(arr)

    assert runs["positive_run_count"] == 1.0
    assert runs["positive_run_max"] == 3.0
    assert runs["negative_run_count"] == 1.0
    assert runs["negative_run_max"] == 2.0
