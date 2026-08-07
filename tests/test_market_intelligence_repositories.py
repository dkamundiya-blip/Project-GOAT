"""
Project GOAT Phase 4 — Unit Tests for In-Memory & SQLite Storage Repositories
"""

import sqlite3
import pytest

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
from goat.market_intelligence.persistence import (
    InMemoryCandleRepository,
    InMemoryDataQualityRepository,
    InMemoryEventRepository,
    InMemoryMarketStateRepository,
    InMemoryMarketStatisticsRepository,
    InMemoryTickRepository,
    SQLiteCandleRepository,
    SQLiteDataQualityRepository,
    SQLiteEventRepository,
    SQLiteMarketStateRepository,
    SQLiteMarketStatisticsRepository,
    SQLiteTickRepository,
    init_market_intelligence_db,
)


@pytest.fixture
def memory_db():
    conn = sqlite3.connect(":memory:")
    init_market_intelligence_db(conn)
    return conn


def test_in_memory_repositories():
    tick_repo = InMemoryTickRepository()
    candle_repo = InMemoryCandleRepository()
    stats_repo = InMemoryMarketStatisticsRepository()
    state_repo = InMemoryMarketStateRepository()
    event_repo = InMemoryEventRepository()
    quality_repo = InMemoryDataQualityRepository()

    # Tick test
    t_id, t_hash = compute_recorded_tick_id("V100", 10.0, 10.2, 10.1, "2026-08-07T12:00:00Z", 1)
    tick = RecordedTick(
        tick_id=t_id,
        symbol="V100",
        timestamp="2026-08-07T12:00:00Z",
        bid=10.0,
        ask=10.2,
        mid_price=10.1,
        spread=0.2,
        latency_ms=5.0,
        sequence_number=1,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=t_hash,
    )
    tick_repo.save_tick(tick)
    assert tick_repo.count("V100") == 1
    assert tick_repo.get_latest_tick("V100").tick_id == t_id

    # Candle test
    c_id, c_hash = compute_intelligence_candle_id("V100", "1m", 10.0, 10.5, 9.8, 10.2, "2026-08-07T12:00:00Z", "2026-08-07T12:01:00Z")
    candle = IntelligenceCandle(
        candle_id=c_id,
        symbol="V100",
        timeframe=IntelligenceTimeframe.M1,
        open=10.0,
        high=10.5,
        low=9.8,
        close=10.2,
        volume=10.0,
        open_timestamp="2026-08-07T12:00:00Z",
        close_timestamp="2026-08-07T12:01:00Z",
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )
    candle_repo.save_candle(candle)
    assert candle_repo.count("V100", "1m") == 1
    assert candle_repo.get_latest_candle("V100", "1m").candle_id == c_id


