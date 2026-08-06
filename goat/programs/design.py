"""
Project GOAT v0.7 — Program Design Model

Defines the immutable ProgramDesign model (PDES_<HEX16>) specifying strategic objectives, roadmaps, and governance metadata.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_program_design_id(objectives: str, roadmap: list[str], version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Program Design ID (PDES_<HEX16>) and full SHA-256 design hash.

    Args:
        objectives: Strategic objectives string.
        roadmap: Ordered list of research roadmap milestone titles.
        version: Version string.

    Returns:
        Tuple of (design_id, design_hash).
    """
    payload = {
        "objectives": str(objectives).strip(),
        "roadmap": [str(r).strip() for r in roadmap],
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    design_id = f"PDES_{digest[:16].upper()}"
    return design_id, digest


class ProgramDesign(BaseModel):
    """Immutable scientific design specifying program strategic objectives, research roadmap, and governance."""

    design_id: str = Field(
        ...,
        description="Unique Program Design ID formatted as PDES_<HEX16>",
        pattern=r"^PDES_[A-Fa-f0-9]{16}$",
    )
    design_version: str = Field(default="1.0.0", description="Program design specification version")
    strategic_objectives: str = Field(..., description="Formal strategic objectives statement")
    research_roadmap: list[str] = Field(default_factory=list, description="Ordered list of research roadmap milestones")
    participating_study_ids: list[str] = Field(default_factory=list, description="Target participating Study IDs")
    dependency_model: dict[str, Any] = Field(default_factory=dict, description="Study dependency graph model")
    milestone_ids: list[str] = Field(default_factory=list, description="Associated Milestone IDs (MS_<HEX16>)")
    completion_criteria: dict[str, Any] = Field(default_factory=dict, description="Program completion criteria bounds")
    review_schedule: dict[str, Any] = Field(default_factory=dict, description="Periodic scientific review schedule")
    governance_metadata: dict[str, Any] = Field(default_factory=dict, description="Program governance metadata")
    design_hash: str = Field(..., description="Full 64-character SHA-256 canonical design hash digest")

    class Config:
        frozen = True
        extra = "forbid"
