"""
Project GOAT Phase 5 — Integration Tests for Master Feature Engineering Engine
"""

import sqlite3
import pytest

from goat.feature_engineering import FeatureVector, MasterFeatureEngineeringEngine
from goat.market_intelligence.models import IntelligenceCandle, IntelligenceTimeframe, compute_intelligence_candle_id


def make_candle(symbol: str, price: float, ts_iso: str) -> IntelligenceCandle:
    c_id, c_hash = compute_intelligence_candle_id(symbol, "1m", price - 1, price + 2, price - 2, price, ts_iso, ts_iso)
    return IntelligenceCandle(
        candle_id=c_id,
        symbol=symbol,
        timeframe=IntelligenceTimeframe.M1,
        open=price - 1,
        high=price + 2,
        low=price - 2,
        close=price,
        volume=100.0,
        open_timestamp=ts_iso,
        close_timestamp=ts_iso,
        completed=True,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_master_feature_engineering_engine_pipeline():
    conn = sqlite3.connect(":memory:")
    engine = MasterFeatureEngineeringEngine(db_path=conn)

    received_vectors: list[FeatureVector] = []
    engine.subscribe_feature_vectors(lambda v: received_vectors.append(v))

    # Ingest 10 candles
    for i in range(1, 11):
        ts = f"2026-08-07T12:00:{i:02d}+00:00"
        candle = make_candle("VOLATILITY_100", 100.0 + i * 0.5, ts)
        vec = engine.process_candle(candle)

        assert vec.vector_id.startswith("FVR_")
        assert len(vec.features) == 64  # Exactly 64 quantitative features engineered!

    assert len(received_vectors) == 10

    # Query from SQLite Feature Store
    latest = engine.get_latest_feature_vector("VOLATILITY_100", "1m")
    assert latest is not None
    assert latest.vector_id == received_vectors[-1].vector_id
    assert engine.repository.count("VOLATILITY_100", "1m") == 10
