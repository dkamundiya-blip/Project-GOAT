"""
Project GOAT Phase 6 — Edge Ranking Engine (`goat.edge_discovery.ranking`)

Ranks discovered quantitative edges using configurable multi-criteria composite scoring models.
"""

from __future__ import annotations

import math
from typing import Sequence

from goat.edge_discovery.models.edge import DiscoveredEdge, EdgeStatus


class EdgeRankingEngine:
    """Quantitative Edge Ranking Engine computing composite scores and multi-dimensional filtering."""

    def __init__(
        self,
        w_ev: float = 0.25,
        w_sharpe: float = 0.25,
        w_pvalue: float = 0.20,
        w_sample: float = 0.15,
        w_drawdown: float = 0.15,
    ):
        self.w_ev = w_ev
        self.w_sharpe = w_sharpe
        self.w_pvalue = w_pvalue
        self.w_sample = w_sample
        self.w_drawdown = w_drawdown

    def compute_composite_score(self, edge: DiscoveredEdge) -> float:
        """Compute multi-factor composite ranking score for a DiscoveredEdge."""
        m = edge.metrics

        # 1. EV Score (scaled by 1000 for small return values)
        ev_score = min(1.0, max(0.0, m.expected_value * 500.0))

        # 2. Sharpe Score
        sharpe_score = min(1.0, max(0.0, m.sharpe_ratio / 3.0))

        # 3. P-Value Significance Score
        p_score = max(0.0, 1.0 - (edge.p_value / 0.05)) if edge.p_value <= 0.05 else 0.0

        # 4. Sample Size Score
        sample_score = min(1.0, m.sample_size / 100.0)

        # 5. Drawdown Penalty Score
        dd_score = max(0.0, 1.0 - m.max_drawdown * 2.0)

        composite = (
            (ev_score * self.w_ev)
            + (sharpe_score * self.w_sharpe)
            + (p_score * self.w_pvalue)
            + (sample_score * self.w_sample)
            + (dd_score * self.w_drawdown)
        )
        return round(max(0.0, min(1.0, composite)), 4)

    def rank_edges(
        self,
        edges: Sequence[DiscoveredEdge],
        symbol: str | None = None,
        timeframe: str | None = None,
        min_composite_score: float = 0.0,
        status: EdgeStatus | None = EdgeStatus.ACTIVE,
        top_n: int = 50,
    ) -> list[DiscoveredEdge]:
        """Filter and rank edges ordered descending by composite score."""
        filtered: list[DiscoveredEdge] = []

        for e in edges:
            if status and e.status != status:
                continue
            if symbol and symbol.upper() not in [s.upper() for s in e.supported_symbols]:
                continue
            if timeframe and timeframe.lower() not in [tf.lower() for tf in e.supported_timeframes]:
                continue
            if e.composite_score < min_composite_score:
                continue
            filtered.append(e)

        filtered.sort(key=lambda x: x.composite_score, reverse=True)
        return filtered[:top_n]
