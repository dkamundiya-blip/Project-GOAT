"""
Project GOAT v0.7 — Artifact Tracker

Defines ArtifactRecord model and ArtifactTracker class for tracking generated scientific artifacts across pipeline runs.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.orchestration.enums import ArtifactType


class ArtifactRecord(BaseModel):
    """Immutable record representing a scientific artifact generated during pipeline execution."""

    artifact_id: str = Field(..., description="Target scientific artifact ID")
    pipeline_id: str = Field(..., description="Parent Research Pipeline ID (PIPE_<HEX16>)")
    artifact_type: ArtifactType = Field(..., description="Artifact type classification")
    registration_timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Artifact metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"


class ArtifactTracker:
    """Scientific artifact tracking registry mapping artifacts to pipeline executions."""

    def __init__(self) -> None:
        self._artifacts: dict[str, ArtifactRecord] = {}  # artifact_id -> ArtifactRecord
        self._pipeline_artifacts: dict[str, list[str]] = {}  # pipeline_id -> list of artifact_ids

    def register_artifact(self, record: ArtifactRecord) -> None:
        """Register an artifact record in the tracker.

        Args:
            record: ArtifactRecord instance.
        """
        aid = record.artifact_id
        pid = record.pipeline_id

        if aid in self._artifacts:
            # Idempotent registration
            return

        self._artifacts[aid] = record
        if pid not in self._pipeline_artifacts:
            self._pipeline_artifacts[pid] = []
        self._pipeline_artifacts[pid].append(aid)

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        """Retrieve ArtifactRecord by Artifact ID."""
        if artifact_id not in self._artifacts:
            raise KeyError(f"Artifact ID '{artifact_id}' not found in ArtifactTracker")
        return self._artifacts[artifact_id]

    def get_pipeline_artifacts(self, pipeline_id: str) -> list[ArtifactRecord]:
        """Retrieve all ArtifactRecords linked to a Research Pipeline ID."""
        aids = self._pipeline_artifacts.get(pipeline_id, [])
        return [self._artifacts[aid] for aid in aids]

    def list_all(self) -> list[ArtifactRecord]:
        """List all tracked ArtifactRecords."""
        return list(self._artifacts.values())
