"""
Project GOAT v0.8 — Liquidity Assessment Engine

Measures bid/ask spread quality, tick activity frequency, and market depth proxies,
assigning deterministic LiquidityState, SpreadState, and ActivityState classifications.
"""

from __future__ import annotations

from typing import Sequence

from goat.marketdata.core.models import MarketTick
from goat.marketstate.core.canonical import compute_liquidity_id
from goat.marketstate.core.enums import ActivityState, LiquidityState, SpreadState
from goat.marketstate.core.models import LiquidityAssessment
from goat.research.edge.canonical import compute_canonical_sha256


class LiquidityAssessmentEngine:
    """Engine responsible for calculating deterministic market liquidity and spread metrics."""

    def __init__(
        self,
        tight_spread_max: float = 0.1,
        normal_spread_max: float = 0.5,
        wide_spread_max: float = 2.0,
    ):
        self.tight_spread_max = float(tight_spread_max)
        self.normal_spread_max = float(normal_spread_max)
        self.wide_spread_max = float(wide_spread_max)

    def evaluate_ticks(self, symbol: str, ticks: Sequence[MarketTick]) -> LiquidityAssessment:
        """Evaluate liquidity state from a series of MarketTicks."""
        sym = symbol.strip().upper()

        if not ticks:
            liq_id, canonical_hash = compute_liquidity_id(sym, 0.0, "NORMAL", 50.0)
            return LiquidityAssessment(
                assessment_id=liq_id,
                symbol=sym,
                spread=0.0,
                spread_quality=SpreadState.NORMAL,
                liquidity_score=50.0,
                market_depth_proxy=1.0,
                activity_state=ActivityState.NORMAL,
                liquidity_state=LiquidityState.NORMAL,
                explanation="No tick data available; returning baseline default liquidity assessment",
                metadata={},
                canonical_hash=canonical_hash,
            )

        latest_tick = ticks[-1]
        spreads = [t.spread for t in ticks]
        avg_spread = sum(spreads) / len(spreads) if spreads else latest_tick.spread

        # Classify Spread State
        if avg_spread <= self.tight_spread_max:
            spread_st = SpreadState.TIGHT
            spread_score = 90.0
        elif avg_spread <= self.normal_spread_max:
            spread_st = SpreadState.NORMAL
            spread_score = 75.0
        elif avg_spread <= self.wide_spread_max:
            spread_st = SpreadState.WIDE
            spread_score = 40.0
        else:
            spread_st = SpreadState.EXTREME
            spread_score = 15.0

        # Classify Activity State based on sample count
        tick_count = len(ticks)
        if tick_count < 5:
            act_st = ActivityState.QUIET
            act_score = 30.0
        elif tick_count < 20:
            act_st = ActivityState.NORMAL
            act_score = 60.0
        elif tick_count < 50:
            act_st = ActivityState.ACTIVE
            act_score = 80.0
        else:
            act_st = ActivityState.VERY_ACTIVE
            act_score = 95.0

        # Composite Liquidity Score (0..100)
        liq_score = round(0.6 * spread_score + 0.4 * act_score, 2)

        # Classify Liquidity State
        if liq_score >= 80.0:
            liq_st = LiquidityState.HIGH
        elif liq_score >= 50.0:
            liq_st = LiquidityState.NORMAL
        elif liq_score >= 30.0:
            liq_st = LiquidityState.LOW
        else:
            liq_st = LiquidityState.VERY_LOW

        depth_proxy = round(float(tick_count) / max(1.0, avg_spread), 2)
        explanation = f"Average spread {avg_spread:.4f} ({spread_st.value}), tick activity count {tick_count} ({act_st.value}) yielding liquidity score {liq_score:.2f} ({liq_st.value})"

        liq_id, canonical_hash = compute_liquidity_id(sym, avg_spread, spread_st.value, liq_score)

        return LiquidityAssessment(
            assessment_id=liq_id,
            symbol=sym,
            spread=round(avg_spread, 6),
            spread_quality=spread_st,
            liquidity_score=liq_score,
            market_depth_proxy=depth_proxy,
            activity_state=act_st,
            liquidity_state=liq_st,
            explanation=explanation,
            metadata={"sample_ticks": tick_count},
            canonical_hash=canonical_hash,
        )
