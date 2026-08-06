"""
Project GOAT v0.7 — Validation Decision Model

Defines the immutable ValidationDecision model (VDC_<HEX16>) representing
the final deterministic scientific validation outcome.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.validation.core.enums import DecisionType


def compute_decision_id(
    validation_run_id: str,
    decision_type: str,
    timestamp: str,
) -> tuple[str, str]:
    """Compute deterministic Validation Decision ID (VDC_<HEX16>) and full SHA-256 hash.

    Args:
        validation_run_id: Parent Validation Run ID (VRN_<HEX16>).
        decision_type: Decision type string.
        timestamp: ISO 8601 UTC timestamp.

    Returns:
        Tuple of (decision_id, decision_hash).
    """
    payload = {
        "decision_type": str(decision_type).strip(),
        "timestamp": str(timestamp).strip(),
        "validation_run_id": str(validation_run_id).strip(),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"VDC_{digest[:16].upper()}"
    return decision_id, digest


class ValidationDecision(BaseModel):
    """Immutable decision representing the final scientific validation outcome."""

    decision_id: str = Field(
        ...,
        description="Unique Decision ID formatted as VDC_<HEX16>",
        pattern=r"^VDC_[A-Fa-f0-9]{16}$",
    )
    decision_hash: str = Field(..., description="Full 64-character SHA-256 canonical decision hash")
    validation_run_id: str = Field(..., description="Parent Validation Run ID (VRN_<HEX16>)")
    decision_type: DecisionType = Field(..., description="Final decision outcome")
    reasoning: str = Field(default="", description="Human-readable decision reasoning")
    evidence_used: list[str] = Field(default_factory=list, description="Evidence IDs used for this decision")
    statistical_summary: dict[str, float] = Field(default_factory=dict, description="Statistical score summary")
    threshold_results: dict[str, Any] = Field(default_factory=dict, description="Threshold evaluation results")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Decision confidence [0.0, 1.0]")
    timestamp: str = Field(..., description="ISO 8601 UTC decision timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Decision metadata")

    class Config:
        frozen = True
        extra = "forbid"
