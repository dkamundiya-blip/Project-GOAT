"""
Project GOAT v0.7 — Scientific Research Execution Engine

Implements ScientificResearchExecutionEngine for consuming Research Schedules,
coordinating deterministic task execution lifecycle, generating execution events,
and supporting replay.

The engine SHALL coordinate execution only.
Actual scientific computation remains delegated to downstream engines.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.execution.enums import ExecutionState
from goat.execution.event import ExecutionEvent, compute_event_id
from goat.execution.history import ExecutionHistory
from goat.execution.model import (
    ScientificExecutionSession,
    compute_session_fingerprint,
    compute_session_id,
)
from goat.scheduling.enums import ScheduleExecutionState
from goat.scheduling.model import ResearchSchedule
from goat.scheduling.task import ScheduledTask


# ---------------------------------------------------------------------------
# Valid execution state transitions — deterministic enforcement
# ---------------------------------------------------------------------------
VALID_EXECUTION_TRANSITIONS: dict[ExecutionState, list[ExecutionState]] = {
    ExecutionState.CREATED: [
        ExecutionState.QUEUED,
        ExecutionState.CANCELLED,
    ],
    ExecutionState.QUEUED: [
        ExecutionState.READY,
        ExecutionState.CANCELLED,
    ],
    ExecutionState.READY: [
        ExecutionState.STARTED,
        ExecutionState.CANCELLED,
    ],
    ExecutionState.STARTED: [
        ExecutionState.RUNNING,
        ExecutionState.FAILED,
        ExecutionState.CANCELLED,
    ],
    ExecutionState.RUNNING: [
        ExecutionState.COMPLETED,
        ExecutionState.PAUSED,
        ExecutionState.FAILED,
        ExecutionState.CANCELLED,
    ],
    ExecutionState.PAUSED: [
        ExecutionState.RUNNING,
        ExecutionState.CANCELLED,
    ],
    ExecutionState.COMPLETED: [],  # Terminal state
    ExecutionState.FAILED: [
        ExecutionState.CANCELLED,
    ],
    ExecutionState.CANCELLED: [],  # Terminal state
}


class ScientificExecutionValidationError(ValueError):
    """Raised when execution validation fails (fail-closed)."""
    pass


class ScientificResearchExecutionEngine:
    """Master engine consuming Research Schedules and coordinating deterministic task execution.

    The engine:
    - Consumes ResearchSchedule + ScheduledTask list from the scheduling module.
    - Creates ScientificExecutionSession instances.
    - Transitions task states through the execution lifecycle.
    - Generates ExecutionEvent for every state change (append-only).
    - Maintains ExecutionHistory for replay and audit.

    The engine SHALL NOT execute actual scientific computation, modify schedules,
    plans, or priorities.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ScientificExecutionSession] = {}
        self._task_states: dict[str, ExecutionState] = {}  # stk_id -> current state
        self._history = ExecutionHistory()
        self._event_sequence: int = 0  # Monotonic event counter for deterministic timestamps

    @property
    def history(self) -> ExecutionHistory:
        """Access the append-only execution history."""
        return self._history

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------

    def create_session(
        self,
        schedule: ResearchSchedule,
        tasks: list[ScheduledTask],
        version: str = "1.0.0",
    ) -> ScientificExecutionSession:
        """Create a deterministic ScientificExecutionSession from a ResearchSchedule.

        Args:
            schedule: Immutable ResearchSchedule instance.
            tasks: List of ScheduledTask instances belonging to the schedule.
            version: Semantic version string.

        Returns:
            Immutable ScientificExecutionSession.

        Raises:
            ScientificExecutionValidationError: If schedule is invalid or session already exists.
        """
        if not tasks:
            raise ScientificExecutionValidationError(
                f"Cannot create execution session for schedule '{schedule.schedule_id}': no tasks"
            )

        # Validate all tasks reference the schedule
        for task in tasks:
            if task.parent_schedule_id != schedule.schedule_id:
                raise ScientificExecutionValidationError(
                    f"Task '{task.task_schedule_id}' has parent_schedule_id "
                    f"'{task.parent_schedule_id}' but expected '{schedule.schedule_id}'"
                )

        # Compute session identity
        executed_task_ids = [t.task_schedule_id for t in sorted(tasks, key=lambda t: t.execution_position)]
        fingerprint = compute_session_fingerprint(
            source_schedule_id=schedule.schedule_id,
            executed_task_ids=executed_task_ids,
            version=version,
        )
        session_id, canon_hash = compute_session_id(fingerprint, version)

        # Validate no duplicate session IDs
        if session_id in self._sessions:
            raise ScientificExecutionValidationError(
                f"Duplicate Session ID '{session_id}' — session already exists"
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        session = ScientificExecutionSession(
            session_id=session_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            semantic_version=version,
            creation_timestamp=timestamp,
            source_schedule_id=schedule.schedule_id,
            executed_task_ids=executed_task_ids,
            session_status=ExecutionState.CREATED,
            start_timestamp="",
            end_timestamp="",
            audit_metadata={
                "source_schedule_id": schedule.schedule_id,
                "task_count": len(tasks),
            },
        )

        # Register session and initialize task states
        self._sessions[session.session_id] = session
        for task in tasks:
            self._task_states[task.task_schedule_id] = ExecutionState.CREATED

        return session

    # ------------------------------------------------------------------
    # Task lifecycle management
    # ------------------------------------------------------------------

    def transition_task(
        self,
        session_id: str,
        scheduled_task_id: str,
        target_state: ExecutionState,
        event_metadata: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        """Transition a scheduled task to a new execution state, generating an event.

        Args:
            session_id: Session ID (SES_<HEX16>).
            scheduled_task_id: Scheduled Task ID (STK_<HEX16>).
            target_state: Target ExecutionState.
            event_metadata: Optional metadata for the event.

        Returns:
            Immutable ExecutionEvent recording the transition.

        Raises:
            ScientificExecutionValidationError: If transition is invalid.
            KeyError: If session or task not found.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session ID '{session_id}' not found")

        if scheduled_task_id not in self._task_states:
            raise ScientificExecutionValidationError(
                f"Scheduled Task ID '{scheduled_task_id}' not registered in execution engine"
            )

        current_state = self._task_states[scheduled_task_id]
        self.validate_state_transition(current_state, target_state)

        # Generate deterministic event
        self._event_sequence += 1
        event_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        event_type = f"task_{current_state.value}_to_{target_state.value}"

        event_id, event_hash = compute_event_id(
            session_id=session_id,
            scheduled_task_id=scheduled_task_id,
            event_type=event_type,
            event_timestamp=event_timestamp,
        )

        # Validate no duplicate event IDs
        try:
            self._history.get_event(event_id)
            raise ScientificExecutionValidationError(
                f"Duplicate Event ID '{event_id}' — event already exists"
            )
        except KeyError:
            pass  # Expected: event doesn't exist yet

        event = ExecutionEvent(
            event_id=event_id,
            parent_session_id=session_id,
            scheduled_task_id=scheduled_task_id,
            event_type=event_type,
            event_timestamp=event_timestamp,
            previous_state=current_state,
            current_state=target_state,
            event_hash=event_hash,
            event_metadata=event_metadata or {},
        )

        # Update state and record event
        self._task_states[scheduled_task_id] = target_state
        self._history.append(event)

        return event

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start_session(self, session_id: str) -> ScientificExecutionSession:
        """Mark session as started with a start timestamp.

        Returns:
            Updated (new) immutable session.
        """
        session = self.get_session(session_id)
        if session.session_status != ExecutionState.CREATED:
            raise ScientificExecutionValidationError(
                f"Cannot start session '{session_id}': current status is '{session.session_status.value}', expected 'created'"
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated = ScientificExecutionSession(
            session_id=session.session_id,
            canonical_hash=session.canonical_hash,
            scientific_fingerprint=session.scientific_fingerprint,
            semantic_version=session.semantic_version,
            creation_timestamp=session.creation_timestamp,
            source_schedule_id=session.source_schedule_id,
            executed_task_ids=list(session.executed_task_ids),
            session_status=ExecutionState.RUNNING,
            start_timestamp=timestamp,
            end_timestamp="",
            audit_metadata=dict(session.audit_metadata),
        )
        self._sessions[session_id] = updated
        return updated

    def complete_session(self, session_id: str) -> ScientificExecutionSession:
        """Mark session as completed with an end timestamp.

        Returns:
            Updated (new) immutable session.
        """
        session = self.get_session(session_id)
        if session.session_status != ExecutionState.RUNNING:
            raise ScientificExecutionValidationError(
                f"Cannot complete session '{session_id}': current status is '{session.session_status.value}', expected 'running'"
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated = ScientificExecutionSession(
            session_id=session.session_id,
            canonical_hash=session.canonical_hash,
            scientific_fingerprint=session.scientific_fingerprint,
            semantic_version=session.semantic_version,
            creation_timestamp=session.creation_timestamp,
            source_schedule_id=session.source_schedule_id,
            executed_task_ids=list(session.executed_task_ids),
            session_status=ExecutionState.COMPLETED,
            start_timestamp=session.start_timestamp,
            end_timestamp=timestamp,
            audit_metadata=dict(session.audit_metadata),
        )
        self._sessions[session_id] = updated
        return updated

    def fail_session(self, session_id: str) -> ScientificExecutionSession:
        """Mark session as failed with an end timestamp.

        Returns:
            Updated (new) immutable session.
        """
        session = self.get_session(session_id)
        if session.session_status != ExecutionState.RUNNING:
            raise ScientificExecutionValidationError(
                f"Cannot fail session '{session_id}': current status is '{session.session_status.value}', expected 'running'"
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated = ScientificExecutionSession(
            session_id=session.session_id,
            canonical_hash=session.canonical_hash,
            scientific_fingerprint=session.scientific_fingerprint,
            semantic_version=session.semantic_version,
            creation_timestamp=session.creation_timestamp,
            source_schedule_id=session.source_schedule_id,
            executed_task_ids=list(session.executed_task_ids),
            session_status=ExecutionState.FAILED,
            start_timestamp=session.start_timestamp,
            end_timestamp=timestamp,
            audit_metadata=dict(session.audit_metadata),
        )
        self._sessions[session_id] = updated
        return updated

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_session(self, session_id: str) -> ScientificExecutionSession:
        """Retrieve ScientificExecutionSession by Session ID.

        Raises:
            KeyError: If session_id is not found.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session ID '{session_id}' not found in ScientificResearchExecutionEngine")
        return self._sessions[session_id]

    def get_task_state(self, scheduled_task_id: str) -> ExecutionState:
        """Retrieve current execution state for a scheduled task.

        Raises:
            KeyError: If scheduled_task_id is not registered.
        """
        if scheduled_task_id not in self._task_states:
            raise KeyError(f"Scheduled Task ID '{scheduled_task_id}' not registered")
        return self._task_states[scheduled_task_id]

    def get_events_for_session(self, session_id: str) -> list[ExecutionEvent]:
        """Retrieve all events for a session in chronological order."""
        return self._history.get_events_for_session(session_id)

    def get_events_for_task(self, scheduled_task_id: str) -> list[ExecutionEvent]:
        """Retrieve all events for a task in chronological order."""
        return self._history.get_events_for_task(scheduled_task_id)

    # ------------------------------------------------------------------
    # State transition validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_state_transition(
        current: ExecutionState,
        target: ExecutionState,
    ) -> None:
        """Validate that a state transition is deterministically legal.

        Raises:
            ScientificExecutionValidationError: If the transition is invalid.
        """
        allowed = VALID_EXECUTION_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise ScientificExecutionValidationError(
                f"Invalid execution state transition: {current.value} -> {target.value}"
            )

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    def replay_session(self, session_id: str) -> tuple[ScientificExecutionSession, list[ExecutionEvent]]:
        """Replay execution session events deterministically.

        Args:
            session_id: Target Session ID (SES_<HEX16>).

        Returns:
            Tuple of (ScientificExecutionSession, list of ExecutionEvents in chronological order).
        """
        session = self.get_session(session_id)
        events = self.get_events_for_session(session_id)
        return session, events

    # ------------------------------------------------------------------
    # Integrity verification
    # ------------------------------------------------------------------

    def verify_session_integrity(self, session: ScientificExecutionSession) -> bool:
        """Verify that a session's canonical hash matches recomputation.

        Returns:
            True if integrity check passes.

        Raises:
            ScientificExecutionValidationError: If hash mismatch detected.
        """
        _, expected_hash = compute_session_id(
            session.scientific_fingerprint, session.semantic_version
        )
        if expected_hash != session.canonical_hash:
            raise ScientificExecutionValidationError(
                f"Canonical hash mismatch for session '{session.session_id}': "
                f"expected '{expected_hash}', got '{session.canonical_hash}'"
            )
        return True

    def verify_history_integrity(self) -> bool:
        """Verify the integrity of the entire execution history chain.

        Returns:
            True if integrity is valid.
        """
        return self._history.verify_integrity()
