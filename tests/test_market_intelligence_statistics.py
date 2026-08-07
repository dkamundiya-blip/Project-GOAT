"""
Project GOAT Phase 4 — Unit Tests for Market Statistics Engine
"""

from goat.market_intelligence.models import RecordedTick, compute_recorded_tick_id
from goat.market_intelligence.persistence import InMemoryMarketStatisticsRepository
from goat.market_intelligence.statistics import MarketStatisticsEngine


def make_tick(symbol: str, price: float, ts_iso: str, seq: int) -> RecordedTick:
    t_id, t_hash = compute_recorded_tick_id(symbol, price - 0.2, price + 0.2, price, ts_iso, seq)
    return RecordedTick(
        tick_id=t_id,
        symbol=symbol,
        timestamp=ts_iso,
        bid=price - 0.2,
        ask=price + 0.2,
        mid_price=price,
        spread=0.4,
        latency_ms=8.0,
        sequence_number=seq,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=t_hash,
    )


def test_market_statistics_engine_computation():
    repo = InMemoryMarketStatisticsRepository()
    engine = MarketStatisticsEngine(repository=repo, window_size=50)

    # Ingest sequence of prices
    prices = [100.0, 102.0, 101.0, 104.0, 103.0, 106.0, 105.0]
    for idx, p in enumerate(prices, start=1):
        ts = f"2026-08-07T12:00:0{idx}+00:00"
        t = make_tick("VOLATILITY_100", p, ts, idx)
        stats = engine.process_tick(t)

    assert stats.window_size == len(prices)
    assert stats.rolling_high == 106.0
    assert stats.rolling_low == 100.0
    assert stats.mean_spread == 0.4
    assert stats.standard_deviation > 0.0
    assert stats.variance > 0.0
    assert stats.average_tick_rate > 0.0
    assert stats.rolling_vwap > 0.0

    # Verify repository storage
    assert repo.get_latest_statistics("VOLATILITY_100").stat_id == stats.stat_id
