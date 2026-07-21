"""
Project GOAT v0.2 — Unit Tests for Deriv Historical Data Importer
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from goat.data.historical import DerivHistoricalImporter
from goat.data.schemas import DataSource


@pytest.mark.asyncio
async def test_deriv_historical_importer_ticks() -> None:
    """Test historical tick retrieval and HISTORICAL_IMPORT provenance."""
    mock_collector = AsyncMock()
    mock_collector.request.return_value = {
        "msg_type": "history",
        "history": {
            "prices": [100.5, 100.6, 100.4],
            "times": [1721623200, 1721623201, 1721623202],
        },
    }

    importer = DerivHistoricalImporter(collector=mock_collector)
    start = datetime(2024, 7, 22, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 7, 22, 1, 0, tzinfo=timezone.utc)

    ticks = await importer.fetch_historical_ticks("R_10", start, end)

    assert len(ticks) == 3
    assert ticks[0].symbol == "R_10"
    assert ticks[0].source == DataSource.HISTORICAL_IMPORT
    assert float(ticks[0].price) == 100.5
    assert ticks[0].metadata["query"] == "ticks_history"
