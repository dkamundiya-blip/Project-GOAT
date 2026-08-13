"""
Project GOAT — Test Suite: Time-Aligned Forward Return Alignment (`tests/test_forward_return_alignment.py`)

Verifies:
1. Zero lookahead leakage in feature-to-return pairing.
2. Step-by-step observation buffer lifecycle across C1(1000) -> C2(1010) -> C3(1005).
3. Exact mathematical forward return calculation:
   - R1 = (1010 - 1000) / 1000 = +0.0100 (+1.00%)
   - R2 = (1005 - 1010) / 1010 = -0.004950495... (-0.495%)
4. FV_t timestamps strictly precede the closing timestamp of the candle used to compute R_t.
5. Immutability: Future candle data cannot alter the previously frozen FeatureVector.
"""

from __future__ import annotations

import datetime
from datetime import timezone
import pytest

from goat.integration.master import MasterSystemIntegrationEngine
from goat.market_intelligence.models.candle import (
    IntelligenceCandle,
    IntelligenceTimeframe,
    compute_intelligence_candle_id,
)


def test_leakage_free_forward_return_alignment():
    """Verify exact step-by-step time-aligned forward return calculation across 3 candles."""
    engine = MasterSystemIntegrationEngine(db_path=":memory:", symbol="BOOM_1000", timeframe="1m")
    key = ("BOOM_1000", "1m")

    t0_iso = "2026-08-14T02:00:00Z"
    t1_iso = "2026-08-14T02:01:00Z"
    t2_iso = "2026-08-14T02:02:00Z"
    t3_iso = "2026-08-14T02:03:00Z"

    # Candle 1: Open=1000, Close=1000, Closed at t1
    cid1, chash1 = compute_intelligence_candle_id(
        symbol="BOOM_1000", timeframe="1m", open_price=1000.0, high_price=1002.0, low_price=998.0, close_price=1000.0,
        open_timestamp=t0_iso, close_timestamp=t1_iso
    )
    c1 = IntelligenceCandle(
        candle_id=cid1, symbol="BOOM_1000", timeframe=IntelligenceTimeframe.M1, open=1000.0, high=1002.0, low=998.0, close=1000.0,
        volume=10.0, open_timestamp=t0_iso, close_timestamp=t1_iso, completed=True, checksum="CHK1", metadata={}, canonical_hash=chash1
    )

    # Candle 2: Open=1000, Close=1010, Closed at t2
    cid2, chash2 = compute_intelligence_candle_id(
        symbol="BOOM_1000", timeframe="1m", open_price=1000.0, high_price=1012.0, low_price=999.0, close_price=1010.0,
        open_timestamp=t1_iso, close_timestamp=t2_iso
    )
    c2 = IntelligenceCandle(
        candle_id=cid2, symbol="BOOM_1000", timeframe=IntelligenceTimeframe.M1, open=1000.0, high=1012.0, low=999.0, close=1010.0,
        volume=15.0, open_timestamp=t1_iso, close_timestamp=t2_iso, completed=True, checksum="CHK2", metadata={}, canonical_hash=chash2
    )

    # Candle 3: Open=1010, Close=1005, Closed at t3
    cid3, chash3 = compute_intelligence_candle_id(
        symbol="BOOM_1000", timeframe="1m", open_price=1010.0, high_price=1015.0, low_price=1003.0, close_price=1005.0,
        open_timestamp=t2_iso, close_timestamp=t3_iso
    )
    c3 = IntelligenceCandle(
        candle_id=cid3, symbol="BOOM_1000", timeframe=IntelligenceTimeframe.M1, open=1010.0, high=1015.0, low=1003.0, close=1005.0,
        volume=12.0, open_timestamp=t2_iso, close_timestamp=t3_iso, completed=True, checksum="CHK3", metadata={}, canonical_hash=chash3
    )

    # --- STEP 1: Process Candle 1 ---
    engine._on_candle(c1)
    assert key in engine._pending_observations
    pending_fv1, pending_close1 = engine._pending_observations[key]
    assert pending_close1 == 1000.0
    # Zero completed forward returns yet (outcome of C1 is in the future)
    assert len(engine._observation_returns.get(key, [])) == 0
    assert len(engine._observation_fvs.get(key, [])) == 0

    # Save frozen copy of FV1 to verify future candles do not mutate it
    frozen_fv1_dict = dict(pending_fv1.features)

    # --- STEP 2: Process Candle 2 ---
    engine._on_candle(c2)
    # Exactly 1 completed observation now (C1 -> C2 return is realized)
    fvs_step2 = engine._observation_fvs[key]
    rets_step2 = engine._observation_returns[key]
    assert len(fvs_step2) == 1
    assert len(rets_step2) == 1

    # R1 = (1010 - 1000) / 1000 = +0.0100
    assert rets_step2[0] == pytest.approx(0.0100, rel=1e-5)
    # FV paired with R1 is strictly FV1
    assert fvs_step2[0].vector_id == pending_fv1.vector_id
    assert fvs_step2[0].features == frozen_fv1_dict
    # Timestamp of FV1 precedes close of C2 (t1 < t2)
    assert fvs_step2[0].timestamp <= c1.close_timestamp < c2.close_timestamp

    # --- STEP 3: Process Candle 3 ---
    engine._on_candle(c3)
    # Exactly 2 completed observations now (C2 -> C3 return is realized)
    fvs_step3 = engine._observation_fvs[key]
    rets_step3 = engine._observation_returns[key]
    assert len(fvs_step3) == 2
    assert len(rets_step3) == 2

    # R2 = (1005 - 1010) / 1010 = -0.004950495...
    expected_r2 = (1005.0 - 1010.0) / 1010.0
    assert rets_step3[1] == pytest.approx(expected_r2, rel=1e-5)
    assert rets_step3[0] == pytest.approx(0.0100, rel=1e-5)

    # Verify FV1 remains strictly unchanged and unmodified
    assert fvs_step3[0].features == frozen_fv1_dict
