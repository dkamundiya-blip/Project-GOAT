"""
Project GOAT Phase 5 — Market Structure Feature Engine (`goat.feature_engineering.structure`)

Engineers 10 quantitative market structure features:
Swing Highs, Swing Lows, Higher Highs, Higher Lows, Lower Highs, Lower Lows,
Break Of Structure (BOS), Change Of Character (CHoCH), Structure Strength, and Trend Transition Probability.
"""

from __future__ import annotations

from collections import deque
import threading

from goat.market_intelligence.models.candle import IntelligenceCandle


class MarketStructureFeatureEngine:
    """Quantitative Market Structure Feature Engine tracking swings, BOS, CHoCH, and transition probabilities."""

    def __init__(self, pivot_left: int = 2, pivot_right: int = 2):
        self.pivot_left = pivot_left
        self.pivot_right = pivot_right

        self._candle_history: dict[tuple[str, str], deque[IntelligenceCandle]] = {}
        self._swing_highs: dict[tuple[str, str], list[float]] = {}
        self._swing_lows: dict[tuple[str, str], list[float]] = {}
        self._last_trend: dict[tuple[str, str], str] = {}  # "UPTREND", "DOWNTREND", "NEUTRAL"
        self._lock = threading.RLock()

    def compute_features(self, candle: IntelligenceCandle) -> dict[str, float]:
        """Compute 10 quantitative market structure features."""
        key = (candle.symbol.upper(), candle.timeframe.value.lower())

        with self._lock:
            if key not in self._candle_history:
                self._candle_history[key] = deque(maxlen=50)
                self._swing_highs[key] = [candle.high]
                self._swing_lows[key] = [candle.low]
                self._last_trend[key] = "NEUTRAL"

            history = self._candle_history[key]
            history.append(candle)
            n = len(history)

            swings_h = self._swing_highs[key]
            swings_l = self._swing_lows[key]

            # Detect Pivot Swings if enough history
            if n >= self.pivot_left + self.pivot_right + 1:
                mid_idx = n - 1 - self.pivot_right
                mid_c = history[mid_idx]

                is_pivot_high = all(mid_c.high >= history[i].high for i in range(mid_idx - self.pivot_left, mid_idx + self.pivot_right + 1) if i != mid_idx)
                is_pivot_low = all(mid_c.low <= history[i].low for i in range(mid_idx - self.pivot_left, mid_idx + self.pivot_right + 1) if i != mid_idx)

                if is_pivot_high:
                    if not swings_h or mid_c.high != swings_h[-1]:
                        swings_h.append(mid_c.high)
                        if len(swings_h) > 20:
                            swings_h.pop(0)

                if is_pivot_low:
                    if not swings_l or mid_c.low != swings_l[-1]:
                        swings_l.append(mid_c.low)
                        if len(swings_l) > 20:
                            swings_l.pop(0)

            latest_sh = swings_h[-1] if swings_h else candle.high
            prev_sh = swings_h[-2] if len(swings_h) > 1 else latest_sh

            latest_sl = swings_l[-1] if swings_l else candle.low
            prev_sl = swings_l[-2] if len(swings_l) > 1 else latest_sl

            higher_high = 1.0 if latest_sh > prev_sh else 0.0
            higher_low = 1.0 if latest_sl > prev_sl else 0.0
            lower_high = 1.0 if latest_sh < prev_sh else 0.0
            lower_low = 1.0 if latest_sl < prev_sl else 0.0

            # 2. BOS & CHoCH Detection
            bos = 0.0
            choch = 0.0
            structure_strength = 0.0
            current_trend = self._last_trend[key]

            if candle.close > latest_sh:
                if current_trend == "UPTREND":
                    bos = 1.0  # Bullish BOS
                elif current_trend == "DOWNTREND":
                    choch = 1.0  # Bullish CHoCH
                    self._last_trend[key] = "UPTREND"
                else:
                    self._last_trend[key] = "UPTREND"
                structure_strength = (candle.close - latest_sh) / max(latest_sh, 1e-6)

            elif candle.close < latest_sl:
                if current_trend == "DOWNTREND":
                    bos = -1.0  # Bearish BOS
                elif current_trend == "UPTREND":
                    choch = -1.0  # Bearish CHoCH
                    self._last_trend[key] = "DOWNTREND"
                else:
                    self._last_trend[key] = "DOWNTREND"
                structure_strength = (latest_sl - candle.close) / max(latest_sl, 1e-6)

            # 3. Trend Transition Probability
            # Higher probability when CHoCH occurs or multiple counter-swings develop
            if choch != 0.0:
                transition_prob = 0.85
            elif lower_high == 1.0 and lower_low == 1.0 and current_trend == "UPTREND":
                transition_prob = 0.70
            elif higher_high == 1.0 and higher_low == 1.0 and current_trend == "DOWNTREND":
                transition_prob = 0.70
            else:
                transition_prob = 0.15

            return {
                "swing_high": round(latest_sh, 8),
                "swing_low": round(latest_sl, 8),
                "higher_high": higher_high,
                "higher_low": higher_low,
                "lower_high": lower_high,
                "lower_low": lower_low,
                "bos": bos,
                "choch": choch,
                "structure_strength": round(structure_strength, 6),
                "trend_transition_prob": round(transition_prob, 4),
            }
