"""
Project GOAT Phase 4 — Data Quality Domain Models & Issue Categories

Defines quality rejection reasons, check results, and immutable DataQualityReport models.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class QualityIssueReason(str, Enum):
    """Specific data quality defect categories evaluated by DataQualityEngine."""

    DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
    OUT_OF_ORDER_TICK = "OUT_OF_ORDER_TICK"
    IMPOSSIBLE_PRICE = "IMPOSSIBLE_PRICE"
    NEGATIVE_SPREAD = "NEGATIVE_SPREAD"
    MISSING_CANDLE = "MISSING_CANDLE"
    TIME_GAP = "TIME_GAP"
    CORRUPTED_PAYLOAD = "CORRUPTED_PAYLOAD"
    LATENCY_ANOMALY = "LATENCY_ANOMALY"


class QualityIssue(BaseModel):
    """Immutable record of an identified data quality defect."""

    reason: QualityIssueReason = Field(..., description="Category of quality violation")
    description: str = Field(..., description="Human-readable explanation of defect")
    details: dict[str, Any] = Field(default_factory=dict, description="Raw context or offending payload values")

    class Config:
        frozen = True
        extra = "forbid"


class DataQualityCheckResult(BaseModel):
    """Result emitted by DataQualityEngine for single tick/candle evaluation."""

    passed: bool = Field(..., description="True if payload satisfies all quality rules")
    symbol: str = Field(..., description="Target market symbol")
    timestamp: str = Field(..., description="Evaluation timestamp")
    issues: list[QualityIssue] = Field(default_factory=list, description="List of identified issues if passed is False")

    class Config:
        frozen = True
        extra = "forbid"


class DataQualityReport(BaseModel):
    """Immutable domain model representing an aggregate operational data quality audit report."""

    report_id: str = Field(
        ...,
        description="Unique data quality report ID formatted as DQR_<HEX16>",
        pattern=r"^DQR_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of report generation")
    total_ticks_checked: int = Field(..., ge=0, description="Total tick count evaluated")
    valid_ticks_count: int = Field(..., ge=0, description="Count of valid accepted ticks")
    rejected_ticks_count: int = Field(..., ge=0, description="Count of rejected invalid ticks")
    pass_rate: float = Field(..., ge=0.0, le=1.0, description="Percentage of valid ticks [0.0, 1.0]")
    issues_breakdown: dict[str, int] = Field(default_factory=dict, description="Count per QualityIssueReason")
    checksum: str = Field(..., description="SHA-256 canonical digest of report core fields")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_data_quality_report_id(
    symbol: str,
    timestamp: str,
    total_ticks_checked: int,
    rejected_ticks_count: int,
    pass_rate: float,
) -> tuple[str, str]:
    """Compute deterministic (report_id, canonical_hash) for DataQualityReport.

    Returns:
        Tuple of (DQR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "pass_rate": round(float(pass_rate), 4),
        "rejected_ticks_count": int(rejected_ticks_count),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "total_ticks_checked": int(total_ticks_checked),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"DQR_{digest[:16].upper()}"
    return report_id, digest.upper()
