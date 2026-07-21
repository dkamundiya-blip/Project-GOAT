"""
Project GOAT v0.3 — Dataset Sufficiency Evaluator

Evaluates whether a dataset has sufficient sample size and temporal coverage
to produce statistically reliable research fingerprint conclusions.
Prefers INSUFFICIENT_DATA status over producing unstable or misleading conclusions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from goat.logging import get_logger

_log = get_logger("research.sufficiency")


class DatasetSufficiencyReport(BaseModel):
    """Structured report on dataset sufficiency for quantitative research."""

    symbol: str
    timeframe: str
    observation_count: int
    temporal_coverage_hours: float
    gap_count: int = 0
    impulse_count: int = 0
    is_sufficient: bool = True
    status: str = "SUFFICIENT"
    warnings: list[str] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


def evaluate_dataset_sufficiency(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str = "M1",
    min_observations: int = 500,
    min_autocorr_observations: int = 1000,
    min_impulses: int = 20,
    gap_threshold_count: int = 10,
) -> DatasetSufficiencyReport:
    """Evaluate dataset sufficiency against configurable methodological default thresholds.

    Args:
        df: Input research DataFrame.
        symbol: Instrument identifier.
        timeframe: Timeframe label.
        min_observations: Minimum total observations required.
        min_autocorr_observations: Minimum observations for reliable autocorrelation.
        min_impulses: Minimum detected impulses for impulse stats.
        gap_threshold_count: Max tolerated missing data gaps.

    Returns:
        ``DatasetSufficiencyReport`` instance.
    """
    warnings: list[str] = []
    n = len(df)

    if n == 0:
        return DatasetSufficiencyReport(
            symbol=symbol,
            timeframe=timeframe,
            observation_count=0,
            temporal_coverage_hours=0.0,
            is_sufficient=False,
            status="INSUFFICIENT_DATA",
            warnings=["Dataset is completely empty."],
        )

    # 1. Observation count check
    if n < min_observations:
        warnings.append(
            f"Observation count ({n}) is below methodological threshold ({min_observations})."
        )
    if n < min_autocorr_observations:
        warnings.append(
            f"Observation count ({n}) is below recommended autocorrelation threshold ({min_autocorr_observations})."
        )

    # 2. Temporal coverage
    coverage_hours = 0.0
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], utc=True)
        if len(ts) > 1:
            coverage_hours = float((ts.iloc[-1] - ts.iloc[0]).total_seconds() / 3600.0)

    if coverage_hours < 1.0:
        warnings.append(f"Temporal coverage ({coverage_hours:.2f} hours) is under 1 hour.")

    # 3. Impulses
    impulse_count = 0
    if "is_impulse" in df.columns:
        impulse_count = int(df["is_impulse"].sum())
        if impulse_count < min_impulses:
            warnings.append(
                f"Impulse count ({impulse_count}) is below minimum threshold ({min_impulses})."
            )

    is_sufficient = len(warnings) == 0
    status = "SUFFICIENT" if is_sufficient else "INSUFFICIENT_DATA"

    _log.info(
        "dataset_sufficiency_evaluated",
        symbol=symbol,
        timeframe=timeframe,
        status=status,
        warnings_count=len(warnings),
    )

    return DatasetSufficiencyReport(
        symbol=symbol,
        timeframe=timeframe,
        observation_count=n,
        temporal_coverage_hours=round(coverage_hours, 2),
        impulse_count=impulse_count,
        is_sufficient=is_sufficient,
        status=status,
        warnings=warnings,
    )
