"""
Project GOAT v0.2 — Unit Tests for Collection Session Manager
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from goat.data.collector.session import CollectionSessionManager
from goat.data.schemas import DataSource, Tick


@pytest.mark.asyncio
async def test_session_manager_metrics_and_summary(tmp_path) -> None:
    """Test session summary calculation and formatting."""
    mock_collector = MagicMock()
    mock_collector.reconnect_count = 1

    mock_storage = MagicMock()
    mock_storage.store_ticks.return_value = 2

    session = CollectionSessionManager(
        collector=mock_collector,
        storage=mock_storage,
    )

    t1 = Tick(
        symbol="R_10",
        timestamp=datetime.now(timezone.utc),
        price=Decimal("10.5"),
        source=DataSource.LIVE,
    )

    session.start_time = datetime.now(timezone.utc)
    session.symbols_subscribed = ["R_10"]
    session.tick_counts["R_10"] = 2
    session.last_tick_timestamps["R_10"] = t1.timestamp
    session.records_written = 2
    session.duplicate_count = 0
    session.end_time = datetime.now(timezone.utc)

    summary = session.get_summary()
    assert summary["symbols_subscribed"] == ["R_10"]
    assert summary["total_ticks_received"] == 2
    assert summary["records_written"] == 2
    assert summary["reconnect_count"] == 1

    summary_text = session.format_summary_text()
    assert "PROJECT GOAT v0.2 — COLLECTION SESSION SUMMARY" in summary_text
    assert "R_10: 2 ticks" in summary_text
