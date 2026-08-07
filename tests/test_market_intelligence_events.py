"""
Project GOAT Phase 4 — Unit Tests for Event Detection Engine
"""

from goat.market_intelligence.events import EventDetectionEngine
from goat.market_intelligence.models import (
    IntelligenceCandle,
    IntelligenceEventType,
    IntelligenceTimeframe,
    MarketStatistics,
    RecordedTick,
    compute_intelligence_candle_id,
    compute_market_statistics_id,
    compute_recorded_tick_id,
)
from goat.market_intelligence.persistence import InMemoryEventRepository


def test_event_detection_spike_crash_gap_spread():
    repo = InMemoryEventRepository()
    engine = EventDetectionEngine(
        repository=repo,
        spike_threshold_pct=0.01,
        crash_threshold_pct=0.01,
        gap_threshold_sec=5.0,
        spread_anomaly_mult=2.0,
    )

    t1_id, h1 = compute_recorded_tick_id("VOLATILITY_100", 100.0, 100.2, 100.1, "2026-08-07T12:00:00+00:00", 1)
    t1 = RecordedTick(
        tick_id=t1_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00+00:00",
        bid=100.0,
        ask=100.2,
        mid_price=100.1,
        spread=0.2,
        latency_ms=5.0,
        sequence_number=1,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=h1,
    )
    engine.process_tick(t1)

    # 1. Large Spike (+3% price jump) & Time Gap (10 seconds later)
    t2_id, h2 = compute_recorded_tick_id("VOLATILITY_100", 103.0, 103.2, 103.1, "2026-08-07T12:00:10+00:00", 2)
    t2 = RecordedTick(
        tick_id=t2_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:10+00:00",
        bid=103.0,
        ask=103.2,
        mid_price=103.1,
        spread=0.2,
        latency_ms=5.0,
        sequence_number=2,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=h2,
    )
    events2 = engine.process_tick(t2)
    event_types2 = [e.event_type for e in events2]
    assert IntelligenceEventType.LARGE_SPIKE in event_types2
    assert IntelligenceEventType.GAP in event_types2

    # 2. Spread Anomaly
    s_id, sh = compute_market_statistics_id("VOLATILITY_100", "2026-08-07T12:00:10+00:00", 10, 1.0, 0.001, 103.0)
    stats = MarketStatistics(
        stat_id=s_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:10+00:00",
        window_size=10,
        atr=1.0,
        true_range=1.0,
        rolling_volatility=0.001,
        standard_deviation=1.0,
        variance=1.0,
        average_tick_rate=2.0,
        average_candle_size=1.5,
        mean_spread=0.2,
        min_spread=0.1,
        max_spread=0.3,
        spread_variance=0.01,
        market_speed=0.1,
        rolling_high=105.0,
        rolling_low=99.0,
        rolling_vwap=103.0,
        checksum="CHK",
        metadata={},
        canonical_hash=sh,
    )

    t3_id, h3 = compute_recorded_tick_id("VOLATILITY_100", 103.0, 104.0, 103.5, "2026-08-07T12:00:11+00:00", 3)
    t3 = RecordedTick(
        tick_id=t3_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:11+00:00",
        bid=103.0,
        ask=104.0,
        mid_price=103.5,
        spread=1.0,  # 5x mean spread of 0.2
        latency_ms=5.0,
        sequence_number=3,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=h3,
    )
    events3 = engine.process_tick(t3, current_stats=stats)
    event_types3 = [e.event_type for e in events3]
    assert IntelligenceEventType.SPREAD_ANOMALY in event_types3

    # Check repository events
    assert len(repo.get_recent_events("VOLATILITY_100")) >= 3


def test_event_detection_extreme_candle():
    repo = InMemoryEventRepository()
    engine = EventDetectionEngine(repository=repo, extreme_candle_mult=2.0)

    s_id, sh = compute_market_statistics_id("VOLATILITY_100", "2026-08-07T12:00:00Z", 10, 1.0, 0.001, 100.0)
    stats = MarketStatistics(
        stat_id=s_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        window_size=10,
        atr=1.0,
        true_range=1.0,
        rolling_volatility=0.001,
        standard_deviation=1.0,
        variance=1.0,
        average_tick_rate=2.0,
        average_candle_size=2.0,  # Average size = 2.0
        mean_spread=0.2,
        min_spread=0.1,
        max_spread=0.3,
        spread_variance=0.01,
        market_speed=0.1,
        rolling_high=105.0,
        rolling_low=99.0,
        rolling_vwap=100.0,
        checksum="CHK",
        metadata={},
        canonical_hash=sh,
    )

    c_id, ch = compute_intelligence_candle_id("VOLATILITY_100", "1m", 100.0, 108.0, 99.0, 107.0, "2026-08-07T12:00:00Z", "2026-08-07T12:01:00Z")
    candle = IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=100.0,
        high=108.0,
        low=99.0,
        close=107.0,
        volume=30.0,
        open_timestamp="2026-08-07T12:00:00Z",
        close_timestamp="2026-08-07T12:01:00Z",
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=ch,
    )

    events = engine.process_candle(candle, current_stats=stats)
    assert len(events) == 1
    assert events[0].event_type == IntelligenceEventType.EXTREME_CANDLE
