"""
Project GOAT v0.8 — Execution Lifecycle Engine

Tracks execution state transitions across CREATED, VALIDATED, READY, DISPATCHED,
ACKNOWLEDGED, PARTIALLY_FILLED, FILLED, REJECTED, CANCELLED, and FAILED.
Every state transition is immutable and auditable.
"""

from __future__ import annotations

import datetime

from goat.execution.core.canonical import compute_execution_lifecycle_id
from goat.execution.core.enums import ExecutionState
from goat.execution.core.models import ExecutionLifecycle

VALID_TRANSITIONS: dict[ExecutionState, set[ExecutionState]] = {
    ExecutionState.CREATED: {ExecutionState.VALIDATED, ExecutionState.REJECTED, ExecutionState.FAILED},
    ExecutionState.VALIDATED: {ExecutionState.READY, ExecutionState.REJECTED, ExecutionState.FAILED},
    ExecutionState.READY: {ExecutionState.DISPATCHED, ExecutionState.CANCELLED, ExecutionState.FAILED},
    ExecutionState.DISPATCHED: {ExecutionState.ACKNOWLEDGED, ExecutionState.FILLED, ExecutionState.REJECTED, ExecutionState.FAILED},
    ExecutionState.ACKNOWLEDGED: {ExecutionState.PARTIALLY_FILLED, ExecutionState.FILLED, ExecutionState.REJECTED, ExecutionState.FAILED},
    ExecutionState.PARTIALLY_FILLED: {ExecutionState.FILLED, ExecutionState.CANCELLED, ExecutionState.FAILED},
    ExecutionState.FILLED: set(),
    ExecutionState.REJECTED: set(),
    ExecutionState.CANCELLED: set(),
    ExecutionState.FAILED: set(),
}


class ExecutionLifecycleEngine:
    """Engine managing execution state machine transitions and audit logging."""

    def __init__(self):
        self._current_states: dict[str, ExecutionState] = {}
        self._history: list[ExecutionLifecycle] = []

    def transition_state(
        self,
        intent_id: str,
        new_state: ExecutionState,
        explanation: str,
        timestamp: str | None = None,
    ) -> ExecutionLifecycle:
        """Transition intent_id to a new ExecutionState if valid, emitting an immutable ExecutionLifecycle record."""
        now_iso = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()
        current = self._current_states.get(intent_id, ExecutionState.CREATED)

        if current != new_state and current in VALID_TRANSITIONS:
            allowed = VALID_TRANSITIONS[current]
            if new_state not in allowed and new_state != ExecutionState.FAILED:
                # Force transition to FAILED if invalid transition requested
                explanation = f"Invalid state transition attempted from {current.value} to {new_state.value}: {explanation}"
                new_state = ExecutionState.FAILED

        self._current_states[intent_id] = new_state
        lifecycle_id, canonical_hash = compute_execution_lifecycle_id(intent_id, new_state.value, now_iso)

        entry = ExecutionLifecycle(
            lifecycle_id=lifecycle_id,
            intent_id=intent_id,
            state=new_state,
            previous_state=current if current != new_state else None,
            transition_timestamp=now_iso,
            explanation=explanation,
            metadata={},
            canonical_hash=canonical_hash,
        )
        self._history.append(entry)
        return entry

    def get_current_state(self, intent_id: str) -> ExecutionState:
        """Retrieve current ExecutionState for intent_id."""
        return self._current_states.get(intent_id, ExecutionState.CREATED)

    def get_history(self, intent_id: str | None = None) -> list[ExecutionLifecycle]:
        """Retrieve transition history filtered by intent_id if provided."""
        if intent_id:
            return [e for e in self._history if e.intent_id == intent_id]
        return list(self._history)
