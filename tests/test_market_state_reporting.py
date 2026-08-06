"""
Project GOAT v0.8 — Test Suite: Reporting & Executive Reports (Exhaustive Matrix)
"""

import pytest
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
from goat.marketstate.reporting.reports import (
    LiquidityReport,
    MarketStateExecutiveReport,
    MarketStateReport,
    QualityReport,
    StructureReport,
    VolatilityReport,
)

SYMBOLS = [s.value for s in DerivSymbol]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_volatility_report_matrix(symbol):
    rep_id, canonical_hash = compute_report_id("VOLATILITY", "2026-07-31T12:00:00Z")
    vol_id, v_hash = compute_volatility_id(symbol, "1M", "NORMAL", 40.0)
    vol = VolatilityAssessment(
        assessment_id=vol_id, symbol=symbol, timeframe="1M", realized_volatility=0.01,
        volatility_class=VolatilityState.NORMAL, volatility_score=40.0, explanation="test", metadata={}, canonical_hash=v_hash,
    )
    report = VolatilityReport(report_id=rep_id, symbol=symbol, assessment=vol, timestamp="2026-07-31T12:00:00Z", canonical_hash=canonical_hash)
    md = report.to_markdown()
    js = report.to_json()
    assert symbol in md
    assert rep_id in js


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_market_state_report_matrix(symbol):
    rep_id, canonical_hash = compute_report_id("STATE", "2026-07-31T12:00:00Z")
    state_id, s_hash = compute_market_state_id(symbol, "2026-07-31T12:00:00Z", "UPTREND", "NORMAL", "NORMAL", "BULLISH")
    state = MarketState(
        state_id=state_id, symbol=symbol, timestamp="2026-07-31T12:00:00Z", trend_state=TrendState.UPTREND,
        volatility_state=VolatilityState.NORMAL, liquidity_state=LiquidityState.NORMAL, spread_state=SpreadState.NORMAL,
        activity_state=ActivityState.NORMAL, structure_state=StructureState.BULLISH, overall_quality=QualityState.GOOD,
        confidence=0.85, explanation="test", metadata={}, canonical_hash=s_hash,
    )
    report = MarketStateReport(report_id=rep_id, market_state=state, timestamp="2026-07-31T12:00:00Z", canonical_hash=canonical_hash)
    md = report.to_markdown()
    js = report.to_json()
    assert symbol in md
    assert state_id in md
    assert rep_id in js
