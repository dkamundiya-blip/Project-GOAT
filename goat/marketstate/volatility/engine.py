"""
Project GOAT v0.8 — Volatility Assessment Engine

Measures realized volatility, price range consistency, and movement intensity,
assigning deterministic VolatilityState classifications and VolatilityAssessment (VOL_<HEX16>) models.
"""

from __future__ import annotations

import math
from typing import Sequence

from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.marketstate.core.canonical import compute_volatility_id
from goat.marketstate.core.enums import VolatilityState
from goat.marketstate.core.models import VolatilityAssessment
from goat.research.edge.canonical import compute_canonical_sha256


class VolatilityAssessmentEngine:
    """Engine responsible for calculating deterministic market volatility metrics."""

    def __init__(
        self,
        very_low_threshold: float = 5.0,
        low_threshold: float = 15.0,
        normal_threshold: float = 40.0,
        high_threshold: float = 75.0,
    ):
        self.very_low_threshold = float(very_low_threshold)
        self.low_threshold = float(low_threshold)
        self.normal_threshold = float(normal_threshold)
        self.high_threshold = float(high_threshold)

    def evaluate_ticks(self, symbol: str, ticks: Sequence[MarketTick]) -> VolatilityAssessment:
        """Evaluate volatility state from a series of MarketTicks."""
        sym = symbol.strip().upper()
        if not ticks or len(ticks) < 2:
            vol_id, canonical_hash = compute_volatility_id(sym, "TICK", "NORMAL", 20.0)
            checksum = compute_canonical_sha256({"realized_volatility": 0.0, "symbol": sym})
            return VolatilityAssessment(
                assessment_id=vol_id,
                symbol=sym,
                timeframe="TICK",
                realized_volatility=0.0,
                volatility_class=VolatilityState.NORMAL,
                volatility_score=20.0,
                explanation="Insufficient tick sample size for realized volatility calculation (defaulting to NORMAL)",
                metadata={"tick_count": len(ticks)},
                canonical_hash=canonical_hash,
            )

        mid_prices = [t.mid_price for t in ticks]
        returns = []
        for i in range(1, len(mid_prices)):
            p_prev = mid_prices[i - 1]
            p_curr = mid_prices[i]
            if p_prev > 0.0:
                ret = math.log(p_curr / p_prev)
                returns.append(ret)

        if not returns:
            std_dev = 0.0
        else:
            mean_ret = sum(returns) / len(returns)
            variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
            std_dev = math.sqrt(variance)

        # Scale volatility score 0..100
        vol_score = min(100.0, round(std_dev * 10000.0, 2))

        vol_class = self.classify_score(vol_score)
        explanation = f"Realized tick log-return standard deviation is {std_dev:.6f} yielding volatility score {vol_score:.2f} ({vol_class.value})"

        vol_id, canonical_hash = compute_volatility_id(sym, "TICK", vol_class.value, vol_score)
        checksum = compute_canonical_sha256({"realized_volatility": round(std_dev, 6), "symbol": sym})

        return VolatilityAssessment(
            assessment_id=vol_id,
            symbol=sym,
            timeframe="TICK",
            realized_volatility=round(std_dev, 6),
            volatility_class=vol_class,
            volatility_score=vol_score,
            explanation=explanation,
            metadata={"sample_size": len(ticks)},
            canonical_hash=canonical_hash,
        )

    def evaluate_candles(self, symbol: str, candles: Sequence[MarketCandle]) -> VolatilityAssessment:
        """Evaluate volatility state from a series of MarketCandles."""
        sym = symbol.strip().upper()
        if not candles:
            vol_id, canonical_hash = compute_volatility_id(sym, "1M", "NORMAL", 20.0)
            return VolatilityAssessment(
                assessment_id=vol_id,
                symbol=sym,
                timeframe="1M",
                realized_volatility=0.0,
                volatility_class=VolatilityState.NORMAL,
                volatility_score=20.0,
                explanation="No candle data provided for volatility evaluation",
                metadata={},
                canonical_hash=canonical_hash,
            )

        tf = candles[0].timeframe.value
        ranges = [(c.high - c.low) for c in candles]
        avg_range = sum(ranges) / len(ranges) if ranges else 0.0
        closes = [c.close for c in candles]
        avg_price = sum(closes) / len(closes) if closes else 1.0

        rel_range_pct = (avg_range / avg_price) * 100.0 if avg_price > 0 else 0.0
        vol_score = min(100.0, round(rel_range_pct * 50.0, 2))

        vol_class = self.classify_score(vol_score)
        explanation = f"Average candle range is {avg_range:.5f} ({rel_range_pct:.4f}% of price) giving volatility score {vol_score:.2f} ({vol_class.value})"

        vol_id, canonical_hash = compute_volatility_id(sym, tf, vol_class.value, vol_score)

        return VolatilityAssessment(
            assessment_id=vol_id,
            symbol=sym,
            timeframe=tf,
            realized_volatility=round(avg_range, 6),
            volatility_class=vol_class,
            volatility_score=vol_score,
            explanation=explanation,
            metadata={"candle_count": len(candles)},
            canonical_hash=canonical_hash,
        )

    def classify_score(self, vol_score: float) -> VolatilityState:
        """Classify a 0..100 volatility score into VolatilityState enum."""
        if vol_score <= self.very_low_threshold:
            return VolatilityState.VERY_LOW
        elif vol_score <= self.low_threshold:
            return VolatilityState.LOW
        elif vol_score <= self.normal_threshold:
            return VolatilityState.NORMAL
        elif vol_score <= self.high_threshold:
            return VolatilityState.HIGH
        else:
            return VolatilityState.EXTREME
