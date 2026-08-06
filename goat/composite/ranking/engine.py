"""
Project GOAT v0.7 — Composite Edge Ranking Engine

Ranks candidate synthesized CompositeEdges deterministically:
- Overall Score
- Synergy Score
- Robustness Score
- Deterministic, stable tie-breaking
"""

from __future__ import annotations

from typing import Any

from goat.composite.core.canonical import (
    compute_canonical_sha256,
    compute_composite_ranking_id,
)
from goat.composite.core.enums import RankingStrategy
from goat.composite.core.models import (
    CompositeEdge,
    CompositeRanking,
    CompositeScore,
)


class CompositeRankingEngine:
    """Engine for deterministic, stable ranking of synthesized CompositeEdges."""

    def rank_composites(
        self,
        composites: list[CompositeEdge],
        scores: list[CompositeScore],
        timestamp: str,
        ranking_strategy: RankingStrategy = RankingStrategy.OVERALL_QUALITY,
    ) -> CompositeRanking:
        """Rank synthesized CompositeEdges deterministically.

        Args:
            composites: List of candidate CompositeEdge models.
            scores: List of corresponding CompositeScore models.
            timestamp: ISO 8601 UTC timestamp string.
            ranking_strategy: Ranking strategy enum.

        Returns:
            CompositeRanking model with ranked_composites sorted deterministically.
        """
        score_map = {s.composite_id: s for s in scores}
        comp_map = {c.composite_id: c for c in composites}

        # Deterministic sorting key with stable tie-breaking
        def _sort_key(composite_id: str) -> tuple[float, float, float, str]:
            sc = score_map.get(composite_id)
            if not sc:
                return (0.0, 0.0, 0.0, composite_id)
            return (
                -sc.overall_score,       # Primary: overall score (descending)
                -sc.synergy_score,       # Tie-breaker 1: synergy score (descending)
                -sc.robustness_score,    # Tie-breaker 2: robustness score (descending)
                composite_id,            # Tie-breaker 3: composite_id (alphabetical ascending)
            )

        sorted_composite_ids = sorted(list(comp_map.keys()), key=_sort_key)
        sorted_scores = [score_map[cid] for cid in sorted_composite_ids if cid in score_map]

        ranking_id, _ = compute_composite_ranking_id(sorted_composite_ids, timestamp)

        payload = {
            "ranking_id": ranking_id,
            "ranking_timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        strat_name = ranking_strategy.value if hasattr(ranking_strategy, "value") else str(ranking_strategy)

        return CompositeRanking(
            ranking_id=ranking_id,
            ranked_composites=sorted_composite_ids,
            composite_scores=sorted_scores,
            ranking_timestamp=timestamp,
            ranking_rules=[strat_name, "STABLE_TIE_BREAKING_SCORE_SYNERGY_ID"],
            metadata={"composite_count": len(sorted_composite_ids)},
            canonical_hash=canonical_hash,
        )
