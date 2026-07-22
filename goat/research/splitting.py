"""
Project GOAT v0.3 — Chronological Time-Series Splitter

Splits research datasets into Train, Validation, and Holdout partitions chronologically.
Enforces zero random shuffling and sealed holdout partition discipline.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from goat.config import GoatSettings
from goat.logging import get_logger
from goat.research.returns import _verify_causal_dataframe

_log = get_logger("research.splitting")


class ChronologicalSplitter:
    """Chronological time-series partition splitter.

    Args:
        train_ratio: Fraction of dataset allocated to TRAIN (default 0.60).
        val_ratio: Fraction of dataset allocated to VALIDATION (default 0.20).
        holdout_ratio: Fraction of dataset allocated to HOLDOUT (default 0.20).
    """

    def __init__(
        self,
        train_ratio: float = 0.60,
        val_ratio: float = 0.20,
        holdout_ratio: float = 0.20,
    ) -> None:
        if not np.isclose(train_ratio + val_ratio + holdout_ratio, 1.0):
            raise ValueError("Partition ratios (train, val, holdout) must sum to 1.0")

        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.holdout_ratio = holdout_ratio

    def split(
        self,
        df: pd.DataFrame,
        allow_holdout: bool = False,
    ) -> dict[str, pd.DataFrame]:
        """Split DataFrame into chronological train, validation, and holdout partitions.

        Args:
            df: Input research DataFrame (must be chronologically sorted).
            allow_holdout: If False, holdout partition is sealed and returns empty DataFrame.

        Returns:
            Dict containing ``"train"``, ``"validation"``, and ``"holdout"`` DataFrames.
        """
        if df.empty:
            return {"train": df, "validation": df, "holdout": df}

        n = len(df)
        train_end = int(n * self.train_ratio)
        val_end = train_end + int(n * self.val_ratio)

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        holdout_df = df.iloc[val_end:].copy()

        train_df.attrs = df.attrs.copy()
        val_df.attrs = df.attrs.copy()
        holdout_df.attrs = df.attrs.copy()

        _log.info(
            "chronological_split_completed",
            total_records=n,
            train_records=len(train_df),
            val_records=len(val_df),
            holdout_records=len(holdout_df),
            allow_holdout=allow_holdout,
        )

        if not allow_holdout:
            _log.info("holdout_partition_sealed_by_default")
            # Sealed holdout returns empty DataFrame to prevent exploratory overfitting
            holdout_df = pd.DataFrame(columns=df.columns)

        return {
            "train": train_df,
            "validation": val_df,
            "holdout": holdout_df,
        }


import numpy as np
