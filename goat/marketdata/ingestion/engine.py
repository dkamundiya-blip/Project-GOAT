"""
Project GOAT v0.8 — Market Ingestion Engine

Receives raw broker payloads (Deriv WebSocket tick format, generic JSON dicts),
validates structure, normalizes values, rejects malformed payloads,
assigns deterministic IDs (MTK_, MCD_), and forwards validated data objects.
"""

from __future__ import annotations

import datetime
import math
from typing import Any
from pydantic import BaseModel, Field

from goat.marketdata.core.canonical import compute_candle_id, compute_tick_id
from goat.marketdata.core.enums import MarketTimeframe
from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.research.edge.canonical import compute_canonical_sha256


class IngestionResult(BaseModel):
    """Immutable result emitted by MarketIngestionEngine upon processing a payload."""

    success: bool = Field(..., description="True if payload was valid and normalized")
    tick: MarketTick | None = Field(default=None, description="Normalized MarketTick if tick payload")
    candle: MarketCandle | None = Field(default=None, description="Normalized MarketCandle if candle payload")
    rejection_reason: str | None = Field(default=None, description="Explanation if payload was rejected")
    raw_payload: dict[str, Any] = Field(default_factory=dict, description="Original input raw payload dictionary")

    class Config:
        frozen = True
        extra = "forbid"


