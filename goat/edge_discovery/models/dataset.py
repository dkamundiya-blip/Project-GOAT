"""
Project GOAT Phase 6 — Research Dataset Domain Models

Defines immutable Pydantic models for reproducible research datasets and experiment export.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class ResearchDataset(BaseModel):
    """Immutable domain model representing an exported research experiment dataset."""

    dataset_id: str = Field(
        ...,
        description="Unique experiment dataset ID formatted as EXP_<HEX16>",
        pattern=r"^EXP_[A-Fa-f0-9]{16}$",
    )
    experiment_name: str = Field(..., description="Descriptive experiment identifier")
    version: str = Field(default="6.0.0", description="Dataset schema version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    symbols: list[str] = Field(..., description="Instruments included in experiment")
    timeframes: list[str] = Field(..., description="Resolutions included in experiment")
    raw_inputs_count: int = Field(..., description="Number of raw input ticks/bars")
    feature_vectors_count: int = Field(..., description="Number of feature vectors processed")
    edges_count: int = Field(..., description="Number of discovered edges in dataset")
    regime_distribution: dict[str, int] = Field(..., description="Distribution of market state regimes")
    validation_summary: dict[str, Any] = Field(..., description="Summary of validation & significance results")
    checksum: str = Field(..., description="SHA-256 canonical digest of dataset payload")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible experiment metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_dataset_id(
    experiment_name: str,
    symbols: list[str],
    timeframes: list[str],
    feature_vectors_count: int,
    version: str = "6.0.0",
) -> tuple[str, str]:
    """Compute deterministic (dataset_id, canonical_hash) for ResearchDataset.

    Returns:
        Tuple of (EXP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "experiment_name": str(experiment_name).strip(),
        "feature_vectors_count": feature_vectors_count,
        "symbols": sorted(list(set(str(s).strip().upper() for s in symbols))),
        "timeframes": sorted(list(set(str(tf).strip().lower() for tf in timeframes))),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    ds_id = f"EXP_{digest[:16].upper()}"
    return ds_id, digest.upper()
