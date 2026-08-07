"""
Project GOAT Phase 5 — Unit Tests for Statistical Feature Engine
"""

from goat.feature_engineering.statistical import StatisticalFeatureEngine
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
        volume=10.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_statistical_feature_engine():
    engine = StatisticalFeatureEngine(window_size=20)
    prices = [100.0, 102.0, 99.0, 101.0, 105.0, 98.0, 103.0, 100.0, 104.0, 102.0]
    res = {}
    for idx, p in enumerate(prices, start=1):
        ts = f"2026-08-07T12:00:{idx:02d}+00:00"
        c = make_candle(p, ts)
        res = engine.compute_features(c)

    assert "z_score" in res
    assert "percentile_rank" in res
    assert "rolling_mean" in res
    assert "rolling_median" in res
    assert "rolling_entropy" in res
    assert "hurst_exponent" in res
    assert "mean_reversion_score" in res
    assert "autocorrelation" in res
    assert "distribution_skew" in res
    assert "distribution_kurtosis" in res

    assert 0.0 <= res["percentile_rank"] <= 1.0
    assert res["rolling_mean"] > 0.0
