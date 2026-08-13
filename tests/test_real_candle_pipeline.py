"""
Project GOAT — Test Suite: Real Multi-Tick Candle Pipeline (`tests/test_real_candle_pipeline.py`)

Verifies:
1. Multiple distinct ticks form a genuine OHLCV candle.
2. Open, High, Low, Close are not artificially identical.
3. Candle completion occurs at the correct interval boundary.
4. Feature generation is triggered strictly from genuine completed candles.
5. Feature indicators reflect real intra-bar variance and range.
"""

from __future__ import annotations

import datetime
from datetime import timezone
import pytest

from goat.integration.master import MasterSystemIntegrationEngine
from goat.market_intelligence.models.candle import IntelligenceCandle, IntelligenceTimeframe


def test_real_multi_tick_candle_formation_and_features():
    """Verify that multiple ticks across interval produce a real non-flat candle and features."""
    engine = MasterSystemIntegrationEngine(db_path=":memory:", symbol="BOOM_1000", timeframe="1m")

    # Base interval start at 02:00:00 UTC
    base_epoch = 1723590000  # aligned to 60s
    t0 = datetime.datetime.fromtimestamp(base_epoch, tz=timezone.utc).isoformat()
    t1 = datetime.datetime.fromtimestamp(base_epoch + 15, tz=timezone.utc).isoformat()
    t2 = datetime.datetime.fromtimestamp(base_epoch + 30, tz=timezone.utc).isoformat()
    t3 = datetime.datetime.fromtimestamp(base_epoch + 45, tz=timezone.utc).isoformat()
    t_next = datetime.datetime.fromtimestamp(base_epoch + 60, tz=timezone.utc).isoformat()  # Crosses boundary

    # Stream 4 ticks within the 1-minute window
    engine.process_tick(symbol="BOOM_1000", price=1000.0, timestamp_iso=t0)  # Open
    engine.process_tick(symbol="BOOM_1000", price=1010.0, timestamp_iso=t1)  # High
    engine.process_tick(symbol="BOOM_1000", price=995.0, timestamp_iso=t2)   # Low
    engine.process_tick(symbol="BOOM_1000", price=1005.0, timestamp_iso=t3)  # Close

    # Before crossing interval boundary: 0 closed 1m candles
    assert engine.candles_closed == 0
    assert engine.feature_vectors_generated == 0

    # Tick crossing boundary at 02:01:00 UTC triggers 1m candle finalization & feature generation
    engine.process_tick(symbol="BOOM_1000", price=1006.0, timestamp_iso=t_next)

    # 1. Verify candle closed
    assert engine.candles_closed >= 1
    assert engine.feature_vectors_generated >= 1

    # 2. Verify stored candle in repository has real distinct OHLC
    candles = engine.market_intel_engine.candle_repo.get_candles(symbol="BOOM_1000", timeframe="1m")
    assert len(candles) >= 1
    closed_candle = candles[0]

    assert closed_candle.open == 1000.0
    assert closed_candle.high == 1010.0
    assert closed_candle.low == 995.0
    assert closed_candle.close == 1005.0
    assert closed_candle.volume == 4.0
    assert closed_candle.open != closed_candle.high
    assert closed_candle.high != closed_candle.low
    assert closed_candle.low != closed_candle.close

    # 3. Verify feature vector in feature store has non-zero range/volatility indicators
    fvs = engine.feature_eng_engine.repository.get_recent_vectors(symbol="BOOM_1000", timeframe="1m")
    assert len(fvs) >= 1
    fv = fvs[0]

    assert "swing_high" in fv.features
    assert "swing_low" in fv.features
    assert fv.features["swing_high"] == pytest.approx(1010.0, rel=1e-3)
    assert fv.features["swing_low"] == pytest.approx(995.0, rel=1e-3)
    assert fv.features["rolling_mean"] == pytest.approx(1005.0, rel=1e-3)
    assert fv.features["liquidity_density"] > 0.0
