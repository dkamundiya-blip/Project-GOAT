"""
Project GOAT v0.7 — Execution History

Implements append-only ExecutionHistory for chronological event tracking,
event lookup, replay support, and integrity verification.
"""

from __future__ import annotations

from goat.execution.event import ExecutionEvent
from goat.research.edge.canonical import compute_canonical_sha256


class ExecutionHistory:
    """Append-only chronological execution event log.

    Responsibilities:
    - Append-only event storage (events can never be removed or modified).
    - Chronological ordering.
    - Event lookup by ID, task, or session.
    - Replay support via ordered event traversal.
    - Integrity verification via chain hashing.
    """

    def __init__(self) -> None:
        self._events: list[ExecutionEvent] = []
        self._event_index: dict[str, ExecutionEvent] = {}  # event_id -> event
        self._task_events: dict[str, list[ExecutionEvent]] = {}  # task_id -> events
        self._session_events: dict[str, list[ExecutionEvent]] = {}  # session_id -> events
        self._chain_hash: str = ""  # Rolling integrity hash

    def append(self, event: ExecutionEvent) -> None:
        """Append an execution event to the history (append-only).

        Args:
            event: Immutable ExecutionEvent to record.

        Raises:
            ValueError: If event_id already exists (duplicate rejection).
        """
        if event.event_id in self._event_index:
            raise ValueError(f"Duplicate Event ID '{event.event_id}' — history is append-only")

        self._events.append(event)
        self._event_index[event.event_id] = event

        # Index by task
        if event.scheduled_task_id not in self._task_events:
            self._task_events[event.scheduled_task_id] = []
        self._task_events[event.scheduled_task_id].append(event)

        # Index by session
        if event.parent_session_id not in self._session_events:
            self._session_events[event.parent_session_id] = []
        self._session_events[event.parent_session_id].append(event)

        # Update chain hash for integrity verification
        self._chain_hash = compute_canonical_sha256({
            "previous_chain_hash": self._chain_hash,
            "event_id": event.event_id,
            "event_hash": event.event_hash,
        })

    def get_event(self, event_id: str) -> ExecutionEvent:
        """Retrieve an event by Event ID.

        Raises:
            KeyError: If event_id is not found.
        """
        if event_id not in self._event_index:
            raise KeyError(f"Event ID '{event_id}' not found in ExecutionHistory")
        return self._event_index[event_id]

    def get_events_for_task(self, scheduled_task_id: str) -> list[ExecutionEvent]:
        """Retrieve all events for a given scheduled task, in chronological order."""
        return list(self._task_events.get(scheduled_task_id, []))

    def get_events_for_session(self, session_id: str) -> list[ExecutionEvent]:
        """Retrieve all events for a given session, in chronological order."""
        return list(self._session_events.get(session_id, []))

    def get_all_events(self) -> list[ExecutionEvent]:
        """Return all events in chronological (append) order."""
        return list(self._events)

    def get_chain_hash(self) -> str:
        """Return the current rolling integrity chain hash."""
        return self._chain_hash

    @property
    def event_count(self) -> int:
        """Total number of recorded events."""
        return len(self._events)

    def replay(self) -> list[ExecutionEvent]:
        """Replay the complete execution history in chronological order.

        Returns:
            List of all ExecutionEvents in the order they were appended.
        """
        return list(self._events)

    def verify_integrity(self) -> bool:
        """Verify the integrity of the event chain by recomputing chain hashes.

        Returns:
            True if integrity is valid.

        Raises:
            ValueError: If chain hash mismatch detected.
        """
        recomputed_hash = ""
        for event in self._events:
            recomputed_hash = compute_canonical_sha256({
                "previous_chain_hash": recomputed_hash,
                "event_id": event.event_id,
                "event_hash": event.event_hash,
            })

        if recomputed_hash != self._chain_hash:
            raise ValueError(
                f"ExecutionHistory integrity violation: "
                f"expected chain hash '{self._chain_hash}', recomputed '{recomputed_hash}'"
            )
        return True
