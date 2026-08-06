"""
Project GOAT v0.8 — Archive Index Engine

Builds replay-safe deterministic secondary indexes across time, subsystem, entity_type, entity_id, signal_id, execution_id, portfolio_id, broker_id, instrument, market_regime, session, and date.
"""

from __future__ import annotations

from typing import Any

from goat.archive.core.enums import ArchiveEntityType, ArchiveSubsystemOrigin
from goat.archive.core.models import ArchiveRecord


class ArchiveIndexEngine:
    """Engine managing replay-safe multi-attribute secondary indexes."""

    def __init__(self):
        self._by_subsystem: dict[ArchiveSubsystemOrigin, list[ArchiveRecord]] = {}
        self._by_entity_type: dict[ArchiveEntityType, list[ArchiveRecord]] = {}
        self._by_entity_id: dict[str, list[ArchiveRecord]] = {}
        self._by_instrument: dict[str, list[ArchiveRecord]] = {}
        self._by_signal_id: dict[str, list[ArchiveRecord]] = {}
        self._by_execution_id: dict[str, list[ArchiveRecord]] = {}

    def index_record(self, record: ArchiveRecord) -> None:
        """Index an ArchiveRecord across all secondary attribute keys."""
        # Subsystem index
        self._by_subsystem.setdefault(record.source_subsystem, []).append(record)

        # Entity type index
        self._by_entity_type.setdefault(record.entity_type, []).append(record)

        # Entity ID index
        self._by_entity_id.setdefault(record.entity_id, []).append(record)

        # Payload attribute indexing
        payload = record.payload
        if "instrument" in payload:
            inst = str(payload["instrument"]).upper()
            self._by_instrument.setdefault(inst, []).append(record)

        if "signal_id" in payload:
            sig = str(payload["signal_id"])
            self._by_signal_id.setdefault(sig, []).append(record)

        if "execution_id" in payload:
            exc = str(payload["execution_id"])
            self._by_execution_id.setdefault(exc, []).append(record)

    def query_by_subsystem(self, subsystem: ArchiveSubsystemOrigin | str) -> list[ArchiveRecord]:
        sub_enum = (
            ArchiveSubsystemOrigin(str(subsystem).upper())
            if not isinstance(subsystem, ArchiveSubsystemOrigin)
            else subsystem
        )
        return list(self._by_subsystem.get(sub_enum, []))

    def query_by_entity_type(self, entity_type: ArchiveEntityType | str) -> list[ArchiveRecord]:
        type_enum = (
            ArchiveEntityType(str(entity_type).upper())
            if not isinstance(entity_type, ArchiveEntityType)
            else entity_type
        )
        return list(self._by_entity_type.get(type_enum, []))

    def query_by_entity_id(self, entity_id: str) -> list[ArchiveRecord]:
        return list(self._by_entity_id.get(entity_id, []))

    def query_by_instrument(self, instrument: str) -> list[ArchiveRecord]:
        return list(self._by_instrument.get(str(instrument).upper(), []))
