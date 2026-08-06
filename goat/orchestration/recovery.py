"""
Project GOAT v0.7 — Pipeline Checkpoint & Recovery Engine

Defines PipelineCheckpoint model (CHK_<HEX16>) and PipelineRecoveryEngine for deterministic recovery and replay.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_checkpoint_id(pipeline_id: str, stage_id: str, timestamp: str) -> str:
    """Compute deterministic Checkpoint ID (CHK_<HEX16>).

    Args:
        pipeline_id: Parent Research Pipeline ID.
        stage_id: Stage ID at checkpoint creation.
        timestamp: ISO 8601 creation timestamp string.

    Returns:
        String formatted as 'CHK_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "pipeline_id": str(pipeline_id).strip(),
        "stage_id": str(stage_id).strip(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"CHK_{digest[:16].upper()}"


class PipelineCheckpoint(BaseModel):
    """Immutable representation of a research pipeline checkpoint snapshot."""

    checkpoint_id: str = Field(
        ...,
        description="Unique Checkpoint ID formatted as CHK_<HEX16>",
        pattern=r"^CHK_[A-Fa-f0-9]{16}$",
    )
    pipeline_id: str = Field(..., description="Parent Research Pipeline ID (PIPE_<HEX16>)")
    stage_id: str = Field(..., description="Stage ID at checkpoint creation (STAGE_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    completed_stage_indices: list[int] = Field(default_factory=list, description="List of completed stage indices")
    context_snapshot: dict[str, Any] = Field(default_factory=dict, description="Serialized ResearchExecutionContext snapshot")
    checkpoint_hash: str = Field(..., description="Full 64-character SHA-256 canonical checkpoint hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class PipelineRecoveryEngine:
    """Engine handling deterministic checkpoint restoration, stage replay, and restart."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, PipelineCheckpoint] = {}  # checkpoint_id -> PipelineCheckpoint

    def register_checkpoint(self, checkpoint: PipelineCheckpoint) -> None:
        """Register a checkpoint in memory."""
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> PipelineCheckpoint:
        """Retrieve checkpoint by Checkpoint ID."""
        if checkpoint_id not in self._checkpoints:
            raise KeyError(f"Checkpoint ID '{checkpoint_id}' not found in PipelineRecoveryEngine")
        return self._checkpoints[checkpoint_id]

    def get_latest_checkpoint(self, pipeline_id: str) -> PipelineCheckpoint | None:
        """Retrieve the most recent checkpoint for a pipeline."""
        p_chks = [c for c in self._checkpoints.values() if c.pipeline_id == pipeline_id]
        if not p_chks:
            return None
        return max(p_chks, key=lambda c: c.timestamp)
