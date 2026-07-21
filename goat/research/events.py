"""
Project GOAT v0.3 — Impulse & Pullback Event Characterization

Provides objective, parameterized mathematical definitions for price impulses
and retrospective pullback/retracement behavior for descriptive research only.
Thresholds are research parameters — NOT trading parameters or profitability optimizations.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from goat.logging import get_logger
from goat.research.returns import _verify_causal_dataframe

_log = get_logger("research.events")


class ImpulseCharacterization:
    """Detects and characterizes price impulse events using trailing volatility.

    Args:
        std_threshold: Number of trailing standard deviations defining an impulse (default 2.0).
        lookback_window: Window size for trailing standard deviation calculation (default 20).
    """

    def __init__(
        self,
        std_threshold: float = 2.0,
        lookback_window: int = 20,
    ) -> None:
        self.std_threshold = std_threshold
        self.lookback_window = lookback_window

    def detect_impulses(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
    ) -> pd.DataFrame:
        """Identify impulse observations using right-aligned trailing standard deviation.

        Args:
            df: DataFrame containing price and returns.

        Returns:
            DataFrame containing detected impulse metadata rows.
        """
        _verify_causal_dataframe(df)

        if price_col not in df.columns:
            if "price" in df.columns:
                price_col = "price"
            else:
                raise ValueError(f"Price column '{price_col}' not found")

        data = df.copy()
        prices = pd.to_numeric(data[price_col], errors="coerce")

        # Causal trailing return and trailing volatility (right-aligned)
        returns = prices.pct_change(fill_method=None)
        trailing_std = returns.rolling(window=self.lookback_window, closed="right").std()

        # Impulse condition: abs(return) >= std_threshold * trailing_std
        with np.errstate(divide="ignore", invalid="ignore"):
            is_impulse = (returns.abs() >= (self.std_threshold * trailing_std)) & (trailing_std > 0)

        data["is_impulse"] = is_impulse.fillna(False)
        data["impulse_direction"] = np.sign(returns.fillna(0))
        data["impulse_magnitude"] = returns.abs()
        data["normalized_magnitude"] = returns.abs() / trailing_std

        impulses = data[data["is_impulse"]].copy()

        _log.info(
            "impulses_detected",
            total_observations=len(df),
            impulses_found=len(impulses),
            std_threshold=self.std_threshold,
        )

        return impulses


class PullbackCharacterization:
    """Measures retrospective retracement behavior following detected impulse events.

    .. important::
        Retrospective pullback measurements are assigned to forward horizons for research analysis.
        They must NEVER be used as causal features at timestamp t.
    """

    def __init__(self, forward_horizon: int = 10) -> None:
        self.forward_horizon = forward_horizon

    def analyze_pullbacks(
        self,
        df: pd.DataFrame,
        impulses_df: pd.DataFrame,
        price_col: str = "close",
    ) -> pd.DataFrame:
        """Measure retracement magnitude and horizon duration following impulse events.

        Args:
            df: Full sequential price DataFrame.
            impulses_df: Subset DataFrame of detected impulses.
            price_col: Column name for price.

        Returns:
            DataFrame of impulse-pullback event summaries.
        """
        if impulses_df.empty or df.empty:
            return pd.DataFrame()

        prices = pd.to_numeric(df[price_col], errors="coerce").to_numpy()
        results: list[dict[str, Any]] = []

        for idx, row in impulses_df.iterrows():
            pos = df.index.get_loc(idx) if idx in df.index else None
            if pos is None or pos + self.forward_horizon >= len(prices):
                continue

            start_price = prices[pos]
            direction = row.get("impulse_direction", 1)

            future_prices = prices[pos + 1 : pos + 1 + self.forward_horizon]
            if len(future_prices) == 0:
                continue

            if direction > 0:
                # Bullish impulse: pullback is price decrease below start_price
                max_adverse_price = np.min(future_prices)
                retracement = max(0.0, (start_price - max_adverse_price) / start_price)
                max_favorable_price = np.max(future_prices)
                continuation = max(0.0, (max_favorable_price - start_price) / start_price)
            else:
                # Bearish impulse: pullback is price increase above start_price
                max_adverse_price = np.max(future_prices)
                retracement = max(0.0, (max_adverse_price - start_price) / start_price)
                max_favorable_price = np.min(future_prices)
                continuation = max(0.0, (start_price - max_favorable_price) / start_price)

            imp_mag = row.get("impulse_magnitude", 0.001)
            retracement_fraction = retracement / imp_mag if imp_mag > 0 else 0.0

            results.append({
                "timestamp": row.get("timestamp", df.iloc[pos].get("timestamp")),
                "impulse_direction": direction,
                "impulse_magnitude": float(imp_mag),
                "retracement_magnitude": float(retracement),
                "retracement_fraction": float(retracement_fraction),
                "continuation_magnitude": float(continuation),
                "horizon_bars": self.forward_horizon,
            })

        return pd.DataFrame(results)
