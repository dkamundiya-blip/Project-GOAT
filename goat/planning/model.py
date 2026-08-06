"""
Project GOAT v0.7 — Scientific Plan Model

Defines the immutable ScientificPlan model (PLN_<HEX16>) representing top-level scientific research execution plans.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_plan_fingerprint(
    research_objective: str,
    source_priority_ids: list[str],
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Scientific Plan Fingerprint (PLFP_<HEX64>).

    Args:
        research_objective: Formal research objective statement.
        source_priority_ids: Source Priority IDs (RPR_<HEX16>).
        version: Version string.

    Returns:
        String formatted as 'PLFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "objective": str(research_objective).strip(),
        "source_priority_ids": sorted([str(p).strip() for p in source_priority_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PLFP_{digest.upper()}"


def compute_plan_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Scientific Plan ID (PLN_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Scientific Plan Fingerprint (PLFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (plan_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    plan_id = f"PLN_{digest[:16].upper()}"
    return plan_id, digest


class ScientificPlan(BaseModel):
    """Immutable scientific object representing a deterministic research execution plan."""

    plan_id: str = Field(
        ...,
        description="Unique Plan ID formatted as PLN_<HEX16>",
        pattern=r"^PLN_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Scientific Plan Fingerprint (PLFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    source_priority_ids: list[str] = Field(default_factory=list, description="Source Research Priority IDs (RPR_<HEX16>)")
    research_objective: str = Field(..., description="Formal scientific research objective statement")
    planned_study_ids: list[str] = Field(default_factory=list, description="Planned Study IDs (STD_<HEX16>)")
    planned_experiment_ids: list[str] = Field(default_factory=list, description="Planned Experiment IDs (EXP_<HEX16>)")
    dependency_graph_id: str = Field(default="", description="Planning Graph ID")
    estimated_complexity: str = Field(default="moderate", description="Estimated plan complexity rating")
    execution_status: str = Field(default="proposed", description="Execution status ('proposed', 'scheduled', 'executing', 'completed', 'failed')")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
