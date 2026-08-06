"""
Project GOAT v0.8 — Trade Event Engine

Generates immutable, append-only, replayable TradeEvent log records across all 15 trade lifecycle event types.
"""

from __future__ import annotations

from typing import Any

from goat.lifecycle.core.canonical import compute_trade_event_id
from goat.lifecycle.core.enums import TradeEventType
from goat.lifecycle.core.models import TradeEvent


class TradeEventEngine:
    """Engine maintaining append-only replayable event streams for trade lifecycles."""

    def __init__(self):
        self._events: list[TradeEvent] = []  # Append-only list
        self._lifecycle_events: dict[str, list[TradeEvent]] = {}  # lifecycle_id -> list[TradeEvent]

    def record_event(
        self,
        lifecycle_id: str,
        event_type: TradeEventType | str,
        timestamp: str,
        details: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> TradeEvent:
        """Record an immutable append-only TradeEvent."""
        evt_type = TradeEventType(str(event_type).upper()) if not isinstance(event_type, TradeEventType) else event_type
        lid = str(lifecycle_id).strip()
        meta = metadata or {}

        event_id, canonical_hash = compute_trade_event_id(
            lifecycle_id=lid,
            event_type=evt_type.value,
            timestamp=timestamp,
        )

        event = TradeEvent(
            event_id=event_id,
            lifecycle_id=lid,
            event_type=evt_type,
            timestamp=timestamp,
            details=details or f"Event {evt_type.value} recorded",
            metadata=meta,
            canonical_hash=canonical_hash,
        )

        self._events.append(event)
        if lid not in self._lifecycle_events:
            self._lifecycle_events[lid] = []
        self._lifecycle_events[lid].append(event)

        return event

    def get_events_for_lifecycle(self, lifecycle_id: str) -> list[TradeEvent]:
        """Retrieve all events recorded for a specific lifecycle ID in chronological order."""
        return list(self._lifecycle_events.get(lifecycle_id, []))

    def get_all_events(self) -> list[TradeEvent]:
        """Retrieve full append-only event stream."""
        return list(self._events)
