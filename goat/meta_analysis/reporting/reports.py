"""
Project GOAT v0.7 — Meta-Analysis Reports

Provides immutable, deterministic report models and renderers:
- MetaAnalysisReport
- ResearchClusterReport
- ResearchPatternReport
- ResearchTrendReport
- ScientificSummaryReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.meta_analysis.core.models import (
    MetaAnalysisResult,
    ResearchCluster,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
)


class MetaAnalysisReport(BaseModel):
    """Report summarizing complete MetaAnalysisResult."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    result: MetaAnalysisResult = Field(..., description="Target MetaAnalysisResult model")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        res = self.result
        lines = [
            f"# Scientific Meta-Analysis Report ({self.report_id})",
            "",
            f"- **Analysis ID**: `{res.analysis_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Overall Confidence**: `{res.confidence:.4f}`",
            f"- **Reproducibility**: `{res.reproducibility:.4f}`",
            "",
            "## Summary Statistics",
            f"- **Analyzed Knowledge States**: {len(res.analyzed_knowledge_states)}",
            f"- **Research Clusters**: {len(res.clusters)}",
            f"- **Discovered Patterns**: {len(res.patterns)}",
            f"- **Active Trends**: {len(res.trends)}",
            f"- **Contradictions Identified**: {len(res.contradictions)}",
            "",
            "## Intelligence Metrics",
            f"- **Knowledge Density**: `{res.intelligence_metrics.knowledge_density:.4f}`",
            f"- **Evidence Density**: `{res.intelligence_metrics.evidence_density:.4f}`",
            f"- **Validation Stability**: `{res.intelligence_metrics.validation_stability:.4f}`",
            f"- **Knowledge Maturity**: `{res.intelligence_metrics.knowledge_maturity:.4f}`",
            f"- **Scientific Confidence**: `{res.intelligence_metrics.scientific_confidence:.4f}`",
        ]
        return "\n".join(lines)


class ResearchClusterReport(BaseModel):
    """Report detailing generated ResearchClusters."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    clusters: list[ResearchCluster] = Field(default_factory=list, description="List of clusters")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Research Clusters Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Clusters**: {len(self.clusters)}",
            "",
            "| Cluster ID | Title | Type | Nodes | Confidence | Reproducibility |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for c in sorted(self.clusters, key=lambda x: x.cluster_id):
            c_type = c.cluster_type.value if hasattr(c.cluster_type, "value") else str(c.cluster_type)
            lines.append(
                f"| `{c.cluster_id}` | {c.title} | `{c_type}` | {len(c.participating_nodes)} | `{c.confidence:.2f}` | `{c.reproducibility:.2f}` |"
            )
        return "\n".join(lines)


class ResearchPatternReport(BaseModel):
    """Report detailing discovered ResearchPatterns."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    patterns: list[ResearchPattern] = Field(default_factory=list, description="List of patterns")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Research Patterns Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Patterns Discovered**: {len(self.patterns)}",
            "",
            "| Pattern ID | Name | Category | Frequency | Confidence |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for p in sorted(self.patterns, key=lambda x: x.pattern_id):
            p_cat = p.category.value if hasattr(p.category, "value") else str(p.category)
            lines.append(
                f"| `{p.pattern_id}` | {p.pattern_name} | `{p_cat}` | {p.frequency} | `{p.confidence:.2f}` |"
            )
        return "\n".join(lines)


class ResearchTrendReport(BaseModel):
    """Report detailing generated ResearchTrends."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    trends: list[ResearchTrend] = Field(default_factory=list, description="List of trends")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Research Trends Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Trends Generated**: {len(self.trends)}",
            "",
            "| Trend ID | Topic | Direction | Strength | Persistence |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for t in sorted(self.trends, key=lambda x: x.trend_id):
            t_dir = t.direction.value if hasattr(t.direction, "value") else str(t.direction)
            lines.append(
                f"| `{t.trend_id}` | {t.topic} | `{t_dir}` | `{t.strength:.2f}` | `{t.persistence:.2f}` |"
            )
        return "\n".join(lines)


class ScientificSummaryReport(BaseModel):
    """Report rendering ScientificSummary."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    summary: ScientificSummary = Field(..., description="ScientificSummary model")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        s = self.summary
        lines = [
            f"# Executive Scientific Summary ({self.report_id})",
            "",
            f"- **Summary ID**: `{s.summary_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Validated Knowledge Count**: {s.validated_knowledge_count}",
            f"- **Integrated Knowledge Count**: {s.integrated_knowledge_count}",
            f"- **Conflict Count**: {s.conflict_count}",
            f"- **Cluster Count**: {s.cluster_count}",
            f"- **Pattern Count**: {s.pattern_count}",
            f"- **Trend Count**: {s.trend_count}",
            "",
            "## Strongest Research Areas",
        ]
        for sa in s.strongest_research_areas:
            lines.append(f"- {sa}")

        lines.extend(["", "## Weakest Research Areas"])
        for wa in s.weakest_research_areas:
            lines.append(f"- {wa}")

        lines.extend(["", "## Recommendations"])
        for rec in s.future_investigation_recommendations:
            lines.append(f"- {rec}")

        return "\n".join(lines)
