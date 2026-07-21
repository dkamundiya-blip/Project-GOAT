"""
Project GOAT v0.1 — Mock Market Data Collector

.. warning::

    THIS COLLECTOR GENERATES DETERMINISTIC **TEST DATA** ONLY.

    - Observations produced by this collector are **NOT** real market data.
    - Do **NOT** use this data for quantitative conclusions or research.
    - All ticks are tagged with ``DataSource.TEST`` provenance.
    - Every tick's metadata explicitly identifies the generator.

This collector exists solely to support automated testing and development
of the data pipeline.  A real external market-data connector will be
implemented in a later approved milestone.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import numpy as np

from goat.data.collector.base import AbstractCollector, CollectorStatus
from goat.data.schemas import DataSource, Tick
from goat.logging import get_logger

_log = get_logger("collector.mock")


class MockMarketDataCollector(AbstractCollector):
    """Deterministic mock collector for testing and development.

    Generates tick data using a seeded pseudo-random walk.  Every run with
    the same ``seed`` produces identical output, ensuring test
    reproducibility.

    .. warning::
        THIS IS **TEST DATA** — NOT REAL MARKET DATA.
        Generated observations must never be used for quantitative
        conclusions or mistaken for genuine market observations.

    Args:
        seed: Random seed for reproducibility.
        initial_price: Starting price for the generated walk.
        tick_interval_ms: Milliseconds between generated ticks.
        volatility: Standard deviation of per-tick price changes.
    """

    def __init__(
        self,
        seed: int = 42,
        initial_price: float = 1.10000,
        tick_interval_ms: int = 250,
        volatility: float = 0.00005,
    ) -> None:
        self._seed = seed
        self._initial_price = initial_price
        self._tick_interval_ms = tick_interval_ms
        self._volatility = volatility
        self._status = CollectorStatus.DISCONNECTED
        self._rng = np.random.default_rng(seed)

    async def connect(self) -> None:
        """Simulate connection establishment (TEST ONLY)."""
        _log.info(
            "mock_collector_connecting",
            seed=self._seed,
            initial_price=self._initial_price,
        )
        self._status = CollectorStatus.CONNECTED
        # Reset RNG on connect so repeated connect→collect cycles are deterministic
        self._rng = np.random.default_rng(self._seed)
        _log.info("mock_collector_connected")

    async def disconnect(self) -> None:
        """Simulate connection teardown (TEST ONLY)."""
        _log.info("mock_collector_disconnecting")
        self._status = CollectorStatus.DISCONNECTED
        _log.info("mock_collector_disconnected")

    async def get_status(self) -> CollectorStatus:
        """Return the current mock connection status."""
        return self._status

    async def collect_ticks(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> AsyncIterator[Tick]:
        """Generate deterministic mock tick data.

        .. warning::
            THIS IS **TEST DATA** — NOT REAL MARKET DATA.

        Args:
            symbol: Instrument identifier for generated ticks.
            start: Start time (inclusive) for tick generation.
            end: End time (exclusive) for tick generation.

        Yields:
            ``Tick`` objects tagged with ``DataSource.TEST`` provenance.

        Raises:
            RuntimeError: If the collector is not connected.
        """
        if self._status != CollectorStatus.CONNECTED:
            raise RuntimeError("MockMarketDataCollector is not connected")

        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        interval = timedelta(milliseconds=self._tick_interval_ms)

        current_time = start_utc
        current_price = self._initial_price
        tick_count = 0

        while current_time < end_utc:
            # Small pseudo-random perturbation
            change = self._rng.normal(0, self._volatility)
            current_price = max(current_price + change, 0.00001)

            tick = Tick(
                symbol=symbol,
                timestamp=current_time,
                price=Decimal(str(round(current_price, 5))),
                tick_id=f"MOCK-{tick_count:010d}",
                source=DataSource.TEST,
                metadata={
                    "generator": "MockMarketDataCollector",
                    "seed": self._seed,
                    "WARNING": "TEST DATA ONLY — NOT REAL MARKET DATA",
                },
            )
            yield tick

            current_time += interval
            tick_count += 1

        _log.info(
            "mock_collection_complete",
            symbol=symbol,
            ticks_generated=tick_count,
        )
