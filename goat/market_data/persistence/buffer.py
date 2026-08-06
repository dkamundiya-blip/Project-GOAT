"""
Project GOAT v1.0 — Live Tick In-Memory Buffer

High-performance sliding-window ring buffer for LiveTick objects and quote metric calculation.
"""

from __future__ import annotations

import datetime
from collections import deque
from goat.market_data.models.quote import LiveQuote
from goat.market_data.models.symbol import SUPPORTED_SYMBOLS
from goat.market_data.models.tick import LiveTick


class LiveTickBuffer:
    """In-memory sliding window tick buffer per symbol."""

    def __init__(self, max_ticks_per_symbol: int = 2000):
        self.max_ticks_per_symbol = max_ticks_per_symbol
        self._ticks: dict[str, deque[LiveTick]] = {}
        self._total_ticks_received = 0
        self._start_time = datetime.datetime.now(datetime.timezone.utc)

    def append_tick(self, tick: LiveTick) -> None:
        """Append a normalized LiveTick to symbol queue."""
        sym = tick.symbol.strip().upper()
        if sym not in self._ticks:
            self._ticks[sym] = deque(maxlen=self.max_ticks_per_symbol)
        self._ticks[sym].append(tick)
        self._total_ticks_received += 1

    def get_latest_tick(self, symbol: str) -> LiveTick | None:
        """Get the most recent LiveTick for a symbol."""
        sym = symbol.strip().upper()
        if sym in self._ticks and len(self._ticks[sym]) > 0:
            return self._ticks[sym][-1]
        return None

    def get_recent_ticks(self, symbol: str, limit: int = 100) -> list[LiveTick]:
        """Get recent ticks for a symbol ordered chronologically."""
        sym = symbol.strip().upper()
        if sym not in self._ticks:
            return []
        return list(self._ticks[sym])[-limit:]

    def get_tick_frequency(self, symbol: str, window_seconds: float = 10.0) -> float:
        """Calculate recent tick frequency (ticks per second) over time window."""
        sym = symbol.strip().upper()
        if sym not in self._ticks or len(self._ticks[sym]) == 0:
            return 0.0

        now = datetime.datetime.now(datetime.timezone.utc)
        recent_count = 0
        for tick in reversed(self._ticks[sym]):
            try:
                arr_dt = datetime.datetime.fromisoformat(tick.arrival_timestamp)
                if arr_dt.tzinfo is None:
                    arr_dt = arr_dt.replace(tzinfo=datetime.timezone.utc)
                if (now - arr_dt).total_seconds() <= window_seconds:
                    recent_count += 1
                else:
                    break
            except Exception:
                continue

        return round(recent_count / window_seconds, 2)

    def get_live_quote(self, symbol: str, connection_status: str = "CONNECTED") -> LiveQuote:
        """Generate a LiveQuote snapshot for a symbol."""
        sym = symbol.strip().upper()
        latest = self.get_latest_tick(sym)

        deriv_ws_sym = sym
        if sym in SUPPORTED_SYMBOLS:
            deriv_ws_sym = SUPPORTED_SYMBOLS[sym].deriv_ws_symbol

        if latest is None:
            return LiveQuote(
                symbol=sym,
                deriv_ws_symbol=deriv_ws_sym,
                connection_status=connection_status,
                streaming_status="IDLE",
            )

        freq = self.get_tick_frequency(sym)
        count = len(self._ticks.get(sym, []))

        return LiveQuote(
            symbol=sym,
            deriv_ws_symbol=deriv_ws_sym,
            live_price=latest.price,
            bid=latest.bid,
            ask=latest.ask,
            spread=latest.spread,
            connection_status=connection_status,
            latency_ms=latest.latency_ms,
            tick_frequency=freq,
            streaming_status="STREAMING" if connection_status == "CONNECTED" else "PAUSED",
            last_tick_time=latest.arrival_timestamp,
            total_ticks=count,
        )

    def get_all_quotes(self, connection_status: str = "CONNECTED") -> list[LiveQuote]:
        """Generate LiveQuote snapshots for all supported symbols."""
        quotes = []
        for sym_id in SUPPORTED_SYMBOLS.keys():
            quotes.append(self.get_live_quote(sym_id, connection_status=connection_status))
        return quotes

    @property
    def total_ticks_received(self) -> int:
        """Total count of ingested ticks across all symbols."""
        return self._total_ticks_received

    def clear(self) -> None:
        """Clear all buffer memory."""
        self._ticks.clear()
        self._total_ticks_received = 0
