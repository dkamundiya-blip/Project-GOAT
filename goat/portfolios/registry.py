"""
Project GOAT v0.7 — Portfolio Program Registry

Defines PortfolioProgramRecord model and PortfolioProgramRegistry for managing program collections within a research portfolio.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field


class PortfolioProgramRecord(BaseModel):
    """Immutable record representing a scientific research program linked to a portfolio."""

    program_id: str = Field(..., description="Target Program ID (PRG_<HEX16>)")
    portfolio_id: str = Field(..., description="Parent Portfolio ID (PFO_<HEX16>)")
    execution_order: int = Field(..., ge=1, description="1-indexed execution order position")
    registration_timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    dependencies: list[str] = Field(default_factory=list, description="Prerequisite Program IDs")

    class Config:
        frozen = True
        extra = "forbid"


class PortfolioProgramRegistry:
    """Registry maintaining program ordering, dependencies, and lookup within a Scientific Research Portfolio."""

    def __init__(self) -> None:
        self._portfolio_programs: dict[str, list[PortfolioProgramRecord]] = {}  # portfolio_id -> list of PortfolioProgramRecords

    def register_program(
        self,
        portfolio_id: str,
        program_id: str,
        execution_order: int | None = None,
        dependencies: list[str] | None = None,
    ) -> PortfolioProgramRecord:
        """Register a program into a portfolio's program collection.

        Args:
            portfolio_id: Target Portfolio ID (PFO_<HEX16>).
            program_id: Target Program ID (PRG_<HEX16>).
            execution_order: Optional order position integer.
            dependencies: Optional prerequisite Program IDs.

        Returns:
            Registered PortfolioProgramRecord.
        """
        if portfolio_id not in self._portfolio_programs:
            self._portfolio_programs[portfolio_id] = []

        existing = self._portfolio_programs[portfolio_id]
        if any(r.program_id == program_id for r in existing):
            return [r for r in existing if r.program_id == program_id][0]

        order = execution_order or (len(existing) + 1)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        record = PortfolioProgramRecord(
            program_id=program_id,
            portfolio_id=portfolio_id,
            execution_order=order,
            registration_timestamp=timestamp,
            dependencies=dependencies or [],
        )

        existing.append(record)
        existing.sort(key=lambda r: r.execution_order)
        return record

    def get_portfolio_programs(self, portfolio_id: str) -> list[PortfolioProgramRecord]:
        """Retrieve ordered list of PortfolioProgramRecords for a Portfolio ID."""
        return list(self._portfolio_programs.get(portfolio_id, []))

    def remove_program(self, portfolio_id: str, program_id: str) -> bool:
        """Remove a program from a portfolio."""
        if portfolio_id in self._portfolio_programs:
            orig_len = len(self._portfolio_programs[portfolio_id])
            self._portfolio_programs[portfolio_id] = [r for r in self._portfolio_programs[portfolio_id] if r.program_id != program_id]
            return len(self._portfolio_programs[portfolio_id]) < orig_len
        return False
