"""
Project GOAT v0.7 — Composite Reports

Provides immutable, deterministic report models and renderers:
- CompositeEdgeReport
- CompositeEvidenceReport
- CompositeScoreReport
- CompositeRankingReport
- CompositeAnalysisReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.composite.core.models import (
    CompositeEdge,
    CompositeEvidence,
    CompositeExplainabilityRecord,
    CompositeRanking,
    CompositeScore,
)
from goat.integration.core.canonical import serialize_canonical_json


class CompositeEdgeReport(BaseModel):
    """Report detailing single or multiple CompositeEdges."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    composites: list[CompositeEdge] = Field(default_factory=list, description="List of synthesized CompositeEdges")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Composite Candidate Edge Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Composites**: {len(self.composites)}",
            "",
            "| Composite ID | Title | Edges Count | Hypotheses Count | Evidence Count |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for c in sorted(self.composites, key=lambda x: x.composite_id):
            lines.append(
                f"| `{c.composite_id}` | {c.title} | {len(c.participating_edges)} | {len(c.participating_hypotheses)} | {len(c.supporting_evidence)} |"
            )
        return "\n".join(lines)


class CompositeEvidenceReport(BaseModel):
    """Report detailing CompositeEvidence and explainability records."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    evidence_records: list[CompositeEvidence] = Field(default_factory=list, description="List of CompositeEvidence models")
    explainability_records: list[CompositeExplainabilityRecord] = Field(default_factory=list, description="List of explainability records")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Composite Evidence & Traceability Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Evidence Records**: {len(self.evidence_records)}",
            f"- **Total Traceability Records**: {len(self.explainability_records)}",
            "",
            "## Evidence Records",
            "| Evidence ID | Composite ID | Contributing Edge | Strength | Rationale |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for ev in sorted(self.evidence_records, key=lambda x: x.evidence_id):
            lines.append(
                f"| `{ev.evidence_id}` | `{ev.composite_id}` | `{ev.contributing_edge}` | `{ev.contribution_strength:.2f}` | {ev.explanation} |"
            )

        lines.extend(["", "## Traceability Explanations"])
        for ex in sorted(self.explainability_records, key=lambda x: x.explanation_id):
            lines.append(f"- **`{ex.composite_id}`**: {ex.scientific_explanation}")

        return "\n".join(lines)


class CompositeScoreReport(BaseModel):
    """Report detailing multi-dimensional CompositeScore metrics."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    scores: list[CompositeScore] = Field(default_factory=list, description="List of CompositeScore models")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Composite Quality Score Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Evaluated Composites**: {len(self.scores)}",
            "",
            "| Score ID | Composite ID | Synergy | Robustness | Diversity | Penalty | Overall |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for s in sorted(self.scores, key=lambda x: x.score_id):
            lines.append(
                f"| `{s.score_id}` | `{s.composite_id}` | `{s.synergy_score:.2f}` | `{s.robustness_score:.2f}` | `{s.diversity_score:.2f}` | `{s.conflict_penalty:.2f}` | `{s.overall_score:.2f}` |"
            )
        return "\n".join(lines)


class CompositeRankingReport(BaseModel):
    """Report detailing deterministic CompositeRanking results."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    ranking: CompositeRanking = Field(..., description="Target CompositeRanking model")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        rk = self.ranking
        lines = [
            f"# Composite Ranking Report ({self.report_id})",
            "",
            f"- **Ranking ID**: `{rk.ranking_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Ranked Composites**: {len(rk.ranked_composites)}",
            f"- **Ranking Rules**: {', '.join(rk.ranking_rules)}",
            "",
            "| Rank | Composite ID | Overall Score | Synergy | Robustness | Conflict Penalty |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        score_map = {s.composite_id: s for s in rk.composite_scores}
        for rank_idx, comp_id in enumerate(rk.ranked_composites, 1):
            sc = score_map.get(comp_id)
            if sc:
                lines.append(
                    f"| {rank_idx} | `{comp_id}` | `{sc.overall_score:.4f}` | `{sc.synergy_score:.4f}` | `{sc.robustness_score:.4f}` | `{sc.conflict_penalty:.4f}` |"
                )
            else:
                lines.append(f"| {rank_idx} | `{comp_id}` | N/A | N/A | N/A | N/A |")
        return "\n".join(lines)


class CompositeAnalysisReport(BaseModel):
    """Executive root report for Composite Edge Synthesis Engine."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_active_edges_input: int = Field(..., ge=0)
    total_composites_synthesized: int = Field(..., ge=0)
    top_ranked_composite_id: str = Field(default="")
    top_composite_score: float = Field(default=0.0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Composite Edge Synthesis Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Active Input Edges**: {self.total_active_edges_input}",
            f"- **Total Composites Synthesized**: {self.total_composites_synthesized}",
            f"- **Top Ranked Composite**: `{self.top_ranked_composite_id or 'NONE'}`",
            f"- **Top Composite Quality Score**: `{self.top_composite_score:.4f}`",
            "",
            "## Summary Rationale",
            self.summary_notes or "Composite edge synthesis completed deterministically without ML or LLM inference.",
        ]
        return "\n".join(lines)
