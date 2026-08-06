"""
Project GOAT v0.7 — Scientific Execution Session Model

Defines the immutable ScientificExecutionSession model (SES_<HEX16>) representing
top-level deterministic execution sessions across scheduled research tasks.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.execution.enums import ExecutionState
from goat.research.edge.canonical import compute_canonical_sha256


def compute_session_fingerprint(
    source_schedule_id: str,
    executed_task_ids: list[str],
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Execution Session Fingerprint (SESFP_<HEX64>).

    Args:
        source_schedule_id: Source Schedule ID (SCH_<HEX16>).
        executed_task_ids: Scheduled Task IDs (STK_<HEX16>).
        version: Version string.

    Returns:
        String formatted as 'SESFP_' + 64 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "executed_task_ids": sorted([str(t).strip() for t in executed_task_ids]),
        "source_schedule_id": str(source_schedule_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"SESFP_{digest.upper()}"


def compute_session_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Execution Session ID (SES_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Execution Session Fingerprint (SESFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (session_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    session_id = f"SES_{digest[:16].upper()}"
    return session_id, digest


class ScientificExecutionSession(BaseModel):
    """Immutable scientific object representing a deterministic execution session."""

    session_id: str = Field(
        ...,
        description="Unique Session ID formatted as SES_<HEX16>",
        pattern=r"^SES_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Execution Session Fingerprint (SESFP_<HEX64>)")
    semantic_version: str = Field(default="1.0.0", description="Semantic specification version")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    source_schedule_id: str = Field(..., description="Source Schedule ID (SCH_<HEX16>)")
    executed_task_ids: list[str] = Field(default_factory=list, description="Executed Scheduled Task IDs (STK_<HEX16>)")
    session_status: ExecutionState = Field(default=ExecutionState.CREATED, description="Overall session execution state")
    start_timestamp: str = Field(default="", description="ISO 8601 UTC session start timestamp")
    end_timestamp: str = Field(default="", description="ISO 8601 UTC session end timestamp")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
