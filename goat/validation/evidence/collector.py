"""
Project GOAT v0.7 — Evidence Collector

Collects and organizes validation evidence from experiments, studies,
consensus, and execution outcomes.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.validation.evidence.models import ValidationEvidence, compute_evidence_id


class EvidenceCollector:
    """Collects validation evidence from multiple scientific subsystem sources.

    The collector does NOT perform scientific reasoning. It collects,
    indexes, and organizes evidence deterministically.
    """

    def __init__(self) -> None:
        self._evidence: dict[str, ValidationEvidence] = {}
        self._hypothesis_evidence: dict[str, list[str]] = {}  # hyp_id -> [evidence_ids]

    def collect_from_experiment(
        self,
        validation_run_id: str,
        hypothesis_id: str,
        experiment_reference: str,
        confidence: float = 0.5,
        weight: float = 1.0,
        supports: bool = True,
        notes: str = "",
    ) -> ValidationEvidence:
        """Collect evidence from an experiment outcome.

        Args:
            validation_run_id: Parent Validation Run ID.
            hypothesis_id: Target Hypothesis ID.
            experiment_reference: Source Experiment ID.
            confidence: Evidence confidence [0.0, 1.0].
            weight: Evidence weight.
            supports: Whether evidence supports the hypothesis.
            notes: Optional notes.

        Returns:
            Immutable ValidationEvidence.
        """
        return self._create_evidence(
            validation_run_id=validation_run_id,
            hypothesis_id=hypothesis_id,
            experiment_reference=experiment_reference,
            evidence_type="experiment",
            confidence=confidence,
            weight=weight,
            supports=supports,
            notes=notes,
        )

    def collect_from_study(
        self,
        validation_run_id: str,
        hypothesis_id: str,
        study_reference: str,
        confidence: float = 0.5,
        weight: float = 1.0,
        supports: bool = True,
        notes: str = "",
    ) -> ValidationEvidence:
        """Collect evidence from a study outcome."""
        return self._create_evidence(
            validation_run_id=validation_run_id,
            hypothesis_id=hypothesis_id,
            study_reference=study_reference,
            evidence_type="study",
            confidence=confidence,
            weight=weight,
            supports=supports,
            notes=notes,
        )

    def collect_from_consensus(
        self,
        validation_run_id: str,
        hypothesis_id: str,
        consensus_reference: str,
        confidence: float = 0.5,
        weight: float = 1.5,
        supports: bool = True,
        notes: str = "",
    ) -> ValidationEvidence:
        """Collect evidence from a consensus outcome (higher default weight)."""
        return self._create_evidence(
            validation_run_id=validation_run_id,
            hypothesis_id=hypothesis_id,
            consensus_reference=consensus_reference,
            evidence_type="consensus",
            confidence=confidence,
            weight=weight,
            supports=supports,
            notes=notes,
        )

    def collect_from_execution(
        self,
        validation_run_id: str,
        hypothesis_id: str,
        execution_reference: str,
        confidence: float = 0.5,
        weight: float = 1.0,
        supports: bool = True,
        notes: str = "",
    ) -> ValidationEvidence:
        """Collect evidence from an execution outcome."""
        return self._create_evidence(
            validation_run_id=validation_run_id,
            hypothesis_id=hypothesis_id,
            execution_reference=execution_reference,
            evidence_type="execution",
            confidence=confidence,
            weight=weight,
            supports=supports,
            notes=notes,
        )

    def get_evidence(self, evidence_id: str) -> ValidationEvidence:
        """Retrieve evidence by ID.

        Raises:
            KeyError: If evidence_id not found.
        """
        if evidence_id not in self._evidence:
            raise KeyError(f"Evidence ID '{evidence_id}' not found in EvidenceCollector")
        return self._evidence[evidence_id]

    def get_evidence_for_hypothesis(self, hypothesis_id: str) -> list[ValidationEvidence]:
        """Retrieve all evidence collected for a hypothesis, in insertion order."""
        evidence_ids = self._hypothesis_evidence.get(hypothesis_id, [])
        return [self._evidence[eid] for eid in evidence_ids]

    @property
    def evidence_count(self) -> int:
        """Total number of evidence records collected."""
        return len(self._evidence)

    def _create_evidence(
        self,
        validation_run_id: str,
        hypothesis_id: str,
        evidence_type: str,
        confidence: float,
        weight: float,
        supports: bool,
        notes: str,
        experiment_reference: str = "",
        study_reference: str = "",
        consensus_reference: str = "",
        execution_reference: str = "",
    ) -> ValidationEvidence:
        """Internal helper to create and register evidence."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Build reference for ID computation
        ref = experiment_reference or study_reference or consensus_reference or execution_reference or "unknown"
        evidence_id, evidence_hash = compute_evidence_id(
            validation_run_id=validation_run_id,
            experiment_reference=ref,
            evidence_type=evidence_type,
            timestamp=timestamp,
        )

        evidence = ValidationEvidence(
            evidence_id=evidence_id,
            evidence_hash=evidence_hash,
            validation_run_id=validation_run_id,
            experiment_reference=experiment_reference,
            study_reference=study_reference,
            consensus_reference=consensus_reference,
            execution_reference=execution_reference,
            evidence_type=evidence_type,
            confidence=confidence,
            weight=weight,
            supports_hypothesis=supports,
            notes=notes,
            timestamp=timestamp,
        )

        self._evidence[evidence_id] = evidence

        if hypothesis_id not in self._hypothesis_evidence:
            self._hypothesis_evidence[hypothesis_id] = []
        self._hypothesis_evidence[hypothesis_id].append(evidence_id)

        return evidence
