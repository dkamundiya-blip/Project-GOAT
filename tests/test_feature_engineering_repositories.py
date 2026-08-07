"""
Project GOAT Phase 5 — Unit Tests for Feature Repositories (In-Memory & SQLite)
"""

import sqlite3
import pytest

from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id
from goat.feature_engineering.persistence import (
    InMemoryFeatureRepository,
    SQLiteFeatureRepository,
    init_feature_store_db,
)


def make_vector(symbol: str, timeframe: str, ts_iso: str, offset: float) -> FeatureVector:
    features = {"trend_direction": 1.0, "z_score": 0.5 + offset, "slope": 0.01 * offset}
    v_id, c_hash = compute_feature_vector_id(symbol, timeframe, ts_iso, features)
    return FeatureVector(
        vector_id=v_id,
        symbol=symbol,
        timeframe=timeframe,
        timestamp=ts_iso,
        version="5.0.0",
        features=features,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )


def test_in_memory_feature_repository():
    repo = InMemoryFeatureRepository()
    v1 = make_vector("VOLATILITY_100", "1m", "2026-08-07T12:00:01Z", 1.0)
    v2 = make_vector("VOLATILITY_100", "1m", "2026-08-07T12:00:02Z", 2.0)

    repo.save_vector(v1)
    repo.save_vector(v2)

    assert repo.count("VOLATILITY_100", "1m") == 2
    latest = repo.get_latest_vector("VOLATILITY_100", "1m")
    assert latest is not None
    assert latest.vector_id == v2.vector_id

    recent = repo.get_recent_vectors("VOLATILITY_100", "1m", limit=10)
    assert len(recent) == 2


def test_sqlite_feature_repository():
    conn = sqlite3.connect(":memory:")
    init_feature_store_db(conn)
    repo = SQLiteFeatureRepository(conn)

    vectors = [
        make_vector("VOLATILITY_100", "1m", f"2026-08-07T12:00:{i:02d}Z", float(i))
        for i in range(1, 6)
    ]
    repo.save_vectors(vectors)

    assert repo.count("VOLATILITY_100", "1m") == 5
    latest = repo.get_latest_vector("VOLATILITY_100", "1m")
    assert latest is not None
    assert latest.vector_id == vectors[-1].vector_id

    range_vecs = repo.get_vectors_range("VOLATILITY_100", "1m", "2026-08-07T12:00:02Z", "2026-08-07T12:00:04Z")
    assert len(range_vecs) == 3
