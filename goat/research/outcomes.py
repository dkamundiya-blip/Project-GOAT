"""
Project GOAT v0.3 — Forward Outcome Table Generator

Computes fixed-horizon forward returns, Maximum Favorable Excursion (MFE),
Maximum Adverse Excursion (MAE), and future range metrics for RESEARCH ONLY.

CRITICAL HARD BOUNDARY:
----------------------
Forward outcome tables carry explicit non-causal metadata classification
(classification='FORWARD_NON_CAUSAL', is_causal=False) and must NEVER be
joined into causal feature tables or real-time pipelines.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from goat.logging import get_logger

_log = get_logger("research.outcomes")


class ForwardOutcomeTable:
    """Generates non-causal forward outcome tables over configurable horizons."""

    def __init__(self, horizons: list[int] | None = None) -> None:
        self.horizons = horizons or [1, 3, 5, 10, 20]

    def compute_outcomes(
        self,
        df: pd.DataFrame,
        price_col: str = "close",
    ) -> pd.DataFrame:
        """Compute forward return, MFE, and MAE for each observation over horizons.

        Args:
            df: DataFrame containing canonical prices (close, open, high, low).
            price_col: Column name to use for entry price.

        Returns:
            DataFrame containing ONLY non-causal forward outcome columns.
            Annotated with metadata classification='FORWARD_NON_CAUSAL'.
        """
        if price_col not in df.columns:
            if "price" in df.columns:
                price_col = "price"
            else:
                raise ValueError(f"Price column '{price_col}' not found")

        n = len(df)
        outcomes_df = pd.DataFrame(index=df.index)
        if "timestamp" in df.columns:
            outcomes_df["timestamp"] = df["timestamp"]

        prices = pd.to_numeric(df[price_col], errors="coerce").to_numpy(dtype=np.float64)

        has_ohlc = {"high", "low"}.issubset(df.columns)
        highs = pd.to_numeric(df["high"], errors="coerce").to_numpy(dtype=np.float64) if has_ohlc else prices
        lows = pd.to_numeric(df["low"], errors="coerce").to_numpy(dtype=np.float64) if has_ohlc else prices

        for k in self.horizons:
            fwd_ret = np.full(n, np.nan, dtype=np.float64)
            fwd_mfe = np.full(n, np.nan, dtype=np.float64)
            fwd_mae = np.full(n, np.nan, dtype=np.float64)
            fwd_max_range = np.full(n, np.nan, dtype=np.float64)

            for i in range(n - k):
                p0 = prices[i]
                if np.isnan(p0) or p0 <= 0:
                    continue

                # Future price at t + k
                pk = prices[i + k]
                if np.isfinite(pk):
                    fwd_ret[i] = (pk - p0) / p0

                # Window of future prices from t+1 to t+k
                future_h = highs[i + 1 : i + k + 1]
                future_l = lows[i + 1 : i + k + 1]

                if len(future_h) > 0 and len(future_l) > 0:
                    max_h = np.max(future_h)
                    min_l = np.min(future_l)

                    fwd_mfe[i] = max(0.0, (max_h - p0) / p0)
                    fwd_mae[i] = max(0.0, (p0 - min_l) / p0)
                    fwd_max_range[i] = (max_h - min_l) / p0

            outcomes_df[f"fwd_return_{k}"] = fwd_ret
            outcomes_df[f"fwd_mfe_{k}"] = fwd_mfe
            outcomes_df[f"fwd_mae_{k}"] = fwd_mae
            outcomes_df[f"fwd_max_range_{k}"] = fwd_max_range

        # Explicit non-causal metadata classification
        outcomes_df.attrs["classification"] = "FORWARD_NON_CAUSAL"
        outcomes_df.attrs["is_causal"] = False

        _log.info(
            "forward_outcomes_computed",
            records=n,
            horizons=self.horizons,
            classification="FORWARD_NON_CAUSAL",
        )

        return outcomes_df
