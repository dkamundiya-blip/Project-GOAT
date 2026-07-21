"""
Project GOAT v0.1 — Core Data Schemas

Strongly-validated, immutable Pydantic models for market-data observations.
These schemas define the canonical contracts for all data in the system.

Design Principles
-----------------
- **Decimal prices** for API-level precision; storage and research layers may
  convert to float64 for computational efficiency when appropriate.
- **Frozen models** enforce immutability of raw observations.
- **DataSource provenance** distinguishes real, imported, and test data so
  mock observations can never be confused with genuine market data.
- **metadata dict** holds optional provider-specific extensions only; all
  core quantitative fields are always explicit schema fields.
- **Timestamps** are timezone-aware and normalized to UTC.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class DataSource(str, enum.Enum):
    """Provenance classification for market observations.

    Every data point in Project GOAT carries an explicit provenance tag
    so test/mock data can never be mistaken for genuine market observations.

    Members:
        LIVE: Real-time data from an external market feed.
        HISTORICAL_IMPORT: Imported historical dataset.
        TEST: Generated test/mock data — NOT real market data.
    """

    LIVE = "live"
    HISTORICAL_IMPORT = "historical"
    TEST = "test"


class Timeframe(str, enum.Enum):
    """Supported OHLC candle timeframes.

    Members:
        M1: One-minute candles.
        M5: Five-minute candles.
        M15: Fifteen-minute candles.
        M30: Thirty-minute candles.
        H1: One-hour candles.
    """

    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"


class Tick(BaseModel):
    """A single atomic price observation (tick).

    Immutable once created to preserve raw-observation integrity.

    Attributes:
        symbol: Instrument identifier (e.g. ``"EURUSD"``, ``"Volatility_75"``).
        timestamp: Observation time, timezone-aware, normalized to UTC.
        price: Observed price as ``Decimal`` for precision.
        tick_id: Optional provider-assigned tick identifier.
        source: Provenance tag — ``LIVE``, ``HISTORICAL_IMPORT``, or ``TEST``.
        metadata: Optional dict for **provider-specific extensions only**.
                  Core quantitative fields must be explicit schema fields.
    """

    model_config = ConfigDict(frozen=True)

    symbol: str
    timestamp: datetime
    price: Decimal
    tick_id: str | None = None
    source: DataSource = DataSource.TEST
    metadata: dict[str, Any] | None = None

    @field_validator("symbol")
    @classmethod
    def _symbol_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("symbol must be a non-empty string")
        return v

    @field_validator("timestamp")
    @classmethod
    def _timestamp_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (UTC expected)")
        return v.astimezone(timezone.utc)

    @field_validator("price")
    @classmethod
    def _price_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError(f"price must be positive, got {v}")
        return v


class Candle(BaseModel):
    """An OHLC candle aggregated from tick observations.

    Immutable once created.  Cross-validated to ensure OHLC consistency::

        high >= open   and   high >= close
        low  <= open   and   low  <= close
        high >= low

    Attributes:
        symbol: Instrument identifier.
        timeframe: Aggregation period (e.g. ``Timeframe.M1``).
        timestamp: Period-start time, timezone-aware, normalized to UTC.
        open: First price in the period.
        high: Highest price in the period.
        low: Lowest price in the period.
        close: Last price in the period.
        source: Provenance tag.
        metadata: Optional provider-specific extensions
                  (``tick_count``, ``volume``, etc.).
    """

    model_config = ConfigDict(frozen=True)

    symbol: str
    timeframe: Timeframe
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    source: DataSource = DataSource.TEST
    metadata: dict[str, Any] | None = None

    @field_validator("symbol")
    @classmethod
    def _symbol_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("symbol must be a non-empty string")
        return v

    @field_validator("timestamp")
    @classmethod
    def _timestamp_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (UTC expected)")
        return v.astimezone(timezone.utc)

    @field_validator("open", "high", "low", "close")
    @classmethod
    def _prices_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError(f"price must be positive, got {v}")
        return v

    @model_validator(mode="after")
    def _ohlc_consistency(self) -> Candle:
        """Enforce OHLC invariants after all fields are set."""
        errors: list[str] = []
        if self.high < self.open:
            errors.append(f"high ({self.high}) < open ({self.open})")
        if self.high < self.close:
            errors.append(f"high ({self.high}) < close ({self.close})")
        if self.low > self.open:
            errors.append(f"low ({self.low}) > open ({self.open})")
        if self.low > self.close:
            errors.append(f"low ({self.low}) > close ({self.close})")
        if self.high < self.low:
            errors.append(f"high ({self.high}) < low ({self.low})")
        if errors:
            raise ValueError(f"OHLC inconsistency: {'; '.join(errors)}")
        return self
