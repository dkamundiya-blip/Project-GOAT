"""
Project GOAT Phase 4 — Tick Recorder (`goat.market_intelligence.recorder`)

Records, normalizes, enriches, and persists every incoming raw websocket market price tick.
"""

from __future__ import annotations

import datetime
import math
import threading
from typing import Any

from goat.market_intelligence.models.tick import RecordedTick, compute_recorded_tick_id
from goat.market_intelligence.persistence.interfaces import ITickRepository
from goat.research.edge.canonical import compute_canonical_sha256


class TickRecorder:
    """Thread-safe, high-throughput Tick Recorder for recording websocket ticks."""

    def __init__(
        self,
        repository: ITickRepository,
        default_source: str = "WEBSOCKET",
    ):
        self.repository = repository
        self.default_source = default_source
        self._sequence_counters: dict[str, int] = {}
        self._lock = threading.RLock()

    def record_raw_tick(self, raw_payload: dict[str, Any], arrival_latency_ms: float = 0.0) -> RecordedTick:
        """Parse raw broker payload dictionary into canonical RecordedTick and persist."""
        tick_dict = raw_payload.get("tick", raw_payload) if isinstance(raw_payload.get("tick"), dict) else raw_payload

        raw_sym = str(tick_dict.get("symbol", tick_dict.get("underlying_symbol", "UNKNOWN"))).strip()
        symbol = self._normalize_symbol(raw_sym)

        with self._lock:
            seq = self._sequence_counters.get(symbol, 0) + 1
            self._sequence_counters[symbol] = seq

        # Price extraction
        price: float | None = None
        bid: float | None = None
        ask: float | None = None

        if "quote" in tick_dict or "price" in tick_dict:
            try:
                price = float(tick_dict.get("quote", tick_dict.get("price")))
            except (ValueError, TypeError):
                price = None

        if "bid" in tick_dict and "ask" in tick_dict and tick_dict["bid"] is not None and tick_dict["ask"] is not None:
            try:
                bid = float(tick_dict["bid"])
                ask = float(tick_dict["ask"])
            except (ValueError, TypeError):
                bid = None
                ask = None

        # Infer mid, bid, ask if partial
        if price is not None and (bid is None or ask is None):
            half_spread = 0.005
            bid = round(price - half_spread, 8)
            ask = round(price + half_spread, 8)

        if price is None and bid is not None and ask is not None:
            price = round((bid + ask) / 2.0, 8)

        if price is None:
            price = 1.0
        if bid is None:
            bid = price - 0.005
        if ask is None:
            ask = price + 0.005

        mid_price = round((bid + ask) / 2.0, 8)
        spread = round(ask - bid, 8)

        # Timestamp
        epoch_raw = tick_dict.get("epoch", tick_dict.get("timestamp", tick_dict.get("time")))
        if epoch_raw is not None:
            if isinstance(epoch_raw, (int, float)):
                ts_iso = datetime.datetime.fromtimestamp(int(epoch_raw), tz=datetime.timezone.utc).isoformat()
            elif isinstance(epoch_raw, str):
                try:
                    epoch_sec = int(epoch_raw)
                    ts_iso = datetime.datetime.fromtimestamp(epoch_sec, tz=datetime.timezone.utc).isoformat()
                except ValueError:
                    try:
                        dt = datetime.datetime.fromisoformat(epoch_raw.replace("Z", "+00:00"))
                        ts_iso = dt.isoformat()
                    except Exception:
                        ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            else:
                ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        else:
            ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        source = str(raw_payload.get("source", tick_dict.get("source", self.default_source))).strip().upper()

        tick_id, canon_hash = compute_recorded_tick_id(
            symbol=symbol,
            bid=bid,
            ask=ask,
            mid_price=mid_price,
            timestamp=ts_iso,
            sequence_number=seq,
            source=source,
        )

        checksum = compute_canonical_sha256(
            {
                "ask": ask,
                "bid": bid,
                "mid_price": mid_price,
                "sequence_number": seq,
                "symbol": symbol,
            }
        )

        tick = RecordedTick(
            tick_id=tick_id,
            symbol=symbol,
            timestamp=ts_iso,
            bid=bid,
            ask=ask,
            mid_price=mid_price,
            spread=spread,
            latency_ms=round(float(arrival_latency_ms), 2),
            sequence_number=seq,
            source=source,
            checksum=checksum,
            metadata={"raw_keys": sorted(list(raw_payload.keys()))},
            canonical_hash=canon_hash,
        )

        self.repository.save_tick(tick)
        return tick

    def record_tick(self, tick: RecordedTick) -> RecordedTick:
        """Persist a pre-constructed RecordedTick object."""
        self.repository.save_tick(tick)
        return tick

    @staticmethod
    def _normalize_symbol(sym: string) -> str:
        s = sym.strip().upper()
        mapping = {
            "R_10": "VOLATILITY_10",
            "R_25": "VOLATILITY_25",
            "R_50": "VOLATILITY_50",
            "R_75": "VOLATILITY_75",
            "R_100": "VOLATILITY_100",
            "BOOM1000": "BOOM_1000",
            "BOOM500": "BOOM_500",
            "CRASH1000": "CRASH_1000",
            "CRASH500": "CRASH_500",
            "STPRNG": "STEP_INDEX",
            "STEP": "STEP_INDEX",
        }
        return mapping.get(s, s)
