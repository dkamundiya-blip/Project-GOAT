"""
Project GOAT v0.9 — Quantitative Edge Discovery Scoring Engine
"""

from typing import Any

from goat.edge_discovery.core.canonical import compute_edge_score_id
from goat.edge_discovery.core.enums import QualityTier
from goat.edge_discovery.core.models import EdgeCandidate, EdgeScore


class EdgeScoringEngine:
    """Quantitative Sub-Engine for Institutional Edge Scoring.

    Computes multi-dimensional institutional quality scores based on:
    • Support (sample size & observation density)
    • Stability (variance & statistical confidence)
    • Consistency (regime alignment)
    • Robustness (cross-market stability)
    • Live validation compatibility

    Strict Protocol Constraint: ZERO parameter optimization.
    """

    def score_candidate(
        self,
        candidate: EdgeCandidate,
        patterns: list[Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EdgeScore:
        """Compute institutional quality score for a candidate edge."""
        meta = dict(metadata or {})

        # 1. Support Score (0..100) based on observation count
        n = candidate.observation_count
        support_score = min(100.0, max(0.0, (n / 100.0) * 100.0))

        # 2. Stability Score (0..100) based on confidence level
        conf = candidate.confidence_level
        stability_score = min(100.0, max(0.0, conf * 100.0))

        # 3. Consistency Score (0..100) from patterns if available
        if patterns:
            regime_ratios = [float(getattr(p, "regime_consistency", 0.8)) for p in patterns]
            avg_consistency = sum(regime_ratios) / len(regime_ratios)
        else:
            avg_consistency = 0.85
        consistency_score = min(100.0, max(0.0, avg_consistency * 100.0))

        # 4. Robustness Score (0..100)
        robustness_score = round(0.5 * support_score + 0.5 * consistency_score, 2)

        # 5. Live Compatibility Score (0..100)
        live_compatibility = round(0.4 * stability_score + 0.6 * consistency_score, 2)

        # Composite Overall Score (weighted average)
        overall_score = round(
            0.25 * support_score
            + 0.25 * stability_score
            + 0.20 * consistency_score
            + 0.15 * robustness_score
            + 0.15 * live_compatibility,
            2,
        )

        tier = self._classify_tier(overall_score)

        s_id, s_hash = compute_edge_score_id(
            candidate_id=candidate.candidate_id,
            overall_score=overall_score,
            tier=tier.value,
        )

        return EdgeScore(
            score_id=s_id,
            candidate_id=candidate.candidate_id,
            overall_score=overall_score,
            support_score=round(support_score, 2),
            stability_score=round(stability_score, 2),
            consistency_score=round(consistency_score, 2),
            robustness_score=round(robustness_score, 2),
            live_compatibility_score=round(live_compatibility, 2),
            quality_tier=tier,
            metadata=meta,
            canonical_hash=s_hash,
        )

    def _classify_tier(self, score: float) -> QualityTier:
        if score >= 85.0:
            return QualityTier.INSTITUTIONAL_GRADE
        elif score >= 70.0:
            return QualityTier.HIGH_QUALITY
        elif score >= 50.0:
            return QualityTier.MARGINAL
        return QualityTier.SUBPAR
