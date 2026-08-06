"""
Project GOAT v0.8 — Test Suite: SQLite Persistence & Round-Trip Repositories (Exhaustive Matrix)
"""

import sqlite3
import pytest

from goat.marketdata.core.enums import DerivSymbol
from goat.marketstate.core.canonical import (
    compute_liquidity_id,
    compute_market_state_id,
    compute_quality_id,
    compute_structure_id,
    compute_volatility_id,
)
from goat.marketstate.core.enums import (
    ActivityState,
    LiquidityState,
    QualityState,
    SpreadState,
    StructureState,
    TrendState,
    VolatilityState,
)
from goat.marketstate.core.models import (
    LiquidityAssessment,
    MarketQualityAssessment,
    MarketState,
    StructureAssessment,
    VolatilityAssessment,
)
from goat.marketstate.persistence.repository import (
    LiquidityRepository,
    MarketStateRepository,
    QualityRepository,
    StructureRepository,
    VolatilityRepository,
    init_marketstate_db,
)

SYMBOLS = [s.value for s in DerivSymbol]


@pytest.fixture
def db_conn():
    conn = init_marketstate_db(":memory:")
    yield conn
    conn.close()


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_volatility_persistence_roundtrip_matrix(db_conn, symbol):
    repo = VolatilityRepository(db_conn)
    vol_id, canonical_hash = compute_volatility_id(symbol, "1M", "NORMAL", 40.0)
    vol = VolatilityAssessment(
        assessment_id=vol_id, symbol=symbol, timeframe="1M", realized_volatility=0.015,
        volatility_class=VolatilityState.NORMAL, volatility_score=40.0, explanation="test", metadata={"s": symbol}, canonical_hash=canonical_hash,
    )
    repo.save(vol)
    fetched = repo.get_by_id(vol_id)
    assert fetched is not None
    assert fetched.symbol == symbol
    assert fetched.volatility_score == 40.0


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_liquidity_persistence_roundtrip_matrix(db_conn, symbol):
    repo = LiquidityRepository(db_conn)
    liq_id, canonical_hash = compute_liquidity_id(symbol, 0.2, "NORMAL", 70.0)
    liq = LiquidityAssessment(
        assessment_id=liq_id, symbol=symbol, spread=0.2, spread_quality=SpreadState.NORMAL,
        liquidity_score=70.0, market_depth_proxy=10.0, activity_state=ActivityState.NORMAL,
        liquidity_state=LiquidityState.NORMAL, explanation="test", metadata={"s": symbol}, canonical_hash=canonical_hash,
    )
    repo.save(liq)
    fetched = repo.get_by_id(liq_id)
    assert fetched is not None
    assert fetched.symbol == symbol
    assert fetched.liquidity_score == 70.0


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_structure_persistence_roundtrip_matrix(db_conn, symbol):
    repo = StructureRepository(db_conn)
    str_id, canonical_hash = compute_structure_id(symbol, "BULLISH", 5, 1, 80.0)
    struct = StructureAssessment(
        assessment_id=str_id, symbol=symbol, structure_state=StructureState.BULLISH,
        trend_state=TrendState.UPTREND, higher_highs=5, lower_lows=1, higher_lows=4,
        lower_highs=1, trend_strength=80.0, explanation="test", metadata={"s": symbol}, canonical_hash=canonical_hash,
    )
    repo.save(struct)
    fetched = repo.get_by_id(str_id)
    assert fetched is not None
    assert fetched.symbol == symbol
    assert fetched.trend_strength == 80.0


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_quality_persistence_roundtrip_matrix(db_conn, symbol):
    repo = QualityRepository(db_conn)
    mqa_id, canonical_hash = compute_quality_id(symbol, "EXCELLENT", "EXCELLENT", "EXCELLENT")
    qual = MarketQualityAssessment(
        assessment_id=mqa_id, symbol=symbol, data_quality=QualityState.EXCELLENT,
        stream_health=QualityState.EXCELLENT, latency_quality=QualityState.EXCELLENT,
        replay_quality=QualityState.EXCELLENT, overall_quality=QualityState.EXCELLENT,
        explanation="test", metadata={"s": symbol}, canonical_hash=canonical_hash,
    )
    repo.save(qual)
    fetched = repo.get_by_id(mqa_id)
    assert fetched is not None
    assert fetched.symbol == symbol
    assert fetched.overall_quality == QualityState.EXCELLENT


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_market_state_persistence_roundtrip_matrix(db_conn, symbol):
    repo = MarketStateRepository(db_conn)
    state_id, canonical_hash = compute_market_state_id(symbol, "2026-07-31T12:00:00Z", "UPTREND", "NORMAL", "NORMAL", "BULLISH")
    state = MarketState(
        state_id=state_id, symbol=symbol, timestamp="2026-07-31T12:00:00Z", trend_state=TrendState.UPTREND,
        volatility_state=VolatilityState.NORMAL, liquidity_state=LiquidityState.NORMAL, spread_state=SpreadState.NORMAL,
        activity_state=ActivityState.NORMAL, structure_state=StructureState.BULLISH, overall_quality=QualityState.GOOD,
        confidence=0.85, explanation="test", metadata={"s": symbol}, canonical_hash=canonical_hash,
    )
    repo.save(state)
    fetched = repo.get_by_id(state_id)
    assert fetched is not None
    assert fetched.state_id == state_id
    assert fetched.symbol == symbol
    assert fetched.confidence == 0.85
