"""
Project GOAT Phase 4 — Integration Tests for Master Market Intelligence Engine
"""

import sqlite3
import pytest

from goat.market_intelligence import (
    DataQualityReport,
    IntelligenceCandle,
    MarketEvent,
    MarketIntelligenceEngine,
    MarketState,
    MarketStatistics,
    RecordedTick,
)


@pytest.fixture
def memory_db():
    conn = sqlite3.connect(":memory:")
    return conn


def test_market_intelligence_engine_pipeline(memory_db):
    engine = MarketIntelligenceEngine(db_path=memory_db)

    received_ticks: list[RecordedTick] = []
    received_candles: list[IntelligenceCandle] = []
    received_stats: list[MarketStatistics] = []
    received_states: list[MarketState] = []
    received_events: list[MarketEvent] = []

    engine.subscribe_ticks(lambda t: received_ticks.append(t))
    engine.subscribe_candles(lambda c: received_candles.append(c))
    engine.subscribe_statistics(lambda s: received_stats.append(s))
    engine.subscribe_states(lambda st: received_states.append(st))
    engine.subscribe_events(lambda e: received_events.append(e))

    # Feed sequence of raw ticks
    base_time = "2026-08-07T12:00:"
    for i in range(1, 10):
        raw = {
            "symbol": "VOLATILITY_100",
            "quote": 4500.0 + i * 2.0,
            "bid": 4500.0 + i * 2.0 - 0.2,
            "ask": 4500.0 + i * 2.0 + 0.2,
            "timestamp": f"{base_time}{i:02d}+00:00",
            "sequence_number": i,
            "source": "WEBSOCKET",
        }
        tick = engine.process_raw_tick(raw, arrival_latency_ms=12.0)
        assert tick is not None

    assert len(received_ticks) == 9
    assert len(received_stats) == 9
    assert len(received_states) == 9

    # Generate Data Quality Report
    report = engine.generate_quality_report("VOLATILITY_100")
    assert isinstance(report, DataQualityReport)
    assert report.total_ticks_checked == 9
    assert report.valid_ticks_count == 9
    assert report.pass_rate == 1.0

    # Test invalid tick rejection
    invalid_raw = {
        "symbol": "VOLATILITY_100",
        "quote": -100.0,  # Negative price
        "timestamp": "2026-08-07T12:00:10+00:00",
        "sequence_number": 10,
    }
    rejected_tick = engine.process_raw_tick(invalid_raw)
    assert rejected_tick is None

    report2 = engine.generate_quality_report("VOLATILITY_100")
    assert report2.total_ticks_checked == 10
    assert report2.valid_ticks_count == 9
    assert report2.rejected_ticks_count == 1
