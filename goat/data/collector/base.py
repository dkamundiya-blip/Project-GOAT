"""
Project GOAT v0.1 — Abstract Market Data Collector

Defines the async interface that all market-data collectors must implement.
This abstraction ensures the research engine is never coupled to a single
data provider or broker.

No strategy logic should ever be placed in a collector.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from goat.data.schemas import Tick


class CollectorStatus(str, enum.Enum):
    """Connection status for a market-data collector."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class AbstractCollector(ABC):
    """Abstract base for all market-data collectors.

    Subclasses must implement the ``connect``/``disconnect`` lifecycle and
    the ``collect_ticks`` async generator.  The collector supports the
    async context-manager protocol for safe resource management.

    Example usage::

        async with MyCollector() as collector:
            async for tick in collector.collect_ticks("EURUSD", start, end):
                process(tick)
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source.

        Implementations should log startup status.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully close the data-source connection.

        Implementations should log shutdown status and release resources.
        """

    @abstractmethod
    async def collect_ticks(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> AsyncIterator[Tick]:
        """Yield ticks for the given symbol and time range.

        Args:
            symbol: Instrument identifier (e.g. ``"EURUSD"``).
            start: Start of collection window (inclusive), UTC.
            end: End of collection window (exclusive), UTC.

        Yields:
            ``Tick`` objects in chronological order.
        """
        # pragma: no cover — required for AsyncIterator typing
        yield  # type: ignore[misc]

    @abstractmethod
    async def get_status(self) -> CollectorStatus:
        """Return the current connection status."""

    async def __aenter__(self) -> AbstractCollector:
        """Enter the async context manager — connects to the data source."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the async context manager — disconnects cleanly."""
        await self.disconnect()
