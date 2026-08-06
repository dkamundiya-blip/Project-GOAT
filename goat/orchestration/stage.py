"""
Project GOAT v0.7 — Pipeline Stage Model

Defines the immutable PipelineStage model (STAGE_<HEX16>) representing single steps in the research pipeline.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.orchestration.enums import PipelineStageType
from goat.research.edge.canonical import compute_canonical_sha256


def compute_stage_id(pipeline_id: str, stage_type: str, stage_index: int) -> str:
    """Compute deterministic Pipeline Stage ID (STAGE_<HEX16>).

    Args:
        pipeline_id: Parent Research Pipeline ID (PIPE_<HEX16>).
        stage_type: PipelineStageType string.
        stage_index: Integer stage order index.

    Returns:
        String formatted as 'STAGE_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "index": int(stage_index),
        "pipeline_id": str(pipeline_id).strip(),
        "stage_type": str(stage_type).strip().lower(),
    }
    digest = compute_canonical_sha256(payload)
    return f"STAGE_{digest[:16].upper()}"


class PipelineStage(BaseModel):
    """Immutable representation of a research pipeline stage execution step."""

    stage_id: str = Field(
        ...,
        description="Unique Stage ID formatted as STAGE_<HEX16>",
        pattern=r"^STAGE_[A-Fa-f0-9]{16}$",
    )
    stage_type: PipelineStageType = Field(..., description="Stage type classification")
    stage_index: int = Field(..., ge=1, description="1-indexed stage position")
    status: str = Field(default="pending", description="Stage execution status ('pending', 'running', 'completed', 'failed')")
    execution_hash: str = Field(default="", description="Full 64-character SHA-256 canonical execution hash digest")
    start_time: str = Field(default="", description="ISO 8601 UTC execution start timestamp")
    end_time: str = Field(default="", description="ISO 8601 UTC execution completion timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Stage execution metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
