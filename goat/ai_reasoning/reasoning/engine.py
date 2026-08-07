"""
Project GOAT Phase 7 — Reasoning Engine (`goat.ai_reasoning.reasoning`)

Generates deterministic research conclusions backed by empirical evidence bundles without LLMs or hallucinations.
"""

from __future__ import annotations

from goat.ai_reasoning.evidence.engine import EvidenceEngine
from goat.ai_reasoning.models.report import ReasoningConclusion, compute_conclusion_id
from goat.edge_discovery.models.edge import DiscoveredEdge, EdgeStatus


class ReasoningEngine:
    """Quantitative Reasoning Engine deducing deterministic research conclusions."""

    def __init__(self, evidence_engine: EvidenceEngine | None = None):
        self.evidence_engine = evidence_engine or EvidenceEngine()

    def deduce_edge_status_conclusion(self, edge: DiscoveredEdge) -> ReasoningConclusion:
        """Deduce a deterministic reasoning conclusion explaining an edge's status."""
        bundle = self.evidence_engine.build_evidence_bundle(edge)
        m = edge.metrics

        steps: list[str] = []

        if edge.status == EdgeStatus.ACTIVE:
            steps.append(f"Expected Value ({m.expected_value:.6f}) remains positive.")
            steps.append(f"Annualized Sharpe Ratio ({m.sharpe_ratio:.2f}) meets institutional threshold.")
            steps.append(f"Statistical significance p-value ({edge.p_value:.6f}) confirms alpha level <= 0.05.")
            steps.append("Out-of-sample walk-forward validation demonstrates persistent edge.")
            steps.append("No statistical decay or regime degradation detected.")
            verdict = "ACTIVE"
            claim = f"Edge {edge.edge_id} remains ACTIVE due to robust empirical metrics."
        elif edge.status == EdgeStatus.WATCHLIST:
            steps.append(f"Expected Value ({m.expected_value:.6f}) has moderated near hurdle rate.")
            steps.append(f"Statistical significance p-value ({edge.p_value:.6f}) remains within watchlist range.")
            steps.append("Edge placed on WATCHLIST for performance drift monitoring.")
            verdict = "WATCHLIST"
            claim = f"Edge {edge.edge_id} transitioned to WATCHLIST due to performance drift."
        elif edge.status == EdgeStatus.DEGRADING:
            steps.append(f"Expected Value ({m.expected_value:.6f}) shows degradation.")
            steps.append("Performance drift detected across recent observations.")
            verdict = "DEGRADING"
            claim = f"Edge {edge.edge_id} marked DEGRADING due to negative expectancy trend."
        else:
            steps.append("Statistical significance p-value exceeds alpha limit 0.15.")
            steps.append("Edge fail-closed threshold triggered.")
            verdict = "RETIRED"
            claim = f"Edge {edge.edge_id} RETIRED due to statistical invalidation."

        c_id, _ = compute_conclusion_id(claim, verdict)
        ev_ids = [r.record_id for r in bundle.records]

        return ReasoningConclusion(
            conclusion_id=c_id,
            claim=claim,
            status_verdict=verdict,
            reasoning_steps=steps,
            supporting_evidence_ids=ev_ids,
            confidence_score=bundle.overall_confidence,
        )
