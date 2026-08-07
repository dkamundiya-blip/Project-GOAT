"""
Project GOAT Phase 5 — Unit Tests for FeatureVector Domain Model
"""

from pydantic import ValidationError
import pytest

from goat.feature_engineering.models import FeatureVector, compute_feature_vector_id


def test_feature_vector_creation_and_canonical_id():
    features = {
        "trend_direction": 1.0,
        "slope": 0.0025,
        "z_score": 1.45,
        "rsi": 65.2,
    }
    v_id, canon_hash = compute_feature_vector_id("VOLATILITY_100", "1m", "2026-08-07T12:00:00Z", features)

    assert v_id.startswith("FVR_")
    assert len(v_id) == 20  # FVR_ (4) + HEX16 (16)
    assert len(canon_hash) == 64

    vec = FeatureVector(
        vector_id=v_id,
        symbol="VOLATILITY_100",
        timeframe="1m",
        timestamp="2026-08-07T12:00:00Z",
        version="5.0.0",
        features=features,
        checksum="CHK",
        metadata={"count": 4},
        canonical_hash=canon_hash,
    )

    assert vec.vector_id == v_id
    assert vec.get_feature("z_score") == 1.45
    assert vec.get_feature("non_existent", default=-99.0) == -99.0

    # Immutability verification
    with pytest.raises(ValidationError):
        vec.symbol = "CRASH_500"  # Should fail on frozen model
