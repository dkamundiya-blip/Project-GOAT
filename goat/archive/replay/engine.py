"""
Project GOAT v0.8 — Deterministic Replay Engine

Reconstructs historical event streams in their exact original chronological sequence.
Enforces 100% deterministic fidelity: zero synthetic events, zero inferred data.
"""

from __future__ import annotations

from typing import Any

from goat.archive.core.canonical import (
    compute_replay_checkpoint_id,
    compute_replay_request_id,
    compute_replay_session_id,
)
from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin, ReplayStatus
from goat.archive.core.models import (
    ArchiveRecord,
    ReplayCheckpoint,
    ReplayRequest,
    ReplaySession,
)


class ReplayEngine:
    """Deterministic replay engine reconstructing event logs in exact chronological order."""

    def __init__(self):
        self._sessions: list[ReplaySession] = []
        self._checkpoints: list[ReplayCheckpoint] = []

    def create_replay_request(
        self,
        start_time: str,
        end_time: str,
        subsystems: list[ArchiveSubsystemOrigin | str] | None = None,
        entity_types: list[ArchiveEntityType | str] | None = None,
        instrument: str = "",
        session_id: str = "",
    ) -> ReplayRequest:
        """Create a deterministic ReplayRequest query specification."""
        parsed_sub = (
            [
                s if isinstance(s, ArchiveSubsystemOrigin) else ArchiveSubsystemOrigin(str(s).upper())
                for s in subsystems
            ]
            if subsystems
            else []
        )
        parsed_types = (
            [
                t if isinstance(t, ArchiveEntityType) else ArchiveEntityType(str(t).upper())
                for t in entity_types
            ]
            if entity_types
            else []
        )

        rrq_id, rrq_hash = compute_replay_request_id(start_time, end_time)

        return ReplayRequest(
            request_id=rrq_id,
            start_time=start_time,
            end_time=end_time,
            subsystems=parsed_sub,
            entity_types=parsed_types,
            instrument=instrument,
            session_id=session_id,
            canonical_hash=rrq_hash,
        )

    def execute_replay(
        self,
        request: ReplayRequest,
        records: list[ArchiveRecord],
        execution_timestamp: str,
    ) -> tuple[ReplaySession, list[ArchiveRecord], list[ReplayCheckpoint]]:
        """Filter records by request constraints and replay in exact chronological order."""
        filtered: list[ArchiveRecord] = []

        for record in records:
            # Time filter
            if record.timestamp < request.start_time or record.timestamp > request.end_time:
                continue

            # Subsystem filter
            if request.subsystems and record.source_subsystem not in request.subsystems:
                continue

            # Entity type filter
            if request.entity_types and record.entity_type not in request.entity_types:
                continue

            # Instrument filter
            if request.instrument and record.payload.get("instrument") != request.instrument:
                continue

            filtered.append(record)

        # Sort strictly by timestamp and archive_id to guarantee deterministic ordering
        filtered.sort(key=lambda r: (r.timestamp, r.archive_id))

        # Generate sequence checkpoints
        checkpoints: list[ReplayCheckpoint] = []
        for idx, rec in enumerate(filtered, start=1):
            rcp_id, rcp_hash = compute_replay_checkpoint_id(
                sequence=idx,
                record_id=rec.archive_id,
                timestamp=rec.timestamp,
            )
            cp = ReplayCheckpoint(
                checkpoint_id=rcp_id,
                sequence=idx,
                record_id=rec.archive_id,
                timestamp=rec.timestamp,
                canonical_hash=rcp_hash,
            )
            checkpoints.append(cp)
            self._checkpoints.append(cp)

        rps_id, rps_hash = compute_replay_session_id(request.request_id, execution_timestamp)

        session = ReplaySession(
            session_id=rps_id,
            request_id=request.request_id,
            records_replayed=len(filtered),
            start_time=request.start_time,
            end_time=request.end_time,
            status=ReplayStatus.COMPLETED,
            canonical_hash=rps_hash,
        )

        self._sessions.append(session)
        return session, filtered, checkpoints

    def get_all_sessions(self) -> list[ReplaySession]:
        return list(self._sessions)

    def get_all_checkpoints(self) -> list[ReplayCheckpoint]:
        return list(self._checkpoints)
