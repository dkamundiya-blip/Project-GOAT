"""
Project GOAT v0.7 — Program Study Registry

Defines ProgramStudyRecord model and ProgramStudyRegistry for managing study collections within a research program.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProgramStudyRecord(BaseModel):
    """Immutable record representing a scientific study linked to a research program."""

    study_id: str = Field(..., description="Target Study ID (STD_<HEX16>)")
    program_id: str = Field(..., description="Parent Program ID (PRG_<HEX16>)")
    execution_order: int = Field(..., ge=1, description="1-indexed execution order position")
    registration_timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    dependencies: list[str] = Field(default_factory=list, description="Prerequisite Study IDs")

    class Config:
        frozen = True
        extra = "forbid"


class ProgramStudyRegistry:
    """Registry maintaining study ordering, dependencies, and lookup within a Scientific Research Program."""

    def __init__(self) -> None:
        self._program_studies: dict[str, list[ProgramStudyRecord]] = {}  # program_id -> list of ProgramStudyRecords

    def register_study(
        self,
        program_id: str,
        study_id: str,
        execution_order: int | None = None,
        dependencies: list[str] | None = None,
    ) -> ProgramStudyRecord:
        """Register a study into a program's study collection.

        Args:
            program_id: Target Program ID (PRG_<HEX16>).
            study_id: Target Study ID (STD_<HEX16>).
            execution_order: Optional order position integer.
            dependencies: Optional prerequisite Study IDs.

        Returns:
            Registered ProgramStudyRecord.
        """
        if program_id not in self._program_studies:
            self._program_studies[program_id] = []

        existing = self._program_studies[program_id]
        if any(r.study_id == study_id for r in existing):
            return [r for r in existing if r.study_id == study_id][0]

        order = execution_order or (len(existing) + 1)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        record = ProgramStudyRecord(
            study_id=study_id,
            program_id=program_id,
            execution_order=order,
            registration_timestamp=timestamp,
            dependencies=dependencies or [],
        )

        existing.append(record)
        existing.sort(key=lambda r: r.execution_order)
        return record

    def get_program_studies(self, program_id: str) -> list[ProgramStudyRecord]:
        """Retrieve ordered list of ProgramStudyRecords for a Program ID."""
        return list(self._program_studies.get(program_id, []))

    def remove_study(self, program_id: str, study_id: str) -> bool:
        """Remove a study from a program."""
        if program_id in self._program_studies:
            orig_len = len(self._program_studies[program_id])
            self._program_studies[program_id] = [r for r in self._program_studies[program_id] if r.study_id != study_id]
            return len(self._program_studies[program_id]) < orig_len
        return False
