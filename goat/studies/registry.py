"""
Project GOAT v0.7 — Study Experiment Registry

Defines StudyExperimentRecord model and StudyExperimentRegistry for managing experiment collections within a research study.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field


class StudyExperimentRecord(BaseModel):
    """Immutable record representing an experiment linked to a research study."""

    experiment_id: str = Field(..., description="Target Experiment ID (EXP_<HEX16>)")
    study_id: str = Field(..., description="Parent Study ID (STD_<HEX16>)")
    execution_order: int = Field(..., ge=1, description="1-indexed execution order position")
    registration_timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    dependencies: list[str] = Field(default_factory=list, description="Prerequisite Experiment IDs")

    class Config:
        frozen = True
        extra = "forbid"


class StudyExperimentRegistry:
    """Registry maintaining experiment ordering, dependencies, and lookup within a Scientific Study."""

    def __init__(self) -> None:
        self._study_experiments: dict[str, list[StudyExperimentRecord]] = {}  # study_id -> list of StudyExperimentRecords

    def register_experiment(
        self,
        study_id: str,
        experiment_id: str,
        execution_order: int | None = None,
        dependencies: list[str] | None = None,
    ) -> StudyExperimentRecord:
        """Register an experiment into a study's experiment collection.

        Args:
            study_id: Target Study ID (STD_<HEX16>).
            experiment_id: Target Experiment ID (EXP_<HEX16>).
            execution_order: Optional order position integer.
            dependencies: Optional prerequisite Experiment IDs.

        Returns:
            Registered StudyExperimentRecord.
        """
        if study_id not in self._study_experiments:
            self._study_experiments[study_id] = []

        existing = self._study_experiments[study_id]
        if any(r.experiment_id == experiment_id for r in existing):
            # Already registered
            return [r for r in existing if r.experiment_id == experiment_id][0]

        order = execution_order or (len(existing) + 1)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        record = StudyExperimentRecord(
            experiment_id=experiment_id,
            study_id=study_id,
            execution_order=order,
            registration_timestamp=timestamp,
            dependencies=dependencies or [],
        )

        existing.append(record)
        existing.sort(key=lambda r: r.execution_order)
        return record

    def get_study_experiments(self, study_id: str) -> list[StudyExperimentRecord]:
        """Retrieve ordered list of StudyExperimentRecords for a Study ID."""
        return list(self._study_experiments.get(study_id, []))

    def remove_experiment(self, study_id: str, experiment_id: str) -> bool:
        """Remove an experiment from a study."""
        if study_id in self._study_experiments:
            orig_len = len(self._study_experiments[study_id])
            self._study_experiments[study_id] = [r for r in self._study_experiments[study_id] if r.experiment_id != experiment_id]
            return len(self._study_experiments[study_id]) < orig_len
        return False
