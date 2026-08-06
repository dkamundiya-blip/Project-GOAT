"""
Project GOAT v0.9 — Validation Retirement Engine
"""

from datetime import datetime, timezone
from typing import Sequence

from goat.live_validation.core.canonical import compute_validation_decision_id
from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
)
from goat.live_validation.core.models import (
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
)


class ValidationRetirementEngine:
    """Validation Retirement Engine for deriving scientific conclusions and recommending edge promotion

    or edge retirement based on empirical live validation observations.

    IMPORTANT: Final authority for promotion or retirement remains with Step 9.6 governance.
    This engine ONLY derives and appends immutable scientific recommendations.
    """

    def __init__(self) -> None:
        self._decisions: dict[str, ValidationDecision] = {}

    def derive_recommendation(
        self,
        session: ValidationSession,
        observations: Sequence[ValidationObservation],
        monitoring_status: MonitoringStatus = MonitoringStatus.NORMAL,
        min_required_observations: int = 30,
        authorizer: str = "RETIREMENT_ENGINE",
        timestamp: str | None = None,
    ) -> ValidationDecision:
        """Derive scientific validation conclusion and recommendation for a live validation session."""
        if not observations:
            outcome = ValidationDecisionOutcome.INCONCLUSIVE
            rationale = "Zero live observations recorded for session."
        elif len(observations) < min_required_observations:
            outcome = ValidationDecisionOutcome.INCONCLUSIVE
            rationale = f"Insufficient sample size ({len(observations)} < {min_required_observations})."
        elif monitoring_status == MonitoringStatus.CRITICAL:
            outcome = ValidationDecisionOutcome.RETIREMENT_RECOMMENDED
            rationale = "Monitoring status is CRITICAL due to severe execution breakdown or slippage."
        else:
            live_outcomes = [o.live_outcome for o in observations]
            avg_live = sum(live_outcomes) / float(len(live_outcomes))
            avg_expected = sum(o.expected_outcome for o in observations) / float(len(observations))

            if avg_live > 0.0 and (avg_live >= 0.70 * avg_expected) and len(observations) >= 50:
                outcome = ValidationDecisionOutcome.PROMOTION_RECOMMENDED
                rationale = f"Live validation passed with positive live expectancy ({avg_live:.4f}) matching benchmark."
            elif avg_live > 0.0:
                outcome = ValidationDecisionOutcome.SUPPORTED
                rationale = f"Live validation supported with positive live expectancy ({avg_live:.4f})."
            elif avg_live < 0.0 or monitoring_status == MonitoringStatus.WARNING:
                outcome = ValidationDecisionOutcome.RETIREMENT_RECOMMENDED
                rationale = f"Live validation failed with negative live expectancy ({avg_live:.4f}) or warning status."
            else:
                outcome = ValidationDecisionOutcome.FAILED
                rationale = f"Live validation failed with average outcome {avg_live:.4f}."

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        vdc_id, canonical_hash = compute_validation_decision_id(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            decision=outcome.value,
        )

        decision = ValidationDecision(
            decision_id=vdc_id,
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            decision=outcome,
            rationale=rationale,
            timestamp=now_str,
            authorizer=authorizer,
            metadata={"total_observations": len(observations)},
            canonical_hash=canonical_hash,
        )

        self._decisions[vdc_id] = decision
        return decision

    def get_decision(self, decision_id: str) -> ValidationDecision | None:
        """Retrieve decision by ID."""
        return self._decisions.get(decision_id)

    def list_all_decisions(self) -> list[ValidationDecision]:
        """List all decisions sorted by timestamp."""
        return sorted(self._decisions.values(), key=lambda d: d.timestamp)
