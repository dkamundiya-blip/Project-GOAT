"""
Project GOAT Phase 4 — Unit Tests for Domain Models & Canonical IDs
"""

import pytest
from pydantic import ValidationError

from goat.market_intelligence.models import (
    DataQualityReport,
    IntelligenceCandle,
    IntelligenceEventType,
    IntelligenceTimeframe,
    LiquidityLevel,
    MarketEvent,
    MarketState,
    MarketStatistics,
    MomentumState,
    RecordedTick,
    RegimeState,
    TrendState,
    VolatilityLevel,
    compute_data_quality_report_id,
    compute_intelligence_candle_id,
    compute_market_event_id,
    compute_market_state_id,
    compute_market_statistics_id,
    compute_recorded_tick_id,
)


def test_recorded_tick_model_and_id():
    tick_id, canon_hash = compute_recorded_tick_id(
        symbol="VOLATILITY_100",
        bid=4532.10,
        ask=4532.50,
        mid_price=4532.30,
        timestamp="2026-08-07T12:00:00+00:00",
        sequence_number=1,
        source="WEBSOCKET",
    )
    assert tick_id.startswith("RTK_")
    assert len(canon_hash) == 64

    tick = RecordedTick(
        tick_id=tick_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        bid=4532.10,
        ask=4532.50,
        mid_price=4532.30,
        spread=0.40,
        latency_ms=12.5,
        sequence_number=1,
        source="WEBSOCKET",
        checksum="ABC123CHECKSUM",
        metadata={"feed": "test"},
        canonical_hash=canon_hash,
    )

    assert tick.symbol == "VOLATILITY_100"
    assert tick.mid_price == 4532.30

    # Immutability check
    with pytest.raises(ValidationError):
        tick.mid_price = 9999.0


def test_intelligence_candle_model_and_timeframes():
    assert len(IntelligenceTimeframe) == 12

    c_id, c_hash = compute_intelligence_candle_id(
        symbol="VOLATILITY_100",
        timeframe="1m",
        open_price=100.0,
        high_price=105.0,
        low_price=98.0,
        close_price=103.0,
        open_timestamp="2026-08-07T12:00:00+00:00",
        close_timestamp="2026-08-07T12:01:00+00:00",
    )
    assert c_id.startswith("ICD_")

    candle = IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=100.0,
        high=105.0,
        low=98.0,
        close=103.0,
        volume=24.0,
        open_timestamp="2026-08-07T12:00:00+00:00",
        close_timestamp="2026-08-07T12:01:00+00:00",
        completed=True,
        checksum="CHECKSUM123",
        metadata={},
        canonical_hash=c_hash,
    )

    assert candle.is_bullish is True
    assert candle.price_range == 7.0


def test_market_statistics_model():
    s_id, s_hash = compute_market_statistics_id(
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        window_size=100,
        atr=1.5,
        rolling_volatility=0.002,
        rolling_vwap=4532.0,
    )
    assert s_id.startswith("MST_")

    stats = MarketStatistics(
        stat_id=s_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        window_size=100,
        atr=1.5,
        true_range=1.6,
        rolling_volatility=0.002,
        standard_deviation=2.1,
        variance=4.41,
        average_tick_rate=4.5,
        average_candle_size=3.2,
        mean_spread=0.4,
        min_spread=0.2,
        max_spread=0.6,
        spread_variance=0.01,
        market_speed=0.5,
        rolling_high=4540.0,
        rolling_low=4520.0,
        rolling_vwap=4532.0,
        checksum="CKSUM",
        metadata={},
        canonical_hash=s_hash,
    )
    assert stats.window_size == 100
    assert stats.rolling_high == 4540.0


def test_market_state_model():
    st_id, st_hash = compute_market_state_id(
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        trend=TrendState.BULLISH,
        volatility=VolatilityLevel.HIGH,
        momentum=MomentumState.POSITIVE,
        regime=RegimeState.EXPANSION,
        liquidity=LiquidityLevel.HIGH,
    )
    assert st_id.startswith("MKS_")

    state = MarketState(
        state_id=st_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        trend=TrendState.BULLISH,
        volatility=VolatilityLevel.HIGH,
        momentum=MomentumState.POSITIVE,
        regime=RegimeState.EXPANSION,
        liquidity=LiquidityLevel.HIGH,
        trend_score=0.8,
        volatility_score=0.9,
        momentum_score=0.75,
        liquidity_score=0.85,
        checksum="CKSUM",
        metadata={},
        canonical_hash=st_hash,
    )

    assert state.trend == TrendState.BULLISH
    assert state.regime == RegimeState.EXPANSION


def test_market_event_model():
    ev_id, ev_hash = compute_market_event_id(
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        event_type=IntelligenceEventType.LARGE_SPIKE,
        confidence=0.95,
    )
    assert ev_id.startswith("MKE_")

    ev = MarketEvent(
        event_id=ev_id,
        timestamp="2026-08-07T12:00:00+00:00",
        symbol="VOLATILITY_100",
        event_type=IntelligenceEventType.LARGE_SPIKE,
        confidence=0.95,
        checksum="CKSUM",
        metadata={"jump": 0.02},
        canonical_hash=ev_hash,
    )
    assert ev.event_type == IntelligenceEventType.LARGE_SPIKE
