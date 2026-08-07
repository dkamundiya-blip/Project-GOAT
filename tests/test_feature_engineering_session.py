"""
Project GOAT Phase 5 — Unit Tests for Session Intelligence Engine
"""

from goat.feature_engineering.session import SessionIntelligenceEngine
from goat.market_intelligence.models import IntelligenceCandle, IntelligenceTimeframe, compute_intelligence_candle_id


def make_candle(close: float, open_ts_iso: str) -> IntelligenceCandle:
    c_id, c_hash = compute_intelligence_candle_id("VOLATILITY_100", "1m", close - 1, close + 1, close - 2, close, open_ts_iso, open_ts_iso)
    return IntelligenceCandle(
        candle_id=c_id,
        symbol="VOLATILITY_100",
        timeframe=IntelligenceTimeframe.M1,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=50.0,
        open_timestamp=open_ts_iso,
        close_timestamp=open_ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_session_intelligence_engine():
    engine = SessionIntelligenceEngine()

    # 1. Asian Session (04:00 UTC)
    c_asian = make_candle(100.0, "2026-08-07T04:30:00+00:00")
    res_asian = engine.compute_features(c_asian)

    assert res_asian["current_session"] == 1.0  # ASIAN
    assert res_asian["hour_of_day"] == 4.0
    assert res_asian["overlap_detection"] == 0.0

    # 2. London/NY Overlap Session (14:30 UTC)
    c_overlap = make_candle(105.0, "2026-08-07T14:30:00+00:00")
    res_overlap = engine.compute_features(c_overlap)

    assert res_overlap["current_session"] == 4.0  # OVERLAP
    assert res_overlap["hour_of_day"] == 14.0
    assert res_overlap["overlap_detection"] == 1.0
    assert "time_until_session_close" in res_overlap
    assert "time_since_session_open" in res_overlap
    assert "session_volatility" in res_overlap
    assert "session_momentum" in res_overlap
