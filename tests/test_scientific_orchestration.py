"""
Project GOAT v0.7 — Step 4.5 Scientific Research Orchestration Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.orchestration import (
    ArtifactRecord,
    ArtifactTracker,
    ArtifactType,
    PipelineAuditEvent,
    PipelineCheckpoint,

    PipelineReport,
    PipelineState,
    PipelineStageType,
    PipelineValidationError,
    ResearchExecutionContext,
    ResearchOrchestrator,
    ResearchPipeline,
    SQLiteOrchestrationRepository,
    compute_checkpoint_id,
    compute_pipeline_id,
    compute_stage_id,
)


@pytest.fixture
def temp_orchestrator():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteOrchestrationRepository(db_path)
    orchestrator = ResearchOrchestrator(repository=repo)
    yield orchestrator, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_pipeline_identity_and_stage_initialization():
    """Verify ResearchPipeline identity (PIPE_<HEX16>) and 11-stage initialization."""
    pid, p_hash = compute_pipeline_id("TestPipeline", "1.0.0", "2026-07-30T00:00:00Z")
    assert pid.startswith("PIPE_")
    assert len(pid) == 21
    assert len(p_hash) == 64

    orchestrator = ResearchOrchestrator()
    pipeline = orchestrator.create_pipeline(name="TestPipeline")

    assert pipeline.pipeline_id.startswith("PIPE_")
    assert len(pipeline.registered_stages) == 11
    assert pipeline.current_state == PipelineState.CREATED

    # Verify stage ordering (1 to 11)
    stage_types = [s.stage_type for s in pipeline.registered_stages]
    assert stage_types[0] == PipelineStageType.FEATURE_CONSTRUCTION
    assert stage_types[-1] == PipelineStageType.SCIENTIFIC_MEMORY_UPDATE

    # Immutability check
    with pytest.raises(ValidationError):
        pipeline.current_state = PipelineState.COMPLETED


def test_pipeline_state_machine_transitions(temp_orchestrator):
    """Verify state machine legal transitions and illegal transition rejection."""
    orchestrator, _, _ = temp_orchestrator
    pipeline = orchestrator.create_pipeline()

    # Legal transition CREATED -> READY
    p_ready = orchestrator.transition_state(pipeline.pipeline_id, PipelineState.READY)
    assert p_ready.current_state == PipelineState.READY

    # Legal transition READY -> RUNNING
    p_running = orchestrator.transition_state(pipeline.pipeline_id, PipelineState.RUNNING)
    assert p_running.current_state == PipelineState.RUNNING

    # Illegal transition RUNNING -> CREATED must raise PipelineValidationError
    with pytest.raises(PipelineValidationError, match="Illegal state transition"):
        orchestrator.transition_state(pipeline.pipeline_id, PipelineState.CREATED)


def test_sequential_stage_execution_and_dependency_enforcement(temp_orchestrator):
    """Verify sequential stage execution and out-of-order stage execution rejection."""
    orchestrator, _, _ = temp_orchestrator
    pipeline = orchestrator.create_pipeline()
    pid = pipeline.pipeline_id

    # Execute Stage 1 (Feature Construction)
    stg1 = orchestrator.execute_stage(pid, stage_index=1)
    assert stg1.status == "completed"

    # Out-of-order execution of Stage 5 before Stages 2-4 complete must raise PipelineValidationError
    with pytest.raises(PipelineValidationError, match="Dependency violation"):
        orchestrator.execute_stage(pid, stage_index=5)

    # Execute Stages 2 to 11 sequentially
    for idx in range(2, 12):
        stg = orchestrator.execute_stage(pid, stage_index=idx)
        assert stg.status == "completed"

    final_pipeline = orchestrator.get_pipeline(pid)
    assert final_pipeline.current_state == PipelineState.COMPLETED


def test_artifact_tracking_and_checkpoint_creation(temp_orchestrator):
    """Verify ArtifactTracker and PipelineCheckpoint snapshot creation."""
    orchestrator, _, _ = temp_orchestrator
    pipeline = orchestrator.create_pipeline()
    pid = pipeline.pipeline_id

    # Register scientific artifact
    art = orchestrator.register_artifact(pid, "FEAT_1234567890ABCDEF", ArtifactType.FEATURE)
    assert art.pipeline_id == pid
    assert art.artifact_type == ArtifactType.FEATURE

    # Execute Stage 1 to create checkpoint
    stg1 = orchestrator.execute_stage(pid, stage_index=1)
    chk = orchestrator.create_checkpoint(pid, stg1.stage_id)

    assert chk.checkpoint_id.startswith("CHK_")
    assert chk.pipeline_id == pid
    assert 1 in chk.completed_stage_indices


def test_pipeline_reporting(temp_orchestrator):
    """Verify generate_pipeline_report produces deterministic PipelineReport."""
    orchestrator, _, _ = temp_orchestrator
    pipeline = orchestrator.create_pipeline()
    pid = pipeline.pipeline_id

    orchestrator.register_artifact(pid, "FEAT_1111", ArtifactType.FEATURE)
    orchestrator.execute_stage(pid, stage_index=1)

    report = orchestrator.generate_report(pid)
    assert isinstance(report, PipelineReport)
    assert report.report_id.startswith("PREP_")
    assert report.completed_stages_count == 1
    assert report.total_stages_count == 11
    assert report.artifact_counts.get("feature", 0) == 1