class MarketIngestionEngine:
    """Engine responsible for receiving, parsing, validating structure, and normalizing broker market payloads."""

    def __init__(self, default_broker: str = "DERIV"):
        self.default_broker = default_broker.strip().upper()

    def process_raw_tick(
        self,
        raw_data: dict[str, Any],
        sequence_number: int = 0,
        source_latency: float = 0.0,
    ) -> IngestionResult:
        """Parse and normalize a raw tick payload from broker streams (e.g. Deriv WS API or generic schema)."""

        if not isinstance(raw_data, dict) or not raw_data:
            return IngestionResult(
                success=False,
                rejection_reason="REJECTED_MALFORMED_PAYLOAD: Payload must be a non-empty dictionary",
                raw_payload=raw_data if isinstance(raw_data, dict) else {"invalid": str(raw_data)},
            )

        # Handle Deriv WebSocket tick schema: {"tick": {"symbol": "R_100", "quote": 1234.56, "epoch": 1690000000, "pip_size": 2, ...}}
        tick_dict = raw_data.get("tick", raw_data) if isinstance(raw_data.get("tick"), dict) else raw_data

        symbol = str(tick_dict.get("symbol", tick_dict.get("instrument", ""))).strip().upper()
        if not symbol:
            return IngestionResult(
                success=False,
                rejection_reason="REJECTED_MISSING_SYMBOL: Symbol field is missing or empty",
                raw_payload=raw_data,
            )

        # Derive Bid / Ask / Quote
        bid: float | None = None
        ask: float | None = None

        if "bid" in tick_dict and "ask" in tick_dict:
            try:
                bid = float(tick_dict["bid"])
                ask = float(tick_dict["ask"])
                if math.isnan(bid) or math.isnan(ask) or math.isinf(bid) or math.isinf(ask):
                    return IngestionResult(
                        success=False,
                        rejection_reason="REJECTED_INVALID_NUMERIC: bid/ask values cannot be NaN or Infinity",
                        raw_payload=raw_data,
                    )
            except (ValueError, TypeError):
                return IngestionResult(
                    success=False,
                    rejection_reason="REJECTED_INVALID_NUMERIC: bid/ask values could not be converted to float",
                    raw_payload=raw_data,
                )
        elif "quote" in tick_dict:
            try:
                quote = float(tick_dict["quote"])
                pip_size = int(tick_dict.get("pip_size", 2))
                half_spread = round(0.5 * (10 ** (-pip_size)), 8) if pip_size > 0 else 0.01
                bid = round(quote - half_spread, 8)
                ask = round(quote + half_spread, 8)
            except (ValueError, TypeError):
                return IngestionResult(
                    success=False,
                    rejection_reason="REJECTED_INVALID_QUOTE: quote value could not be converted to float",
                    raw_payload=raw_data,
                )

        if bid is None or ask is None:
            return IngestionResult(
                success=False,
                rejection_reason="REJECTED_MISSING_PRICES: Payload does not contain valid bid/ask or quote fields",
                raw_payload=raw_data,
            )

        if bid <= 0.0 or ask <= 0.0:
            return IngestionResult(
                success=False,
                rejection_reason=f"REJECTED_NON_POSITIVE_PRICE: Bid ({bid}) and Ask ({ask}) must be positive floats",
                raw_payload=raw_data,
            )

        if ask < bid:
            return IngestionResult(
                success=False,
                rejection_reason=f"REJECTED_NEGATIVE_SPREAD: Ask ({ask}) is less than Bid ({bid})",
                raw_payload=raw_data,
            )

        spread = round(ask - bid, 8)

        # Process Timestamp
        raw_timestamp = tick_dict.get("timestamp", tick_dict.get("epoch", tick_dict.get("time")))
        timestamp_str: str

        if isinstance(raw_timestamp, (int, float)):
            dt = datetime.datetime.fromtimestamp(float(raw_timestamp), tz=datetime.timezone.utc)
            timestamp_str = dt.isoformat()
        elif isinstance(raw_timestamp, str) and raw_timestamp.strip():
            timestamp_str = raw_timestamp.strip()
        else:
            dt = datetime.datetime.now(datetime.timezone.utc)
            timestamp_str = dt.isoformat()

        broker = str(tick_dict.get("broker", self.default_broker)).strip().upper()

        # Compute Deterministic ID and Checksum
        tick_id, canonical_hash = compute_tick_id(
            symbol=symbol,
            broker=broker,
            bid=bid,
            ask=ask,
            timestamp=timestamp_str,
            sequence_number=sequence_number,
        )

        checksum = compute_canonical_sha256(
            {
                "ask": ask,
                "bid": bid,
                "broker": broker,
                "sequence_number": sequence_number,
                "symbol": symbol,
                "timestamp": timestamp_str,
            }
        )

        tick = MarketTick(
            tick_id=tick_id,
            symbol=symbol,
            broker=broker,
            bid=bid,
            ask=ask,
            spread=spread,
            timestamp=timestamp_str,
            sequence_number=sequence_number,
            source_latency=float(source_latency),
            checksum=checksum,
            metadata={"raw_keys": sorted(list(raw_data.keys()))},
            canonical_hash=canonical_hash,
        )

        return IngestionResult(success=True, tick=tick, raw_payload=raw_data)

    def process_raw_candle(
        self,
        raw_data: dict[str, Any],
    ) -> IngestionResult:
        """Parse and normalize a raw candle payload."""

        if not isinstance(raw_data, dict) or not raw_data:
            return IngestionResult(
                success=False,
                rejection_reason="REJECTED_MALFORMED_PAYLOAD: Candle payload must be a non-empty dictionary",
                raw_payload=raw_data if isinstance(raw_data, dict) else {"invalid": str(raw_data)},
            )

        candle_dict = raw_data.get("ohlc", raw_data) if isinstance(raw_data.get("ohlc"), dict) else raw_data

        symbol = str(candle_dict.get("symbol", candle_dict.get("instrument", ""))).strip().upper()
        if not symbol:
            return IngestionResult(
                success=False,
                rejection_reason="REJECTED_MISSING_SYMBOL: Candle symbol field is missing or empty",
                raw_payload=raw_data,
            )

        try:
            open_price = float(candle_dict["open"])
            high_price = float(candle_dict["high"])
            low_price = float(candle_dict["low"])
            close_price = float(candle_dict["close"])
        except (KeyError, ValueError, TypeError) as e:
            return IngestionResult(
                success=False,
                rejection_reason=f"REJECTED_INVALID_OHLC: Missing or non-numeric OHLC value ({e})",
                raw_payload=raw_data,
            )

        if min(open_price, high_price, low_price, close_price) <= 0.0:
            return IngestionResult(
                success=False,
                rejection_reason="REJECTED_NON_POSITIVE_PRICE: OHLC prices must be strictly positive",
                raw_payload=raw_data,
            )

        if high_price < max(open_price, close_price) or low_price > min(open_price, close_price):
            return IngestionResult(
                success=False,
                rejection_reason=f"REJECTED_INVALID_BOUNDS: High ({high_price}) or Low ({low_price}) violate OHLC bounds",
                raw_payload=raw_data,
            )

        raw_tf = str(candle_dict.get("timeframe", candle_dict.get("granularity", "1M"))).strip().upper()
        tf_mapping = {"60": "1M", "300": "5M", "900": "15M", "3600": "1H", "86400": "1D"}
        timeframe_str = tf_mapping.get(raw_tf, raw_tf)

        try:
            timeframe = MarketTimeframe(timeframe_str)
        except ValueError:
            timeframe = MarketTimeframe.M1

        raw_open_ts = candle_dict.get("open_timestamp", candle_dict.get("epoch", candle_dict.get("open_time")))
        raw_close_ts = candle_dict.get("close_timestamp", candle_dict.get("close_time"))

        def _fmt_ts(val: Any) -> str:
            if isinstance(val, (int, float)):
                return datetime.datetime.fromtimestamp(float(val), tz=datetime.timezone.utc).isoformat()
            if isinstance(val, str) and val.strip():
                return val.strip()
            return datetime.datetime.now(datetime.timezone.utc).isoformat()

        open_timestamp = _fmt_ts(raw_open_ts)
        close_timestamp = _fmt_ts(raw_close_ts) if raw_close_ts else open_timestamp

        volume = float(candle_dict.get("volume", candle_dict.get("tick_count", 0.0)))
        completed = bool(candle_dict.get("completed", True))

        candle_id, canonical_hash = compute_candle_id(
            symbol=symbol,
            timeframe=timeframe.value,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            open_timestamp=open_timestamp,
            close_timestamp=close_timestamp,
        )

        checksum = compute_canonical_sha256(
            {
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "open": open_price,
                "symbol": symbol,
                "timeframe": timeframe.value,
            }
        )

        candle = MarketCandle(
            candle_id=candle_id,
            symbol=symbol,
            timeframe=timeframe,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
            open_timestamp=open_timestamp,
            close_timestamp=close_timestamp,
            completed=completed,
            checksum=checksum,
            metadata={"raw_keys": sorted(list(raw_data.keys()))},
            canonical_hash=canonical_hash,
        )

        return IngestionResult(success=True, candle=candle, raw_payload=raw_data)
