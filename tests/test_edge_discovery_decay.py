"""
Project GOAT Phase 6 — Unit Tests for Edge Decay Engine
"""

from goat.edge_discovery.decay import EdgeDecayEngine
from goat.edge_discovery.models import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    compute_edge_id,
)


def test_edge_decay_engine():
    engine = EdgeDecayEngine(min_active_ev=0.0005)

    def make_metrics(ev: float, n: int = 50) -> EdgePerformanceMetrics:
        return EdgePerformanceMetrics(
            sample_size=n,
            win_rate=0.55,
            loss_rate=0.45,
            expected_value=ev,
            average_return=ev,
            median_return=ev,
            max_gain=0.01,
            max_loss=-0.005,
            profit_factor=1.3,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            calmar_ratio=2.0,
            max_drawdown=0.05,
            recovery_factor=2.0,
            trade_frequency=3.0,
            holding_period=5.0,
        )

    e_id, c_hash = compute_edge_id("HYP_1", ["f1"], ["VOLATILITY_100"], ["1m"])
    edge = DiscoveredEdge(
        edge_id=e_id,
        version="6.0.0",
        hypothesis_id="HYP_1",
        feature_combination=["f1"],
        supported_symbols=["VOLATILITY_100"],
        supported_timeframes=["1m"],
        metrics=make_metrics(0.001),
        p_value=0.01,
        confidence_interval_low=0.0005,
        confidence_interval_high=0.0015,
        effect_size=0.6,
        composite_score=0.8,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )

    # 1. High EV & low p-value -> ACTIVE
    status1 = engine.evaluate_decay(edge, make_metrics(0.001), 0.02)
    assert status1 == EdgeStatus.ACTIVE

    # 2. Borderline EV -> WATCHLIST
    status2 = engine.evaluate_decay(edge, make_metrics(0.0001), 0.06)
    assert status2 == EdgeStatus.WATCHLIST

    # 3. Negative EV -> DEGRADING / RETIRED
    status3 = engine.evaluate_decay(edge, make_metrics(-0.002), 0.20)
    assert status3 == EdgeStatus.RETIRED
