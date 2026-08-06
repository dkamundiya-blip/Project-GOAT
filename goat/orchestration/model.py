"""
Project GOAT v0.7 — Research Pipeline Model

Defines the master ResearchPipeline model (PIPE_<HEX16>) representing an end-to-end scientific research execution.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.orchestration.enums import PipelineState
from goat.orchestration.stage import PipelineStage
from goat.research.edge.canonical import compute_canonical_sha256


def compute_pipeline_id(name: str, version: str, timestamp: str) -> tuple[str, str]:
    """Compute deterministic Pipeline ID (PIPE_<HEX16>) and full SHA-256 pipeline hash.

    Args:
        name: Pipeline specification name.
        version: Semantic version string.
        timestamp: ISO 8601 creation timestamp string.

    Returns:
        Tuple of (pipeline_id, pipeline_hash).
    """
    payload = {
        "name": str(name).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    pipeline_id = f"PIPE_{digest[:16].upper()}"
    return pipeline_id, digest


class ResearchPipeline(BaseModel):
    """Immutable representation of a master scientific research pipeline."""

    pipeline_id: str = Field(
        ...,
        description="Unique Research Pipeline ID formatted as PIPE_<HEX16>",
        pattern=r"^PIPE_[A-Fa-f0-9]{16}$",
    )
    pipeline_version: str = Field(default="1.0.0", description="Semantic pipeline specification version")
    pipeline_hash: str = Field(..., description="Full 64-character SHA-256 canonical pipeline hash digest")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    current_state: PipelineState = Field(default=PipelineState.CREATED, description="Pipeline state machine state")
    registered_stages: list[PipelineStage] = Field(default_factory=list, description="Ordered list of registered PipelineStages")
    pipeline_metadata: dict[str, Any] = Field(default_factory=dict, description="Pipeline metadata annotations")
    execution_policy: dict[str, Any] = Field(default_factory=dict, description="Execution policy configuration")
    failure_policy: dict[str, Any] = Field(default_factory=dict, description="Failure and recovery policy configuration")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Pipeline audit trail metadata")

    class Config:
        frozen = True
        extra = "forbid"
