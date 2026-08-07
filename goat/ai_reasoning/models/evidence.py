"""
Project GOAT Phase 7 — Evidence Engine Domain Models

Defines immutable Pydantic models for EvidenceRecord and EvidenceBundle ensuring 100% evidence traceability.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class EvidenceType(str, Enum):
    """Classification of quantitative evidence records."""
    STATISTICAL_METRIC = "STATISTICAL_METRIC"
    REGIME_PERFORMANCE = "REGIME_PERFORMANCE"
    WALK_FORWARD_OOS = "WALK_FORWARD_OOS"
    HYPOTHESIS_CONDITION = "HYPOTHESIS_CONDITION"
    DECAY_METRIC = "DECAY_METRIC"


class EvidenceRecord(BaseModel):
    """Immutable single piece of quantitative evidence."""

    record_id: str = Field(..., description="Unique evidence record ID formatted as EVR_<HEX16>", pattern=r"^EVR_[A-Fa-f0-9]{16}$")
    evidence_type: EvidenceType = Field(..., description="Type of quantitative evidence")
    claim: str = Field(..., description="Statement supported by this evidence")
    metric_name: str = Field(..., description="Name of quantitative metric (e.g. sharpe_ratio, p_value)")
    metric_value: float = Field(..., description="Empirical numerical value")
    threshold_value: float = Field(..., description="Validation threshold or target value")
    is_supporting: bool = Field(..., description="True if evidence supports claim, False if refuting")
    canonical_hash: str = Field(..., description="SHA-256 canonical digest")

    class Config:
        frozen = True
        extra = "forbid"


class EvidenceBundle(BaseModel):
    """Immutable container aggregating evidence records for a specific research target."""

    bundle_id: str = Field(..., description="Unique evidence bundle ID formatted as EVB_<HEX16>", pattern=r"^EVB_[A-Fa-f0-9]{16}$")
    target_id: str = Field(..., description="ID of research subject (e.g. edge_id or hypothesis_id)")
    target_type: str = Field(..., description="Subject category (EDGE, HYPOTHESIS, REGIME)")
    records: list[EvidenceRecord] = Field(..., description="List of supporting/refuting evidence records")
    sample_size: int = Field(..., description="Total observation sample size backing evidence")
    overall_confidence: float = Field(..., description="Aggregated evidence confidence score [0.0, 1.0]")
    canonical_hash: str = Field(..., description="SHA-256 canonical digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_evidence_record_id(claim: str, metric_name: str, metric_value: float) -> tuple[str, str]:
    """Compute deterministic record_id and canonical_hash for an EvidenceRecord."""
    payload = {"claim": claim.strip(), "metric_name": metric_name.strip(), "metric_value": round(float(metric_value), 6)}
    digest = compute_canonical_sha256(payload)
    return f"EVR_{digest[:16].upper()}", digest.upper()


def compute_evidence_bundle_id(target_id: str, records: list[EvidenceRecord]) -> tuple[str, str]:
    """Compute deterministic bundle_id and canonical_hash for an EvidenceBundle."""
    rec_hashes = sorted([r.canonical_hash for r in records])
    payload = {"records_hashes": rec_hashes, "target_id": target_id.strip()}
    digest = compute_canonical_sha256(payload)
    return f"EVB_{digest[:16].upper()}", digest.upper()
