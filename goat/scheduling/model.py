"""
Project GOAT v0.7 — Research Schedule Model

Defines the immutable ResearchSchedule model (SCH_<HEX16>) representing top-level scientific research execution schedules.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.scheduling.enums import ScheduleExecutionState


def compute_schedule_fingerprint(
    source_plan_ids: list[str],
    scheduled_task_ids: list[str],
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Research Schedule Fingerprint (SCHFP_<HEX64>).

    Args:
        source_plan_ids: Source Plan IDs (PLN_<HEX16>).
        scheduled_task_ids: Scheduled Task IDs (STK_<HEX16>).
        version: Version string.

    Returns:
        String formatted as 'SCHFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "scheduled_task_ids": sorted([str(t).strip() for t in scheduled_task_ids]),
        "source_plan_ids": sorted([str(p).strip() for p in source_plan_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SCHFP_{digest.upper()}"


def compute_schedule_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Research Schedule ID (SCH_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Research Schedule Fingerprint (SCHFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (schedule_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    schedule_id = f"SCH_{digest[:16].upper()}"
    return schedule_id, digest


class ResearchSchedule(BaseModel):
    """Immutable scientific object representing a deterministic execution schedule across plan tasks."""

    schedule_id: str = Field(
        ...,
        description="Unique Schedule ID formatted as SCH_<HEX16>",
        pattern=r"^SCH_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Research Schedule Fingerprint (SCHFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    source_plan_ids: list[str] = Field(default_factory=list, description="Source Plan IDs (PLN_<HEX16>)")
    scheduled_task_ids: list[str] = Field(default_factory=list, description="Scheduled Task IDs (STK_<HEX16>)")
    execution_order: list[str] = Field(default_factory=list, description="Ordered Scheduled Task IDs (STK_<HEX16>)")
    schedule_status: ScheduleExecutionState = Field(default=ScheduleExecutionState.PENDING, description="Overall schedule execution state")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
