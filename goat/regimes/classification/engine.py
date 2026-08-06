"""
Project GOAT v0.7 — Market Regime Classification Engine

Classifies current market state into one of 12 supported regimes deterministically:
- TRENDING
- RANGING
- BREAKOUT
- REVERSAL
- ACCUMULATION
- DISTRIBUTION
- HIGH_VOLATILITY
- LOW_VOLATILITY
- LIQUIDITY_EXPANSION
- LIQUIDITY_CONTRACTION
- TRANSITIONAL
- UNDEFINED
"""

from __future__ import annotations

from typing import Any

from goat.regimes.core.canonical import compute_canonical_sha256, compute_regime_id
from goat.regimes.core.enums import (
    LiquidityState,
    ParticipationState,
    RegimeType,
    StructuralState,
    TrendState,
    VolatilityState,
)
from goat.regimes.core.models import MarketRegime, RegimeRule
from goat.regimes.rules.engine import RegimeRuleEngine


class MarketRegimeClassificationEngine:
    """Engine for classifying market regimes deterministically using rule evaluation."""

    def __init__(self, rule_engine: RegimeRuleEngine | None = None) -> None:
        self.rule_engine = rule_engine or RegimeRuleEngine()

    def classify_regime(
        self,
        observations: dict[str, Any],
        timestamp: str,
    ) -> tuple[MarketRegime, list[RegimeRule]]:
        """Classify current market regime from market observation metrics deterministically.

        Args:
            observations: Dict containing market metrics (trend_strength, volatility_zscore, etc.).
            timestamp: ISO 8601 UTC timestamp string.

        Returns:
            Tuple of (MarketRegime, list[matching RegimeRules]).
        """
        rule_evals = self.rule_engine.evaluate_all_rules(observations)
        matching_rules = [r for r, matched in rule_evals if matched]

        selected_type: RegimeType
        confidence: float

        if matching_rules:
            # Pick matching rule with highest priority (sorted descending)
            primary_rule = matching_rules[0]
            selected_type = primary_rule.expected_regime
            confidence = round(min(1.0, 0.70 + 0.05 * len(matching_rules)), 4)
        else:
            # Fallback heuristics if no rule explicitly matched
            trend_str = float(observations.get("trend_strength", 0.5))
            vol_z = float(observations.get("volatility_zscore", 0.0))

            if trend_str >= 0.65:
                selected_type = RegimeType.TRENDING
                confidence = 0.65
            elif vol_z >= 1.5:
                selected_type = RegimeType.HIGH_VOLATILITY
                confidence = 0.65
            elif trend_str <= 0.35:
                selected_type = RegimeType.RANGING
                confidence = 0.60
            else:
                selected_type = RegimeType.UNDEFINED
                confidence = 0.40

        # Sub-state classifications
        vol_z = float(observations.get("volatility_zscore", 0.0))
        vol_state = VolatilityState.HIGH if vol_z >= 1.0 else (VolatilityState.LOW if vol_z <= -1.0 else VolatilityState.NORMAL)

        vol_ratio = float(observations.get("volume_ratio", 1.0))
        liq_state = LiquidityState.EXPANSION if vol_ratio >= 1.2 else (LiquidityState.CONTRACTION if vol_ratio <= 0.8 else LiquidityState.NORMAL)

        part_str = str(observations.get("participation_state", "BALANCED")).upper()
        part_state = ParticipationState.INSTITUTIONAL if "INSTITUTIONAL" in part_str else (ParticipationState.RETAIL if "RETAIL" in part_str else ParticipationState.BALANCED)

        trend_dir = str(observations.get("trend_direction", "NEUTRAL")).upper()
        tr_state = TrendState.BULLISH if "BULL" in trend_dir else (TrendState.BEARISH if "BEAR" in trend_dir else TrendState.NEUTRAL)

        mom_state = str(observations.get("momentum_state", "FLAT")).upper()

        struct_str = str(observations.get("structural_state", "CONSOLIDATION")).upper()
        struct_state = StructuralState.BREAKOUT_EXPANSION if "BREAKOUT" in struct_str else (StructuralState.MEAN_REVERTING if "MEAN" in struct_str else StructuralState.CONSOLIDATION)

        regime_id, _ = compute_regime_id(selected_type.value, timestamp)

        payload = {
            "confidence": confidence,
            "regime_id": regime_id,
            "regime_type": selected_type.value,
            "timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        regime = MarketRegime(
            regime_id=regime_id,
            timestamp=timestamp,
            regime_type=selected_type,
            volatility_state=vol_state,
            liquidity_state=liq_state,
            participation_state=part_state,
            trend_state=tr_state,
            momentum_state=mom_state,
            structural_state=struct_state,
            confidence=confidence,
            metadata={"observations_count": len(observations), "matching_rules_count": len(matching_rules)},
            canonical_hash=canonical_hash,
        )

        return regime, matching_rules
