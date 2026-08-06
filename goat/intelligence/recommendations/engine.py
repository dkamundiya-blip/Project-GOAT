"""
Project GOAT v0.9 — Institutional Research Recommendation Engine
"""

from typing import Any

from goat.intelligence.core.canonical import compute_institutional_recommendation_id
from goat.intelligence.core.enums import RecommendationPriority
from goat.intelligence.core.models import InstitutionalRecommendation, ResearchInsight


class RecommendationEngine:
    """Quantitative Sub-Engine for Institutional Research Priorities.

    Produces institutional recommendations concerning FUTURE SCIENTIFIC RESEARCH PRIORITIES ONLY.
    STRICTLY PROHIBITED from producing trading, broker, signal, or portfolio recommendations.
    """

    def generate_recommendation(
        self,
        topic: str,
        rationale: str,
        priority: RecommendationPriority | str = RecommendationPriority.P2_HIGH,
        expected_utility: float = 80.0,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> InstitutionalRecommendation:
        """Generate a scientific research recommendation."""
        if isinstance(priority, str):
            priority = RecommendationPriority(priority)

        meta = dict(metadata or {})

        rec_id, r_hash = compute_institutional_recommendation_id(
            priority=priority.value,
            topic=topic,
            timestamp=timestamp_str,
        )

        return InstitutionalRecommendation(
            recommendation_id=rec_id,
            priority=priority,
            topic=topic,
            rationale=rationale,
            expected_utility=expected_utility,
            timestamp=timestamp_str,
            metadata=meta,
            canonical_hash=r_hash,
        )

    def formulate_recommendations_from_insights(
        self,
        insights: list[ResearchInsight],
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> list[InstitutionalRecommendation]:
        """Derive actionable research recommendations from accumulated research insights."""
        recs: list[InstitutionalRecommendation] = []

        for insight in insights:
            if insight.category.value == "HYPOTHESIS_SUCCESS":
                top_cat = insight.supporting_data.get("category", "HIGH_PERFORMING")
                recs.append(
                    self.generate_recommendation(
                        topic=f"Expand Hypothesis Generation in Category: {top_cat}",
                        rationale=f"Scientific evidence demonstrates high success rate ({insight.supporting_data.get('success_rate', 0.0):.2%}). Prioritize new hypothesis formulations in this domain.",
                        priority=RecommendationPriority.P1_URGENT,
                        expected_utility=90.0,
                        timestamp_str=timestamp_str,
                    )
                )

            elif insight.category.value == "EXPERIMENT_EFFICIENCY" and insight.supporting_data.get("efficiency_score", 100) < 50:
                recs.append(
                    self.generate_recommendation(
                        topic="Refine Experiment Window & Sample Size Allocation",
                        rationale="Experiment efficiency score is sub-optimal. Recommend tightening observation window parameters to minimize sample waste.",
                        priority=RecommendationPriority.P2_HIGH,
                        expected_utility=75.0,
                        timestamp_str=timestamp_str,
                    )
                )

            elif insight.category.value == "REGIME_INVALIDATION":
                regime = insight.supporting_data.get("regime", "HIGH_VOLATILITY")
                recs.append(
                    self.generate_recommendation(
                        topic=f"Investigate Cross-Regime Robustness in {regime}",
                        rationale=f"Market regime '{regime}' causes frequent invalidations. Recommend targeted regime transition studies prior to hypothesis promotion.",
                        priority=RecommendationPriority.P2_HIGH,
                        expected_utility=85.0,
                        timestamp_str=timestamp_str,
                    )
                )

        return recs
