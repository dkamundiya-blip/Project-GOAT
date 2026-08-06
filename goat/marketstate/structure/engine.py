"""
Project GOAT v0.8 — Structure Assessment Engine

Evaluates observable price action structure: higher highs, lower lows, higher lows,
lower highs, directional consistency, and trend strength without predicting or forecasting.
Assigns deterministic StructureState, TrendState, and StructureAssessment (STR_<HEX16>) models.
"""

from __future__ import annotations

from typing import Sequence

from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.marketstate.core.canonical import compute_structure_id
from goat.marketstate.core.enums import StructureState, TrendState
from goat.marketstate.core.models import StructureAssessment
from goat.research.edge.canonical import compute_canonical_sha256


class StructureAssessmentEngine:
    """Engine responsible for classifying current market price structure and trend state."""

    def __init__(self):
        pass

    def evaluate_candles(self, symbol: str, candles: Sequence[MarketCandle]) -> StructureAssessment:
        """Evaluate market structure from a series of MarketCandles."""
        sym = symbol.strip().upper()

        if not candles or len(candles) < 3:
            str_id, canonical_hash = compute_structure_id(sym, "UNKNOWN", 0, 0, 0.0)
            return StructureAssessment(
                assessment_id=str_id,
                symbol=sym,
                structure_state=StructureState.UNKNOWN,
                trend_state=TrendState.UNKNOWN,
                higher_highs=0,
                lower_lows=0,
                higher_lows=0,
                lower_highs=0,
                trend_strength=0.0,
                explanation="Insufficient candle bar history to determine market structure (minimum 3 bars required)",
                metadata={"candle_count": len(candles)},
                canonical_hash=canonical_hash,
            )

        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        closes = [c.close for c in candles]

        hh_count = 0
        lh_count = 0
        hl_count = 0
        ll_count = 0

        for i in range(1, len(candles)):
            if highs[i] > highs[i - 1]:
                hh_count += 1
            elif highs[i] < highs[i - 1]:
                lh_count += 1

            if lows[i] > lows[i - 1]:
                hl_count += 1
            elif lows[i] < lows[i - 1]:
                ll_count += 1

        total_transitions = max(1, len(candles) - 1)
        bullish_score = ((hh_count + hl_count) / (2.0 * total_transitions)) * 100.0
        bearish_score = ((lh_count + ll_count) / (2.0 * total_transitions)) * 100.0

        # Classify Structure & Trend
        if bullish_score >= 70.0:
            struct_st = StructureState.BULLISH
            trend_st = TrendState.STRONG_UPTREND if bullish_score >= 85.0 else TrendState.UPTREND
            strength = bullish_score
        elif bearish_score >= 70.0:
            struct_st = StructureState.BEARISH
            trend_st = TrendState.STRONG_DOWNTREND if bearish_score >= 85.0 else TrendState.DOWNTREND
            strength = bearish_score
        elif abs(bullish_score - bearish_score) <= 15.0:
            struct_st = StructureState.RANGING
            trend_st = TrendState.SIDEWAYS
            strength = round(abs(bullish_score - bearish_score), 2)
        else:
            struct_st = StructureState.TRANSITIONAL
            trend_st = TrendState.UPTREND if bullish_score > bearish_score else TrendState.DOWNTREND
            strength = round(max(bullish_score, bearish_score), 2)

        explanation = (
            f"Price action displays {hh_count} higher highs, {hl_count} higher lows, {lh_count} lower highs, "
            f"and {ll_count} lower lows; classified as {struct_st.value} / {trend_st.value} (Strength: {strength:.1f})"
        )

        str_id, canonical_hash = compute_structure_id(sym, struct_st.value, hh_count, ll_count, strength)

        return StructureAssessment(
            assessment_id=str_id,
            symbol=sym,
            structure_state=struct_st,
            trend_state=trend_st,
            higher_highs=hh_count,
            lower_lows=ll_count,
            higher_lows=hl_count,
            lower_highs=lh_count,
            trend_strength=round(strength, 2),
            explanation=explanation,
            metadata={"bar_count": len(candles)},
            canonical_hash=canonical_hash,
        )

    def evaluate_ticks(self, symbol: str, ticks: Sequence[MarketTick]) -> StructureAssessment:
        """Evaluate structure from tick series by building tick mid-price extrema."""
        sym = symbol.strip().upper()
        if not ticks or len(ticks) < 4:
            str_id, canonical_hash = compute_structure_id(sym, "UNKNOWN", 0, 0, 0.0)
            return StructureAssessment(
                assessment_id=str_id,
                symbol=sym,
                structure_state=StructureState.UNKNOWN,
                trend_state=TrendState.UNKNOWN,
                higher_highs=0,
                lower_lows=0,
                higher_lows=0,
                lower_highs=0,
                trend_strength=0.0,
                explanation="Insufficient tick count to derive structure extrema",
                metadata={"tick_count": len(ticks)},
                canonical_hash=canonical_hash,
            )

        mids = [t.mid_price for t in ticks]
        up_moves = sum(1 for i in range(1, len(mids)) if mids[i] > mids[i - 1])
        down_moves = sum(1 for i in range(1, len(mids)) if mids[i] < mids[i - 1])
        total_moves = max(1, len(mids) - 1)

        pct_up = (up_moves / total_moves) * 100.0
        pct_down = (down_moves / total_moves) * 100.0

        if pct_up >= 65.0:
            struct_st = StructureState.BULLISH
            trend_st = TrendState.UPTREND
            strength = pct_up
        elif pct_down >= 65.0:
            struct_st = StructureState.BEARISH
            trend_st = TrendState.DOWNTREND
            strength = pct_down
        else:
            struct_st = StructureState.RANGING
            trend_st = TrendState.SIDEWAYS
            strength = round(abs(pct_up - pct_down), 2)

        explanation = f"Tick directional consistency: {pct_up:.1f}% up moves, {pct_down:.1f}% down moves ({struct_st.value})"

        str_id, canonical_hash = compute_structure_id(sym, struct_st.value, up_moves, down_moves, strength)

        return StructureAssessment(
            assessment_id=str_id,
            symbol=sym,
            structure_state=struct_st,
            trend_state=trend_st,
            higher_highs=up_moves,
            lower_lows=down_moves,
            higher_lows=0,
            lower_highs=0,
            trend_strength=round(strength, 2),
            explanation=explanation,
            metadata={"tick_count": len(ticks)},
            canonical_hash=canonical_hash,
        )
