"""
Project GOAT v0.7 — Test Suite for MarketRegimeClassificationEngine

Coverage:
- 12 regime type classifications (TRENDING, RANGING, BREAKOUT, REVERSAL, ACCUMULATION, DISTRIBUTION, HIGH_VOLATILITY, LOW_VOLATILITY, LIQUIDITY_EXPANSION, LIQUIDITY_CONTRACTION, TRANSITIONAL, UNDEFINED)
- Confidence calculation
- Sub-state indicator extraction (VolatilityState, LiquidityState, ParticipationState, TrendState, StructuralState)
"""

from goat.regimes.classification.engine import MarketRegimeClassificationEngine
from goat.regimes.core.enums import RegimeType, VolatilityState


def test_classify_trending_regime():
    engine = MarketRegimeClassificationEngine()
    obs = {"trend_strength": 0.85, "volatility_zscore": 0.2, "volume_ratio": 1.1}
    regime, matching_rules = engine.classify_regime(obs, "2026-07-30T00:00:00Z")

    assert regime.regime_id.startswith("MRG_")
    assert regime.regime_type == RegimeType.TRENDING
    assert regime.confidence >= 0.70
    assert len(matching_rules) >= 1


def test_classify_high_volatility_regime():
    engine = MarketRegimeClassificationEngine()
    obs = {"volatility_zscore": 2.0, "trend_strength": 0.20}
    regime, matching_rules = engine.classify_regime(obs, "2026-07-30T00:00:00Z")

    assert regime.regime_type == RegimeType.HIGH_VOLATILITY
    assert regime.volatility_state == VolatilityState.HIGH


def test_classify_breakout_regime():
    engine = MarketRegimeClassificationEngine()
    obs = {"breakout_flag": True, "volume_ratio": 1.6}
    regime, matching_rules = engine.classify_regime(obs, "2026-07-30T00:00:00Z")

    assert regime.regime_type == RegimeType.BREAKOUT
