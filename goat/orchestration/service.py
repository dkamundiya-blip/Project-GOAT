"""
Project GOAT v0.7 — Scientific Research Orchestrator Service

Implements ResearchOrchestrator for master workflow scheduling, fail-closed state transitions,
dependency resolution, checkpoint creation, and subsystem coordination.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from goat.orchestration.artifacts import ArtifactRecord, ArtifactTracker
from goat.orchestration.audit import PipelineAuditEvent
from goat.orchestration.context import ResearchExecutionContext
from goat.orchestration.enums import ArtifactType, PipelineState, PipelineStageType
from goat.orchestration.model import ResearchPipeline, compute_pipeline_id
from goat.orchestration.recovery import PipelineCheckpoint, compute_checkpoint_id
from goat.orchestration.reporting import PipelineReport, generate_pipeline_report
from goat.orchestration.sqlite import SQLiteOrchestrationRepository
from goat.orchestration.stage import PipelineStage, compute_stage_id
from goat.research.edge.canonical import compute_canonical_sha256


class PipelineValidationError(ValueError):
    """Raised when pipeline validation, transition, or execution fails."""
    pass


# Legal State Machine Transitions
LEGAL_TRANSITIONS: dict[PipelineState, set[PipelineState]] = {
    PipelineState.CREATED: {PipelineState.READY, PipelineState.ABORTED},
    PipelineState.READY: {PipelineState.RUNNING, PipelineState.ABORTED},
    PipelineState.RUNNING: {PipelineState.WAITING, PipelineState.COMPLETED, PipelineState.FAILED, PipelineState.ABORTED},
    PipelineState.WAITING: {PipelineState.RUNNING, PipelineState.FAILED, PipelineState.ABORTED},
    PipelineState.COMPLETED: {PipelineState.ARCHIVED},
    PipelineState.FAILED: {PipelineState.READY, PipelineState.ABORTED, PipelineState.ARCHIVED},
    PipelineState.ABORTED: {PipelineState.ARCHIVED},
    PipelineState.ARCHIVED: set(),
}


class ResearchOrchestrator:
    """Master scientific research orchestrator coordinating end-to-end subsystem workflows."""

    def __init__(
        self,
        repository: SQLiteOrchestrationRepository | None = None,
        artifact_tracker: ArtifactTracker | None = None,
    ) -> None:
        self._repo = repository
        self._artifact_tracker = artifact_tracker or ArtifactTracker()
        self._active_pipelines: dict[str, ResearchPipeline] = {}
        self._active_contexts: dict[str, ResearchExecutionContext] = {}

    def create_pipeline(
        self,
        name: str = "standard_research_pipeline",
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> ResearchPipeline:
        """Create a new master ResearchPipeline initialized with all 11 scientific stages.

        Args:
            name: Pipeline specification name.
            version: Version string.
            metadata: Metadata dictionary.

        Returns:
            Created ResearchPipeline instance in CREATED state.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        pipeline_id, pipeline_hash = compute_pipeline_id(name, version, timestamp)

        # Initialize 11 standard scientific stages
        stages: list[PipelineStage] = []
        for idx, stg_type in enumerate(PipelineStageType, start=1):
            stage_id = compute_stage_id(pipeline_id, stg_type.value, idx)
            stage = PipelineStage(
                stage_id=stage_id,
                stage_type=stg_type,
                stage_index=idx,
                status="pending",
                metadata={"name": stg_type.value},
            )
            stages.append(stage)

        pipeline = ResearchPipeline(
            pipeline_id=pipeline_id,
            pipeline_version=version,
            pipeline_hash=pipeline_hash,
            creation_timestamp=timestamp,
            current_state=PipelineState.CREATED,
            registered_stages=stages,
            pipeline_metadata=metadata or {},
        )

        context = ResearchExecutionContext(
            pipeline_id=pipeline_id,
            registry_version=version,
        )

        self._active_pipelines[pipeline_id] = pipeline
        self._active_contexts[pipeline_id] = context

        if self._repo:
            self._repo.save_pipeline(pipeline)
            self._repo.save_context(context)

        self._log_audit(pipeline_id, "", "CREATED", "Created master ResearchPipeline")
        return pipeline

    def transition_state(self, pipeline_id: str, new_state: PipelineState, notes: str = "") -> ResearchPipeline:
        """Transition pipeline to a new state with state machine validation.

        Args:
            pipeline_id: Target Pipeline ID.
            new_state: Target PipelineState.
            notes: Transition notes.

        Returns:
            Updated ResearchPipeline instance.
        """
        pipeline = self.get_pipeline(pipeline_id)
        current = pipeline.current_state

        if new_state not in LEGAL_TRANSITIONS.get(current, set()):
            raise PipelineValidationError(
                f"Illegal state transition for Pipeline '{pipeline_id}': cannot transition from '{current.value}' to '{new_state.value}'"
            )

        updated_dict = pipeline.model_dump()
        updated_dict["current_state"] = new_state
        updated_pipeline = ResearchPipeline(**updated_dict)

        self._active_pipelines[pipeline_id] = updated_pipeline
        if self._repo:
            self._repo.save_pipeline(updated_pipeline)

        self._log_audit(pipeline_id, current.value, new_state.value, notes or f"Transitioned to '{new_state.value}'")
        return updated_pipeline

    def execute_stage(
        self,
        pipeline_id: str,
        stage_index: int,
        subsystem_action: Any | None = None,
    ) -> PipelineStage:
        """Execute a specific stage in the pipeline with fail-closed validation.

        Args:
            pipeline_id: Target Pipeline ID.
            stage_index: 1-indexed stage position.
            subsystem_action: Optional callable executing subsystem logic.

        Returns:
            Executed PipelineStage instance.
        """
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline.current_state not in [PipelineState.READY, PipelineState.RUNNING]:
            if pipeline.current_state == PipelineState.CREATED:
                pipeline = self.transition_state(pipeline_id, PipelineState.READY, "Prepared for execution")
                pipeline = self.transition_state(pipeline_id, PipelineState.RUNNING, "Started stage execution")
            elif pipeline.current_state == PipelineState.READY:
                pipeline = self.transition_state(pipeline_id, PipelineState.RUNNING, "Started stage execution")
            else:
                raise PipelineValidationError(f"Cannot execute stage on Pipeline in '{pipeline.current_state.value}' state")

        target_stage = None
        for s in pipeline.registered_stages:
            if s.stage_index == stage_index:
                target_stage = s
                break

        if target_stage is None:
            raise PipelineValidationError(f"Stage index {stage_index} not found in Pipeline '{pipeline_id}'")

        # Verify previous stages are completed
        for s in pipeline.registered_stages:
            if s.stage_index < stage_index and s.status != "completed":
                raise PipelineValidationError(
                    f"Dependency violation: Stage {s.stage_index} ({s.stage_type.value}) is not completed (status: '{s.status}')"
                )

        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Update stage status to running
        stages_updated = []
        for s in pipeline.registered_stages:
            if s.stage_index == stage_index:
                stg_dict = s.model_dump()
                stg_dict["status"] = "running"
                stg_dict["start_time"] = start_time
                stages_updated.append(PipelineStage(**stg_dict))
            else:
                stages_updated.append(s)

        p_dict = pipeline.model_dump()
        p_dict["registered_stages"] = stages_updated
        pipeline = ResearchPipeline(**p_dict)
        self._active_pipelines[pipeline_id] = pipeline

        # Execute optional subsystem callable
        exec_meta: dict[str, Any] = {}
        try:
            if subsystem_action:
                res = subsystem_action()
                if isinstance(res, dict):
                    exec_meta = res
            status = "completed"
        except Exception as err:
            status = "failed"
            self.transition_state(pipeline_id, PipelineState.FAILED, f"Stage {stage_index} failed: {err}")
            raise PipelineValidationError(f"Subsystem execution failed in stage {stage_index}: {err}") from err

        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        exec_payload = {"index": stage_index, "pipeline_id": pipeline_id, "start": start_time, "end": end_time}
        exec_hash = compute_canonical_sha256(exec_payload)

        # Update stage status to completed
        final_stages = []
        for s in pipeline.registered_stages:
            if s.stage_index == stage_index:
                stg_dict = s.model_dump()
                stg_dict["status"] = status
                stg_dict["end_time"] = end_time
                stg_dict["execution_hash"] = exec_hash
                stg_dict["metadata"].update(exec_meta)
                final_stage = PipelineStage(**stg_dict)
                final_stages.append(final_stage)
            else:
                final_stages.append(s)

        p_dict = pipeline.model_dump()
        p_dict["registered_stages"] = final_stages
        
        # Check if all 11 stages completed
        if all(s.status == "completed" for s in final_stages):
            p_dict["current_state"] = PipelineState.COMPLETED

        pipeline = ResearchPipeline(**p_dict)
        self._active_pipelines[pipeline_id] = pipeline

        if self._repo:
            self._repo.save_pipeline(pipeline)

        # Create checkpoint snapshot after stage completion
        self.create_checkpoint(pipeline_id, target_stage.stage_id)

        self._log_audit(pipeline_id, "RUNNING", status, f"Stage {stage_index} ({target_stage.stage_type.value}) executed")
        return final_stage

    def create_checkpoint(self, pipeline_id: str, stage_id: str) -> PipelineCheckpoint:
        """Create an immutable checkpoint snapshot after stage execution."""
        pipeline = self.get_pipeline(pipeline_id)
        context = self.get_context(pipeline_id)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        chk_id = compute_checkpoint_id(pipeline_id, stage_id, timestamp)
        completed_indices = [s.stage_index for s in pipeline.registered_stages if s.status == "completed"]

        payload = {
            "completed": completed_indices,
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "timestamp": timestamp,
        }
        chk_hash = compute_canonical_sha256(payload)

        checkpoint = PipelineCheckpoint(
            checkpoint_id=chk_id,
            pipeline_id=pipeline_id,
            stage_id=stage_id,
            timestamp=timestamp,
            completed_stage_indices=completed_indices,
            context_snapshot=context.model_dump(mode="json"),
            checkpoint_hash=chk_hash,
        )

        if self._repo:
            self._repo.save_checkpoint(checkpoint)

        return checkpoint

    def get_pipeline(self, pipeline_id: str) -> ResearchPipeline:
        """Retrieve active or persisted ResearchPipeline."""
        if pipeline_id in self._active_pipelines:
            return self._active_pipelines[pipeline_id]
        if self._repo:
            p = self._repo.get_pipeline(pipeline_id)
            if p:
                self._active_pipelines[pipeline_id] = p
                return p
        raise KeyError(f"Research Pipeline ID '{pipeline_id}' not found")

    def get_context(self, pipeline_id: str) -> ResearchExecutionContext:
        """Retrieve active or persisted ResearchExecutionContext."""
        if pipeline_id in self._active_contexts:
            return self._active_contexts[pipeline_id]
        if self._repo:
            c = self._repo.get_context(pipeline_id)
            if c:
                self._active_contexts[pipeline_id] = c
                return c
        raise KeyError(f"Execution context for Pipeline '{pipeline_id}' not found")

    def register_artifact(self, pipeline_id: str, artifact_id: str, artifact_type: ArtifactType) -> ArtifactRecord:
        """Register a generated artifact linked to a pipeline run."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record = ArtifactRecord(
            artifact_id=artifact_id,
            pipeline_id=pipeline_id,
            artifact_type=artifact_type,
            registration_timestamp=timestamp,
        )
        self._artifact_tracker.register_artifact(record)
        if self._repo:
            self._repo.save_artifact(record)
        return record

    def generate_report(self, pipeline_id: str) -> PipelineReport:
        """Generate PipelineReport for a pipeline execution."""
        pipeline = self.get_pipeline(pipeline_id)
        artifacts = self._artifact_tracker.get_pipeline_artifacts(pipeline_id)
        audit_events = self.get_audit_trail(pipeline_id)
        return generate_pipeline_report(pipeline, artifacts, audit_events)

    def get_audit_trail(self, pipeline_id: str) -> list[PipelineAuditEvent]:
        """Retrieve audit trail log for a pipeline execution."""
        if self._repo:
            return self._repo.get_audit_trail(pipeline_id)
        return []

    def _log_audit(self, pipeline_id: str, prev_state: str, new_state: str, notes: str) -> None:
        """Helper logging pipeline audit event."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {"new": new_state, "pipeline_id": pipeline_id, "prev": prev_state, "timestamp": timestamp}
        event_hash = compute_canonical_sha256(payload)
        event = PipelineAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            pipeline_id=pipeline_id,
            event_type="PIPELINE_EVENT",
            timestamp=timestamp,
            previous_state=prev_state,
            new_state=new_state,
            notes=notes,
            execution_hash=event_hash,
        )
        if self._repo:
            self._repo.log_audit_event(event)
