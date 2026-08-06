"""
Project GOAT v0.8 — Market Validation Engine

Executes deterministic checks on market ticks and candles:
- Timestamp ordering
- Sequence number continuity & duplicate detection
- Price bounds & spread validity
- Checksum integrity
- Rejection logging with deterministic explanations
"""

from __future__ import annotations

import datetime
from typing import Any
from pydantic import BaseModel, Field

from goat.marketdata.core.models import MarketCandle, MarketTick
from goat.research.edge.canonical import compute_canonical_sha256


class ValidationResult(BaseModel):
    """Immutable result emitted by MarketValidationEngine upon evaluating a tick or candle."""

    is_valid: bool = Field(..., description="True if tick/candle passes all deterministic validation rules")
    rejection_reason: str | None = Field(default=None, description="Deterministic rejection explanation if invalid")
    rule_breached: str | None = Field(default=None, description="Name of the specific validation rule breached")
    details: dict[str, Any] = Field(default_factory=dict, description="Diagnostic details dictionary")

    class Config:
        frozen = True
        extra = "forbid"


class MarketValidationEngine:
    """Engine executing rigorous validation rules on market data streams."""

    def __init__(self, max_allowed_spread: float = 100.0, max_future_skew_seconds: float = 300.0):
        self.max_allowed_spread = float(max_allowed_spread)
        self.max_future_skew_seconds = float(max_future_skew_seconds)
        self._last_sequence: dict[str, int] = {}
        self._last_timestamp: dict[str, datetime.datetime] = {}
        self._seen_sequence_numbers: dict[str, set[int]] = {}

    def reset_state(self, symbol: str | None = None) -> None:
        """Reset sequence/timestamp memory state for symbol or all symbols."""
        if symbol:
            sym = symbol.strip().upper()
            self._last_sequence.pop(sym, None)
            self._last_timestamp.pop(sym, None)
            self._seen_sequence_numbers.pop(sym, None)
        else:
            self._last_sequence.clear()
            self._last_timestamp.clear()
            self._seen_sequence_numbers.clear()

    def validate_tick(self, tick: MarketTick) -> ValidationResult:
        """Execute deterministic validation checks on a MarketTick model."""

        sym = tick.symbol.strip().upper()

        # 1. Non-positive price check
        if tick.bid <= 0.0 or tick.ask <= 0.0:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_NON_POSITIVE_PRICES: Bid ({tick.bid}) and Ask ({tick.ask}) must be > 0",
                rule_breached="NON_POSITIVE_PRICE",
                details={"bid": tick.bid, "ask": tick.ask, "symbol": sym},
            )

        # 2. Ask < Bid check
        if tick.ask < tick.bid:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_NEGATIVE_SPREAD: Ask ({tick.ask}) is less than Bid ({tick.bid})",
                rule_breached="NEGATIVE_SPREAD",
                details={"bid": tick.bid, "ask": tick.ask, "spread": tick.spread, "symbol": sym},
            )

        # 3. Excessive spread check
        if tick.spread > self.max_allowed_spread:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_EXCESSIVE_SPREAD: Spread ({tick.spread}) exceeds max threshold ({self.max_allowed_spread})",
                rule_breached="EXCESSIVE_SPREAD",
                details={"spread": tick.spread, "max_allowed": self.max_allowed_spread, "symbol": sym},
            )

        # 4. Timestamp format & skew check
        try:
            ts_dt = datetime.datetime.fromisoformat(tick.timestamp)
            if ts_dt.tzinfo is None:
                ts_dt = ts_dt.replace(tzinfo=datetime.timezone.utc)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_MALFORMED_TIMESTAMP: Failed to parse timestamp '{tick.timestamp}' ({e})",
                rule_breached="MALFORMED_TIMESTAMP",
                details={"timestamp": tick.timestamp, "symbol": sym},
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        if (ts_dt - now).total_seconds() > self.max_future_skew_seconds:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_FUTURE_TIMESTAMP: Timestamp ({tick.timestamp}) is skewed into the future",
                rule_breached="FUTURE_TIMESTAMP_SKEW",
                details={"timestamp": tick.timestamp, "max_future_skew": self.max_future_skew_seconds, "symbol": sym},
            )

        # 5. Timestamp order check
        if sym in self._last_timestamp:
            last_ts = self._last_timestamp[sym]
            if ts_dt < last_ts:
                return ValidationResult(
                    is_valid=False,
                    rejection_reason=f"REJECTED_OUT_OF_ORDER_TIMESTAMP: Tick timestamp ({ts_dt}) is older than last seen ({last_ts})",
                    rule_breached="TIMESTAMP_OUT_OF_ORDER",
                    details={"current_timestamp": ts_dt.isoformat(), "last_timestamp": last_ts.isoformat(), "symbol": sym},
                )

        # 6. Duplicate & Sequence check
        seen_set = self._seen_sequence_numbers.setdefault(sym, set())
        if tick.sequence_number in seen_set:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_DUPLICATE_SEQUENCE: Sequence number ({tick.sequence_number}) already processed",
                rule_breached="DUPLICATE_SEQUENCE_NUMBER",
                details={"sequence_number": tick.sequence_number, "symbol": sym},
            )

        # 7. Checksum Verification
        expected_checksum = compute_canonical_sha256(
            {
                "ask": tick.ask,
                "bid": tick.bid,
                "broker": tick.broker,
                "sequence_number": tick.sequence_number,
                "symbol": tick.symbol,
                "timestamp": tick.timestamp,
            }
        )
        if tick.checksum and tick.checksum != expected_checksum:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_CHECKSUM_MISMATCH: Provided checksum ({tick.checksum}) does not match expected ({expected_checksum})",
                rule_breached="CHECKSUM_MISMATCH",
                details={"provided_checksum": tick.checksum, "expected_checksum": expected_checksum},
            )

        # Record state updates
        self._last_sequence[sym] = tick.sequence_number
        self._last_timestamp[sym] = ts_dt
        seen_set.add(tick.sequence_number)

        return ValidationResult(is_valid=True, details={"symbol": sym, "sequence_number": tick.sequence_number})

    def validate_candle(self, candle: MarketCandle) -> ValidationResult:
        """Execute deterministic validation checks on a MarketCandle model."""

        sym = candle.symbol.strip().upper()

        if min(candle.open, candle.high, candle.low, candle.close) <= 0.0:
            return ValidationResult(
                is_valid=False,
                rejection_reason="REJECTED_NON_POSITIVE_CANDLE_PRICES: Open, High, Low, Close must be > 0",
                rule_breached="NON_POSITIVE_PRICE",
                details={"open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close},
            )

        if candle.high < max(candle.open, candle.close):
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_INVALID_HIGH_BOUND: High ({candle.high}) is lower than max(Open, Close)",
                rule_breached="INVALID_CANDLE_BOUNDS",
                details={"high": candle.high, "open": candle.open, "close": candle.close},
            )

        if candle.low > min(candle.open, candle.close):
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_INVALID_LOW_BOUND: Low ({candle.low}) is higher than min(Open, Close)",
                rule_breached="INVALID_CANDLE_BOUNDS",
                details={"low": candle.low, "open": candle.open, "close": candle.close},
            )

        expected_checksum = compute_canonical_sha256(
            {
                "close": candle.close,
                "high": candle.high,
                "low": candle.low,
                "open": candle.open,
                "symbol": candle.symbol,
                "timeframe": candle.timeframe.value,
            }
        )
        if candle.checksum and candle.checksum != expected_checksum:
            return ValidationResult(
                is_valid=False,
                rejection_reason=f"REJECTED_CHECKSUM_MISMATCH: Provided checksum ({candle.checksum}) does not match expected ({expected_checksum})",
                rule_breached="CHECKSUM_MISMATCH",
                details={"provided": candle.checksum, "expected": expected_checksum},
            )

        return ValidationResult(is_valid=True, details={"symbol": sym, "candle_id": candle.candle_id})
