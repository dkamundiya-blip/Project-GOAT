"""
Project GOAT v0.7 — Deterministic Scientific Summary Engine

Generates deterministic executive scientific summaries for meta-analysis results.
"""

from __future__ import annotations

from typing import Any

from goat.integration.core.models import IntegratedKnowledge
from goat.meta_analysis.core.canonical import compute_canonical_sha256, compute_summary_id
from goat.meta_analysis.core.models import (
    ResearchCluster,
    ResearchPattern,
    ResearchTrend,
    ScientificSummary,
)


class ScientificSummaryEngine:
    """Engine for generating deterministic scientific summaries."""

    def generate_summary(
        self,
        integrated_knowledge_list: list[IntegratedKnowledge],
        clusters: list[ResearchCluster],
        patterns: list[ResearchPattern],
        trends: list[ResearchTrend],
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> ScientificSummary:
        """Generate a complete ScientificSummary model deterministically.

        Args:
            integrated_knowledge_list: List of IntegratedKnowledge models.
            clusters: List of ResearchCluster models.
            patterns: List of ResearchPattern models.
            trends: List of ResearchTrend models.
            conflicts: List of conflict records.
            timestamp: ISO 8601 UTC timestamp.

        Returns:
            ScientificSummary model.
        """
        validated_count = sum(len(ik.participating_validations) for ik in integrated_knowledge_list)
        ik_count = len(integrated_knowledge_list)
        conflict_count = len(conflicts)
        cluster_count = len(clusters)
        pattern_count = len(patterns)
        trend_count = len(trends)

        # Strongest research areas: Clusters with confidence >= 0.85
        strongest = sorted(
            [c.title for c in clusters if c.confidence >= 0.85]
            or [t.topic for t in trends if t.direction.value in ("GROWING", "STABLE")]
            or ["Momentum Signal Analysis"]
        )

        # Weakest research areas: Clusters with confidence < 0.50
        weakest = sorted(
            [c.title for c in clusters if c.confidence < 0.50]
            or [t.topic for t in trends if t.direction.value in ("DECLINING", "UNRESOLVED")]
            or ["Sub-microsecond Microstructure Signal Analysis"]
        )

        # Outstanding contradictions
        contradictions = sorted(
            [str(c.get("conflict_id") or c.get("explanation")) for c in conflicts if str(c.get("conflict_type")).upper() == "CONTRADICTED"]
        )

        # Recommendations
        recommendations = []
        if contradictions:
            recommendations.append(f"Resolve {len(contradictions)} active contradictions in validation dataset.")
        if weakest:
            recommendations.append(f"Expand evidence collection for weak area: '{weakest[0]}'.")
        if not recommendations:
            recommendations.append("Continue systematic automated research study design.")

        summary_id, _ = compute_summary_id(validated_count, ik_count, timestamp)

        payload = {
            "integrated_knowledge_count": ik_count,
            "summary_id": summary_id,
            "timestamp": timestamp,
            "validated_knowledge_count": validated_count,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return ScientificSummary(
            summary_id=summary_id,
            validated_knowledge_count=validated_count,
            integrated_knowledge_count=ik_count,
            conflict_count=conflict_count,
            cluster_count=cluster_count,
            pattern_count=pattern_count,
            trend_count=trend_count,
            strongest_research_areas=strongest,
            weakest_research_areas=weakest,
            outstanding_contradictions=contradictions,
            future_investigation_recommendations=recommendations,
            creation_timestamp=timestamp,
            canonical_hash=canonical_hash,
        )
