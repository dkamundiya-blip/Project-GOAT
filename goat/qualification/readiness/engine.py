"""
Project GOAT v0.7 — Decision Readiness Engine

Determines authorized decision readiness levels deterministically:
- NOT_READY
- EARLY_RESEARCH
- EXPERIMENTAL
- CANDIDATE
- READY_FOR_SIMULATION
- READY_FOR_FORWARD_TESTING
- Identifies active blocking conditions preventing advancement
"""

from __future__ import annotations

from typing import Any

from goat.composite.core.models import CompositeEdge
from goat.qualification.core.canonical import (
    compute_canonical_sha256,
    compute_qualification_explanation_id,
    compute_readiness_id,
)
from goat.qualification.core.enums import (
    BlockingConditionType,
    QualificationState,
    ReadinessLevel,
)
from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    QualificationExplainabilityRecord,
    ScientificQualification,
)


class DecisionReadinessEngine:
    """Engine for aggregating qualification gate evaluations into authorized decision readiness states."""

    def evaluate_readiness(
        self,
        qualification: ScientificQualification,
        gate_evals: list[GateEvaluation],
        composite: CompositeEdge,
        timestamp: str,
    ) -> tuple[DecisionReadiness, QualificationExplainabilityRecord]:
        """Determine decision readiness level and blocking conditions deterministically.

        Args:
            qualification: Target ScientificQualification model.
            gate_evals: List of component GateEvaluations.
            composite: Target CompositeEdge model.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (DecisionReadiness, QualificationExplainabilityRecord).
        """
        blocking_conditions: list[str] = []
        satisfied_conditions: list[str] = []

        passed_evals = [e for e in gate_evals if e.passed]
        failed_evals = [e for e in gate_evals if not e.passed]

        passed_gate_ids = sorted([e.gate_id for e in passed_evals])
        failed_gate_ids = sorted([e.gate_id for e in failed_evals])

        # Evaluate blocking condition types
        if qualification.evidence_strength < 0.50:
            blocking_conditions.append(BlockingConditionType.INSUFFICIENT_EVIDENCE.value)
        else:
            satisfied_conditions.append("SUFFICIENT_EVIDENCE")

        if qualification.reproducibility < 0.65:
            blocking_conditions.append(BlockingConditionType.WEAK_REPRODUCIBILITY.value)
        else:
            satisfied_conditions.append("STRONG_REPRODUCIBILITY")

        if qualification.scientific_confidence < 0.65:
            blocking_conditions.append(BlockingConditionType.LOW_SCIENTIFIC_CONFIDENCE.value)
        else:
            satisfied_conditions.append("HIGH_SCIENTIFIC_CONFIDENCE")

        if qualification.explainability < 0.70:
            blocking_conditions.append(BlockingConditionType.INCOMPLETE_EXPLAINABILITY.value)
        else:
            satisfied_conditions.append("COMPLETE_EXPLAINABILITY")

        if qualification.qualification_state == QualificationState.DISQUALIFIED:
            blocking_conditions.append("MANDATORY_GATE_DISQUALIFICATION")

        # Determine Readiness Level
        readiness_score = qualification.overall_readiness
        level: ReadinessLevel

        if qualification.qualification_state == QualificationState.DISQUALIFIED or len(blocking_conditions) >= 3:
            level = ReadinessLevel.NOT_READY
        elif readiness_score >= 0.85 and len(blocking_conditions) == 0:
            level = ReadinessLevel.READY_FOR_FORWARD_TESTING
        elif readiness_score >= 0.75 and len(blocking_conditions) <= 1:
            level = ReadinessLevel.READY_FOR_SIMULATION
        elif readiness_score >= 0.65:
            level = ReadinessLevel.CANDIDATE
        elif readiness_score >= 0.50:
            level = ReadinessLevel.EXPERIMENTAL
        else:
            level = ReadinessLevel.EARLY_RESEARCH

        r_id, _ = compute_readiness_id(qualification.qualification_id, level.value)

        summary_text = (
            f"Qualification {qualification.qualification_id} assigned readiness level '{level.value}' "
            f"with overall readiness score {readiness_score:.4f}. Active blocking conditions: {len(blocking_conditions)}."
        )

        payload_dcr = {
            "qualification_id": qualification.qualification_id,
            "readiness_id": r_id,
            "readiness_level": level.value,
        }
        hash_dcr = compute_canonical_sha256(payload_dcr).upper()

        readiness = DecisionReadiness(
            readiness_id=r_id,
            qualification_id=qualification.qualification_id,
            readiness_level=level,
            blocking_conditions=sorted(blocking_conditions),
            satisfied_conditions=sorted(satisfied_conditions),
            scientific_summary=summary_text,
            timestamp=timestamp,
            canonical_hash=hash_dcr,
        )

        # Build QualificationExplainabilityRecord
        ex_id, _ = compute_qualification_explanation_id(qualification.qualification_id)

        sci_rationale = (
            f"Scientific qualification for composite '{composite.title}' ({composite.composite_id}) "
            f"evaluated under regime '{qualification.regime_id}'. Evaluated {len(gate_evals)} gates "
            f"({len(passed_evals)} passed, {len(failed_evals)} failed). Assigned state '{qualification.qualification_state.value}' "
            f"and readiness level '{level.value}'."
        )

        payload_ex = {
            "explanation_id": ex_id,
            "qualification_id": qualification.qualification_id,
        }
        hash_ex = compute_canonical_sha256(payload_ex).upper()

        explainability = QualificationExplainabilityRecord(
            explanation_id=ex_id,
            qualification_id=qualification.qualification_id,
            participating_composites=[composite.composite_id],
            applicable_regimes=[qualification.regime_id],
            passed_gates=passed_gate_ids,
            failed_gates=failed_gate_ids,
            blocking_conditions=sorted(blocking_conditions),
            supporting_evidence=composite.supporting_evidence,
            supporting_hypotheses=composite.participating_hypotheses,
            supporting_validations=composite.participating_validations,
            supporting_knowledge=[],
            scientific_rationale=sci_rationale,
            canonical_hash=hash_ex,
        )

        return readiness, explainability
