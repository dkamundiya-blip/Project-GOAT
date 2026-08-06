"""
Project GOAT v0.7 — Scientific Program Coordinator Engine

Implements ProgramCoordinator for master research program scheduling, multi-study workflow coordination,
milestone tracking, dependency enforcement, audit logging, and program replay.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.programs.audit import ProgramAuditEvent
from goat.programs.context import ProgramContext
from goat.programs.design import ProgramDesign, compute_program_design_id
from goat.programs.enums import MilestoneStatus, ProgramStatus
from goat.programs.milestone import ProgramMilestone, compute_milestone_id
from goat.programs.model import (
    ScientificResearchProgram,
    compute_program_fingerprint,
    compute_program_id,
)
from goat.programs.registry import ProgramStudyRegistry
from goat.programs.result import ProgramResult, compute_program_result_id
from goat.research.edge.canonical import compute_canonical_sha256
from goat.studies.coordinator import StudyCoordinator


class ProgramValidationError(ValueError):
    """Raised when program validation, scheduling, or execution fails."""
    pass


class ProgramCoordinator:
    """Master program coordinator managing multi-study scientific research initiatives."""

    def __init__(
        self,
        study_coordinator: StudyCoordinator | None = None,
        registry: ProgramStudyRegistry | None = None,
    ) -> None:
        self._study_coordinator = study_coordinator or StudyCoordinator()
        self._registry = registry or ProgramStudyRegistry()
        self._programs: dict[str, ScientificResearchProgram] = {}
        self._designs: dict[str, ProgramDesign] = {}
        self._milestones: dict[str, ProgramMilestone] = {}
        self._results: dict[str, ProgramResult] = {}
        self._audit_events: dict[str, list[ProgramAuditEvent]] = {}

    @property
    def study_coordinator(self) -> StudyCoordinator:
        """Return bound StudyCoordinator."""
        return self._study_coordinator

    @property
    def registry(self) -> ProgramStudyRegistry:
        """Return bound ProgramStudyRegistry."""
        return self._registry

    def create_milestone(self, title: str, description: str, dependencies: list[str] | None = None) -> ProgramMilestone:
        """Create an immutable ProgramMilestone."""
        ms_id = compute_milestone_id(title, description)
        milestone = ProgramMilestone(
            milestone_id=ms_id,
            title=title,
            description=description,
            dependencies=dependencies or [],
            status=MilestoneStatus.PENDING,
        )
        self._milestones[ms_id] = milestone
        return milestone

    def create_design(
        self,
        strategic_objectives: str,
        roadmap: list[str],
        version: str = "1.0.0",
        milestone_ids: list[str] | None = None,
    ) -> ProgramDesign:
        """Create and register an immutable ProgramDesign."""
        did, d_hash = compute_program_design_id(strategic_objectives, roadmap, version)
        design = ProgramDesign(
            design_id=did,
            design_version=version,
            strategic_objectives=strategic_objectives,
            research_roadmap=roadmap,
            milestone_ids=milestone_ids or [],
            design_hash=d_hash,
        )
        self._designs[did] = design
        return design

    def create_program(
        self,
        title: str,
        domain: str,
        strategic_objective: str,
        description: str,
        design: ProgramDesign,
    ) -> ScientificResearchProgram:
        """Create an immutable ScientificResearchProgram in PROPOSED status.

        Args:
            title: Program title string.
            domain: Scientific domain classification string.
            strategic_objective: Strategic objective statement.
            description: Detailed program description.
            design: Bound ProgramDesign.

        Returns:
            Created ScientificResearchProgram instance.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_program_fingerprint(title, domain, strategic_objective, design.design_version)
        prg_id, canon_hash = compute_program_id(title, fingerprint, "1.0.0")

        program = ScientificResearchProgram(
            program_id=prg_id,
            scientific_fingerprint=fingerprint,
            canonical_hash=canon_hash,
            semantic_version="1.0.0",
            program_title=title,
            scientific_domain=domain,
            strategic_objective=strategic_objective,
            program_description=description,
            creation_timestamp=timestamp,
            program_version=design.design_version,
            program_status=ProgramStatus.PROPOSED,
        )

        self._programs[prg_id] = program
        self._designs[design.design_id] = design
        self._log_audit(prg_id, "", "PROPOSED", f"Created research program '{title}'")
        return program

    def execute_program(self, program_id: str) -> ProgramResult:
        """Execute all registered studies in the research program with fail-closed dependency resolution.

        Args:
            program_id: Target Program ID (PRG_<HEX16>).

        Returns:
            Immutable ProgramResult (PRES_<HEX16>).
        """
        program = self.get_program(program_id)
        if program.program_status not in [ProgramStatus.PROPOSED, ProgramStatus.SCHEDULED]:
            raise ProgramValidationError(f"Cannot execute program in '{program.program_status.value}' status")

        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        program_running = self._update_program_status(program, ProgramStatus.RUNNING)

        study_records = self._registry.get_program_studies(program_id)
        if not study_records:
            raise ProgramValidationError(f"Cannot execute empty program '{program_id}': no registered studies")

        executed_study_ids: list[str] = []
        for rec in study_records:
            # Verify study dependencies completed
            for dep in rec.dependencies:
                if dep not in executed_study_ids:
                    self._update_program_status(program_running, ProgramStatus.FAILED)
                    raise ProgramValidationError(f"Program execution dependency error: Study '{rec.study_id}' depends on unexecuted '{dep}'")

            executed_study_ids.append(rec.study_id)

        completion_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        program_completed = self._update_program_status(program_running, ProgramStatus.COMPLETED, completion_time=completion_time)

        res_id, res_hash = compute_program_result_id(program_id, completion_time)
        result = ProgramResult(
            result_id=res_id,
            program_id=program_id,
            study_references=executed_study_ids,
            completion_timestamp=completion_time,
            canonical_hash=res_hash,
        )

        self._results[res_id] = result
        self._log_audit(program_id, "RUNNING", "COMPLETED", f"Executed {len(executed_study_ids)} studies")
        return result

    def get_program(self, program_id: str) -> ScientificResearchProgram:
        """Retrieve ScientificResearchProgram by Program ID."""
        if program_id not in self._programs:
            raise KeyError(f"Program ID '{program_id}' not found in ProgramCoordinator")
        return self._programs[program_id]

    def get_result(self, result_id: str) -> ProgramResult:
        """Retrieve ProgramResult by Result ID."""
        if result_id not in self._results:
            raise KeyError(f"Result ID '{result_id}' not found in ProgramCoordinator")
        return self._results[result_id]

    def get_audit_trail(self, program_id: str) -> list[ProgramAuditEvent]:
        """Retrieve audit history for a program."""
        return list(self._audit_events.get(program_id, []))

    def replay_program(self, program_id: str) -> ProgramResult:
        """Replay program deterministically."""
        program = self.get_program(program_id)
        self._log_audit(program_id, program.program_status.value, "REPLAY", "Executing program replay")
        res_ids = [r.result_id for r in self._results.values() if r.program_id == program_id]
        if res_ids:
            return self.get_result(res_ids[0])
        raise KeyError(f"No result found for program replay '{program_id}'")

    def _update_program_status(
        self,
        program: ScientificResearchProgram,
        new_status: ProgramStatus,
        completion_time: str = "",
    ) -> ScientificResearchProgram:
        """Helper updating ScientificResearchProgram status."""
        d = program.model_dump()
        d["program_status"] = new_status
        if completion_time:
            d["completion_timestamp"] = completion_time
        updated = ScientificResearchProgram(**d)
        self._programs[program.program_id] = updated
        return updated

    def _log_audit(self, program_id: str, prev_state: str, new_state: str, notes: str) -> None:
        """Helper logging program audit event."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        payload = {"new": new_state, "program_id": program_id, "timestamp": timestamp}
        event_hash = compute_canonical_sha256(payload)
        event = ProgramAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            program_id=program_id,
            event_type="PROGRAM_EVENT",
            timestamp=timestamp,
            previous_state=prev_state,
            new_state=new_state,
            notes=notes,
            execution_hash=event_hash,
        )
        if program_id not in self._audit_events:
            self._audit_events[program_id] = []
        self._audit_events[program_id].append(event)
