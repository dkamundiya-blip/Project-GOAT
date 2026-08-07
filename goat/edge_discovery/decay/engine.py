"""
Project GOAT Phase 6 — Edge Decay Engine (`goat.edge_discovery.decay`)

Monitors performance drift, expectancy decay, and statistical confidence shift over time to transition edge statuses.
"""

from __future__ import annotations

from goat.edge_discovery.models.edge import DiscoveredEdge, EdgePerformanceMetrics, EdgeStatus


class EdgeDecayEngine:
    """Quantitative Edge Decay Engine managing status lifecycle transitions."""

    def __init__(
        self,
        min_active_ev: float = 0.0005,
        min_watchlist_ev: float = 0.0,
        max_active_pvalue: float = 0.05,
        max_degrading_pvalue: float = 0.15,
    ):
        self.min_active_ev = min_active_ev
        self.min_watchlist_ev = min_watchlist_ev
        self.max_active_pvalue = max_active_pvalue
        self.max_degrading_pvalue = max_degrading_pvalue

    def evaluate_decay(
        self,
        edge: DiscoveredEdge,
        recent_metrics: EdgePerformanceMetrics,
        recent_pvalue: float,
    ) -> EdgeStatus:
        """Evaluate recent performance and p-value to determine updated EdgeStatus."""
        rec_ev = recent_metrics.expected_value

        # Status Transition Logic:
        # ACTIVE: EV >= min_active_ev and p_value <= 0.05
        # WATCHLIST: EV >= 0.0 and p_value <= 0.08
        # DEGRADING: EV < 0.0 or p_value <= 0.15
        # RETIRED: EV < -0.001 or p_value > 0.15 or sample size < 5
        if recent_metrics.sample_size < 5:
            return EdgeStatus.RETIRED

        if rec_ev >= self.min_active_ev and recent_pvalue <= self.max_active_pvalue:
            return EdgeStatus.ACTIVE
        elif rec_ev >= self.min_watchlist_ev and recent_pvalue <= 0.08:
            return EdgeStatus.WATCHLIST
        elif rec_ev >= -0.001 and recent_pvalue <= self.max_degrading_pvalue:
            return EdgeStatus.DEGRADING
        else:
            return EdgeStatus.RETIRED
