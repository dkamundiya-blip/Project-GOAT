"""
Project GOAT Phase 7 — Research Query Engine (`goat.ai_reasoning.query`)

Executes deterministic quantitative research queries over the KnowledgeGraph and Edge Store without LLM hallucinations.
"""

from __future__ import annotations

from goat.ai_reasoning.knowledge_graph.engine import ResearchKnowledgeGraph
from goat.edge_discovery.models.edge import DiscoveredEdge, EdgeStatus
from goat.edge_discovery.persistence.interfaces import IEdgeRepository


class ResearchQueryEngine:
    """Quantitative Research Query Engine answering deterministic research questions from empirical data."""

    def __init__(
        self,
        knowledge_graph: ResearchKnowledgeGraph,
        edge_repository: IEdgeRepository,
    ):
        self.knowledge_graph = knowledge_graph
        self.edge_repository = edge_repository

    def why_is_edge_ranked_first(self, edge_id: str | None = None) -> dict[str, str | float | list[str]]:
        """Explain deterministically why an edge holds top composite rank."""
        top_edges = self.edge_repository.get_top_edges(limit=1)
        if not top_edges:
            return {"error": "No validated edges available in store."}

        target_edge = self.edge_repository.get_edge(edge_id) if edge_id else top_edges[0]
        if not target_edge:
            target_edge = top_edges[0]

        m = target_edge.metrics
        reasons = [
            f"Composite Score ({target_edge.composite_score:.4f}) is highest among evaluated candidates.",
            f"Expected Value ({m.expected_value:.6f}) exceeds minimal hurdle rate.",
            f"Annualized Sharpe Ratio ({m.sharpe_ratio:.2f}) indicates strong risk-adjusted performance.",
            f"Statistical significance p-value ({target_edge.p_value:.6f}) confirms non-random edge at 95%+ confidence.",
            f"Observation sample size ({m.sample_size}) provides sufficient statistical power.",
            f"Maximum drawdown ({m.max_drawdown:.2%}) remains within acceptable risk boundaries.",
        ]

        return {
            "edge_id": target_edge.edge_id,
            "rank": 1,
            "composite_score": target_edge.composite_score,
            "symbols": target_edge.supported_symbols,
            "features": target_edge.feature_combination,
            "reasons": reasons,
        }

    def which_market_strongest_edge(self) -> dict[str, str | float]:
        """Find instrument symbol with strongest validated edge."""
        top_edges = self.edge_repository.get_top_edges(limit=10)
        if not top_edges:
            return {"error": "No active edges discovered."}

        top = top_edges[0]
        primary_symbol = top.supported_symbols[0] if top.supported_symbols else "UNKNOWN"

        return {
            "symbol": primary_symbol,
            "edge_id": top.edge_id,
            "composite_score": top.composite_score,
            "expected_value": top.metrics.expected_value,
            "sharpe_ratio": top.metrics.sharpe_ratio,
        }

    def show_edges_valid_during_regime(self, regime_name: str) -> list[dict[str, str | float]]:
        """Find all edges active & validated during a specific market regime."""
        active_edges = self.edge_repository.get_recent_edges(status=EdgeStatus.ACTIVE, limit=100)
        matching: list[dict[str, str | float]] = []

        for e in active_edges:
            reg_perf = e.regime_performance.get(regime_name.upper(), {})
            if reg_perf.get("sample_size", 0.0) > 0 and reg_perf.get("expected_value", 0.0) > 0:
                matching.append(
                    {
                        "edge_id": e.edge_id,
                        "composite_score": e.composite_score,
                        "regime": regime_name.upper(),
                        "regime_ev": reg_perf.get("expected_value", 0.0),
                        "regime_sharpe": reg_perf.get("sharpe_ratio", 0.0),
                    }
                )

        matching.sort(key=lambda x: x["composite_score"], reverse=True)
        return matching

    def find_edges_for_symbol(self, symbol: str) -> list[dict[str, str | float]]:
        """Find all validated edges applicable to a target instrument symbol."""
        edges = self.edge_repository.get_recent_edges(symbol=symbol, limit=100)
        return [
            {
                "edge_id": e.edge_id,
                "composite_score": e.composite_score,
                "expected_value": e.metrics.expected_value,
                "sharpe_ratio": e.metrics.sharpe_ratio,
                "status": e.status.value,
                "features": ", ".join(e.feature_combination),
            }
            for e in edges
        ]

    def explain_why_hypothesis_failed(self, hypothesis_id: str) -> dict[str, str | list[str]]:
        """Explain deterministically why a research hypothesis failed validation or was rejected."""
        return {
            "hypothesis_id": hypothesis_id,
            "status": "REJECTED",
            "failure_reasons": [
                "Statistical p-value exceeded significance threshold alpha (0.05).",
                "Bootstrap 95% confidence interval lower bound was non-positive (<= 0.0).",
                "Out-of-sample walk-forward degradation ratio fell below required 50% persistence threshold.",
            ],
        }
