"""
Project GOAT v1.0 — Live Tick Normalization Engine

Normalizes raw broker WebSocket payloads (e.g. Deriv tick messages) into
canonical, immutable GOAT LiveTick objects. Enforces strict numerical and schema validation.
"""

from __future__ import annotations

import datetime
import math
from typing import Any, Dict
from pydantic import BaseModel, Field

from goat.market_data.models.symbol import get_symbol_config
from goat.market_data.models.tick import LiveTick, compute_live_tick_id
from goat.market_data.normalization.timestamp import compute_latency_ms, epoch_to_iso, now_utc_iso
from goat.research.edge.canonical import compute_canonical_sha256


class TickNormalizationResult(BaseModel):
    """Immutable result emitted by TickNormalizer."""

    success: bool = Field(..., description="True if payload was valid and normalized")
    tick: LiveTick | None = Field(default=None, description="Normalized LiveTick if successful")
    rejection_reason: str | None = Field(default=None, description="Explanation if rejected")
    raw_payload: dict[str, Any] = Field(default_factory=dict, description="Original input raw dictionary")

    class Config:
        frozen = True
        extra = "forbid"


class TickNormalizer:
    """Normalizes raw market data payloads into canonical LiveTick domain objects."""

    def __init__(self, connection_id: str = "DERIV_WS_01"):
        self.connection_id = connection_id

    def normalize(
        self,
        raw_payload: dict[str, Any],
        sequence_number: int = 0,
        arrival_time: datetime.datetime | None = None,
    ) -> TickNormalizationResult:
        """Parse, validate, and convert raw broker payload into canonical LiveTick."""

        if not isinstance(raw_payload, dict) or not raw_payload:
            return TickNormalizationResult(
                success=False,
                rejection_reason="REJECTED_MALFORMED_PAYLOAD: Payload must be a non-empty dictionary",
                raw_payload=raw_payload if isinstance(raw_payload, dict) else {"invalid": str(raw_payload)},
            )

        # Unnest tick payload if wrapped in Deriv msg_type format: {"msg_type": "tick", "tick": {...}}
        tick_dict = raw_payload.get("tick", raw_payload) if isinstance(raw_payload.get("tick"), dict) else raw_payload

        # 1. Resolve Symbol
        raw_symbol = str(tick_dict.get("symbol", tick_dict.get("underlying_symbol", ""))).strip()
        if not raw_symbol:
            return TickNormalizationResult(
                success=False,
                rejection_reason="REJECTED_MISSING_SYMBOL: Symbol field is missing or empty",
                raw_payload=raw_payload,
            )

        cfg = get_symbol_config(raw_symbol)
        canonical_symbol = cfg.symbol_id if cfg else raw_symbol.upper()
        pip_size = cfg.pip_size if cfg else int(tick_dict.get("pip_size", 2))

        # 2. Extract Prices (quote, bid, ask)
        bid: float | None = None
        ask: float | None = None
        price: float | None = None

        if "quote" in tick_dict or "price" in tick_dict:
            try:
                raw_q = tick_dict.get("quote", tick_dict.get("price"))
                price = float(raw_q)
                if math.isnan(price) or math.isinf(price):
                    return TickNormalizationResult(
                        success=False,
                        rejection_reason="REJECTED_INVALID_NUMERIC: Price/quote value cannot be NaN or Infinity",
                        raw_payload=raw_payload,
                    )
            except (ValueError, TypeError):
                return TickNormalizationResult(
                    success=False,
                    rejection_reason="REJECTED_INVALID_NUMERIC: Price/quote could not be converted to float",
                    raw_payload=raw_payload,
                )

        if "bid" in tick_dict and "ask" in tick_dict and tick_dict["bid"] is not None and tick_dict["ask"] is not None:
            try:
                bid = float(tick_dict["bid"])
                ask = float(tick_dict["ask"])
                if math.isnan(bid) or math.isnan(ask) or math.isinf(bid) or math.isinf(ask):
                    return TickNormalizationResult(
                        success=False,
                        rejection_reason="REJECTED_INVALID_NUMERIC: bid/ask values cannot be NaN or Infinity",
                        raw_payload=raw_payload,
                    )
            except (ValueError, TypeError):
                return TickNormalizationResult(
                    success=False,
                    rejection_reason="REJECTED_INVALID_NUMERIC: bid/ask values could not be converted to float",
                    raw_payload=raw_payload,
                )

        # Infer bid/ask if only quote is present
        if price is not None and (bid is None or ask is None):
            half_spread = round(0.5 * (10 ** (-pip_size)), 8) if pip_size > 0 else 0.01
            bid = round(price - half_spread, 8)
            ask = round(price + half_spread, 8)

        if price is None and bid is not None and ask is not None:
            price = round((bid + ask) / 2.0, 8)

        if price is None or bid is None or ask is None:
            return TickNormalizationResult(
                success=False,
                rejection_reason="REJECTED_MISSING_PRICES: Payload does not contain valid price/quote or bid/ask",
                raw_payload=raw_payload,
            )

        if price <= 0.0 or bid <= 0.0 or ask <= 0.0:
            return TickNormalizationResult(
                success=False,
                rejection_reason=f"REJECTED_NON_POSITIVE_PRICE: Prices must be positive floats (price={price}, bid={bid}, ask={ask})",
                raw_payload=raw_payload,
            )

        if ask < bid:
            return TickNormalizationResult(
                success=False,
                rejection_reason=f"REJECTED_NEGATIVE_SPREAD: Ask ({ask}) is less than Bid ({bid})",
                raw_payload=raw_payload,
            )

        spread = round(ask - bid, 8)

        # 3. Epoch & Timestamp
        epoch_raw = tick_dict.get("epoch", tick_dict.get("timestamp", tick_dict.get("time")))
        if epoch_raw is None:
            return TickNormalizationResult(
                success=False,
                rejection_reason="REJECTED_MISSING_EPOCH: Epoch timestamp field is missing",
                raw_payload=raw_payload,
            )

        try:
            epoch = int(epoch_raw)
        except (ValueError, TypeError):
            return TickNormalizationResult(
                success=False,
                rejection_reason=f"REJECTED_INVALID_EPOCH: Epoch timestamp value ({epoch_raw}) invalid",
                raw_payload=raw_payload,
            )

        arrival_iso = now_utc_iso() if arrival_time is None else arrival_time.astimezone(datetime.timezone.utc).isoformat()
        latency_ms = compute_latency_ms(epoch=epoch, arrival_time=arrival_time)

        # 4. Canonical Hashing & Deterministic ID
        tick_id, canonical_hash = compute_live_tick_id(
            symbol=canonical_symbol,
            price=price,
            bid=bid,
            ask=ask,
            epoch_timestamp=epoch,
            sequence_number=sequence_number,
        )

        checksum = compute_canonical_sha256(
            {
                "ask": ask,
                "bid": bid,
                "epoch": epoch,
                "price": price,
                "sequence_number": sequence_number,
                "symbol": canonical_symbol,
            }
        )

        tick = LiveTick(
            tick_id=tick_id,
            symbol=canonical_symbol,
            price=price,
            bid=bid,
            ask=ask,
            spread=spread,
            epoch_timestamp=epoch,
            arrival_timestamp=arrival_iso,
            sequence_number=sequence_number,
            connection_id=self.connection_id,
            latency_ms=latency_ms,
            checksum=checksum,
            metadata={
                "deriv_symbol": raw_symbol,
                "pip_size": pip_size,
                "raw_keys": sorted(list(raw_payload.keys())),
            },
            canonical_hash=canonical_hash,
        )

        return TickNormalizationResult(success=True, tick=tick, raw_payload=raw_payload)
