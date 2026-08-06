"""
Project GOAT v0.7 — Scientific Research Orchestration Engine Package
"""

from goat.orchestration.artifacts import ArtifactRecord, ArtifactTracker
from goat.orchestration.audit import PipelineAuditEvent
from goat.orchestration.context import ResearchExecutionContext
from goat.orchestration.enums import ArtifactType, PipelineState, PipelineStageType
from goat.orchestration.model import ResearchPipeline, compute_pipeline_id
from goat.orchestration.recovery import (
    PipelineCheckpoint,
    PipelineRecoveryEngine,
    compute_checkpoint_id,
)
from goat.orchestration.reporting import PipelineReport, generate_pipeline_report
from goat.orchestration.service import PipelineValidationError, ResearchOrchestrator
from goat.orchestration.sqlite import SQLiteOrchestrationRepository
from goat.orchestration.stage import PipelineStage, compute_stage_id

__all__ = [
    # Enums
    "PipelineState",
    "PipelineStageType",
    "ArtifactType",
    # Domain Models & Context
    "ResearchPipeline",
    "compute_pipeline_id",
    "PipelineStage",
    "compute_stage_id",
    "ResearchExecutionContext",
    # Artifact Tracker & Audit
    "ArtifactRecord",
    "ArtifactTracker",
    "PipelineAuditEvent",
    # Checkpoint & Recovery
    "PipelineCheckpoint",
    "compute_checkpoint_id",
    "PipelineRecoveryEngine",
    # Persistence & Reporting
    "SQLiteOrchestrationRepository",
    "PipelineReport",
    "generate_pipeline_report",
    # Orchestrator Service
    "ResearchOrchestrator",
    "PipelineValidationError",
]
