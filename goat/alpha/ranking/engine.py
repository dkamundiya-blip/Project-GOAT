"""
Project GOAT v0.7 — Scientific Edge Ranking Engine

Ranks candidate quantitative market edges deterministically:
- Overall Quality Score
- Scientific Quality
- Reproducibility
- Longevity
- Deterministic, stable tie-breaking
"""

from __future__ import annotations

from typing import Any

from goat.alpha.core.canonical import compute_canonical_sha256, compute_ranking_id
from goat.alpha.core.enums import RankingRuleType
from goat.alpha.core.models import EdgeRanking, EdgeScore, ScientificEdge


class EdgeRankingEngine:
    """Engine for deterministic, stable ranking of candidate ScientificEdges."""

    def rank_edges(
        self,
        edges: list[ScientificEdge],
        scores: list[EdgeScore],
        timestamp: str,
        ranking_rule: RankingRuleType = RankingRuleType.OVERALL_QUALITY,
    ) -> EdgeRanking:
        """Rank candidate ScientificEdges deterministically.

        Args:
            edges: List of candidate ScientificEdge models.
            scores: List of corresponding EdgeScore models.
            timestamp: ISO 8601 UTC timestamp string.
            ranking_rule: Ranking rule type enum.

        Returns:
            EdgeRanking model with ranked_edges sorted deterministically.
        """
        score_map = {s.edge_id: s for s in scores}
        edge_map = {e.edge_id: e for e in edges}

        # Deterministic sorting key with stable tie-breaking
        def _sort_key(edge_id: str) -> tuple[float, float, float, str]:
            sc = score_map.get(edge_id)
            if not sc:
                return (0.0, 0.0, 0.0, edge_id)
            return (
                -sc.overall_edge_score,     # Primary: overall score (descending)
                -sc.scientific_quality,      # Tie-breaker 1: scientific quality (descending)
                -sc.reproducibility_score,   # Tie-breaker 2: reproducibility (descending)
                edge_id,                     # Tie-breaker 3: edge_id (alphabetical ascending)
            )

        sorted_edge_ids = sorted(list(edge_map.keys()), key=_sort_key)
        sorted_scores = [score_map[eid] for eid in sorted_edge_ids if eid in score_map]

        ranking_id, _ = compute_ranking_id(sorted_edge_ids, timestamp)

        payload = {
            "ranking_id": ranking_id,

            "ranking_timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        rule_name = ranking_rule.value if hasattr(ranking_rule, "value") else str(ranking_rule)

        return EdgeRanking(
            ranking_id=ranking_id,
            ranked_edges=sorted_edge_ids,
            edge_scores=sorted_scores,
            ranking_timestamp=timestamp,
            ranking_rules=[rule_name, "STABLE_TIE_BREAKING_SCORE_QUALITY_ID"],
            metadata={"edge_count": len(sorted_edge_ids)},
            canonical_hash=canonical_hash,
        )
