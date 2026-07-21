"""
Project GOAT v0.3 — Statistical Fingerprinting Engine

Calculates non-forward-looking descriptive statistics:
- Return distributions (mean, std, skewness, kurtosis, quantiles, MAE, MedAE)
- Rolling volatility and candle range distributions
- Serial dependence (autocorrelation at lags 1..10)
- Directional run-length distributions
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from goat.logging import get_logger
from goat.research.returns import _verify_causal_dataframe

_log = get_logger("research.stats")


def calculate_distribution_stats(series: pd.Series | np.ndarray) -> dict[str, float]:
    """Compute distribution statistics for a numeric return or price series.

    Returns:
        Dict containing count, mean, median, std, var, min, max, skew, kurtosis,
        quantiles (1%, 5%, 25%, 50%, 75%, 95%, 99%), MAE, MedAE.
    """
    arr = np.asarray(series, dtype=np.float64)
    clean = arr[np.isfinite(arr)]

    if len(clean) == 0:
        return {
            "count": 0.0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "variance": 0.0,
            "min": 0.0,
            "max": 0.0,
            "skewness": 0.0,
            "kurtosis": 0.0,
            "q01": 0.0,
            "q05": 0.0,
            "q25": 0.0,
            "q50": 0.0,
            "q75": 0.0,
            "q95": 0.0,
            "q99": 0.0,
            "mae": 0.0,
            "medae": 0.0,
        }

    mean_val = float(np.mean(clean))
    median_val = float(np.median(clean))
    std_val = float(np.std(clean, ddof=1)) if len(clean) > 1 else 0.0
    var_val = std_val ** 2

    # Skewness and Excess Kurtosis using sample statistics
    n = len(clean)
    if n > 2 and std_val > 0:
        m3 = np.sum((clean - mean_val) ** 3) / n
        skew_val = float(m3 / (std_val ** 3))
    else:
        skew_val = 0.0

    if n > 3 and std_val > 0:
        m4 = np.sum((clean - mean_val) ** 4) / n
        kurt_val = float((m4 / (std_val ** 4)) - 3.0)  # Excess kurtosis
    else:
        kurt_val = 0.0

    quantiles = np.percentile(clean, [1, 5, 25, 50, 75, 95, 99])

    mae_val = float(np.mean(np.abs(clean - mean_val)))
    medae_val = float(np.median(np.abs(clean - median_val)))

    return {
        "count": float(n),
        "mean": round(mean_val, 8),
        "median": round(median_val, 8),
        "std": round(std_val, 8),
        "variance": round(var_val, 8),
        "min": round(float(np.min(clean)), 8),
        "max": round(float(np.max(clean)), 8),
        "skewness": round(skew_val, 6),
        "kurtosis": round(kurt_val, 6),
        "q01": round(float(quantiles[0]), 8),
        "q05": round(float(quantiles[1]), 8),
        "q25": round(float(quantiles[2]), 8),
        "q50": round(float(quantiles[3]), 8),
        "q75": round(float(quantiles[4]), 8),
        "q95": round(float(quantiles[5]), 8),
        "q99": round(float(quantiles[6]), 8),
        "mae": round(mae_val, 8),
        "medae": round(medae_val, 8),
    }


def calculate_serial_dependence(
    series: pd.Series | np.ndarray,
    lags: list[int] | None = None,
) -> dict[str, float]:
    """Calculate sample autocorrelation for return series at specified lags.

    Args:
        series: Return series.
        lags: List of lag integers (default ``[1, 2, 3, 5, 10]``).

    Returns:
        Dict mapping lag keys (e.g. ``"autocorr_lag_1"``) to correlation floats.
    """
    if lags is None:
        lags = [1, 2, 3, 5, 10]

    s = pd.Series(series, dtype=np.float64).dropna()
    results: dict[str, float] = {}

    for lag in lags:
        if len(s) > lag + 2:
            corr = float(s.autocorr(lag=lag))
            results[f"autocorr_lag_{lag}"] = 0.0 if np.isnan(corr) else round(corr, 6)
        else:
            results[f"autocorr_lag_{lag}"] = 0.0

    return results


def calculate_run_lengths(series: pd.Series | np.ndarray) -> dict[str, Any]:
    """Analyze consecutive directional movement (positive and negative run lengths).

    Zero returns explicitly break positive and negative runs.

    Returns:
        Dict containing positive/negative mean, median, max run lengths and counts.
    """
    arr = np.asarray(series, dtype=np.float64)
    clean = arr[np.isfinite(arr)]

    pos_runs: list[int] = []
    neg_runs: list[int] = []

    current_pos = 0
    current_neg = 0

    for val in clean:
        if val > 0:
            current_pos += 1
            if current_neg > 0:
                neg_runs.append(current_neg)
                current_neg = 0
        elif val < 0:
            current_neg += 1
            if current_pos > 0:
                pos_runs.append(current_pos)
                current_pos = 0
        else:
            # Zero return breaks both runs
            if current_pos > 0:
                pos_runs.append(current_pos)
                current_pos = 0
            if current_neg > 0:
                neg_runs.append(current_neg)
                current_neg = 0

    if current_pos > 0:
        pos_runs.append(current_pos)
    if current_neg > 0:
        neg_runs.append(current_neg)

    def _run_stats(runs: list[int], prefix: str) -> dict[str, float]:
        if not runs:
            return {
                f"{prefix}_run_count": 0.0,
                f"{prefix}_run_mean": 0.0,
                f"{prefix}_run_median": 0.0,
                f"{prefix}_run_max": 0.0,
            }
        return {
            f"{prefix}_run_count": float(len(runs)),
            f"{prefix}_run_mean": round(float(np.mean(runs)), 4),
            f"{prefix}_run_median": float(np.median(runs)),
            f"{prefix}_run_max": float(np.max(runs)),
        }

    res = {}
    res.update(_run_stats(pos_runs, "positive"))
    res.update(_run_stats(neg_runs, "negative"))
    return res


def calculate_range_stats(df: pd.DataFrame) -> dict[str, float]:
    """Calculate relative candle range metrics: (high - low) / open."""
    _verify_causal_dataframe(df)

    if not {"open", "high", "low"}.issubset(df.columns):
        return {"mean_relative_range": 0.0, "median_relative_range": 0.0}

    o = pd.to_numeric(df["open"], errors="coerce")
    h = pd.to_numeric(df["high"], errors="coerce")
    l = pd.to_numeric(df["low"], errors="coerce")

    with np.errstate(divide="ignore", invalid="ignore"):
        rel_range = (h - l) / o

    rel_range = rel_range.dropna()
    rel_range = rel_range[np.isfinite(rel_range)]

    if rel_range.empty:
        return {"mean_relative_range": 0.0, "median_relative_range": 0.0}

    return {
        "mean_relative_range": round(float(rel_range.mean()), 8),
        "median_relative_range": round(float(rel_range.median()), 8),
        "max_relative_range": round(float(rel_range.max()), 8),
        "min_relative_range": round(float(rel_range.min()), 8),
    }
