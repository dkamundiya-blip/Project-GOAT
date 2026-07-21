"""
Project GOAT v0.3 — Chronological Return Series Engine

Calculates arithmetic, log, and absolute return series.
Enforces strict causality (no look-ahead leakage) and division-by-zero protection.
Defensively rejects input DataFrames containing NON-CAUSAL forward outcomes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from goat.logging import get_logger

_log = get_logger("research.returns")


def _verify_causal_dataframe(df: pd.DataFrame) -> None:
    """Defensive validation: reject DataFrames containing forward-outcome columns or non-causal metadata."""
    if hasattr(df, "attrs") and df.attrs.get("classification") == "FORWARD_NON_CAUSAL":
        raise ValueError(
            "Causal feature functions cannot consume DataFrames classified as FORWARD_NON_CAUSAL"
        )
    for col in df.columns:
        if str(col).startswith("fwd_") or str(col).startswith("forward_"):
            raise ValueError(
                f"Causal feature function rejected input DataFrame containing forward outcome column '{col}'"
            )


def calculate_returns(
    df: pd.DataFrame,
    price_col: str = "close",
) -> pd.DataFrame:
    """Calculate chronological arithmetic, log, and absolute returns.

    Return assigned to row t is computed strictly from P[t-1] and P[t].
    First row t=0 is NaN.

    Args:
        df: DataFrame with price column and timezone-aware timestamp index or column.
        price_col: Column name to use for prices (e.g. ``"close"`` or ``"price"``).

    Returns:
        DataFrame with added columns: ``ret_arithmetic``, ``ret_log``, ``ret_abs``.
    """
    _verify_causal_dataframe(df)

    if price_col not in df.columns:
        if "price" in df.columns:
            price_col = "price"
        else:
            raise ValueError(f"Price column '{price_col}' not found in DataFrame")

    result = df.copy()
    prices = pd.to_numeric(result[price_col], errors="coerce").to_numpy(dtype=np.float64)

    # 1. Arithmetic returns: (P[t] - P[t-1]) / P[t-1]
    prev_prices = np.roll(prices, 1)
    prev_prices[0] = np.nan

    with np.errstate(divide="ignore", invalid="ignore"):
        ret_arithmetic = np.where(
            (prev_prices > 0) & np.isfinite(prev_prices),
            (prices - prev_prices) / prev_prices,
            np.nan,
        )
        ret_arithmetic[0] = np.nan

        # 2. Log returns: ln(P[t] / P[t-1])
        valid_log_mask = (prices > 0) & (prev_prices > 0) & np.isfinite(prices) & np.isfinite(prev_prices)
        ret_log = np.where(valid_log_mask, np.log(prices / prev_prices), np.nan)
        ret_log[0] = np.nan

        # 3. Absolute returns
        ret_abs = np.abs(ret_arithmetic)

    result["ret_arithmetic"] = ret_arithmetic
    result["ret_log"] = ret_log
    result["ret_abs"] = ret_abs

    return result
