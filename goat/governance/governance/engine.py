"""
Project GOAT v0.9 — Edge Governance Engine
"""

from datetime import datetime, timezone

from goat.governance.core.canonical import compute_governance_decision_id
from goat.governance.core.enums import (
    EdgeStatus,
    GovernanceDecisionOutcome,
    GovernanceReason,
)
from goat.governance.core.models import (
    EdgeCandidate,
    GovernanceDecision,
    PromotionAssessment,
    RetirementAssessment,
)
from goat.governance.promotion.engine import EdgePromotionEngine
from goat.governance.retirement.engine import EdgeRetirementEngine


class EdgeGovernanceEngine:
    """Edge Governance Engine representing the constitutional authority responsible for making binding

    governance decisions on quantitative trading edges without human discretion or trade execution.
    """

    def __init__(
        self,
        promotion_engine: EdgePromotionEngine | None = None,
        retirement_engine: EdgeRetirementEngine | None = None,
    ) -> None:
        self._promotion_engine = promotion_engine or EdgePromotionEngine()
        self._retirement_engine = retirement_engine or EdgeRetirementEngine()
        self._decisions: dict[str, GovernanceDecision] = {}

    def make_governance_decision(
        self,
        candidate: EdgeCandidate,
        promotion_assessment: PromotionAssessment | None = None,
        retirement_assessment: RetirementAssessment | None = None,
        authorizer: str = "GOVERNANCE_BOARD",
        timestamp: str | None = None,
    ) -> GovernanceDecision:
        """Derive and record binding constitutional governance decision for an edge candidate."""
        if not promotion_assessment:
            promotion_assessment = self._promotion_engine.evaluate_promotion(candidate)
        if not retirement_assessment:
            retirement_assessment = self._retirement_engine.evaluate_retirement(candidate)

        # Decision derivation logic based exclusively on scientific evidence
        if retirement_assessment.is_retirement_recommended:
            decision_outcome = GovernanceDecisionOutcome.RETIRE
            reason = (
                GovernanceReason.CONSTITUTIONAL_RULE
                if retirement_assessment.amendment_001_violation
                else (
                    GovernanceReason.STRUCTURAL_SHIFT
                    if retirement_assessment.structural_shift_detected
                    else GovernanceReason.EXPECTANCY_DEGRADATION
                )
            )
            rationale = (
                f"Edge '{candidate.edge_id}' retired due to degradation/violation: {retirement_assessment.assessment_notes}"
            )
        elif promotion_assessment.is_promotable:
            decision_outcome = GovernanceDecisionOutcome.PROMOTE
            reason = GovernanceReason.LIVE_CONFIRMATION
            rationale = (
                f"Edge '{candidate.edge_id}' satisfies all constitutional, statistical, and live validation criteria. Recommended for promotion."
            )
        elif not promotion_assessment.is_live_validation_complete:
            decision_outcome = GovernanceDecisionOutcome.RETAIN
            reason = GovernanceReason.INSUFFICIENT_EVIDENCE
            rationale = (
                f"Edge '{candidate.edge_id}' retained in live validation pending further observation."
            )
        elif not promotion_assessment.is_statistics_complete:
            decision_outcome = GovernanceDecisionOutcome.RETURN_TO_RESEARCH
            reason = GovernanceReason.RESEARCH_PROTOCOL
            rationale = (
                f"Edge '{candidate.edge_id}' returned to research for statistical re-evaluation."
            )
        else:
            decision_outcome = GovernanceDecisionOutcome.PAUSE
            reason = GovernanceReason.INSUFFICIENT_EVIDENCE
            rationale = f"Edge '{candidate.edge_id}' paused pending evidence review."

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        gov_id, canonical_hash = compute_governance_decision_id(
            edge_id=candidate.edge_id,
            decision=decision_outcome.value,
            reason=reason.value,
        )

        gov_decision = GovernanceDecision(
            decision_id=gov_id,
            edge_id=candidate.edge_id,
            hypothesis_id=candidate.hypothesis_id,
            decision=decision_outcome,
            reason=reason,
            rationale=rationale,
            authorizer=authorizer,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        self._decisions[gov_id] = gov_decision
        return gov_decision

    def get_decision(self, decision_id: str) -> GovernanceDecision | None:
        """Retrieve decision by ID."""
        return self._decisions.get(decision_id)

    def list_all_decisions(self) -> list[GovernanceDecision]:
        """List all decisions sorted by timestamp."""
        return sorted(self._decisions.values(), key=lambda d: d.timestamp)
