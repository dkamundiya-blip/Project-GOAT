"""
Project GOAT v0.6 — Temporal Leakage Guard

Validates timestamp alignment, partition boundaries, and forward-outcome horizon embargoes
to prevent future information leakage in validation evaluation.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd

from goat.research.edge.validation.exceptions import TemporalLeakageError


class TemporalLeakageGuard:
    """Guard enforcing strict chronological ordering and embargo boundary discipline."""

    @staticmethod
    def verify_chronological_ordering(timestamps: pd.Series | Sequence[Any]) -> None:
        """Verify timestamps are strictly non-decreasing (monotonic)."""
        ts_series = pd.to_datetime(pd.Series(timestamps)).dropna()
        if len(ts_series) < 2:
            return
        if not ts_series.is_monotonic_increasing:
            raise TemporalLeakageError("Timestamps are not strictly chronologically ordered (contains backward jumps)")

    @staticmethod
    def verify_partition_boundaries(
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        timestamp_col: str = "timestamp",
    ) -> None:
        """Verify training partition strictly precedes validation partition in time."""
        if train_df.empty or val_df.empty:
            return

        if timestamp_col not in train_df.columns or timestamp_col not in val_df.columns:
            # Fall back to index if DatetimeIndex
            if isinstance(train_df.index, pd.DatetimeIndex) and isinstance(val_df.index, pd.DatetimeIndex):
                max_train = train_df.index.max()
                min_val = val_df.index.min()
            else:
                return
        else:
            max_train = pd.to_datetime(train_df[timestamp_col]).max()
            min_val = pd.to_datetime(val_df[timestamp_col]).min()

        if max_train >= min_val:
            raise TemporalLeakageError(
                f"Temporal leakage detected: max train timestamp ({max_train}) >= min validation timestamp ({min_val})"
            )

    @staticmethod
    def verify_fold_embargo(
        fold_train_end_idx: int,
        fold_test_start_idx: int,
        horizon_bars: int,
    ) -> None:
        """Verify walk-forward fold gap satisfies minimum embargo horizon bars."""
        gap = fold_test_start_idx - fold_train_end_idx
        if gap < horizon_bars:
            raise TemporalLeakageError(
                f"Fold embargo boundary violation: gap between train end ({fold_train_end_idx}) "
                f"and test start ({fold_test_start_idx}) is {gap} bars, required embargo horizon is {horizon_bars} bars"
            )
