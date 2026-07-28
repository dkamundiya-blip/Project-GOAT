"""
Project GOAT v0.6 — Base Stage Validator Interface

Defines the abstract BaseStageValidator interface and evidence generation helpers for Stage A-G evaluators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import AtomicEvidenceRecord, EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import StageResult, ValidationStage


class BaseStageValidator(ABC):
    """Abstract base class for deterministic Stage A through G validation evaluators."""

    @property
    @abstractmethod
    def stage(self) -> ValidationStage:
        """The formal ValidationStage enum identifier for this validator."""

    @property
    @abstractmethod
    def prerequisite_stage(self) -> ValidationStage | None:
        """The required predecessor stage that must pass before evaluating this stage."""

    @abstractmethod
    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        **kwargs: Any,
    ) -> StageResult:
        """Execute stage evaluation and return deterministic StageResult."""

    def create_evidence_record(
        self,
        validation_run_id: str,
        edge_id: str,
        dimension_type: EvidenceDimensionType,
        dimension_key: str,
        partition_identity: str,
        sample_count: int,
        effect_size: float,
        raw_p_value: float,
        statistic_value: float,
        effect_size_type: str = "cohens_d",
        adjusted_q_value: float | None = None,
        confidence_interval: tuple[float, float] | None = None,
        context_metadata: dict[str, Any] | None = None,
    ) -> AtomicEvidenceRecord:
        """Helper for creating deterministic AtomicEvidenceRecord instances."""
        return AtomicEvidenceRecord(
            validation_run_id=validation_run_id,
            edge_id=edge_id,
            dimension_type=dimension_type,
            dimension_key=dimension_key,
            partition_identity=partition_identity,
            sample_count=sample_count,
            effect_size=effect_size,
            effect_size_type=effect_size_type,
            raw_p_value=raw_p_value,
            adjusted_q_value=adjusted_q_value,
            statistic_value=statistic_value,
            confidence_interval=confidence_interval,
            context_metadata=context_metadata or {},
        )
