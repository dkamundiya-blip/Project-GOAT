"""
Project GOAT v0.7 — Composite Edge Scoring Engine

Calculates multi-dimensional synergy and quality metrics for composite market edges:
- Synergy Score (Knowledge reinforcement)
- Robustness Score (Cross-validation strength)
- Stability Score (Historical consistency)
- Diversity Score (Evidence diversity & scientific breadth)
- Conflict Penalty
- Explainability Score
- Reproducibility Score
- Aggregated Overall Score
"""

from __future__ import annotations

from typing import Any

from goat.alpha.core.models import ScientificEdge
from goat.composite.core.canonical import (
    compute_canonical_sha256,
    compute_composite_score_id,
)
from goat.composite.core.models import CompositeEdge, CompositeScore


class CompositeScoringEngine:
    """Engine for computing deterministic multi-dimensional scores for CompositeEdges."""

    def compute_composite_score(
        self,
        composite: CompositeEdge,
        participating_edges: list[ScientificEdge],
        conflict_penalty: float,
        timestamp: str,
    ) -> CompositeScore:
        """Compute a CompositeScore model deterministically for a CompositeEdge.

        Args:
            composite: Target CompositeEdge model.
            participating_edges: List of component ScientificEdge models.
            conflict_penalty: Evaluated conflict penalty float.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            CompositeScore model.
        """
        if not participating_edges:
            zero_id, zero_hash = compute_composite_score_id(composite.composite_id, 0.0, timestamp)
            return CompositeScore(score_id=zero_id, composite_id=composite.composite_id, timestamp=timestamp, canonical_hash=zero_hash)

        # 1. Reproducibility Score (mean of participating edges)
        repr_scores = [float(e.reproducibility) for e in participating_edges]
        reproducibility_score = round(sum(repr_scores) / len(repr_scores), 4)

        # 2. Robustness Score (mean robustness)
        rob_scores = [float(e.robustness) for e in participating_edges]
        robustness_score = round(sum(rob_scores) / len(rob_scores), 4)

        # 3. Stability Score (mean stability)
        stab_scores = [float(e.stability) for e in participating_edges]
        stability_score = round(sum(stab_scores) / len(stab_scores), 4)

        # 4. Synergy Score (knowledge reinforcement from multiple independent edges)
        conf_scores = [float(e.confidence) for e in participating_edges]
        avg_conf = sum(conf_scores) / len(conf_scores)
        synergy_score = round(min(1.0, avg_conf + 0.05 * (len(participating_edges) - 1)), 4)

        # 5. Diversity Score (diversity of originating hypotheses and evidence)
        all_hyps = set(composite.participating_hypotheses)
        all_ev = set(composite.supporting_evidence)
        diversity_score = round(min(1.0, 0.30 + 0.15 * len(all_hyps) + 0.10 * len(all_ev)), 4)

        # 6. Explainability Score
        expl_score = 0.90 if len(composite.participating_edges) >= 2 else 0.70

        # 7. Overall Score
        raw_overall = (synergy_score + robustness_score + stability_score + diversity_score + reproducibility_score) / 5.0 - conflict_penalty
        overall_score = round(max(0.0, min(1.0, raw_overall)), 4)

        score_id, _ = compute_composite_score_id(composite.composite_id, overall_score, timestamp)

        payload = {
            "composite_id": composite.composite_id,
            "overall_score": overall_score,
            "score_id": score_id,
            "timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return CompositeScore(
            score_id=score_id,
            composite_id=composite.composite_id,
            synergy_score=synergy_score,
            robustness_score=robustness_score,
            stability_score=stability_score,
            diversity_score=diversity_score,
            conflict_penalty=conflict_penalty,
            explainability_score=expl_score,
            reproducibility_score=reproducibility_score,
            overall_score=overall_score,
            timestamp=timestamp,
            canonical_hash=canonical_hash,
        )

    def score_all_composites(
        self,
        composites: list[CompositeEdge],
        edge_map: dict[str, ScientificEdge],
        conflict_map: dict[str, float],
        timestamp: str,
    ) -> list[CompositeScore]:
        """Compute CompositeScore models for a list of CompositeEdges deterministically."""
        scores: list[CompositeScore] = []
        for c in composites:
            p_edges = [edge_map[eid] for eid in c.participating_edges if eid in edge_map]
            pen = conflict_map.get(c.composite_id, 0.0)
            sc = self.compute_composite_score(c, p_edges, pen, timestamp)
            scores.append(sc)
        return sorted(scores, key=lambda s: s.score_id)
