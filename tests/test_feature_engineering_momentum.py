"""
Project GOAT Phase 5 — Unit Tests for Momentum Feature Engine
"""

from goat.feature_engineering.momentum import MomentumFeatureEngine
from goat.market_intelligence.models import IntelligenceCandle, IntelligenceTimeframe, compute_intelligence_candle_id


def make_candle(close: float, ts_iso: str) -> IntelligenceCandle:
    c_id, c_hash = compute_intelligence_candle_id("VOLATILITY_100", "1m", close, close + 1, close - 1, close, ts_iso, ts_iso)
    return IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=close,
        high=close + 1,
        low=close - 1,
        close=close,
        volume=100.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_momentum_feature_engine():
    engine = MomentumFeatureEngine(period=5)
    prices = [100.0, 101.0, 103.0, 106.0, 110.0]
    res = {}
    for idx, p in enumerate(prices, start=1):
        ts = f"2026-08-07T12:00:{idx:02d}+00:00"
        c = make_candle(p, ts)
        res = engine.compute_features(c)

    assert "roc" in res
    assert "momentum_strength" in res
    assert "momentum_acceleration" in res
    assert "momentum_persistence" in res
    assert "price_velocity" in res
    assert "price_acceleration" in res
    assert "directional_impulse" in res
    assert "mtf_momentum" in res

    assert res["roc"] > 0.0
    assert res["momentum_persistence"] > 0
    assert res["price_velocity"] > 0.0
