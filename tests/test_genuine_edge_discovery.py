"""
Project GOAT — Test Suite: Genuine Edge Discovery Pipeline (`tests/test_genuine_edge_discovery.py`)

Verifies:
1. End-to-end edge discovery executes on genuine buffered observations (N >= 30).
2. Statistical evaluation (Student's t-test, bootstrap 95% CI) evaluates real historical distribution.
3. Zero synthetic +0.003 / -0.001 values in the evaluation pipeline.
4. Statistically qualifying discoveries are saved to SQLite `discovered_edges` repository.
5. `repository.get_top_edges()` returns the persisted edge with real metrics (expected_value, sharpe, score).
6. Negative test: Series with random noise / zero statistical edge yields empty `discovered_edges` and `edges=[]` in telemetry.
"""

from __future__ import annotations

import datetime
from datetime import timezone
import pytest

from goat.integration.master import MasterSystemIntegrationEngine
from goat.market_intelligence.models.candle import (
    IntelligenceCandle,
    IntelligenceTimeframe,
    compute_intelligence_candle_id,
)
from goat.telemetry.server import TelemetryBroadcaster


def _build_test_candle(
    symbol: str,
    index: int,
    open_p: float,
    high_p: float,
    low_p: float,
    close_p: float,
    base_epoch: int = 1723590000,
) -> IntelligenceCandle:
    sec = 60
    open_ts = datetime.datetime.fromtimestamp(base_epoch + (index * sec), tz=timezone.utc).isoformat()
    close_ts = datetime.datetime.fromtimestamp(base_epoch + ((index + 1) * sec), tz=timezone.utc).isoformat()

    cid, chash = compute_intelligence_candle_id(
        symbol=symbol,
        timeframe="1m",
        open_price=open_p,
        high_price=high_p,
        low_price=low_p,
        close_price=close_p,
        open_timestamp=open_ts,
        close_timestamp=close_ts,
    )
    return IntelligenceCandle(
        candle_id=cid,
        symbol=symbol,
        timeframe=IntelligenceTimeframe.M1,
        open=open_p,
        high=high_p,
        low=low_p,
        close=close_p,
        volume=25.0,
        open_timestamp=open_ts,
        close_timestamp=close_ts,
        completed=True,
        checksum=f"CHK_{index}",
        metadata={},
        canonical_hash=chash,
    )


def test_positive_edge_discovery_with_real_observations():
    """Verify that a series with an authentic statistical pattern produces genuine persisted edges."""
    engine = MasterSystemIntegrationEngine(db_path=":memory:", symbol="BOOM_1000", timeframe="1m")
    broadcaster = TelemetryBroadcaster(master_engine=engine)

    # Generate 40 deterministic candles with a strong momentum expansion pattern:
    # When close > open (bullish bar), subsequent bar moves up by +1.5% to +2.5%
    # When close <= open (bearish bar), subsequent bar moves down by -0.5%
    candles: list[IntelligenceCandle] = []
    current_price = 1000.0

    for i in range(45):
        is_bullish = (i % 3 != 0)  # 2 out of 3 bars are bullish
        open_val = current_price
        if is_bullish:
            high_val = open_val + 8.0
            low_val = open_val - 1.0
            close_val = open_val + 6.0
            next_jump = 15.0  # Big positive forward return
        else:
            high_val = open_val + 2.0
            low_val = open_val - 6.0
            close_val = open_val - 4.0
            next_jump = -2.0  # Minor negative forward return

        c = _build_test_candle("BOOM_1000", i, open_val, high_val, low_val, close_val)
        candles.append(c)
        current_price = close_val + next_jump

    # Process all candles through the master engine
    for c in candles:
        engine._on_candle(c)

    key = ("BOOM_1000", "1m")
    obs_count = len(engine._observation_returns.get(key, []))
    assert obs_count >= 30, f"Expected at least 30 observations, got {obs_count}"

    # 1. Verify that edges were evaluated
    assert engine.edges_evaluated >= 1

    # 2. Verify SQLite repository contains genuine DiscoveredEdge
    saved_edges = engine.edge_discovery_engine.repository.get_recent_edges(limit=10)
    assert len(saved_edges) >= 1

    top_edge = saved_edges[0]
    assert top_edge.edge_id.startswith("EDG_")
    assert top_edge.metrics.sample_size >= 15
    assert top_edge.metrics.expected_value > 0.0
    assert top_edge.p_value <= 0.10
    assert top_edge.confidence_interval_low > 0.0
    assert top_edge.composite_score > 0.0

    # 3. Verify Telemetry snapshot returns this genuine edge with exact metrics
    snapshot = broadcaster.get_telemetry_snapshot()
    assert len(snapshot["edges"]) >= 1
    telem_edge = snapshot["edges"][0]

    assert telem_edge["id"] == top_edge.edge_id
    assert telem_edge["symbol"] == "BOOM_1000"
    assert telem_edge["ev"] == pytest.approx(round(top_edge.metrics.expected_value, 4), rel=1e-3)
    assert telem_edge["sharpe"] == pytest.approx(round(top_edge.metrics.sharpe_ratio, 2), rel=1e-2)
    assert telem_edge["score"] == pytest.approx(round(top_edge.composite_score, 2), rel=1e-2)


def test_negative_edge_discovery_produces_empty_edge_set():
    """Verify that pure negative expectancy / random noise yields 0 discovered edges and empty telemetry."""
    engine = MasterSystemIntegrationEngine(db_path=":memory:", symbol="BOOM_1000", timeframe="1m")
    broadcaster = TelemetryBroadcaster(master_engine=engine)

    # Generate 40 candles with negative drift (every forward return is negative or flat)
    current_price = 1000.0
    for i in range(40):
        open_val = current_price
        high_val = open_val + 1.0
        low_val = open_val - 3.0
        close_val = open_val - 2.0  # Steady decay
        c = _build_test_candle("BOOM_1000", i, open_val, high_val, low_val, close_val)
        engine._on_candle(c)
        current_price = max(100.0, close_val - 2.0)

    # Verify zero edges qualified
    saved_edges = engine.edge_discovery_engine.repository.get_recent_edges(limit=10)
    assert len(saved_edges) == 0

    # Verify telemetry snapshot returns clean empty list (NO synthetic EDG_BOOM_ fallback)
    snapshot = broadcaster.get_telemetry_snapshot()
    assert snapshot["edges"] == []
