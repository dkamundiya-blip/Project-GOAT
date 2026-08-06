"""
Project GOAT v0.7 — Research Priority Model

Defines the immutable ResearchPriority model (RPR_<HEX16>) representing prioritized scientific research opportunities.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.prioritization.enums import PriorityLevel, ResearchOpportunityType
from goat.research.edge.canonical import compute_canonical_sha256


def compute_priority_fingerprint(
    opportunity_type: str,
    justification: str,
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Research Priority Fingerprint (PRFP_<HEX64>).

    Args:
        opportunity_type: ResearchOpportunityType string.
        justification: Scientific justification statement.
        version: Version string.

    Returns:
        String formatted as 'PRFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "justification": str(justification).strip(),
        "opportunity_type": str(opportunity_type).strip().lower(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PRFP_{digest.upper()}"


def compute_priority_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Research Priority ID (RPR_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Research Priority Fingerprint (PRFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (priority_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    priority_id = f"RPR_{digest[:16].upper()}"
    return priority_id, digest


class ResearchPriority(BaseModel):
    """Immutable scientific object representing a prioritized research opportunity."""

    priority_id: str = Field(
        ...,
        description="Unique Priority ID formatted as RPR_<HEX16>",
        pattern=r"^RPR_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Research Priority Fingerprint (PRFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    priority_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Priority score (0.0 to 1.0)")
    priority_level: PriorityLevel = Field(default=PriorityLevel.LOW, description="Priority level classification")
    opportunity_type: ResearchOpportunityType = Field(..., description="Research opportunity categorization")
    supporting_consensus_ids: list[str] = Field(default_factory=list, description="Supporting Consensus IDs (CNS_<HEX16>)")
    supporting_knowledge_ids: list[str] = Field(default_factory=list, description="Supporting Knowledge IDs (KNW_<HEX16>)")
    supporting_conflict_ids: list[str] = Field(default_factory=list, description="Supporting Conflict IDs (CCF_<HEX16>)")
    supporting_evolution_ids: list[str] = Field(default_factory=list, description="Supporting Evolution IDs (KEV_<HEX16>)")
    scientific_justification: str = Field(..., description="Formal statement explaining scientific rationale for priority score")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
