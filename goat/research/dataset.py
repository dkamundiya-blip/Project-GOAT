"""
Project GOAT v0.3 — Research Dataset Construction & Manifest

Constructs reproducible research datasets from canonical market observations.
Enforces provenance validation (rejecting TEST data), chronological sorting,
duplicate detection, truncation tracking, and deterministic SHA256 fingerprinting.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from goat.logging import get_logger

_log = get_logger("research.dataset")


class DatasetManifest(BaseModel):
    """Manifest describing a constructed research dataset for full reproducibility."""

    dataset_id: str  # Deterministic SHA256 fingerprint
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    timeframe: str
    requested_start_timestamp: datetime | None = None
    requested_end_timestamp: datetime | None = None
    actual_start_timestamp: datetime
    actual_end_timestamp: datetime
    requested_observation_count: int | None = None
    actual_observation_count: int
    history_truncated: bool = False
    truncation_reason: str | None = None
    provenance_counts: dict[str, int] = Field(default_factory=dict)
    duplicate_count: int = 0
    gap_count: int = 0
    canonical_checksum: str
    construction_version: str = "v0.3.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        """Serialize manifest to JSON string."""
        return self.model_dump_json(indent=2)


class ResearchDatasetBuilder:
    """Builder for canonical research datasets.

    Operates on DataFrames containing market observations (Ticks or Candles).
    Ensures zero TEST provenance enters genuine research datasets.
    """

    def __init__(self, version: str = "v0.3.0") -> None:
        self.version = version

    def build_dataset(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str = "M1",
        requested_start: datetime | None = None,
        requested_end: datetime | None = None,
        requested_count: int | None = None,
        config_str: str = "",
    ) -> tuple[pd.DataFrame, DatasetManifest]:
        """Construct research dataset and generate deterministic manifest.

        Args:
            df: Raw or aggregated canonical observation DataFrame.
            symbol: Instrument identifier (e.g. ``"R_75"``).
            timeframe: Timeframe label (e.g. ``"Tick"``, ``"M1"``, ``"M5"``).
            requested_start: Optional user-requested window start UTC.
            requested_end: Optional user-requested window end UTC.
            requested_count: Optional user-requested observation count.
            config_str: Relevant normalized configuration string for checksum.

        Returns:
            Tuple of (cleaned research DataFrame, DatasetManifest).
        """
        if df.empty:
            raise ValueError(f"Cannot build research dataset from empty DataFrame for {symbol}")

        clean_df = df.copy()

        # 1. Provenance exclusion — REJECT TEST data
        if "source" in clean_df.columns:
            test_mask = clean_df["source"].isin(["test", "TEST", "DataSource.TEST"])
            test_count = int(test_mask.sum())
            if test_count > 0:
                _log.warning(
                    "excluding_test_provenance_from_research",
                    symbol=symbol,
                    excluded_count=test_count,
                )
                clean_df = clean_df[~test_mask].copy()
                if clean_df.empty:
                    raise ValueError(
                        f"Dataset for {symbol} contains only TEST observations; "
                        "research datasets require LIVE or HISTORICAL_IMPORT data."
                    )

        # Record provenance counts
        provenance_counts: dict[str, int] = {}
        if "source" in clean_df.columns:
            provenance_counts = clean_df["source"].value_counts().to_dict()

        # 2. Chronological sorting
        clean_df["timestamp"] = pd.to_datetime(clean_df["timestamp"], utc=True)
        clean_df = clean_df.sort_values("timestamp").reset_index(drop=True)

        # 3. Duplicate detection
        dup_mask = clean_df.duplicated(subset=["symbol", "timestamp"], keep="first")
        duplicate_count = int(dup_mask.sum())
        if duplicate_count > 0:
            clean_df = clean_df[~dup_mask].reset_index(drop=True)

        # 4. Actual timestamps
        actual_start = clean_df["timestamp"].iloc[0].to_pydatetime()
        actual_end = clean_df["timestamp"].iloc[-1].to_pydatetime()
        actual_count = len(clean_df)

        # 5. Check historical truncation
        history_truncated = False
        truncation_reason: str | None = None

        if requested_start and actual_start > requested_start:
            history_truncated = True
            truncation_reason = (
                f"Requested start {requested_start.isoformat()} unavailable; "
                f"earliest record is {actual_start.isoformat()}"
            )
        elif requested_count and actual_count < requested_count:
            history_truncated = True
            truncation_reason = (
                f"Requested {requested_count} records; provider supplied {actual_count}"
            )

        # 6. SHA256 Checksums
        price_col = "price" if "price" in clean_df.columns else "close"
        price_bytes = clean_df[price_col].to_numpy().tobytes()
        canonical_checksum = hashlib.sha256(price_bytes).hexdigest()

        # Deterministic Dataset Fingerprint ID
        fp_input = f"{symbol}:{timeframe}:{actual_start.isoformat()}:{actual_end.isoformat()}:{canonical_checksum}:{self.version}:{config_str}"
        dataset_id = hashlib.sha256(fp_input.encode("utf-8")).hexdigest()

        manifest = DatasetManifest(
            dataset_id=dataset_id,
            symbol=symbol,
            timeframe=timeframe,
            requested_start_timestamp=requested_start,
            requested_end_timestamp=requested_end,
            actual_start_timestamp=actual_start,
            actual_end_timestamp=actual_end,
            requested_observation_count=requested_count,
            actual_observation_count=actual_count,
            history_truncated=history_truncated,
            truncation_reason=truncation_reason,
            provenance_counts={str(k): int(v) for k, v in provenance_counts.items()},
            duplicate_count=duplicate_count,
            canonical_checksum=canonical_checksum,
            construction_version=self.version,
        )

        _log.info(
            "research_dataset_built",
            symbol=symbol,
            dataset_id=dataset_id,
            count=actual_count,
            truncated=history_truncated,
        )

        return clean_df, manifest
