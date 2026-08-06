"""
Project GOAT v0.9 — Edge Retirement Engine
"""

from datetime import datetime, timezone

from goat.governance.core.canonical import compute_retirement_assessment_id
from goat.governance.core.models import EdgeCandidate, RetirementAssessment


class EdgeRetirementEngine:
    """Edge Retirement Engine for evaluating edge performance degradation, expectation drift,

    and constitutional violations to determine if an active edge should be retired or paused.

    IMPORTANT: History is NEVER deleted. Decisions append immutable assessment records.
    """

    def __init__(self) -> None:
        self._assessments: dict[str, RetirementAssessment] = {}

    def evaluate_retirement(
        self,
        candidate: EdgeCandidate,
        expectancy_degradation: float = 0.0,
        confidence_decline: float = 0.0,
        structural_shift_detected: bool = False,
        amendment_001_violation: bool = False,
        evaluator: str = "RETIREMENT_ENGINE",
        timestamp: str | None = None,
    ) -> RetirementAssessment:
        """Evaluate edge candidate against retirement and degradation thresholds."""
        is_retired = (
            expectancy_degradation > 0.50
            or confidence_decline > 0.30
            or structural_shift_detected
            or amendment_001_violation
        )

        notes = (
            f"Retirement assessment for edge '{candidate.edge_id}': "
            f"RetirementRecommended={is_retired} (ExpectancyDegradation={expectancy_degradation:.2f}, "
            f"ConfidenceDecline={confidence_decline:.2f}, StructuralShift={structural_shift_detected}, "
            f"Amendment001Violation={amendment_001_violation})."
        )

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        rta_id, canonical_hash = compute_retirement_assessment_id(
            edge_id=candidate.edge_id,
            hypothesis_id=candidate.hypothesis_id,
            evaluator=evaluator,
        )

        assessment = RetirementAssessment(
            assessment_id=rta_id,
            edge_id=candidate.edge_id,
            hypothesis_id=candidate.hypothesis_id,
            expectancy_degradation=expectancy_degradation,
            confidence_decline=confidence_decline,
            structural_shift_detected=structural_shift_detected,
            amendment_001_violation=amendment_001_violation,
            is_retirement_recommended=is_retired,
            assessment_notes=notes,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        self._assessments[rta_id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str) -> RetirementAssessment | None:
        """Retrieve retirement assessment by ID."""
        return self._assessments.get(assessment_id)
