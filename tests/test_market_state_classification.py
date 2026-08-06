"""
Project GOAT v0.8 — Test Suite: Market Classification Engine (Exhaustive Matrix)
"""

import pytest
from goat.marketdata.core.enums import DerivSymbol
from goat.marketstate.classification.engine import MarketClassificationEngine
from goat.marketstate.core.canonical import (
    compute_liquidity_id,
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
    StructureAssessment,
    VolatilityAssessment,
)

SYMBOLS = [s.value for s in DerivSymbol]
VOL_CLASSES = [v.value for v in VolatilityState]
QUALITY_CLASSES = [q.value for q in QualityState]


@pytest.mark.parametrize("symbol", SYMBOLS)
@pytest.mark.parametrize("vol_class", VOL_CLASSES)
@pytest.mark.parametrize("qual_class", QUALITY_CLASSES)
def test_classification_synthesis_matrix(symbol, vol_class, qual_class):
    engine = MarketClassificationEngine()

    vol_id, v_hash = compute_volatility_id(symbol, "1M", vol_class, 35.0)
    vol = VolatilityAssessment(
        assessment_id=vol_id, symbol=symbol, timeframe="1M", realized_volatility=0.01,
        volatility_class=VolatilityState(vol_class), volatility_score=35.0, explanation="Vol test", metadata={}, canonical_hash=v_hash,
    )

    liq_id, l_hash = compute_liquidity_id(symbol, 0.2, "NORMAL", 75.0)
    liq = LiquidityAssessment(
        assessment_id=liq_id, symbol=symbol, spread=0.2, spread_quality=SpreadState.NORMAL,
        liquidity_score=75.0, market_depth_proxy=10.0, activity_state=ActivityState.NORMAL,
        liquidity_state=LiquidityState.NORMAL, explanation="Liq test", metadata={}, canonical_hash=l_hash,
    )

    str_id, s_hash = compute_structure_id(symbol, "BULLISH", 5, 1, 80.0)
    struct = StructureAssessment(
        assessment_id=str_id, symbol=symbol, structure_state=StructureState.BULLISH,
        trend_state=TrendState.UPTREND, higher_highs=5, lower_lows=1, higher_lows=4,
        lower_highs=1, trend_strength=80.0, explanation="Struct test", metadata={}, canonical_hash=s_hash,
    )

    mqa_id, q_hash = compute_quality_id(symbol, qual_class, qual_class, qual_class)
    qual = MarketQualityAssessment(
        assessment_id=mqa_id, symbol=symbol, data_quality=QualityState(qual_class),
        stream_health=QualityState(qual_class), latency_quality=QualityState(qual_class),
        replay_quality=QualityState(qual_class), overall_quality=QualityState(qual_class),
        explanation="Quality test", metadata={}, canonical_hash=q_hash,
    )

    state = engine.classify(symbol, vol, liq, struct, qual)

    assert state.symbol == symbol
    assert state.state_id.startswith("MST_")
    assert state.trend_state == TrendState.UPTREND
    assert state.structure_state == StructureState.BULLISH
    assert state.volatility_state == VolatilityState(vol_class)
    assert state.overall_quality == QualityState(qual_class)
    assert state.confidence >= 0.0
    assert len(state.explanation) > 0
