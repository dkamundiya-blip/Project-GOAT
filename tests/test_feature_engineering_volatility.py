"""
Project GOAT Phase 5 — Unit Tests for Volatility Feature Engine
"""

from goat.feature_engineering.volatility import VolatilityFeatureEngine
from goat.market_intelligence.models import IntelligenceCandle, IntelligenceTimeframe, compute_intelligence_candle_id


def make_candle(price: float, high: float, low: float, ts_iso: str) -> IntelligenceCandle:
    c_id, c_hash = compute_intelligence_candle_id("VOLATILITY_100", "1m", price, high, low, price, ts_iso, ts_iso)
    return IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=price,
        high=high,
        low=low,
        close=price,
        volume=10.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_volatility_feature_engine_computation():
    engine = VolatilityFeatureEngine(window_size=20)
    res = {}
    for i in range(1, 15):
        ts = f"2026-08-07T12:00:{i:02d}+00:00"
        c = make_candle(100.0 + (i % 3), 105.0, 95.0, ts)
        res = engine.compute_features(c)

    assert "atr_percentile" in res
    assert "volatility_expansion" in res
    assert "volatility_compression" in res
    assert "historical_volatility" in res
    assert "realized_volatility" in res
    assert "rolling_variance" in res
    assert "rolling_std" in res
    assert "volatility_regime" in res
    assert "volatility_burst_detection" in res

    assert res["rolling_std"] > 0.0
    assert res["volatility_regime"] in (0.0, 0.5, 1.0)
