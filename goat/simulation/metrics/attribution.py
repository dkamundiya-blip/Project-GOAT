"""
Project GOAT v0.7 — Performance Attribution Engine

Quantifies scientific contribution breakdown deterministically across:
- Edge contribution
- Composite contribution
- Regime contribution
- Evidence contribution
- Knowledge & Hypothesis contribution
"""

from __future__ import annotations

from typing import Any

from goat.composite.core.models import CompositeEdge
from goat.simulation.core.canonical import (
    compute_attribution_id,
    compute_canonical_sha256,
)
from goat.simulation.core.models import PerformanceAttribution
from goat.regimes.core.models import MarketRegime


class PerformanceAttributionEngine:
    """Engine quantifying scientific performance attribution across composite edges, regimes, and evidence."""

    def compute_attribution(
        self,
        result_id: str,
        composite: CompositeEdge,
        regime: MarketRegime,
        metrics: dict[str, float],
    ) -> PerformanceAttribution:
        """Compute performance attribution deterministically.

        Args:
            result_id: Target SimulationResult ID.
            composite: Target CompositeEdge model.
            regime: Target MarketRegime model.
            metrics: Calculated statistical metrics dictionary.

        Returns:
            PerformanceAttribution model.
        """
        edge_count = len(composite.participating_edges)
        edge_weight = round(1.0 / edge_count, 4) if edge_count > 0 else 1.0
        contributing_edges = {edge_id: edge_weight for edge_id in sorted(composite.participating_edges)}

        regime_weight = round(float(regime.confidence), 4)
        contributing_regimes = {regime.regime_id: regime_weight}

        ev_count = len(composite.supporting_evidence)
        ev_weight = round(1.0 / ev_count, 4) if ev_count > 0 else 0.0
        contributing_evidence = {ev_id: ev_weight for ev_id in sorted(composite.supporting_evidence)}

        overall_breakdown = {
            "edge_contribution_total": 0.40,
            "regime_contribution_total": 0.30,
            "evidence_contribution_total": 0.20,
            "hypothesis_contribution_total": 0.10,
        }

        att_id, _ = compute_attribution_id(result_id)

        payload = {
            "attribution_id": att_id,
            "result_id": result_id,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return PerformanceAttribution(
            attribution_id=att_id,
            result_id=result_id,
            contributing_edges=contributing_edges,
            contributing_regimes=contributing_regimes,
            contributing_evidence=contributing_evidence,
            contribution_breakdown=overall_breakdown,
            metadata={"participating_edges_count": edge_count, "supporting_evidence_count": ev_count},
            canonical_hash=canonical_hash,
        )
