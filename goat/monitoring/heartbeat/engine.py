"""
Project GOAT v0.8 — Heartbeat Engine

Manages subsystem heartbeat registration, sequence counter tracking, integrity verification, and replay streams.
"""

from __future__ import annotations

from typing import Any

from goat.monitoring.core.canonical import compute_heartbeat_id
from goat.monitoring.core.enums import SubsystemName
from goat.monitoring.core.models import HeartbeatRecord


class HeartbeatEngine:
    """Engine tracking heartbeat pulses, verifying sequence ordering, and maintaining sequence history."""

    def __init__(self):
        self._sequences: dict[SubsystemName, int] = {}
        self._history: list[HeartbeatRecord] = []

    def generate_heartbeat(
        self,
        subsystem_name: SubsystemName | str,
        timestamp: str,
        metadata: dict[str, Any] | None = None,
    ) -> HeartbeatRecord:
        """Generate and record a new sequential heartbeat pulse for a subsystem."""
        sub_enum = (
            SubsystemName(str(subsystem_name).upper())
            if not isinstance(subsystem_name, SubsystemName)
            else subsystem_name
        )

        current_seq = self._sequences.get(sub_enum, 0) + 1
        self._sequences[sub_enum] = current_seq

        hbt_id, hbt_hash = compute_heartbeat_id(
            subsystem_name=sub_enum.value,
            sequence=current_seq,
            timestamp=timestamp,
        )

        record = HeartbeatRecord(
            heartbeat_id=hbt_id,
            subsystem_name=sub_enum,
            sequence=current_seq,
            timestamp=timestamp,
            metadata=metadata or {},
            canonical_hash=hbt_hash,
        )

        self._history.append(record)
        return record

    def verify_heartbeat(self, record: HeartbeatRecord) -> bool:
        """Verify hash integrity and sequence validity of a heartbeat record."""
        _, expected_hash = compute_heartbeat_id(
            subsystem_name=record.subsystem_name.value,
            sequence=record.sequence,
            timestamp=record.timestamp,
        )
        return record.canonical_hash == expected_hash

    def get_latest_heartbeat(self, subsystem_name: SubsystemName | str) -> HeartbeatRecord | None:
        sub_enum = (
            SubsystemName(str(subsystem_name).upper())
            if not isinstance(subsystem_name, SubsystemName)
            else subsystem_name
        )
        for record in reversed(self._history):
            if record.subsystem_name == sub_enum:
                return record
        return None

    def get_history(self) -> list[HeartbeatRecord]:
        return list(self._history)
