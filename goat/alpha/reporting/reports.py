"""
Project GOAT v0.7 — Scientific Alpha Reports

Provides immutable, deterministic report models and renderers:
- ScientificEdgeReport
- EdgeRankingReport
- EdgeEvidenceReport
- EdgeQualityReport
- ScientificAlphaReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.alpha.core.models import (
    EdgeEvidence,
    EdgeExplainabilityRecord,
    EdgeRanking,
    EdgeScore,
    ScientificEdge,
)
from goat.integration.core.canonical import serialize_canonical_json


class ScientificEdgeReport(BaseModel):
    """Report detailing single or multiple ScientificEdges."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    edges: list[ScientificEdge] = Field(default_factory=list, description="List of candidate ScientificEdges")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Candidate Edge Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Edges**: {len(self.edges)}",
            "",
            "| Edge ID | Title | Maturity | Confidence | Reproducibility | Robustness |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for e in sorted(self.edges, key=lambda x: x.edge_id):
            mat = e.maturity.value if hasattr(e.maturity, "value") else str(e.maturity)
            lines.append(
                f"| `{e.edge_id}` | {e.title} | `{mat}` | `{e.confidence:.2f}` | `{e.reproducibility:.2f}` | `{e.robustness:.2f}` |"
            )
        return "\n".join(lines)


class EdgeRankingReport(BaseModel):
    """Report detailing deterministic EdgeRanking results."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    ranking: EdgeRanking = Field(..., description="Target EdgeRanking model")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        rk = self.ranking
        lines = [
            f"# Edge Ranking Report ({self.report_id})",
            "",
            f"- **Ranking ID**: `{rk.ranking_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Ranked Edges**: {len(rk.ranked_edges)}",
            f"- **Ranking Rules**: {', '.join(rk.ranking_rules)}",
            "",
            "| Rank | Edge ID | Overall Score | Scientific Quality | Longevity | Conflict Penalty |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        score_map = {s.edge_id: s for s in rk.edge_scores}
        for rank_idx, edge_id in enumerate(rk.ranked_edges, 1):
            sc = score_map.get(edge_id)
            if sc:
                lines.append(
                    f"| {rank_idx} | `{edge_id}` | `{sc.overall_edge_score:.4f}` | `{sc.scientific_quality:.4f}` | `{sc.longevity_score:.4f}` | `{sc.conflict_penalty:.4f}` |"
                )
            else:
                lines.append(f"| {rank_idx} | `{edge_id}` | N/A | N/A | N/A | N/A |")
        return "\n".join(lines)


class EdgeEvidenceReport(BaseModel):
    """Report detailing EdgeEvidence and explainability records."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    evidence_records: list[EdgeEvidence] = Field(default_factory=list, description="List of EdgeEvidence models")
    explainability_records: list[EdgeExplainabilityRecord] = Field(default_factory=list, description="List of explainability records")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Edge Evidence & Traceability Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Evidence Records**: {len(self.evidence_records)}",
            f"- **Total Traceability Records**: {len(self.explainability_records)}",
            "",
            "## Evidence Records",
            "| Evidence ID | Edge ID | Source Type | Source Reference | Confidence |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for ev in sorted(self.evidence_records, key=lambda x: x.evidence_id):
            st = ev.source_type.value if hasattr(ev.source_type, "value") else str(ev.source_type)
            lines.append(
                f"| `{ev.evidence_id}` | `{ev.edge_id}` | `{st}` | `{ev.source_reference}` | `{ev.confidence:.2f}` |"
            )

        lines.extend(["", "## Traceability Explanations"])
        for ex in sorted(self.explainability_records, key=lambda x: x.explanation_id):
            lines.append(f"- **`{ex.edge_id}`**: {ex.scientific_explanation}")

        return "\n".join(lines)


class EdgeQualityReport(BaseModel):
    """Report detailing multi-dimensional EdgeScore quality metrics."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    scores: list[EdgeScore] = Field(default_factory=list, description="List of EdgeScore models")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Edge Quality Assessment Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Evaluated Edges**: {len(self.scores)}",
            "",
            "| Score ID | Edge ID | Quality | Evidence Strength | Reproducibility | Stability | Overall |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for s in sorted(self.scores, key=lambda x: x.score_id):
            lines.append(
                f"| `{s.score_id}` | `{s.edge_id}` | `{s.scientific_quality:.2f}` | `{s.evidence_strength:.2f}` | `{s.reproducibility_score:.2f}` | `{s.stability_score:.2f}` | `{s.overall_edge_score:.2f}` |"
            )
        return "\n".join(lines)


class ScientificAlphaReport(BaseModel):
    """Executive root report for Scientific Alpha Engine discovery and ranking."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_edges_discovered: int = Field(..., ge=0)
    top_ranked_edge_id: str = Field(default="")
    top_edge_score: float = Field(default=0.0)
    foundational_count: int = Field(default=0, ge=0)
    mature_count: int = Field(default=0, ge=0)
    validated_count: int = Field(default=0, ge=0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Alpha Engine Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Discovered Edges**: {self.total_edges_discovered}",
            f"- **Top Ranked Edge**: `{self.top_ranked_edge_id or 'NONE'}`",
            f"- **Top Edge Quality Score**: `{self.top_edge_score:.4f}`",
            "",
            "## Edge Maturity Breakdown",
            f"- **Foundational**: {self.foundational_count}",
            f"- **Mature**: {self.mature_count}",
            f"- **Validated**: {self.validated_count}",
            "",
            "## Summary Rationale",
            self.summary_notes or "Alpha discovery completed deterministically without ML or LLM inference.",
        ]
        return "\n".join(lines)
