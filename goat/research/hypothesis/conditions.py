"""
Project GOAT v0.4 — Causal Condition Engine

Evaluates condition primitives at timestamp t using information <= t ONLY.
Defensively rejects DataFrames with FORWARD_NON_CAUSAL metadata or forward outcome columns.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from goat.logging import get_logger
from goat.research.returns import _verify_causal_dataframe

_log = get_logger("hypothesis.conditions")


class CausalConditionEvaluator:
    """Evaluates transparent causal conditions on research DataFrames."""

    def evaluate_condition(
        self,
        df: pd.DataFrame,
        condition_spec: dict[str, Any],
        params: dict[str, Any],
    ) -> pd.Series:
        """Evaluate a causal condition on a DataFrame.

        Args:
            df: Input research DataFrame.
            condition_spec: Dict specifying ``primitive`` and target ``feature``.
            params: Parameters dictionary (e.g. thresholds, percentiles, lookbacks).

        Returns:
            Boolean Series where True indicates the causal condition is met at index t.
        """
        _verify_causal_dataframe(df)

        primitive = condition_spec.get("primitive")
        feature = condition_spec.get("feature")

        if feature not in df.columns:
            # Check if returns need to be dynamically computed
            if feature == "ret_arithmetic" and "close" in df.columns:
                df["ret_arithmetic"] = df["close"].pct_change(fill_method=None)
            elif feature == "ret_abs" and "close" in df.columns:
                df["ret_abs"] = df["close"].pct_change(fill_method=None).abs()
            elif feature == "relative_range" and {"high", "low", "open"}.issubset(df.columns):
                df["relative_range"] = (df["high"] - df["low"]) / df["open"]
            else:
                raise ValueError(f"Required feature column '{feature}' not found in DataFrame")

        series = pd.to_numeric(df[feature], errors="coerce")

        if primitive == "greater_than":
            threshold = params.get("threshold", 0.0)
            mask = series > threshold

        elif primitive == "less_than":
            threshold = params.get("threshold", 0.0)
            mask = series < threshold

        elif primitive == "between":
            lower = params.get("lower", -np.inf)
            upper = params.get("upper", np.inf)
            mask = (series >= lower) & (series <= upper)

        elif primitive == "quantile_membership":
            # Right-aligned trailing rolling quantile
            lookback = params.get("lookback", 50)
            q_lower = params.get("quantile_lower", 0.0)
            q_upper = params.get("quantile_upper", 0.2)

            def _in_q(win: np.ndarray) -> float:
                if len(win) < 2:
                    return 0.0
                q1 = np.percentile(win, q_lower * 100)
                q2 = np.percentile(win, q_upper * 100)
                val = win[-1]
                return 1.0 if (val >= q1 and val <= q2) else 0.0

            rolled = series.rolling(window=lookback, closed="right").apply(_in_q, raw=True)
            mask = rolled == 1.0

        elif primitive == "consecutive_state_count":
            # Count consecutive true values of a base condition
            base_threshold = params.get("base_threshold", 0.0)
            base_operator = params.get("base_operator", "less_than")
            target_count = params.get("consecutive_count", 3)

            base_bool = (series < base_threshold) if base_operator == "less_than" else (series > base_threshold)
            
            # Cumulative count reset on False
            runs = base_bool.groupby((~base_bool).cumsum()).cumsum()
            mask = runs >= target_count

        elif primitive == "regime_membership":
            target_regime = params.get("regime", "HIGH")
            if "volatility_regime" in df.columns:
                mask = df["volatility_regime"] == target_regime
            else:
                # Compute trailing vol regime
                lookback = params.get("lookback", 20)
                std_series = series.rolling(window=lookback, closed="right").std()
                q_low = std_series.quantile(0.33)
                q_high = std_series.quantile(0.67)
                if target_regime == "LOW":
                    mask = std_series <= q_low
                elif target_regime == "HIGH":
                    mask = std_series >= q_high
                else:
                    mask = (std_series > q_low) & (std_series < q_high)

        elif primitive == "std_dev_from_mean":
            lookback = params.get("lookback", 20)
            std_multiplier = params.get("std_multiplier", 2.0)
            mean_series = series.rolling(window=lookback, closed="right").mean()
            std_series = series.rolling(window=lookback, closed="right").std()

            mask = (series - mean_series).abs() >= (std_multiplier * std_series)

        elif primitive == "percentile_rank":
            lookback = params.get("lookback", 50)
            min_rank = params.get("min_rank", 0.8)

            def _pct_rank(win: np.ndarray) -> float:
                if len(win) < 2:
                    return 0.0
                rank = (win < win[-1]).sum() / (len(win) - 1)
                return rank

            rolled_rank = series.rolling(window=lookback, closed="right").apply(_pct_rank, raw=True)
            mask = rolled_rank >= min_rank

        else:
            raise ValueError(f"Unknown condition primitive '{primitive}'")

        return mask.fillna(False)
