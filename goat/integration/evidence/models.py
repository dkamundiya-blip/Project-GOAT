"""
Project GOAT v0.7 — Evidence Merging Models

Defines immutable EvidenceMergeRecord model (EMG_<HEX16>).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class EvidenceMergeRecord(BaseModel):
    """Immutable record of deterministic evidence aggregation."""

    merge_id: str = Field(
        ...,
        description="Unique evidence merge record ID formatted as EMG_<HEX16>",
        pattern=r"^EMG_[A-Fa-f0-9]{16}$",
    )
    source_evidence_ids: list[str] = Field(default_factory=list, description="IDs of component evidence artifacts")
    target_knowledge_id: str = Field(..., description="Target Integrated Knowledge ID (IKN_<HEX16>)")
    accumulated_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Aggregated confidence rating")
    accumulated_reproducibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Aggregated reproducibility score")
    accumulated_consensus: float = Field(default=0.0, ge=0.0, le=1.0, description="Aggregated consensus rating")
    experiment_refs: list[str] = Field(default_factory=list, description="Accumulated experiment IDs")
    study_refs: list[str] = Field(default_factory=list, description="Accumulated study IDs")
    execution_refs: list[str] = Field(default_factory=list, description="Accumulated execution/run IDs")
    feature_refs: list[str] = Field(default_factory=list, description="Accumulated feature IDs/names")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
