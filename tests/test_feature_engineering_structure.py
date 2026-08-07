"""
Project GOAT Phase 5 — Unit Tests for Market Structure Feature Engine
"""

from goat.feature_engineering.structure import MarketStructureFeatureEngine
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
        volume=50.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_market_structure_feature_engine():
    engine = MarketStructureFeatureEngine(pivot_left=1, pivot_right=1)
    candles_data = [
        (100.0, 105.0, 95.0, 102.0),
        (102.0, 110.0, 101.0, 108.0),  # Pivot High (110)
        (108.0, 109.0, 100.0, 101.0),
        (101.0, 103.0, 92.0, 94.0),    # Pivot Low (92)
        (94.0, 115.0, 93.0, 114.0),    # Bullish BOS past 110
    ]

    res = {}
    for idx, (o, h, l, c) in enumerate(candles_data, start=1):
        ts = f"2026-08-07T12:00:{idx:02d}+00:00"
        cd = make_candle(o, h, l, c, ts)
        res = engine.compute_features(cd)

    assert "swing_high" in res
    assert "swing_low" in res
    assert "higher_high" in res
    assert "bos" in res
    assert "choch" in res
    assert "trend_transition_prob" in res
