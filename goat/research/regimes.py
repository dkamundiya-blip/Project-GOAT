"""
Project GOAT v0.3 — Trailing Volatility Regime Classifier

Classifies market regimes (Low, Normal, High Volatility) using explicit fit/apply semantics.
Fills parameter thresholds on TRAIN data and applies frozen parameters to VALIDATION
and HOLDOUT partitions without look-ahead leakage.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from goat.logging import get_logger
from goat.research.returns import _verify_causal_dataframe

_log = get_logger("research.regimes")


class RegimeClassifier:
    """Volatility regime classifier with fit/apply separation.

    Args:
        lookback_window: Window size for trailing rolling volatility (default 20).
        low_quantile: Quantile boundary for Low Volatility regime (default 0.33).
        high_quantile: Quantile boundary for High Volatility regime (default 0.67).
    """

    def __init__(
        self,
        lookback_window: int = 20,
        low_quantile: float = 0.33,
        high_quantile: float = 0.67,
    ) -> None:
        self.lookback_window = lookback_window
        self.low_quantile = low_quantile
        self.high_quantile = high_quantile

        self.is_fitted: bool = False
        self.low_threshold: float | None = None
        self.high_threshold: float | None = None

    def fit(self, train_df: pd.DataFrame, price_col: str = "close") -> RegimeClassifier:
        """Fit volatility regime threshold parameters on TRAIN partition ONLY.

        Args:
            train_df: Training partition DataFrame.
            price_col: Price column name.

        Returns:
            Fitted self.
        """
        _verify_causal_dataframe(train_df)

        if price_col not in train_df.columns:
            if "price" in train_df.columns:
                price_col = "price"
            else:
                raise ValueError(f"Price column '{price_col}' not found")

        prices = pd.to_numeric(train_df[price_col], errors="coerce")
        returns = prices.pct_change(fill_method=None)
        trailing_std = returns.rolling(window=self.lookback_window, closed="right").std().dropna()

        if trailing_std.empty:
            self.low_threshold = 0.001
            self.high_threshold = 0.005
        else:
            self.low_threshold = float(np.percentile(trailing_std, self.low_quantile * 100))
            self.high_threshold = float(np.percentile(trailing_std, self.high_quantile * 100))

        self.is_fitted = True
        _log.info(
            "regime_classifier_fitted_on_train",
            train_records=len(train_df),
            low_threshold=self.low_threshold,
            high_threshold=self.high_threshold,
        )
        return self

    def apply(self, df: pd.DataFrame, price_col: str = "close") -> pd.DataFrame:
        """Apply frozen fitted threshold parameters to target DataFrame (VALIDATION or HOLDOUT).

        Args:
            df: Target partition DataFrame.
            price_col: Price column name.

        Returns:
            DataFrame with added ``volatility_regime`` column ('LOW', 'NORMAL', 'HIGH').
        """
        _verify_causal_dataframe(df)

        if not self.is_fitted or self.low_threshold is None or self.high_threshold is None:
            raise RuntimeError("RegimeClassifier must be fitted on TRAIN partition before calling apply()")

        if price_col not in df.columns:
            if "price" in df.columns:
                price_col = "price"
            else:
                raise ValueError(f"Price column '{price_col}' not found")

        result = df.copy()
        prices = pd.to_numeric(result[price_col], errors="coerce")
        returns = prices.pct_change(fill_method=None)
        trailing_std = returns.rolling(window=self.lookback_window, closed="right").std()

        regimes = np.full(len(df), "NORMAL", dtype=object)

        low_mask = trailing_std <= self.low_threshold
        high_mask = trailing_std >= self.high_threshold

        regimes[low_mask] = "LOW"
        regimes[high_mask] = "HIGH"

        result["volatility_regime"] = regimes
        result["trailing_volatility"] = trailing_std

        return result
