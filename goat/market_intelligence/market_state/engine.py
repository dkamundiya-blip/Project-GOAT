"""
Project GOAT Phase 4 — Market State Engine (`goat.market_intelligence.market_state`)

Continuously classifies market state across 5 core dimensions:
Trend (Bullish/Bearish/Sideways), Volatility (Low/Medium/High), Momentum (Positive/Negative/Neutral),
Regime (Trend/Range/Expansion/Compression), Liquidity (Low/Medium/High).
Returns strongly typed immutable MarketState objects.
"""

from __future__ import annotations

import datetime
import threading
from typing import Any

from goat.market_intelligence.models.market_state import (
    LiquidityLevel,
    MarketState,
    MomentumState,
    RegimeState,
    TrendState,
    VolatilityLevel,
    compute_market_state_id,
)
from goat.market_intelligence.models.statistics import MarketStatistics
from goat.market_intelligence.models.tick import RecordedTick
from goat.market_intelligence.persistence.interfaces import IMarketStateRepository
from goat.research.edge.canonical import compute_canonical_sha256


class MarketStateEngine:
    """Institutional Market State Engine providing multi-dimensional state classification."""

    def __init__(
        self,
        repository: IMarketStateRepository | None = None,
        trend_threshold: float = 0.0005,
        high_volatility_threshold: float = 0.005,
        low_volatility_threshold: float = 0.001,
        momentum_threshold: float = 0.0003,
        low_tick_rate_threshold: float = 1.0,
        high_tick_rate_threshold: float = 5.0,
    ):
        self.repository = repository
        self.trend_threshold = trend_threshold
        self.high_volatility_threshold = high_volatility_threshold
        self.low_volatility_threshold = low_volatility_threshold
        self.momentum_threshold = momentum_threshold
        self.low_tick_rate_threshold = low_tick_rate_threshold
        self.high_tick_rate_threshold = high_tick_rate_threshold

        self._prev_stats: dict[str, MarketStatistics] = {}
        self._lock = threading.RLock()

    def classify_state(self, stats: MarketStatistics, current_tick: RecordedTick | None = None) -> MarketState:
        """Classify current market state from MarketStatistics and optional current RecordedTick."""
        sym = stats.symbol.upper()

        with self._lock:
            prev = self._prev_stats.get(sym)
            self._prev_stats[sym] = stats

            # 1. Trend Classification
            price_change = 0.0
            if prev and prev.rolling_vwap > 0:
                price_change = (stats.rolling_vwap - prev.rolling_vwap) / prev.rolling_vwap

            if current_tick and current_tick.mid_price > 0 and stats.rolling_low > 0:
                rel_pos = (current_tick.mid_price - stats.rolling_low) / max(stats.rolling_high - stats.rolling_low, 1e-8)
                trend_score = round(max(-1.0, min(1.0, (rel_pos - 0.5) * 2.0 + price_change * 100)), 4)
            else:
                trend_score = round(max(-1.0, min(1.0, price_change * 100)), 4)

            if trend_score > 0.2:
                trend = TrendState.BULLISH
            elif trend_score < -0.2:
                trend = TrendState.BEARISH
            else:
                trend = TrendState.SIDEWAYS

            # 2. Volatility Classification
            vol_val = stats.rolling_volatility if stats.rolling_volatility > 0 else (stats.standard_deviation / max(stats.rolling_vwap, 1.0))
            vol_score = round(max(0.0, min(1.0, vol_val / max(self.high_volatility_threshold * 2, 1e-6))), 4)

            if vol_val >= self.high_volatility_threshold:
                volatility = VolatilityLevel.HIGH
            elif vol_val <= self.low_volatility_threshold:
                volatility = VolatilityLevel.LOW
            else:
                volatility = VolatilityLevel.MEDIUM

            # 3. Momentum Classification
            mom_val = stats.market_speed * (1.0 if trend == TrendState.BULLISH else -1.0 if trend == TrendState.BEARISH else 0.0)
            mom_score = round(max(-1.0, min(1.0, mom_val * 10.0)), 4)

            if mom_score > 0.15:
                momentum = MomentumState.POSITIVE
            elif mom_score < -0.15:
                momentum = MomentumState.NEGATIVE
            else:
                momentum = MomentumState.NEUTRAL

            # 4. Regime Classification
            if volatility == VolatilityLevel.HIGH and trend in (TrendState.BULLISH, TrendState.BEARISH):
                regime = RegimeState.EXPANSION
            elif volatility == VolatilityLevel.LOW and trend == TrendState.SIDEWAYS:
                regime = RegimeState.COMPRESSION
            elif trend in (TrendState.BULLISH, TrendState.BEARISH):
                regime = RegimeState.TREND
            else:
                regime = RegimeState.RANGE

            # 5. Liquidity Classification
            t_rate = stats.average_tick_rate
            mean_sp = stats.mean_spread
            liq_score = round(max(0.0, min(1.0, (t_rate / max(self.high_tick_rate_threshold, 1.0)) * (1.0 / (1.0 + mean_sp)))), 4)

            if t_rate >= self.high_tick_rate_threshold:
                liquidity = LiquidityLevel.HIGH
            elif t_rate <= self.low_tick_rate_threshold:
                liquidity = LiquidityLevel.LOW
            else:
                liquidity = LiquidityLevel.MEDIUM

            ts_iso = stats.timestamp
            state_id, canon_hash = compute_market_state_id(
                symbol=sym,
                timestamp=ts_iso,
                trend=trend,
                volatility=volatility,
                momentum=momentum,
                regime=regime,
                liquidity=liquidity,
            )

            checksum = compute_canonical_sha256(
                {
                    "liquidity": liquidity.value,
                    "momentum": momentum.value,
                    "regime": regime.value,
                    "symbol": sym,
                    "trend": trend.value,
                    "volatility": volatility.value,
                }
            )

            market_state = MarketState(
                state_id=state_id,
                symbol=sym,
                timestamp=ts_iso,
                trend=trend,
                volatility=volatility,
                momentum=momentum,
                regime=regime,
                liquidity=liquidity,
                trend_score=trend_score,
                volatility_score=vol_score,
                momentum_score=mom_score,
                liquidity_score=liq_score,
                checksum=checksum,
                metadata={"classified_by": "MarketStateEngine"},
                canonical_hash=canon_hash,
            )

            if self.repository:
                self.repository.save_state(market_state)

            return market_state