def test_sqlite_repositories(memory_db):
    tick_repo = SQLiteTickRepository(memory_db)
    candle_repo = SQLiteCandleRepository(memory_db)
    stats_repo = SQLiteMarketStatisticsRepository(memory_db)
    state_repo = SQLiteMarketStateRepository(memory_db)
    event_repo = SQLiteEventRepository(memory_db)
    quality_repo = SQLiteDataQualityRepository(memory_db)

    # 1. Ticks
    t_id, t_hash = compute_recorded_tick_id("VOLATILITY_100", 100.0, 100.2, 100.1, "2026-08-07T12:00:00Z", 1)
    tick = RecordedTick(
        tick_id=t_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        bid=100.0,
        ask=100.2,
        mid_price=100.1,
        spread=0.2,
        latency_ms=10.0,
        sequence_number=1,
        source="WEBSOCKET",
        checksum="CHK1",
        metadata={"test": 1},
        canonical_hash=t_hash,
    )
    tick_repo.save_tick(tick)
    assert tick_repo.count("VOLATILITY_100") == 1
    fetched_tick = tick_repo.get_latest_tick("VOLATILITY_100")
    assert fetched_tick.tick_id == t_id
    assert fetched_tick.mid_price == 100.1

    # 2. Candles
    c_id, c_hash = compute_intelligence_candle_id("VOLATILITY_100", "5m", 100.0, 105.0, 99.0, 103.0, "2026-08-07T12:00:00Z", "2026-08-07T12:05:00Z")
    candle = IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M5,
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=50.0,
        open_timestamp="2026-08-07T12:00:00Z",
        close_timestamp="2026-08-07T12:05:00Z",
        completed=True,
        checksum="CHK2",
        metadata={},
        canonical_hash=c_hash,
    )
    candle_repo.save_candle(candle)
    assert candle_repo.count("VOLATILITY_100", "5m") == 1
    fetched_candle = candle_repo.get_latest_candle("VOLATILITY_100", "5m")
    assert fetched_candle.candle_id == c_id

    # 3. Statistics
    s_id, s_hash = compute_market_statistics_id("VOLATILITY_100", "2026-08-07T12:00:00Z", 100, 1.2, 0.001, 101.0)
    stats = MarketStatistics(
        stat_id=s_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        window_size=100,
        atr=1.2,
        true_range=1.3,
        rolling_volatility=0.001,
        standard_deviation=1.5,
        variance=2.25,
        average_tick_rate=2.0,
        average_candle_size=2.5,
        mean_spread=0.2,
        min_spread=0.1,
        max_spread=0.3,
        spread_variance=0.001,
        market_speed=0.1,
        rolling_high=105.0,
        rolling_low=99.0,
        rolling_vwap=101.0,
        checksum="CHK3",
        metadata={},
        canonical_hash=s_hash,
    )
    stats_repo.save_statistics(stats)
    fetched_stats = stats_repo.get_latest_statistics("VOLATILITY_100")
    assert fetched_stats.stat_id == s_id

    # 4. Market State
    st_id, st_hash = compute_market_state_id("VOLATILITY_100", "2026-08-07T12:00:00Z", TrendState.BULLISH, VolatilityLevel.MEDIUM, MomentumState.POSITIVE, RegimeState.TREND, LiquidityLevel.HIGH)
    state = MarketState(
        state_id=st_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        trend=TrendState.BULLISH,
        volatility=VolatilityLevel.MEDIUM,
        momentum=MomentumState.POSITIVE,
        regime=RegimeState.TREND,
        liquidity=LiquidityLevel.HIGH,
        trend_score=0.5,
        volatility_score=0.4,
        momentum_score=0.3,
        liquidity_score=0.8,
        checksum="CHK4",
        metadata={},
        canonical_hash=st_hash,
    )
    state_repo.save_state(state)
    fetched_state = state_repo.get_latest_state("VOLATILITY_100")
    assert fetched_state.state_id == st_id
    assert fetched_state.trend == TrendState.BULLISH

    # 5. Events
    ev_id, ev_hash = compute_market_event_id("VOLATILITY_100", "2026-08-07T12:00:00Z", IntelligenceEventType.LARGE_SPIKE, 0.9)
    event = MarketEvent(
        event_id=ev_id,
        timestamp="2026-08-07T12:00:00Z",
        symbol="VOLATILITY_100",
        event_type=IntelligenceEventType.LARGE_SPIKE,
        confidence=0.9,
        checksum="CHK5",
        metadata={"jump": 0.05},
        canonical_hash=ev_hash,
    )
    event_repo.save_event(event)
    events = event_repo.get_recent_events("VOLATILITY_100")
    assert len(events) == 1
    assert events[0].event_id == ev_id

    # 6. Quality Reports
    qr_id, qr_hash = compute_data_quality_report_id("VOLATILITY_100", "2026-08-07T12:00:00Z", 100, 2, 0.98)
    report = DataQualityReport(
        report_id=qr_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        total_ticks_checked=100,
        valid_ticks_count=98,
        rejected_ticks_count=2,
        pass_rate=0.98,
        issues_breakdown={"NEGATIVE_SPREAD": 2},
        checksum="CHK6",
        metadata={},
        canonical_hash=qr_hash,
    )
    quality_repo.save_report(report)
    reports = quality_repo.get_recent_reports("VOLATILITY_100")
    assert len(reports) == 1
    assert reports[0].report_id == qr_id
