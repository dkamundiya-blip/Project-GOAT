"""
Project GOAT v0.7 — Evidence Reference Model

Defines the immutable EvidenceReference model representing supporting evidence references (EVD_<HEX16>)
linking scientific knowledge objects back to feature, decision, and validation artifacts.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from goat.knowledge.enums import EvidenceType
from goat.research.edge.canonical import compute_canonical_sha256


def compute_evidence_id(evidence_type: str, source_id: str, source_uri: str = "") -> str:
    """Compute deterministic Evidence Reference ID (EVD_<HEX16>).

    Args:
        evidence_type: EvidenceType enum string value.
        source_id: Upstream target artifact ID.
        source_uri: Optional source URI or file path.

    Returns:
        String formatted as 'EVD_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "evidence_type": str(evidence_type).strip().lower(),
        "source_id": str(source_id).strip(),
        "source_uri": str(source_uri).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EVD_{digest[:16].upper()}"


class EvidenceReference(BaseModel):
    """Immutable representation of a supporting evidence reference."""

    evidence_id: str = Field(
        ...,
        description="Unique Evidence ID formatted as EVD_<HEX16>",
        pattern=r"^EVD_[A-Fa-f0-9]{16}$",
    )
    evidence_type: EvidenceType = Field(..., description="Evidence source type classification")
    source_id: str = Field(..., description="Upstream artifact target ID (e.g. FEAT_, CAND_, DEC_, VAL_)")
    source_uri: str = Field(default="", description="Artifact URI or file path reference")
    checksum: str = Field(default="", description="SHA-256 checksum digest of source artifact")
    verification_timestamp: str = Field(..., description="ISO 8601 UTC verification timestamp")
    description: str = Field(default="", description="Summary description of supporting evidence")

    class Config:
        frozen = True
        extra = "forbid"
