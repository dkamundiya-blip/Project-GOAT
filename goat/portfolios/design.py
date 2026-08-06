"""
Project GOAT v0.7 — Portfolio Design Model

Defines the immutable PortfolioDesign model (PFD_<HEX16>) specifying strategic roadmaps and program governance.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_portfolio_design_id(strategic_roadmap: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Portfolio Design ID (PFD_<HEX16>) and full SHA-256 design hash.

    Args:
        strategic_roadmap: Strategic roadmap description.
        version: Version string.

    Returns:
        Tuple of (design_id, design_hash).
    """
    payload = {
        "roadmap": str(strategic_roadmap).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    design_id = f"PFD_{digest[:16].upper()}"
    return design_id, digest


class PortfolioDesign(BaseModel):
    """Immutable scientific design specifying portfolio strategic roadmap, governance policies, and program dependencies."""

    design_id: str = Field(
        ...,
        description="Unique Portfolio Design ID formatted as PFD_<HEX16>",
        pattern=r"^PFD_[A-Fa-f0-9]{16}$",
    )
    design_version: str = Field(default="1.0.0", description="Portfolio design specification version")
    strategic_roadmap: str = Field(..., description="Formal strategic roadmap statement")
    participating_program_ids: list[str] = Field(default_factory=list, description="Target participating Program IDs")
    governance_policy_id: str = Field(default="", description="Associated Governance Policy ID (GOV_<HEX16>)")
    resource_policies: dict[str, Any] = Field(default_factory=dict, description="Computational resource allocation policies")
    review_schedule: dict[str, Any] = Field(default_factory=dict, description="Periodic portfolio review schedule")
    dependency_policies: dict[str, Any] = Field(default_factory=dict, description="Cross-program dependency rules")
    archival_policy: dict[str, Any] = Field(default_factory=dict, description="Portfolio archival criteria")
    design_hash: str = Field(..., description="Full 64-character SHA-256 canonical design hash digest")

    class Config:
        frozen = True
        extra = "forbid"
