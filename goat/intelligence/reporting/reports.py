"""
Project GOAT v0.9 — Institutional Research Intelligence Report Generator
"""

from typing import Any

from goat.intelligence.core.canonical import serialize_canonical_json
from goat.intelligence.core.models import (
    InstitutionalRecommendation,
    IntelligenceSummary,
    MetaAnalysis,
    ResearchHealth,
    ResearchInsight,
    ResearchTrend,
)


class IntelligenceReportGenerator:
    """Report Generator for Institutional Research Intelligence Subsystem.

    Generates Markdown reports and Canonical JSON exports for Research Insights,
    Meta-Analyses, Research Trends, Recommendations, Research Health, and Executive Summaries.
    """

    def generate_insight_report(self, insight: ResearchInsight) -> str:
        """Generate Markdown Institutional Insight Report."""
        return (
            f"# INSTITUTIONAL RESEARCH INSIGHT REPORT\n"
            f"**Insight Title**: `{insight.title}`\n"
            f"**Insight ID**: `{insight.insight_id}` | **Canonical Hash**: `{insight.canonical_hash}`\n"
            f"**Category**: `{insight.category.value}` | **Impact**: `{insight.impact.value}`\n\n"
            f"## Explainable Findings\n"
            f"{insight.findings_statement}\n\n"
            f"## Statistical Confidence & Empirical Evidence\n"
            f"- **Confidence Level**: `{insight.confidence_level:.2%}`\n"
            f"- **Timestamp**: `{insight.timestamp}`\n"
        )

    def generate_meta_analysis_report(self, meta: MetaAnalysis) -> str:
        """Generate Markdown Meta Analysis Report."""
        findings_str = "\n".join([f"- {f}" for f in meta.key_findings]) or "- None"
        return (
            f"# INSTITUTIONAL META-ANALYSIS REPORT\n"
            f"**Study Title**: `{meta.analysis_title}`\n"
            f"**Analysis ID**: `{meta.meta_analysis_id}` | **Canonical Hash**: `{meta.canonical_hash}`\n\n"
            f"## Statistical Parameters\n"
            f"- **Sample Size (Completed Studies)**: `{meta.sample_size}`\n"
            f"- **Pooled Effect Size**: `{meta.pooled_effect_size:.4f}`\n"
            f"- **Heterogeneity I2**: `{meta.heterogeneity_i2:.2f}%`\n"
            f"- **P-Value**: `{meta.p_value:.4e}`\n\n"
            f"## Higher-Order Key Findings\n"
            f"{findings_str}\n"
        )

    def generate_research_health_report(self, health: ResearchHealth) -> str:
        """Generate Markdown Research Health Report."""
        diag_str = "\n".join([f"- {d}" for d in health.diagnostics]) or "- None"
        return (
            f"# INSTITUTIONAL RESEARCH HEALTH REPORT\n"
            f"**Health ID**: `{health.health_id}` | **Status**: `{health.status.value}`\n"
            f"**Overall Health Score**: `{health.health_score:.2f}/100` | **Canonical Hash**: `{health.canonical_hash}`\n\n"
            f"## Key Research Metrics\n"
            f"- **Aggregate Hypothesis Success Rate**: `{health.success_rate:.2%}`\n"
            f"- **Experiment Efficiency Score**: `{health.efficiency_score:.2f}/100`\n"
            f"- **Research Time Waste Percentage**: `{health.waste_percentage:.2f}%`\n\n"
            f"## Diagnostic Statements\n"
            f"{diag_str}\n"
        )

    def generate_executive_report(self, summary: IntelligenceSummary) -> str:
        """Generate Markdown Executive Research Intelligence Report."""
        return (
            f"# INSTITUTIONAL RESEARCH INTELLIGENCE EXECUTIVE REPORT\n"
            f"**Summary ID**: `{summary.summary_id}` | **Timestamp**: `{summary.timestamp}`\n"
            f"**Canonical Hash**: `{summary.canonical_hash}`\n\n"
            f"## Institutional Overview\n"
            f"- **Overall Research Health Score**: `{summary.overall_health_score:.2f}/100`\n"
            f"- **Total Insights Generated**: `{summary.total_insights}`\n"
            f"- **Total Meta-Analyses Conducted**: `{summary.total_meta_analyses}`\n"
            f"- **Total Research Recommendations**: `{summary.total_recommendations}`\n\n"
            f"## Insights by Category\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.insights_by_category.items()])
            + "\n\n## Recommendations by Priority Tier\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.recommendations_by_priority.items()])
        )

    def export_canonical_json(self, obj: Any) -> str:
        """Export model as canonical JSON string."""
        return serialize_canonical_json(obj)
