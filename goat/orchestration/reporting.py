"""
Project GOAT v0.7 — Orchestration Reporting Module

Implements immutable PipelineReport summarizing research pipeline execution timeline, artifact counts, audit trail, and recovery actions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.orchestration.artifacts import ArtifactTracker
from goat.orchestration.model import ResearchPipeline
from goat.orchestration.sqlite import SQLiteOrchestrationRepository
from goat.research.edge.canonical import compute_canonical_sha256


class PipelineReport(BaseModel):
    """Immutable report summarizing scientific research pipeline execution and audit state."""

    report_id: str = Field(..., description="Unique Pipeline Report ID (PREP_<HEX16>)")
    pipeline_id: str = Field(..., description="Parent Research Pipeline ID (PIPE_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    final_state: str = Field(..., description="Final PipelineState string")
    completed_stages_count: int = Field(default=0, ge=0, description="Count of completed stages")
    total_stages_count: int = Field(default=0, ge=0, description="Total registered stages count")
    artifact_counts: dict[str, int] = Field(default_factory=dict, description="Artifact counts by ArtifactType")
    stage_durations: dict[str, float] = Field(default_factory=dict, description="Stage execution durations in seconds")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit trail summary")
    recovery_summary: dict[str, Any] = Field(default_factory=dict, description="Recovery and checkpoint summary")
    execution_summary: list[str] = Field(default_factory=list, description="Execution milestone summary notes")

    class Config:
        frozen = True
        extra = "forbid"


def generate_pipeline_report(
    pipeline: ResearchPipeline,
    artifacts: list[Any] | None = None,
    audit_events: list[Any] | None = None,
    timestamp: str = "",
) -> PipelineReport:
    """Generate deterministic PipelineReport.

    Args:
        pipeline: ResearchPipeline instance.
        artifacts: Optional list of ArtifactRecords.
        audit_events: Optional list of PipelineAuditEvents.
        timestamp: Optional ISO 8601 timestamp string.

    Returns:
        Immutable PipelineReport.
    """
    ts = timestamp or "2026-07-30T00:00:00Z"
    completed_stages = [s for s in pipeline.registered_stages if s.status == "completed"]

    artifact_counts: dict[str, int] = {}
    if artifacts:
        for a in artifacts:
            atype = a.artifact_type.value if hasattr(a.artifact_type, "value") else str(a.artifact_type)
            artifact_counts[atype] = artifact_counts.get(atype, 0) + 1

    stage_durations: dict[str, float] = {}
    for s in pipeline.registered_stages:
        stage_durations[s.stage_type.value] = s.metadata.get("duration_seconds", 0.0)

    payload = {
        "completed": len(completed_stages),
        "pipeline_id": pipeline.pipeline_id,
        "timestamp": ts,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"PREP_{digest[:16].upper()}"

    summary_notes = [
        f"Pipeline '{pipeline.pipeline_id}' state: {pipeline.current_state.value}.",
        f"Completed {len(completed_stages)} of {len(pipeline.registered_stages)} registered stages.",
        f"Tracked {sum(artifact_counts.values())} total scientific artifacts.",
    ]

    return PipelineReport(
        report_id=report_id,
        pipeline_id=pipeline.pipeline_id,
        timestamp=ts,
        final_state=pipeline.current_state.value,
        completed_stages_count=len(completed_stages),
        total_stages_count=len(pipeline.registered_stages),
        artifact_counts=artifact_counts,
        stage_durations=stage_durations,
        audit_summary={"total_audit_events": len(audit_events or [])},
        recovery_summary={"status": "clean"},
        execution_summary=summary_notes,
    )
