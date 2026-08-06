"""
Project GOAT v0.7 — Program Milestone Model

Defines the immutable ProgramMilestone model (MS_<HEX16>) representing major milestones in a research program.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.programs.enums import MilestoneStatus
from goat.research.edge.canonical import compute_canonical_sha256


def compute_milestone_id(title: str, criteria_summary: str = "") -> str:
    """Compute deterministic Milestone ID (MS_<HEX16>).

    Args:
        title: Milestone title string.
        criteria_summary: Summary string of completion criteria.

    Returns:
        String formatted as 'MS_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "criteria": str(criteria_summary).strip(),
        "title": str(title).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"MS_{digest[:16].upper()}"


class ProgramMilestone(BaseModel):
    """Immutable scientific representation of a milestone within a research program."""

    milestone_id: str = Field(
        ...,
        description="Unique Milestone ID formatted as MS_<HEX16>",
        pattern=r"^MS_[A-Fa-f0-9]{16}$",
    )
    title: str = Field(..., description="Milestone title")
    description: str = Field(..., description="Detailed milestone description")
    dependencies: list[str] = Field(default_factory=list, description="Prerequisite Milestone IDs")
    completion_criteria: dict[str, Any] = Field(default_factory=dict, description="Completion criteria bounds")
    completion_timestamp: str = Field(default="", description="ISO 8601 UTC completion timestamp")
    status: MilestoneStatus = Field(default=MilestoneStatus.PENDING, description="Milestone status")
    audit_history: list[dict[str, Any]] = Field(default_factory=list, description="Audit history events")

    class Config:
        frozen = True
        extra = "forbid"
