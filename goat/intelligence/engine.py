"""
Project GOAT v0.9 — Master Institutional Research Intelligence & Meta-Analysis Engine
"""

from typing import Any

from goat.intelligence.analytics.engine import ResearchAnalyticsEngine
from goat.intelligence.core.canonical import compute_intelligence_summary_id
from goat.intelligence.core.models import (
    InstitutionalRecommendation,
    IntelligenceSummary,
    MetaAnalysis,
    ResearchHealth,
    ResearchInsight,
    ResearchTrend,
)
from goat.intelligence.insights.engine import InsightEngine
from goat.intelligence.meta.engine import MetaAnalysisEngine
from goat.intelligence.persistence.sqlite import IntelligencePersistenceContext
from goat.intelligence.recommendations.engine import RecommendationEngine
from goat.intelligence.reporting.reports import IntelligenceReportGenerator


class MasterIntelligenceEngine:
    """Master Orchestrator for Step 9.11 Institutional Research Intelligence Subsystem.

    Integrates research analytics, meta-analyses, explainable research insights,
    scientific recommendations, research health scoring, SQLite persistence, and reporting.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.persistence = IntelligencePersistenceContext(db_path)
        self.analytics_engine = ResearchAnalyticsEngine()
        self.meta_engine = MetaAnalysisEngine()
        self.insight_engine = InsightEngine()
        self.recommendation_engine = RecommendationEngine()
        self.report_generator = IntelligenceReportGenerator()

    def evaluate_research_intelligence(
        self,
        hypotheses_records: list[dict[str, Any]],
        experiment_records: list[dict[str, Any]],
        invalidation_records: list[dict[str, Any]],
        study_results: list[dict[str, Any]] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> tuple[ResearchHealth, list[ResearchInsight], list[InstitutionalRecommendation], MetaAnalysis]:
        """Perform end-to-end institutional research intelligence evaluation and save state."""
        # 1. Research Health
        health = self.analytics_engine.compute_research_health(
            hypotheses_records=hypotheses_records,
            experiment_records=experiment_records,
            invalidation_records=invalidation_records,
            timestamp_str=timestamp_str,
        )
        self.persistence.health.save(health)

        # 2. Meta-Analysis
        studies = study_results or experiment_records
        meta = self.meta_engine.perform_meta_analysis(
            analysis_title="Institutional Research Meta-Analysis",
            study_results=studies,
            timestamp_str=timestamp_str,
        )
        self.persistence.meta_analyses.save(meta)

        # 3. Insights
        success_rates = self.analytics_engine.analyze_hypothesis_success_rates(hypotheses_records)
        efficiency = self.analytics_engine.analyze_experiment_efficiency(experiment_records)
        invalidation_counts = self.analytics_engine.analyze_regime_invalidations(invalidation_records)

        insights = self.insight_engine.extract_insights_from_analytics(
            success_rates=success_rates,
            efficiency=efficiency,
            invalidation_counts=invalidation_counts,
            timestamp_str=timestamp_str,
        )
        for ins in insights:
            self.persistence.insights.save(ins)

        # 4. Scientific Recommendations ONLY
        recs = self.recommendation_engine.formulate_recommendations_from_insights(
            insights=insights,
            timestamp_str=timestamp_str,
        )
        for rec in recs:
            self.persistence.recommendations.save(rec)

        return health, insights, recs, meta

    def generate_summary(
        self,
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> IntelligenceSummary:
        """Compute executive summary across persisted research intelligence state."""
        insights = self.persistence.insights.list_all()
        meta_list = self.persistence.meta_analyses.list_all()
        recs = self.persistence.recommendations.list_all()
        health_list = self.persistence.health.list_all()

        current_health_score = health_list[-1].health_score if health_list else 0.0

        i_cat_counts: dict[str, int] = {}
        for ins in insights:
            i_cat_counts[ins.category.value] = i_cat_counts.get(ins.category.value, 0) + 1

        r_prio_counts: dict[str, int] = {}
        for rec in recs:
            r_prio_counts[rec.priority.value] = r_prio_counts.get(rec.priority.value, 0) + 1

        s_id, s_hash = compute_intelligence_summary_id(
            timestamp=timestamp_str,
            total_insights=len(insights),
            total_recommendations=len(recs),
        )

        summary = IntelligenceSummary(
            summary_id=s_id,
            timestamp=timestamp_str,
            total_insights=len(insights),
            total_meta_analyses=len(meta_list),
            total_recommendations=len(recs),
            overall_health_score=current_health_score,
            insights_by_category=i_cat_counts,
            recommendations_by_priority=r_prio_counts,
            metadata={},
            canonical_hash=s_hash,
        )

        self.persistence.summaries.save(summary)
        return summary

    def close(self) -> None:
        """Close database connection."""
        self.persistence.close()
