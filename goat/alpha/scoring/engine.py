"""
Project GOAT v0.7 — Scientific Edge Scoring Engine

Calculates deterministic multi-dimensional quality scores for candidate market edges:
- Evidence Strength
- Scientific Confidence
- Reproducibility
- Stability
- Robustness
- Knowledge Support
- Conflict Penalty
- Longevity
- Overall Edge Quality Score
"""

from __future__ import annotations

from typing import Any

from goat.alpha.core.canonical import compute_canonical_sha256, compute_score_id
from goat.alpha.core.models import EdgeScore, ScientificEdge


class EdgeScoringEngine:
    """Engine for computing deterministic multi-dimensional scores for ScientificEdges."""

    def compute_edge_score(
        self,
        edge: ScientificEdge,
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> EdgeScore:
        """Compute an EdgeScore model deterministically for a candidate ScientificEdge.

        Args:
            edge: Target ScientificEdge model.
            conflicts: List of conflict records.
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            EdgeScore model.
        """
        conf_score = round(max(0.0, min(1.0, float(edge.confidence))), 4)
        repr_score = round(max(0.0, min(1.0, float(edge.reproducibility))), 4)
        rob_score = round(max(0.0, min(1.0, float(edge.robustness))), 4)
        stab_score = round(max(0.0, min(1.0, float(edge.stability))), 4)

        # Evidence Strength calculation
        ev_count = len(edge.supporting_evidence)
        evidence_strength = round(max(0.0, min(1.0, 0.4 * conf_score + min(0.6, 0.15 * ev_count))), 4)

        # Scientific Quality composite
        sci_quality = round(max(0.0, min(1.0, 0.4 * conf_score + 0.3 * repr_score + 0.3 * rob_score)), 4)

        # Longevity score based on maturity
        maturity_weights = {
            "NEW": 0.20,
            "EXPERIMENTAL": 0.40,
            "EMERGING": 0.60,
            "VALIDATED": 0.80,
            "MATURE": 0.90,
            "FOUNDATIONAL": 1.00,
        }
        mat_str = edge.maturity.value if hasattr(edge.maturity, "value") else str(edge.maturity)
        longevity_score = round(maturity_weights.get(mat_str, 0.50), 4)

        # Conflict penalty
        edge_conflicts = [
            c for c in conflicts if any(v in str(c.get("validation_a")) or v in str(c.get("validation_b")) for v in edge.originating_validations)
        ]
        conflict_penalty = round(min(0.50, 0.15 * len(edge_conflicts)), 4)

        # Overall Edge Score
        raw_overall = (sci_quality + evidence_strength + repr_score + stab_score + longevity_score) / 5.0 - conflict_penalty
        overall_score = round(max(0.0, min(1.0, raw_overall)), 4)

        score_id, _ = compute_score_id(edge.edge_id, overall_score, timestamp)

        payload = {
            "edge_id": edge.edge_id,
            "overall_edge_score": overall_score,
            "score_id": score_id,
            "timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return EdgeScore(
            score_id=score_id,
            edge_id=edge.edge_id,
            confidence_score=conf_score,
            reproducibility_score=repr_score,
            robustness_score=rob_score,
            stability_score=stab_score,
            evidence_strength=evidence_strength,
            scientific_quality=sci_quality,
            longevity_score=longevity_score,
            conflict_penalty=conflict_penalty,
            overall_edge_score=overall_score,
            timestamp=timestamp,
            canonical_hash=canonical_hash,
        )

    def score_all_edges(
        self,
        edges: list[ScientificEdge],
        conflicts: list[dict[str, Any]],
        timestamp: str,
    ) -> list[EdgeScore]:
        """Compute EdgeScore models for a list of ScientificEdges deterministically."""
        scores = [self.compute_edge_score(e, conflicts, timestamp) for e in edges]
        return sorted(scores, key=lambda s: s.score_id)
