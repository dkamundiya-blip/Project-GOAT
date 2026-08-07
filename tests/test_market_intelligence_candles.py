"""
Project GOAT Phase 4 — Unit Tests for Universal Candle Builder
"""

from goat.market_intelligence.candles import UniversalCandleBuilder
from goat.market_intelligence.models import IntelligenceTimeframe, RecordedTick, compute_recorded_tick_id
from goat.market_intelligence.persistence import InMemoryCandleRepository


def make_tick(symbol: str, price: float, ts_iso: str, seq: int) -> RecordedTick:
    t_id, t_hash = compute_recorded_tick_id(symbol, price - 0.1, price + 0.1, price, ts_iso, seq)
    return RecordedTick(
        tick_id=t_id,
        symbol=symbol,
        timestamp=ts_iso,
        bid=price - 0.1,
        ask=price + 0.1,
        mid_price=price,
        spread=0.2,
        latency_ms=10.0,
        sequence_number=seq,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=t_hash,
    )


def test_universal_candle_builder_12_timeframes():
    repo = InMemoryCandleRepository()
    builder = UniversalCandleBuilder(repository=repo)

    # 12 Timeframes supported
    assert len(builder.active_timeframes) == 12

    # Ingest series of ticks over 2 minutes (120 seconds)
    # Ticks at t=0s (price=100.0), t=30s (price=105.0), t=60s (price=95.0), t=90s (price=102.0)
    t1 = make_tick("VOLATILITY_100", 100.0, "2026-08-07T12:00:00+00:00", 1)
    t2 = make_tick("VOLATILITY_100", 105.0, "2026-08-07T12:00:30+00:00", 2)
    t3 = make_tick("VOLATILITY_100", 95.0, "2026-08-07T12:00:45+00:00", 3)
    t4 = make_tick("VOLATILITY_100", 102.0, "2026-08-07T12:01:00+00:00", 4)
    t5 = make_tick("VOLATILITY_100", 110.0, "2026-08-07T12:02:00+00:00", 5)

    c1 = builder.process_tick(t1)
    c2 = builder.process_tick(t2)
    c3 = builder.process_tick(t3)  # Crosses 1s, 5s, 15s, 30s, 1m boundaries
    assert len(c3) > 0  # Should finalize completed bars

    c4 = builder.process_tick(t4)
    c5 = builder.process_tick(t5)
    assert len(c5) > 0

    # Force finalize remaining forming bars
    all_finalized = builder.force_finalize_all()
    assert len(all_finalized) > 0

    # Verify 1m candle rules: Open = first tick (100.0), High = max (105.0), Low = min (95.0), Close = last tick (102.0)
    m1_candles = repo.get_candles("VOLATILITY_100", "1m")
    assert len(m1_candles) >= 1
    first_1m = m1_candles[0]
    assert first_1m.open == 100.0
    assert first_1m.high == 105.0
    assert first_1m.low == 95.0
    assert first_1m.close == 95.0  # At boundary t=60s
