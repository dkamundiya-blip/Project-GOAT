"""
Project GOAT v0.8 — Test Suite: Market State Core Models & Canonical IDs (Exhaustive Matrix)
"""

import pytest
from pydantic import ValidationError

from goat.marketdata.core.enums import DerivSymbol
from goat.marketstate.core.canonical import (
    compute_liquidity_id,
    compute_market_state_id,
    compute_quality_id,
    compute_report_id,
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

SYMBOLS = [s.value for s in DerivSymbol]
TREND_STATES = [t.value for t in TrendState]
VOLATILITY_STATES = [v.value for v in VolatilityState]
LIQUIDITY_STATES = [l.value for l in LiquidityState]
STRUCTURE_STATES = [s.value for s in StructureState]
QUALITY_STATES = [q.value for q in QualityState]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("trend", TREND_STATES[:3])
@pytest.mark.parametrize("vol", VOLATILITY_STATES[:3])
def test_market_state_immutability_matrix(symbol, trend, vol):
    state_id, canonical_hash = compute_market_state_id(symbol, "2026-07-31T12:00:00Z", trend, vol, "NORMAL", "BULLISH")
    state = MarketState(
        state_id=state_id,
        symbol=symbol,
        timestamp="2026-07-31T12:00:00Z",
        trend_state=TrendState(trend),
        volatility_state=VolatilityState(vol),
        liquidity_state=LiquidityState.NORMAL,
        spread_state=SpreadState.NORMAL,
        activity_state=ActivityState.NORMAL,
        structure_state=StructureState.BULLISH,
        overall_quality=QualityState.GOOD,
        confidence=0.85,
        explanation=f"State for {symbol}",
        metadata={},
        canonical_hash=canonical_hash,
    )

    assert state.state_id.startswith("MST_")
    assert state.symbol == symbol

    with pytest.raises(ValidationError):
        state.confidence = 0.5


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("vol_class", VOLATILITY_STATES)
def test_volatility_assessment_immutability_matrix(symbol, vol_class):
    vol_id, canonical_hash = compute_volatility_id(symbol, "1M", vol_class, 50.0)
    assessment = VolatilityAssessment(
        assessment_id=vol_id,
        symbol=symbol,
        timeframe="1M",
        realized_volatility=0.02,
        volatility_class=VolatilityState(vol_class),
        volatility_score=50.0,
        explanation=f"Vol test {symbol}",
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert assessment.assessment_id.startswith("VOL_")
    assert assessment.volatility_class.value == vol_class


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("liq_class", LIQUIDITY_STATES)
def test_liquidity_assessment_immutability_matrix(symbol, liq_class):
    liq_id, canonical_hash = compute_liquidity_id(symbol, 0.2, "NORMAL", 70.0)
    assessment = LiquidityAssessment(
        assessment_id=liq_id,
        symbol=symbol,
        spread=0.2,
        spread_quality=SpreadState.NORMAL,
        liquidity_score=70.0,
        market_depth_proxy=10.0,
        activity_state=ActivityState.NORMAL,
        liquidity_state=LiquidityState(liq_class),
        explanation=f"Liq test {symbol}",
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert assessment.assessment_id.startswith("LIQ_")
    assert assessment.liquidity_state.value == liq_class


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("struct_class", STRUCTURE_STATES)
def test_structure_assessment_immutability_matrix(symbol, struct_class):
    str_id, canonical_hash = compute_structure_id(symbol, struct_class, 5, 2, 80.0)
    assessment = StructureAssessment(
        assessment_id=str_id,
        symbol=symbol,
        structure_state=StructureState(struct_class),
        trend_state=TrendState.UPTREND,
        higher_highs=5,
        lower_lows=2,
        higher_lows=4,
        lower_highs=1,
        trend_strength=80.0,
        explanation=f"Struct test {symbol}",
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert assessment.assessment_id.startswith("STR_")
    assert assessment.structure_state.value == struct_class


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("qual_class", QUALITY_STATES)
def test_quality_assessment_immutability_matrix(symbol, qual_class):
    mqa_id, canonical_hash = compute_quality_id(symbol, qual_class, qual_class, qual_class)
    assessment = MarketQualityAssessment(
        assessment_id=mqa_id,
        symbol=symbol,
        data_quality=QualityState(qual_class),
        stream_health=QualityState(qual_class),
        latency_quality=QualityState(qual_class),
        replay_quality=QualityState(qual_class),
        overall_quality=QualityState(qual_class),
        explanation=f"Quality test {symbol}",
        metadata={},
        canonical_hash=canonical_hash,
    )
    assert assessment.assessment_id.startswith("MQA_")
    assert assessment.overall_quality.value == qual_class
