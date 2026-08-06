"""
Project GOAT v0.9 — Edge Promotion Engine
"""

from datetime import datetime, timezone

from goat.governance.core.canonical import compute_promotion_assessment_id
from goat.governance.core.models import EdgeCandidate, PromotionAssessment


class EdgePromotionEngine:
    """Edge Promotion Engine for evaluating whether an edge candidate satisfies all strict constitutional

    and scientific requirements for promotion to production readiness.
    """

    def __init__(self) -> None:
        self._assessments: dict[str, PromotionAssessment] = {}

    def evaluate_promotion(
        self,
        candidate: EdgeCandidate,
        hypothesis_valid: bool = True,
        evidence_valid: bool = True,
        experiment_valid: bool = True,
        statistics_decision: str = "SUPPORTED",
        live_validation_decision: str = "PROMOTION_RECOMMENDED",
        constitution_compliant: bool = True,
        research_protocol_compliant: bool = True,
        evaluator: str = "PROMOTION_ENGINE",
        timestamp: str | None = None,
    ) -> PromotionAssessment:
        """Evaluate edge candidate against strict constitutional promotion criteria."""
        stats_ok = statistics_decision.strip().upper() == "SUPPORTED"
        live_ok = live_validation_decision.strip().upper() in ("SUPPORTED", "PROMOTION_RECOMMENDED")

        is_promotable = (
            hypothesis_valid
            and evidence_valid
            and experiment_valid
            and stats_ok
            and live_ok
            and constitution_compliant
            and research_protocol_compliant
        )

        notes = (
            f"Promotion assessment for edge '{candidate.edge_id}': "
            f"Promotable={is_promotable} (Hypothesis={hypothesis_valid}, Evidence={evidence_valid}, "
            f"Experiment={experiment_valid}, Stats={stats_ok}, LiveVal={live_ok}, "
            f"Constitution={constitution_compliant}, PRSP={research_protocol_compliant})."
        )

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        pra_id, canonical_hash = compute_promotion_assessment_id(
            edge_id=candidate.edge_id,
            hypothesis_id=candidate.hypothesis_id,
            evaluator=evaluator,
        )

        assessment = PromotionAssessment(
            assessment_id=pra_id,
            edge_id=candidate.edge_id,
            hypothesis_id=candidate.hypothesis_id,
            is_hypothesis_passed=hypothesis_valid,
            is_evidence_complete=evidence_valid,
            is_experiment_complete=experiment_valid,
            is_statistics_complete=stats_ok,
            is_live_validation_complete=live_ok,
            is_constitution_satisfied=constitution_compliant,
            is_research_protocol_satisfied=research_protocol_compliant,
            is_promotable=is_promotable,
            assessment_notes=notes,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        self._assessments[pra_id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str) -> PromotionAssessment | None:
        """Retrieve promotion assessment by ID."""
        return self._assessments.get(assessment_id)
