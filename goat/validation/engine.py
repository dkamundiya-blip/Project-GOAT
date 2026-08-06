"""
Project GOAT v0.7 — Scientific Hypothesis Validation Engine

Master orchestrator implementing the full validation pipeline:
hypothesis → evidence → statistics → rules → decision → persist → report.

The engine does NOT generate trading signals. It validates whether a hypothesis
has sufficient scientific evidence to become an accepted research result.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.research.edge.canonical import compute_canonical_sha256
from goat.validation.core.enums import DecisionType, ValidationState
from goat.validation.core.hypothesis import (
    ScientificHypothesis,
    compute_hypothesis_fingerprint,
    compute_hypothesis_id,
)
from goat.validation.core.run import ValidationRun, compute_run_fingerprint, compute_run_id
from goat.validation.decisions.generator import DecisionGenerator
from goat.validation.decisions.models import ValidationDecision
from goat.validation.decisions.rules import ValidationRuleEngine, ValidationThresholds
from goat.validation.evidence.aggregator import EvidenceAggregator
from goat.validation.evidence.collector import EvidenceCollector
from goat.validation.evidence.models import ValidationEvidence
from goat.validation.reporting.generator import generate_validation_report
from goat.validation.reporting.models import ValidationReport
from goat.validation.statistics.calculator import StatisticalCalculator
from goat.validation.statistics.scores import ValidationScores


class ValidationEngineError(ValueError):
    """Raised when validation engine operations fail (fail-closed)."""
    pass


class ScientificHypothesisValidationEngine:
    """Master engine orchestrating the scientific hypothesis validation pipeline.

    Pipeline:
    1. Register hypothesis
    2. Submit evidence (experiment, study, consensus, execution)
    3. Run validation:
       a. Collect evidence
       b. Aggregate evidence
       c. Compute statistical scores
       d. Evaluate rules against thresholds
       e. Generate deterministic decision
       f. Create validation run record
    4. Persist all artifacts
    5. Generate report

    The engine does NOT modify frozen architecture, execute trades, or
    perform probabilistic inference.
    """

    def __init__(
        self,
        thresholds: ValidationThresholds | None = None,
    ) -> None:
        self._hypotheses: dict[str, ScientificHypothesis] = {}
        self._runs: dict[str, ValidationRun] = {}
        self._decisions: dict[str, ValidationDecision] = {}
        self._reports: dict[str, ValidationReport] = {}
        self._collector = EvidenceCollector()
        self._aggregator = EvidenceAggregator()
        self._calculator = StatisticalCalculator()
        self._rule_engine = ValidationRuleEngine(thresholds)
        self._decision_generator = DecisionGenerator()

    # ------------------------------------------------------------------
    # Hypothesis Registration
    # ------------------------------------------------------------------

    def register_hypothesis(
        self,
        title: str,
        description: str = "",
        originating_program: str = "",
        originating_experiment: str = "",
        originating_study: str = "",
        author: str = "system",
        assumptions: list[str] | None = None,
        expected_behavior: str = "",
        version: str = "1.0.0",
    ) -> ScientificHypothesis:
        """Register a new scientific hypothesis for validation.

        Args:
            title: Hypothesis title.
            description: Hypothesis description.
            originating_program: Source Program ID.
            originating_experiment: Source Experiment ID.
            originating_study: Source Study ID.
            author: Author identifier.
            assumptions: List of assumptions.
            expected_behavior: Expected observable behavior.
            version: Hypothesis version.

        Returns:
            Immutable ScientificHypothesis.

        Raises:
            ValidationEngineError: If hypothesis already exists or title is empty.
        """
        if not title.strip():
            raise ValidationEngineError("Hypothesis title cannot be empty")

        fingerprint = compute_hypothesis_fingerprint(
            title=title,
            originating_experiment=originating_experiment,
            originating_study=originating_study,
            version=version,
        )
        hyp_id, canon_hash = compute_hypothesis_id(fingerprint, version)

        if hyp_id in self._hypotheses:
            raise ValidationEngineError(f"Duplicate Hypothesis ID '{hyp_id}' — hypothesis already registered")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        hypothesis = ScientificHypothesis(
            hypothesis_id=hyp_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            hypothesis_version=version,
            title=title,
            description=description,
            originating_program=originating_program,
            originating_experiment=originating_experiment,
            originating_study=originating_study,
            author=author,
            creation_time=timestamp,
            assumptions=assumptions or [],
            expected_behavior=expected_behavior,
            validation_state=ValidationState.PENDING,
        )

        self._hypotheses[hyp_id] = hypothesis
        return hypothesis

    # ------------------------------------------------------------------
    # Evidence Submission
    # ------------------------------------------------------------------

    def submit_evidence(
        self,
        hypothesis_id: str,
        evidence_type: str = "experiment",
        experiment_reference: str = "",
        study_reference: str = "",
        consensus_reference: str = "",
        execution_reference: str = "",
        confidence: float = 0.5,
        weight: float = 1.0,
        supports: bool = True,
        notes: str = "",
    ) -> ValidationEvidence:
        """Submit evidence for a hypothesis.

        Args:
            hypothesis_id: Target Hypothesis ID.
            evidence_type: One of 'experiment', 'study', 'consensus', 'execution'.
            experiment_reference: Experiment ID if applicable.
            study_reference: Study ID if applicable.
            consensus_reference: Consensus ID if applicable.
            execution_reference: Execution ID if applicable.
            confidence: Evidence confidence [0.0, 1.0].
            weight: Evidence weight.
            supports: Whether evidence supports the hypothesis.
            notes: Optional notes.

        Returns:
            Immutable ValidationEvidence.

        Raises:
            ValidationEngineError: If hypothesis not found.
        """
        if hypothesis_id not in self._hypotheses:
            raise ValidationEngineError(f"Hypothesis '{hypothesis_id}' not registered")

        # Use a placeholder run ID for pre-run evidence collection
        placeholder_run_id = f"VRN_{'0' * 16}"

        if evidence_type == "experiment":
            return self._collector.collect_from_experiment(
                validation_run_id=placeholder_run_id,
                hypothesis_id=hypothesis_id,
                experiment_reference=experiment_reference,
                confidence=confidence,
                weight=weight,
                supports=supports,
                notes=notes,
            )
        elif evidence_type == "study":
            return self._collector.collect_from_study(
                validation_run_id=placeholder_run_id,
                hypothesis_id=hypothesis_id,
                study_reference=study_reference,
                confidence=confidence,
                weight=weight,
                supports=supports,
                notes=notes,
            )
        elif evidence_type == "consensus":
            return self._collector.collect_from_consensus(
                validation_run_id=placeholder_run_id,
                hypothesis_id=hypothesis_id,
                consensus_reference=consensus_reference,
                confidence=confidence,
                weight=weight,
                supports=supports,
                notes=notes,
            )
        elif evidence_type == "execution":
            return self._collector.collect_from_execution(
                validation_run_id=placeholder_run_id,
                hypothesis_id=hypothesis_id,
                execution_reference=execution_reference,
                confidence=confidence,
                weight=weight,
                supports=supports,
                notes=notes,
            )
        else:
            raise ValidationEngineError(f"Unknown evidence type: '{evidence_type}'")

    # ------------------------------------------------------------------
    # Validation Execution
    # ------------------------------------------------------------------

    def run_validation(
        self,
        hypothesis_id: str,
        replication_count: int = 0,
        cross_context_count: int = 0,
        consistent_periods: int = 0,
        total_periods: int = 0,
        execution_id: str = "",
        version: str = "1.0.0",
    ) -> ValidationRun:
        """Execute the full validation pipeline for a hypothesis.

        Pipeline:
        1. Collect evidence for the hypothesis
        2. Aggregate evidence
        3. Compute statistical scores
        4. Evaluate validation rules
        5. Generate deterministic decision
        6. Create ValidationRun record

        Args:
            hypothesis_id: Target Hypothesis ID.
            replication_count: Number of independent replications.
            cross_context_count: Number of cross-context confirmations.
            consistent_periods: Temporally consistent periods.
            total_periods: Total temporal periods.
            execution_id: Optional execution session ID.
            version: Version string.

        Returns:
            Immutable ValidationRun.

        Raises:
            ValidationEngineError: If hypothesis not found.
        """
        if hypothesis_id not in self._hypotheses:
            raise ValidationEngineError(f"Hypothesis '{hypothesis_id}' not registered")

        # Step 1: Collect evidence
        evidence_list = self._collector.get_evidence_for_hypothesis(hypothesis_id)
        evidence_ids = [e.evidence_id for e in evidence_list]

        # Step 2: Aggregate evidence
        evidence_summary = self._aggregator.compute_evidence_summary(evidence_list)

        # Step 3: Compute statistical scores
        scores = self._calculator.calculate_all_scores(
            evidence_list=evidence_list,
            evidence_summary=evidence_summary,
            replication_count=replication_count,
            cross_context_count=cross_context_count,
            consistent_periods=consistent_periods,
            total_periods=total_periods,
        )

        # Step 4: Evaluate rules
        rule_result = self._rule_engine.evaluate(
            scores=scores,
            evidence_count=len(evidence_list),
            evidence_summary=evidence_summary.get("overall", evidence_summary),
        )

        # Step 5: Generate decision
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Compute run identity
        fingerprint = compute_run_fingerprint(
            hypothesis_id=hypothesis_id,
            evidence_ids=evidence_ids,
            version=version,
        )
        run_id, canon_hash = compute_run_id(fingerprint, version)

        if run_id in self._runs:
            raise ValidationEngineError(f"Duplicate Validation Run ID '{run_id}'")

        decision = self._decision_generator.generate_decision(
            validation_run_id=run_id,
            scores=scores,
            rule_result=rule_result,
            evidence_ids=evidence_ids,
        )

        # Compute replay hash
        replay_payload = {
            "decision_id": decision.decision_id,
            "evidence_ids": sorted(evidence_ids),
            "hypothesis_id": hypothesis_id,
            "scores": {
                "agreement_score": scores.agreement_score,
                "confidence_score": scores.confidence_score,
                "evidence_score": scores.evidence_score,
                "overall_confidence": scores.overall_confidence,
                "reproducibility_score": scores.reproducibility_score,
                "robustness_score": scores.robustness_score,
                "stability_score": scores.stability_score,
                "validation_score": scores.validation_score,
            },
        }
        replay_hash = compute_canonical_sha256(replay_payload)

        # Step 6: Create validation run
        run = ValidationRun(
            validation_id=run_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            semantic_version=version,
            hypothesis_id=hypothesis_id,
            execution_id=execution_id,
            evidence_ids=evidence_ids,
            statistical_results={
                "confidence_score": scores.confidence_score,
                "evidence_score": scores.evidence_score,
                "agreement_score": scores.agreement_score,
                "reproducibility_score": scores.reproducibility_score,
                "robustness_score": scores.robustness_score,
                "stability_score": scores.stability_score,
                "validation_score": scores.validation_score,
                "overall_confidence": scores.overall_confidence,
            },
            evidence_summary=evidence_summary.get("overall", {}),
            confidence_metrics={
                "overall_confidence": scores.overall_confidence,
                "weighted_evidence_confidence": evidence_summary.get("overall", {}).get("weighted_confidence", 0.0),
            },
            validation_decision=decision.decision_type.value,
            decision_id=decision.decision_id,
            replay_hash=replay_hash,
            validation_state=ValidationState.DECIDED,
            creation_timestamp=timestamp,
            completion_timestamp=timestamp,
            audit_metadata={
                "evidence_count": len(evidence_list),
                "thresholds_passed": rule_result.get("passed_count", 0),
                "total_thresholds": rule_result.get("total_thresholds", 0),
            },
        )

        # Register artifacts
        self._runs[run_id] = run
        self._decisions[decision.decision_id] = decision

        # Generate report
        report = generate_validation_report(
            run=run,
            decision=decision,
            scores=scores,
            evidence_summary=evidence_summary,
            timestamp=timestamp,
        )
        self._reports[report.report_id] = report

        return run

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_hypothesis(self, hypothesis_id: str) -> ScientificHypothesis:
        """Retrieve hypothesis by ID.

        Raises:
            KeyError: If not found.
        """
        if hypothesis_id not in self._hypotheses:
            raise KeyError(f"Hypothesis ID '{hypothesis_id}' not found")
        return self._hypotheses[hypothesis_id]

    def get_validation_run(self, validation_id: str) -> ValidationRun:
        """Retrieve validation run by ID.

        Raises:
            KeyError: If not found.
        """
        if validation_id not in self._runs:
            raise KeyError(f"Validation Run ID '{validation_id}' not found")
        return self._runs[validation_id]

    def get_decision(self, decision_id: str) -> ValidationDecision:
        """Retrieve decision by ID.

        Raises:
            KeyError: If not found.
        """
        if decision_id not in self._decisions:
            raise KeyError(f"Decision ID '{decision_id}' not found")
        return self._decisions[decision_id]

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    def replay_validation(
        self, validation_id: str
    ) -> tuple[ValidationRun, list[ValidationEvidence], ValidationDecision]:
        """Replay a validation run deterministically.

        Args:
            validation_id: Validation Run ID.

        Returns:
            Tuple of (ValidationRun, evidence_list, ValidationDecision).

        Raises:
            KeyError: If validation run not found.
        """
        run = self.get_validation_run(validation_id)
        evidence_list = [
            self._collector.get_evidence(eid)
            for eid in run.evidence_ids
            if eid in self._collector._evidence
        ]
        decision = self._decisions.get(run.decision_id)
        if decision is None:
            raise KeyError(f"Decision '{run.decision_id}' not found for replay")
        return run, evidence_list, decision

    # ------------------------------------------------------------------
    # Integrity Verification
    # ------------------------------------------------------------------

    def verify_integrity(self, validation_id: str) -> bool:
        """Verify the integrity of a validation run by recomputing the replay hash.

        Returns:
            True if integrity is valid.

        Raises:
            ValidationEngineError: If integrity check fails.
        """
        run = self.get_validation_run(validation_id)
        decision = self._decisions.get(run.decision_id)
        if decision is None:
            raise ValidationEngineError(f"Decision '{run.decision_id}' not found for integrity check")

        replay_payload = {
            "decision_id": decision.decision_id,
            "evidence_ids": sorted(run.evidence_ids),
            "hypothesis_id": run.hypothesis_id,
            "scores": {
                "agreement_score": run.statistical_results.get("agreement_score", 0.0),
                "confidence_score": run.statistical_results.get("confidence_score", 0.0),
                "evidence_score": run.statistical_results.get("evidence_score", 0.0),
                "overall_confidence": run.statistical_results.get("overall_confidence", 0.0),
                "reproducibility_score": run.statistical_results.get("reproducibility_score", 0.0),
                "robustness_score": run.statistical_results.get("robustness_score", 0.0),
                "stability_score": run.statistical_results.get("stability_score", 0.0),
                "validation_score": run.statistical_results.get("validation_score", 0.0),
            },
        }
        recomputed_hash = compute_canonical_sha256(replay_payload)

        if recomputed_hash != run.replay_hash:
            raise ValidationEngineError(
                f"Replay hash mismatch for run '{validation_id}': "
                f"expected '{run.replay_hash}', got '{recomputed_hash}'"
            )
        return True
