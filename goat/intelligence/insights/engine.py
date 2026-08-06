"""
Project GOAT v0.9 — Research Insight Engine
"""

from typing import Any

from goat.intelligence.core.canonical import compute_research_insight_id
from goat.intelligence.core.enums import InsightCategory, InsightImpact
from goat.intelligence.core.models import ResearchInsight


class InsightEngine:
    """Quantitative Sub-Engine for Explainable Research Insights.

    Generates structured, explainable research insights answering institutional questions
    about hypothesis categories, experiment designs, market regime invalidations, evidence
    predictive strength, research time waste, and edge longevity.
    """

    def generate_insight(
        self,
        category: InsightCategory | str,
        title: str,
        findings_statement: str,
        impact: InsightImpact | str = InsightImpact.HIGH,
        confidence_level: float = 0.95,
        supporting_data: dict[str, Any] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> ResearchInsight:
        """Generate an explainable ResearchInsight instance."""
        if isinstance(category, str):
            category = InsightCategory(category)
        if isinstance(impact, str):
            impact = InsightImpact(impact)

        supp_data = dict(supporting_data or {})
        meta = dict(metadata or {})

        insight_id, r_hash = compute_research_insight_id(
            category=category.value,
            title=title,
            impact=impact.value,
        )

        return ResearchInsight(
            insight_id=insight_id,
            category=category,
            impact=impact,
            title=title,
            findings_statement=findings_statement,
            confidence_level=confidence_level,
            supporting_data=supp_data,
            timestamp=timestamp_str,
            metadata=meta,
            canonical_hash=r_hash,
        )

    def extract_insights_from_analytics(
        self,
        success_rates: dict[str, float],
        efficiency: dict[str, Any],
        invalidation_counts: dict[str, int],
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> list[ResearchInsight]:
        """Extract automated insights from analytics aggregation."""
        insights: list[ResearchInsight] = []

        # Best performing category insight
        if success_rates:
            best_cat = max(success_rates.items(), key=lambda x: x[1])
            insights.append(
                self.generate_insight(
                    category=InsightCategory.HYPOTHESIS_SUCCESS,
                    title=f"Highest Performing Category: {best_cat[0]}",
                    findings_statement=f"Category '{best_cat[0]}' achieved highest success rate of {best_cat[1]:.2%}.",
                    impact=InsightImpact.HIGH,
                    confidence_level=0.95,
                    supporting_data={"category": best_cat[0], "success_rate": best_cat[1]},
                    timestamp_str=timestamp_str,
                )
            )

        # Efficiency insight
        eff_score = float(efficiency.get("efficiency_score", 50.0))
        eff_impact = InsightImpact.CRITICAL if eff_score < 40.0 else InsightImpact.MEDIUM
        insights.append(
            self.generate_insight(
                category=InsightCategory.EXPERIMENT_EFFICIENCY,
                title="Experiment Efficiency Assessment",
                findings_statement=f"Experiment efficiency score evaluated at {eff_score:.2f}/100.",
                impact=eff_impact,
                confidence_level=0.90,
                supporting_data=efficiency,
                timestamp_str=timestamp_str,
            )
        )

        # Invalidation insight
        if invalidation_counts:
            top_inv = max(invalidation_counts.items(), key=lambda x: x[1])
            insights.append(
                self.generate_insight(
                    category=InsightCategory.REGIME_INVALIDATION,
                    title=f"Primary Invalidation Regime: {top_inv[0]}",
                    findings_statement=f"Regime '{top_inv[0]}' caused the highest number of invalidations ({top_inv[1]} count).",
                    impact=InsightImpact.HIGH,
                    confidence_level=0.95,
                    supporting_data={"regime": top_inv[0], "invalidation_count": top_inv[1]},
                    timestamp_str=timestamp_str,
                )
            )

        return insights
