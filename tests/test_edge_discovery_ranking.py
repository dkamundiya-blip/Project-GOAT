"""
Project GOAT Phase 6 — Unit Tests for Edge Ranking Engine
"""

from goat.edge_discovery.models import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    compute_edge_id,
)
from goat.edge_discovery.ranking import EdgeRankingEngine


def make_edge(symbol: str, ev: float, sharpe: float, pval: float) -> DiscoveredEdge:
    metrics = EdgePerformanceMetrics(
        sample_size=100,
        win_rate=0.6,
        loss_rate=0.4,
        expected_value=ev,
        average_return=ev,
        median_return=ev * 0.9,
        max_gain=0.01,
        max_loss=-0.005,
        profit_factor=1.6,
        sharpe_ratio=sharpe,
        sortino_ratio=2.0,
        calmar_ratio=2.5,
        max_drawdown=0.04,
        recovery_factor=3.0,
        trade_frequency=5.0,
        holding_period=5.0,
    )
    e_id, c_hash = compute_edge_id("HYP_1", ["trend"], [symbol], ["1m"])
    engine = EdgeRankingEngine()

    temp_edge = DiscoveredEdge(
        edge_id=e_id,
        version="6.0.0",
        hypothesis_id="HYP_1",
        feature_combination=["trend"],
        supported_symbols=[symbol],
        supported_timeframes=["1m"],
        metrics=metrics,
        p_value=pval,
        confidence_interval_low=0.0005,
        confidence_interval_high=0.0015,
        effect_size=0.7,
        composite_score=0.0,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )
    score = engine.compute_composite_score(temp_edge)

    return DiscoveredEdge(
        edge_id=e_id,
        version="6.0.0",
        hypothesis_id="HYP_1",
        feature_combination=["trend"],
        supported_symbols=[symbol],
        supported_timeframes=["1m"],
        metrics=metrics,
        p_value=pval,
        confidence_interval_low=0.0005,
        confidence_interval_high=0.0015,
        effect_size=0.7,
        composite_score=score,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_edge_ranking_engine():
    engine = EdgeRankingEngine()
    e1 = make_edge("VOLATILITY_100", 0.001, 1.5, 0.04)
    e2 = make_edge("CRASH_500", 0.003, 2.8, 0.001)

    ranked = engine.rank_edges([e1, e2], top_n=10)

    assert len(ranked) == 2
    assert ranked[0].edge_id == e2.edge_id  # Higher EV & Sharpe ranks first
    assert ranked[0].composite_score > ranked[1].composite_score
