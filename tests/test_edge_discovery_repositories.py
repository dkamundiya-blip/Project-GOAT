"""
Project GOAT Phase 6 — Unit Tests for Edge Persistence Repositories
"""

import sqlite3
import pytest

from goat.edge_discovery.models import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    compute_edge_id,
)
from goat.edge_discovery.persistence import (
    InMemoryEdgeRepository,
    SQLiteEdgeRepository,
    init_edge_discovery_db,
)


def make_edge(symbol: str, score: float) -> DiscoveredEdge:
    metrics = EdgePerformanceMetrics(
        sample_size=50,
        win_rate=0.6,
        loss_rate=0.4,
        expected_value=0.001,
        average_return=0.001,
        median_return=0.0009,
        max_gain=0.01,
        max_loss=-0.005,
        profit_factor=1.5,
        sharpe_ratio=1.8,
        sortino_ratio=2.2,
        calmar_ratio=2.5,
        max_drawdown=0.04,
        recovery_factor=3.0,
        trade_frequency=4.0,
        holding_period=5.0,
    )
    e_id, c_hash = compute_edge_id("HYP_999", ["trend_strength"], [symbol], ["1m"])
    return DiscoveredEdge(
        edge_id=e_id,
        version="6.0.0",
        hypothesis_id="HYP_999",
        feature_combination=["trend_strength"],
        supported_symbols=[symbol],
        supported_timeframes=["1m"],
        metrics=metrics,
        p_value=0.01,
        confidence_interval_low=0.0005,
        confidence_interval_high=0.0015,
        effect_size=0.6,
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


def test_in_memory_edge_repository():
    repo = InMemoryEdgeRepository()
    e1 = make_edge("VOLATILITY_100", 0.75)
    e2 = make_edge("CRASH_500", 0.88)

    repo.save_edge(e1)
    repo.save_edge(e2)

    assert repo.count() == 2
    top = repo.get_top_edges(limit=1)
    assert len(top) == 1
    assert top[0].edge_id == e2.edge_id

    repo.update_edge_status(e1.edge_id, EdgeStatus.WATCHLIST)
    updated = repo.get_edge(e1.edge_id)
    assert updated is not None
    assert updated.status == EdgeStatus.WATCHLIST


def test_sqlite_edge_repository():
    conn = sqlite3.connect(":memory:")
    init_edge_discovery_db(conn)
    repo = SQLiteEdgeRepository(conn)

    e1 = make_edge("VOLATILITY_100", 0.70)
    e2 = make_edge("BOOM_1000", 0.92)

    repo.save_edges([e1, e2])
    assert repo.count() == 2

    top = repo.get_top_edges(limit=1)
    assert top[0].edge_id == e2.edge_id

    repo.update_edge_status(e1.edge_id, EdgeStatus.RETIRED)
    assert repo.count(status=EdgeStatus.RETIRED) == 1
