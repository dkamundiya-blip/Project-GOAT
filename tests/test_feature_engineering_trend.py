"""
Project GOAT Phase 5 — Unit Tests for Trend Feature Engine
"""

from goat.feature_engineering.trend import TrendFeatureEngine
from goat.market_intelligence.models import IntelligenceCandle, IntelligenceTimeframe, compute_intelligence_candle_id


def make_candle(price: float, ts_iso: str) -> IntelligenceCandle:
    c_id, c_hash = compute_intelligence_candle_id("VOLATILITY_100", "1m", price - 1, price + 2, price - 2, price, ts_iso, ts_iso)
    return IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=price - 1,
        high=price + 2,
        low=price - 2,
        close=price,
        volume=10.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_trend_feature_engine_computation():
    engine = TrendFeatureEngine(window_size=20)
    prices = [100.0, 102.0, 104.0, 106.0, 108.0, 110.0]

    last_res = {}
    for idx, p in enumerate(prices, start=1):
        ts = f"2026-08-07T12:00:{idx:02d}+00:00"
        c = make_candle(p, ts)
        last_res = engine.compute_features(c)

    assert "trend_direction" in last_res
    assert "trend_strength" in last_res
    assert "slope" in last_res
    assert "ema_distance" in last_res
    assert "directional_efficiency" in last_res

    assert last_res["trend_direction"] == 1.0  # Upward price progression
    assert last_res["slope"] > 0.0
    assert last_res["directional_efficiency"] == 1.0
