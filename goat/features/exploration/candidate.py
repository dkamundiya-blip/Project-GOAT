"""
Project GOAT v0.7 — Candidate Feature Model

Defines the immutable CandidateFeature model representing generated feature hypotheses during exploration,
with deterministic CAND_<HEX16> identity calculation and decision provenance linkage.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.features.core.base import BaseFeature
from goat.research.edge.canonical import compute_canonical_sha256


def compute_candidate_id(feature_id: str, scientific_fingerprint: str, depth: int = 0) -> str:
    """Compute deterministic Candidate Feature ID (CAND_<HEX16>).

    Args:
        feature_id: Feature ID (FEAT_<HEX16>).
        scientific_fingerprint: Scientific Feature Fingerprint (FPT_<HEX64>).
        depth: Generation depth integer.

    Returns:
        String formatted as 'CAND_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "depth": int(depth),
        "feature_id": str(feature_id).strip(),
        "scientific_fingerprint": str(scientific_fingerprint).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"CAND_{digest[:16].upper()}"


class CandidateFeature(BaseModel):
    """Immutable scientific object representing a generated feature candidate hypothesis."""

    candidate_id: str = Field(
        ...,
        description="Unique Candidate Feature ID formatted as CAND_<HEX16>",
        pattern=r"^CAND_[A-Fa-f0-9]{16}$",
    )
    feature_id: str = Field(..., description="Target Feature ID (FEAT_<HEX16>)")
    scientific_fingerprint: str = Field(..., description="Scientific Feature Fingerprint (FPT_<HEX64>)")
    parent_feature_ids: list[str] = Field(default_factory=list, description="Upstream parent Feature IDs")
    transformation_id: str = Field(default="", description="Applied transformation operator ID (TRNS_<HEX16>)")
    decision_id: str = Field(default="", description="Referenced Exploration Decision ID (DEC_<HEX16>)")
    generation_depth: int = Field(default=0, ge=0, description="Generation depth from root primitives")
    generation_timestamp: str = Field(..., description="ISO 8601 UTC generation timestamp")
    generation_version: str = Field(default="1.0.0", description="Candidate specification version")
    mathematical_definition: str = Field(..., description="LaTeX or formal mathematical definition")
    scientific_notes: str = Field(default="", description="Scientific lineage and exploration notes")
    lineage_hash: str = Field(..., description="Full 64-character SHA-256 canonical lineage hash digest")

    # Private feature instance field excluded from Pydantic validation/json
    feature_instance: Any = Field(default=None, exclude=True)

    class Config:
        frozen = True
        extra = "forbid"
