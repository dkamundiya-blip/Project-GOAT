"""
Project GOAT Phase 5 — Session Intelligence Engine (`goat.feature_engineering.session`)

Engineers 9 quantitative session features:
Current Session, Time Until Session Close, Time Since Session Open, Session Volatility,
Session Momentum, Session Trend, Overlap Detection, Day Of Week, and Hour Of Day.
"""

from __future__ import annotations

import datetime
import math
import threading

from goat.market_intelligence.models.candle import IntelligenceCandle


class SessionIntelligenceEngine:
    """Quantitative Session Intelligence Engine calculating UTC session metrics and window overlaps."""

    def __init__(self):
        # Tracking session open prices per symbol: symbol -> (session_code, open_price, open_timestamp)
        self._session_open_states: dict[str, tuple[float, float, float]] = {}
        self._session_prices: dict[str, list[float]] = {}
        self._lock = threading.RLock()

    def compute_features(self, candle: IntelligenceCandle) -> dict[str, float]:
        """Compute 9 quantitative session features."""
        sym = candle.symbol.upper()
        c_price = candle.close

        try:
            ts_dt = datetime.datetime.fromisoformat(candle.open_timestamp.replace("Z", "+00:00"))
        except Exception:
            ts_dt = datetime.datetime.now(datetime.timezone.utc)

        hour = ts_dt.hour
        day_of_week = float(ts_dt.weekday())

        # Determine current market session & overlap
        # Asian: 00:00 - 09:00 UTC
        # London: 07:00 - 16:00 UTC
        # New York: 13:00 - 22:00 UTC
        is_asian = (0 <= hour < 9)
        is_london = (7 <= hour < 16)
        is_ny = (13 <= hour < 22)

        is_overlap = (7 <= hour < 9) or (13 <= hour < 16)
        overlap_flag = 1.0 if is_overlap else 0.0

        if is_overlap:
            session_code = 4.0  # OVERLAP
        elif is_ny:
            session_code = 3.0  # NEW_YORK
        elif is_london:
            session_code = 2.0  # LONDON
        else:
            session_code = 1.0  # ASIAN

        # Calculate time since open & until close (seconds)
        if session_code == 4.0 and (13 <= hour < 16):
            s_open_hour, s_close_hour = 13, 16
        elif session_code == 4.0 and (7 <= hour < 9):
            s_open_hour, s_close_hour = 7, 9
        elif session_code == 3.0:
            s_open_hour, s_close_hour = 13, 22
        elif session_code == 2.0:
            s_open_hour, s_close_hour = 7, 16
        else:
            s_open_hour, s_close_hour = 0, 9

        cur_sec = ts_dt.minute * 60 + ts_dt.second
        time_since_open = (hour - s_open_hour) * 3600 + cur_sec
        time_until_close = max(0, (s_close_hour - hour) * 3600 - cur_sec)

        with self._lock:
            if sym not in self._session_open_states or self._session_open_states[sym][0] != session_code:
                self._session_open_states[sym] = (session_code, c_price, ts_dt.timestamp())
                self._session_prices[sym] = [c_price]
            else:
                self._session_prices[sym].append(c_price)

            s_open_price = self._session_open_states[sym][1]
            s_prices = self._session_prices[sym]

            # Session Momentum & Trend
            session_mom = (c_price - s_open_price) / max(s_open_price, 1e-6)
            session_trend = round(max(-1.0, min(1.0, session_mom * 100.0)), 4)

            # Session Volatility
            if len(s_prices) > 1:
                s_mean = sum(s_prices) / len(s_prices)
                session_vol = math.sqrt(sum((p - s_mean) ** 2 for p in s_prices) / len(s_prices)) / max(s_mean, 1e-6)
            else:
                session_vol = 0.0

            return {
                "current_session": session_code,
                "time_until_session_close": float(time_until_close),
                "time_since_session_open": float(time_since_open),
                "session_volatility": round(session_vol, 6),
                "session_momentum": round(session_mom, 6),
                "session_trend": session_trend,
                "overlap_detection": overlap_flag,
                "day_of_week": day_of_week,
                "hour_of_day": float(hour),
            }
