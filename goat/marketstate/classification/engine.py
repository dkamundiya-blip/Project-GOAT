"""
Project GOAT v0.8 — Market Classification Engine

Combines VolatilityAssessment, LiquidityAssessment, StructureAssessment, and MarketQualityAssessment
into a unified, deterministic MarketState (MST_<HEX16>) model with complete explainability.
Never predicts price, forecasts direction, or generates trade signals.
"""

from __future__ import annotations

import datetime
from goat.marketstate.core.canonical import compute_market_state_id
from goat.marketstate.core.enums import QualityState
from goat.marketstate.core.models import (
    LiquidityAssessment,
    MarketQualityAssessment,
    MarketState,
    StructureAssessment,
    VolatilityAssessment,
)
from goat.research.edge.canonical import compute_canonical_sha256


class MarketClassificationEngine:
    """Engine responsible for synthesizing component assessments into a unified MarketState."""

    def __init__(self):
        pass

    def classify(
        self,
        symbol: str,
        volatility: VolatilityAssessment,
        liquidity: LiquidityAssessment,
        structure: StructureAssessment,
        quality: MarketQualityAssessment,
        timestamp: str | None = None,
    ) -> MarketState:
        """Synthesize component assessments into a unified MarketState model."""
        sym = symbol.strip().upper()
        ts = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Calculate deterministic confidence score (0.0 to 1.0)
        quality_factor = {
            QualityState.EXCELLENT: 1.0,
            QualityState.GOOD: 0.85,
            QualityState.ACCEPTABLE: 0.70,
            QualityState.POOR: 0.40,
            QualityState.INVALID: 0.0,
        }.get(quality.overall_quality, 0.5)

        struct_factor = structure.trend_strength / 100.0
        liq_factor = liquidity.liquidity_score / 100.0

        confidence = round(0.5 * quality_factor + 0.3 * struct_factor + 0.2 * liq_factor, 4)

        explanation = (
            f"Market State for {sym}: Trend={structure.trend_state.value}, Structure={structure.structure_state.value}, "
            f"Volatility={volatility.volatility_class.value} ({volatility.volatility_score:.1f}), "
            f"Liquidity={liquidity.liquidity_state.value} (Spread: {liquidity.spread:.4f}, Quality: {liquidity.spread_quality.value}), "
            f"Quality={quality.overall_quality.value} (Confidence: {confidence:.2f})."
        )

        state_id, canonical_hash = compute_market_state_id(
            symbol=sym,
            timestamp=ts,
            trend_state=structure.trend_state.value,
            volatility_state=volatility.volatility_class.value,
            liquidity_state=liquidity.liquidity_state.value,
            structure_state=structure.structure_state.value,
        )

        return MarketState(
            state_id=state_id,
            symbol=sym,
            timestamp=ts,
            trend_state=structure.trend_state,
            volatility_state=volatility.volatility_class,
            liquidity_state=liquidity.liquidity_state,
            spread_state=liquidity.spread_quality,
            activity_state=liquidity.activity_state,
            structure_state=structure.structure_state,
            overall_quality=quality.overall_quality,
            confidence=confidence,
            explanation=explanation,
            metadata={
                "volatility_id": volatility.assessment_id,
                "liquidity_id": liquidity.assessment_id,
                "structure_id": structure.assessment_id,
                "quality_id": quality.assessment_id,
            },
            canonical_hash=canonical_hash,
        )
