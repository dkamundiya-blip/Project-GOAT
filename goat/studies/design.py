"""
Project GOAT v0.7 — Study Design Model

Defines the immutable StudyDesign model (DES_<HEX16>) specifying study methodologies, inclusion/exclusion rules, and replication policies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_design_id(objective: str, plan: list[str], version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Study Design ID (DES_<HEX16>) and full SHA-256 design hash.

    Args:
        objective: Research objective string.
        plan: Ordered list of planned experiment steps/titles.
        version: Version string.

    Returns:
        Tuple of (design_id, design_hash).
    """
    payload = {
        "objective": str(objective).strip(),
        "plan": [str(p).strip() for p in plan],
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    design_id = f"DES_{digest[:16].upper()}"
    return design_id, digest


class StudyDesign(BaseModel):
    """Immutable scientific design specifying study methodologies, experiment plan, and validation policies."""

    design_id: str = Field(
        ...,
        description="Unique Study Design ID formatted as DES_<HEX16>",
        pattern=r"^DES_[A-Fa-f0-9]{16}$",
    )
    design_version: str = Field(default="1.0.0", description="Study design specification version")
    research_objective: str = Field(..., description="Formal research objective statement")
    experiment_plan: list[str] = Field(default_factory=list, description="Ordered list of planned experiment steps")
    inclusion_criteria: dict[str, Any] = Field(default_factory=dict, description="Criteria for including features/experiments")
    exclusion_criteria: dict[str, Any] = Field(default_factory=dict, description="Criteria for excluding features/experiments")
    comparison_methodology: str = Field(default="baseline_contrast", description="Statistical comparison methodology")
    replication_policy: dict[str, Any] = Field(default_factory=dict, description="Multi-market or out-of-sample replication rules")
    stopping_criteria: dict[str, Any] = Field(default_factory=dict, description="Early stopping bounds")
    statistical_policy: dict[str, Any] = Field(default_factory=dict, description="Statistical hypothesis test bounds")
    validation_policy: dict[str, Any] = Field(default_factory=dict, description="Stage A-G validation criteria bounds")
    design_hash: str = Field(..., description="Full 64-character SHA-256 canonical design hash digest")

    class Config:
        frozen = True
        extra = "forbid"
