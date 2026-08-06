"""
Project GOAT v0.9 — Quantitative Edge Discovery Validation Engine
"""

from typing import Any

from goat.edge_discovery.core.canonical import compute_discovery_decision_id
from goat.edge_discovery.core.enums import RejectionReason, ValidationStatus
from goat.edge_discovery.core.models import (
    DiscoveryDecision,
    EdgeCandidate,
    EdgeScore,
    NoveltyAssessment,
)


class DiscoveryValidationEngine:
    """Quantitative Sub-Engine for Protocol Edge Validation.

    Validates candidate quantitative edges against research protocol rules.
    Fails closed and rejects candidates violating protocol criteria.
    """

    def validate_candidate(
        self,
        candidate: EdgeCandidate,
        novelty: NoveltyAssessment,
        score: EdgeScore,
        min_observations: int = 5,
        min_confidence: float = 0.50,
        min_score: float = 40.0,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> DiscoveryDecision:
        """Validate candidate edge against institutional protocol rules."""
        meta = dict(metadata or {})

        status = ValidationStatus.PASSED
        reason = RejectionReason.NONE

        # 1. Observation Count Check
        if candidate.observation_count < min_observations:
            status = ValidationStatus.REJECTED
            reason = RejectionReason.INSUFFICIENT_OBSERVATIONS

        # 2. Duplicate Edge Check
        elif not novelty.is_novel:
            status = ValidationStatus.REJECTED
            reason = RejectionReason.DUPLICATE_EDGE

        # 3. Confidence Level Check
        elif candidate.confidence_level < min_confidence:
            status = ValidationStatus.REJECTED
            reason = RejectionReason.POOR_CONFIDENCE

        # 4. Regime Consistency Check
        elif score.consistency_score < 30.0:
            status = ValidationStatus.REJECTED
            reason = RejectionReason.SINGLE_REGIME_BEHAVIOR

        # 5. Score / Overfit Evidence Check
        elif score.overall_score < min_score:
            status = ValidationStatus.REJECTED
            reason = RejectionReason.OVERFIT_EVIDENCE

        d_id, d_hash = compute_discovery_decision_id(
            candidate_id=candidate.candidate_id,
            status=status.value,
            reason=reason.value,
            timestamp=timestamp_str,
        )

        return DiscoveryDecision(
            decision_id=d_id,
            candidate_id=candidate.candidate_id,
            status=status,
            rejection_reason=reason,
            novelty_assessment_id=novelty.assessment_id,
            score_id=score.score_id,
            timestamp=timestamp_str,
            metadata=meta,
            canonical_hash=d_hash,
        )
