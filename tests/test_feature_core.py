"""
Project GOAT v0.7 — Step 4.1B Feature Core & Metadata Verification Test Suite
"""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from goat.features import (
    BarRange,
    BaseFeature,
    BodyRatio,
    CompositeFeature,
    DataType,
    DeprecationStatus,
    DerivedFeature,
    DeterminismClass,
    FeatureMetadata,
    LogReturn,
    LowerWickRatio,
    MarketDataWindow,
    PrimitiveFeature,
    StationarityType,
    TaxonomyCategory,
    UpperWickRatio,
    compute_feature_canonical_hash,
)


@pytest.fixture
def sample_market_data() -> MarketDataWindow:
    """Fixture providing synthetic 5-bar OHLCV market data window."""
    dates = pd.date_range("2026-01-01 09:30", periods=5, freq="5min")
    data = {
        "timestamp": dates,
        "open": [100.0, 102.0, 101.0, 105.0, 104.0],
        "high": [103.0, 104.0, 106.0, 107.0, 105.0],
        "low": [99.0, 100.0, 100.0, 103.0, 101.0],
        "close": [102.0, 101.0, 105.0, 104.0, 102.0],
        "volume": [1000.0, 1500.0, 1200.0, 1800.0, 1100.0],
    }
    return MarketDataWindow(data)


def test_feature_metadata_immutability():
    """Verify FeatureMetadata is frozen and immutable."""
    meta = FeatureMetadata(
        feature_id="FEAT_0123456789ABCDEF",
        canonical_hash="a" * 64,
        scientific_fingerprint="FPT_" + "a" * 64,
        fingerprint_timestamp="2026-07-30T00:00:00Z",
        name="TestFeature",
        version="1.0.0",
        taxonomy_category=TaxonomyCategory.TREND,
        mathematical_definition="x_t",
        algorithmic_spec="x_t = 1.0",
        creation_timestamp="2026-07-30T00:00:00Z",
        provenance_generator="test_suite",
    )
    assert meta.feature_id == "FEAT_0123456789ABCDEF"
    assert meta.taxonomy_category == TaxonomyCategory.TREND

    with pytest.raises(ValidationError):
        meta.name = "MutatedName"  # Frozen check


def test_canonical_feature_hashing():
    """Verify compute_feature_canonical_hash yields deterministic FEAT_<HEX16> IDs."""
    id1, hash1 = compute_feature_canonical_hash(
        name="LogReturn",
        version="1.0.0",
        parameters={"alpha": 0.5},
        ast_spec={"op": "LogReturn", "inputs": ["close"]},
    )
    id2, hash2 = compute_feature_canonical_hash(
        name="LogReturn",
        version="1.0.0",
        parameters={"alpha": 0.5},
        ast_spec={"op": "LogReturn", "inputs": ["close"]},
    )

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("FEAT_")
    assert len(id1) == 21  # 'FEAT_' + 16 hex chars
    assert len(hash1) == 64


def test_market_data_window_validation():
    """Verify MarketDataWindow schema, monotonic timestamp, and price bound checks."""
    # Out of order timestamps
    bad_dates = pd.to_datetime(["2026-01-01 10:00", "2026-01-01 09:00"])
    bad_data = {
        "timestamp": bad_dates,
        "open": [10.0, 11.0],
        "high": [12.0, 12.0],
        "low": [9.0, 10.0],
        "close": [11.0, 10.0],
    }
    with pytest.raises(ValueError, match="strictly monotonically increasing"):
        MarketDataWindow(bad_data)

    # Invalid high < low
    bad_prices = {
        "open": [10.0],
        "high": [8.0],
        "low": [9.0],
        "close": [9.5],
    }
    with pytest.raises(ValueError, match="high < low"):
        MarketDataWindow(bad_prices)


def test_log_return_primitive(sample_market_data):
    """Verify LogReturn calculation correctness down to IEEE 754 float precision."""
    feat = LogReturn()
    res = feat.compute(sample_market_data)

    assert len(res) == 5
    assert res[0] == 0.0

    # Index 1: close 101.0 / 102.0
    expected_1 = math.log(101.0 / 102.0)
    assert pytest.approx(res[1], abs=1e-12) == expected_1

    # Index 2: close 105.0 / 101.0
    expected_2 = math.log(105.0 / 101.0)
    assert pytest.approx(res[2], abs=1e-12) == expected_2


def test_bar_range_primitive(sample_market_data):
    """Verify BarRange calculation."""
    feat = BarRange()
    res = feat.compute(sample_market_data)

    # Bar 0: high 103, low 99 -> 4.0
    # Bar 1: high 104, low 100 -> 4.0
    # Bar 2: high 106, low 100 -> 6.0
    expected = np.array([4.0, 4.0, 6.0, 4.0, 4.0], dtype=np.float64)
    np.testing.assert_allclose(res, expected, rtol=1e-12)


def test_candle_behaviour_primitives(sample_market_data):
    """Verify BodyRatio, UpperWickRatio, and LowerWickRatio sum to 1.0 on standard bars."""
    body_feat = BodyRatio()
    upper_feat = UpperWickRatio()
    lower_feat = LowerWickRatio()

    body = body_feat.compute(sample_market_data)
    upper = upper_feat.compute(sample_market_data)
    lower = lower_feat.compute(sample_market_data)

    # For every bar, body + upper_wick + lower_wick must equal 1.0 (within float precision)
    sum_ratios = body + upper + lower
    np.testing.assert_allclose(sum_ratios, np.ones(5), rtol=1e-10)


def test_causal_execution_invariant(sample_market_data):
    """Verify modifying bar t+1 does not alter feature evaluation at bar t."""
    feat = LogReturn()

    initial_out = feat.compute(sample_market_data)

    # Mutate bar 4 (last bar) with valid OHLC invariants (close=104.5, high=105.0)
    df_mutated = sample_market_data.to_dataframe()
    df_mutated.loc[4, "close"] = 104.5
    mutated_window = MarketDataWindow(df_mutated)

    mutated_out = feat.compute(mutated_window)

    # Bars 0..3 must remain 100% identical
    np.testing.assert_array_equal(initial_out[:4], mutated_out[:4])
    assert initial_out[4] != mutated_out[4]
