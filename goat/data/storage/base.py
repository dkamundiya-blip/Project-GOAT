"""
Project GOAT v0.1 — Abstract Storage Interface

Defines the interface for persisting and retrieving market observations.
Implementations must provide:

- Duplicate protection (skip, never error on duplicates)
- Safe write behavior (no partial/corrupt files)
- Partition strategy encapsulated internally

The storage abstraction is designed so the partition strategy can be
changed later without affecting the research layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

from goat.data.schemas import Candle, Tick, Timeframe


class AbstractStorage(ABC):
    """Abstract base for market-data storage backends.

    Implementations handle partitioning, deduplication, and safe I/O
    internally.  Callers interact only through this interface.
    """

    @abstractmethod
    def write_ticks(self, symbol: str, ticks: list[Tick]) -> int:
        """Persist a batch of tick observations.

        Must handle deduplication and safe writes.  Must not silently
        discard data — duplicates should be skipped, not errored.

        Args:
            symbol: Instrument identifier.
            ticks: List of ``Tick`` objects to persist.

        Returns:
            Number of new (non-duplicate) ticks written.
        """

    @abstractmethod
    def read_ticks(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Read tick data for a symbol within an optional time range.

        Args:
            symbol: Instrument identifier.
            start: Start time (inclusive), or ``None`` for no lower bound.
            end: End time (exclusive), or ``None`` for no upper bound.

        Returns:
            DataFrame with tick data, empty if no data found.
        """

    @abstractmethod
    def write_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        candles: list[Candle],
    ) -> int:
        """Persist a batch of OHLC candle observations.

        Args:
            symbol: Instrument identifier.
            timeframe: Candle aggregation period.
            candles: List of ``Candle`` objects to persist.

        Returns:
            Number of new (non-duplicate) candles written.
        """

    @abstractmethod
    def read_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Read candle data for a symbol/timeframe within an optional range.

        Args:
            symbol: Instrument identifier.
            timeframe: Candle aggregation period.
            start: Start time (inclusive), or ``None`` for no lower bound.
            end: End time (exclusive), or ``None`` for no upper bound.

        Returns:
            DataFrame with candle data, empty if no data found.
        """
