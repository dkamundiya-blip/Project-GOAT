"""
Project GOAT v0.1 — Collector Tests

Tests for the ``MockMarketDataCollector``, verifying:
- Connect/disconnect lifecycle
- Async context manager protocol
- Valid tick production
- Deterministic output with seed
- DataSource.TEST provenance on every tick
- Error on collect without connect

⚠️  All data produced by MockMarketDataCollector is TEST DATA.
    It is NOT real market data and must not be used for research.
"""

from datetime import datetime, timedelta, timezone

import pytest

from goat.data.collector.base import CollectorStatus
from goat.data.collector.mock import MockMarketDataCollector
from goat.data.schemas import DataSource


@pytest.mark.asyncio
class TestMockCollector:
    """Tests for MockMarketDataCollector."""

    async def test_lifecycle(self) -> None:
        """Connect/disconnect lifecycle should update status."""
        collector = MockMarketDataCollector(seed=42)
        assert await collector.get_status() == CollectorStatus.DISCONNECTED

        await collector.connect()
        assert await collector.get_status() == CollectorStatus.CONNECTED

        await collector.disconnect()
        assert await collector.get_status() == CollectorStatus.DISCONNECTED

    async def test_context_manager(self) -> None:
        """Async context manager should handle connect/disconnect."""
        collector = MockMarketDataCollector(seed=42)
        async with collector:
            assert await collector.get_status() == CollectorStatus.CONNECTED
        assert await collector.get_status() == CollectorStatus.DISCONNECTED

    async def test_produces_valid_ticks(self) -> None:
        """Mock collector should produce valid Tick objects."""
        start = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(seconds=5)

        async with MockMarketDataCollector(seed=42) as collector:
            ticks = [t async for t in collector.collect_ticks("TEST-SYM", start, end)]

        assert len(ticks) > 0
        for tick in ticks:
            assert tick.symbol == "TEST-SYM"
            assert tick.source == DataSource.TEST
            assert tick.price > 0
            assert tick.timestamp.tzinfo is not None

    async def test_deterministic_with_seed(self) -> None:
        """Same seed should produce identical output."""
        start = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(seconds=2)

        async with MockMarketDataCollector(seed=99) as c1:
            ticks1 = [t async for t in c1.collect_ticks("SYM", start, end)]

        async with MockMarketDataCollector(seed=99) as c2:
            ticks2 = [t async for t in c2.collect_ticks("SYM", start, end)]

        assert len(ticks1) == len(ticks2)
        for t1, t2 in zip(ticks1, ticks2):
            assert t1.price == t2.price
            assert t1.timestamp == t2.timestamp

    async def test_all_ticks_tagged_as_test(self) -> None:
        """Every tick must carry DataSource.TEST and identify the generator."""
        start = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(seconds=1)

        async with MockMarketDataCollector(seed=42) as collector:
            async for tick in collector.collect_ticks("SYM", start, end):
                assert tick.source == DataSource.TEST
                assert tick.metadata is not None
                assert "MockMarketDataCollector" in tick.metadata.get("generator", "")
                assert "WARNING" in tick.metadata  # explicit test-data warning

    async def test_not_connected_raises(self) -> None:
        """Collecting without connecting should raise RuntimeError."""
        collector = MockMarketDataCollector(seed=42)
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end = start + timedelta(seconds=1)

        with pytest.raises(RuntimeError, match="not connected"):
            async for _ in collector.collect_ticks("SYM", start, end):
                pass

    async def test_different_seeds_produce_different_output(self) -> None:
        """Different seeds should produce different price sequences."""
        start = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(seconds=2)

        async with MockMarketDataCollector(seed=1) as c1:
            ticks1 = [t async for t in c1.collect_ticks("SYM", start, end)]

        async with MockMarketDataCollector(seed=999) as c2:
            ticks2 = [t async for t in c2.collect_ticks("SYM", start, end)]

        # At least one price should differ (extremely unlikely to be identical)
        prices1 = [t.price for t in ticks1]
        prices2 = [t.price for t in ticks2]
        assert prices1 != prices2
