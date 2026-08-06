"""
Project GOAT v0.8 — Market Storage Buffer

In-memory sliding window tick ring-buffer and candle aggregator.
"""

from __future__ import annotations

from collections import deque
from typing import Sequence
from goat.marketdata.core.enums import MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick


class MarketDataBuffer:
    """Sliding-window buffer storing recent MarketTicks and MarketCandles in memory."""

    def __init__(self, max_ticks: int = 1000, max_candles: int = 500):
        self.max_ticks = max_ticks
        self.max_candles = max_candles
        self._ticks: dict[str, deque[MarketTick]] = {}
        self._candles: dict[str, deque[MarketCandle]] = {}

    def append_tick(self, tick: MarketTick) -> None:
        """Add a MarketTick to the sliding window for its symbol."""
        sym = tick.symbol.strip().upper()
        if sym not in self._ticks:
            self._ticks[sym] = deque(maxlen=self.max_ticks)
        self._ticks[sym].append(tick)

    def append_candle(self, candle: MarketCandle) -> None:
        """Add a MarketCandle to the sliding window for its symbol."""
        sym = candle.symbol.strip().upper()
        if sym not in self._candles:
            self._candles[sym] = deque(maxlen=self.max_candles)
        self._candles[sym].append(candle)

    def get_recent_ticks(self, symbol: str, limit: int = 100) -> list[MarketTick]:
        """Retrieve recent ticks for symbol ordered chronologically."""
        sym = symbol.strip().upper()
        if sym not in self._ticks:
            return []
        ticks_deque = self._ticks[sym]
        return list(ticks_deque)[-limit:]

    def get_recent_candles(self, symbol: str, limit: int = 100) -> list[MarketCandle]:
        """Retrieve recent candles for symbol ordered chronologically."""
        sym = symbol.strip().upper()
        if sym not in self._candles:
            return []
        candles_deque = self._candles[sym]
        return list(candles_deque)[-limit:]

    def clear(self, symbol: str | None = None) -> None:
        """Clear buffer data."""
        if symbol:
            sym = symbol.strip().upper()
            self._ticks.pop(sym, None)
            self._candles.pop(sym, None)
        else:
            self._ticks.clear()
            self._candles.clear()
