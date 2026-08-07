"""
Project GOAT Phase 5 — Unit Tests for Liquidity Feature Engine
"""

from goat.feature_engineering.liquidity import LiquidityFeatureEngine
from goat.market_intelligence.models import IntelligenceCandle, IntelligenceTimeframe, compute_intelligence_candle_id


def make_candle(open_p: float, high: float, low: float, close: float, ts_iso: str) -> IntelligenceCandle:
    c_id, c_hash = compute_intelligence_candle_id("VOLATILITY_100", "1m", open_p, high, low, close, ts_iso, ts_iso)
    return IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=open_p,
        high=high,
        low=low,
        close=close,
        volume=100.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_liquidity_feature_engine():
    engine = LiquidityFeatureEngine(tolerance_pct=0.001)

    # 1. First candle with high=105.00
    c1 = make_candle(100.0, 105.00, 95.0, 102.0, "2026-08-07T12:00:01+00:00")
    engine.compute_features(c1)

    # 2. Second candle with high=105.01 (Equal Highs within tolerance)
    c2 = make_candle(102.0, 105.01, 98.0, 103.0, "2026-08-07T12:00:02+00:00")
    res2 = engine.compute_features(c2)

    assert "equal_highs" in res2
    assert "equal_lows" in res2
    assert "liquidity_sweep" in res2
    assert "liquidity_density" in res2
    assert "range_compression" in res2
    assert "range_expansion" in res2
    assert "stop_cluster_prob" in res2
    assert "liquidity_imbalance" in res2

    assert res2["equal_highs"] == 1.0
    assert res2["stop_cluster_prob"] > 0.5
