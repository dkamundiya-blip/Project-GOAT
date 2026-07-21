"""
Project GOAT v0.1 — Shared Test Fixtures

All test data in this module is deterministic, seeded, and explicitly
marked with ``DataSource.TEST`` provenance.

⚠️  These fixtures do NOT represent real market observations.
    They exist solely for automated testing of the data pipeline.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from goat.data.schemas import Candle, DataSource, Tick, Timeframe


@pytest.fixture
def utc_now() -> datetime:
    """A fixed UTC timestamp for reproducible tests."""
    return datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_ticks(utc_now: datetime) -> list[Tick]:
    """Generate a small deterministic set of test ticks.

    120 ticks at 1-second intervals (2 full minutes), with monotonically
    increasing prices starting from 1.10000.

    ⚠️  TEST DATA ONLY — not real market observations.
    """
    ticks: list[Tick] = []
    base_price = Decimal("1.10000")
    for i in range(120):
        ticks.append(
            Tick(
                symbol="TEST-PAIR",
                timestamp=utc_now + timedelta(seconds=i),
                price=base_price + Decimal(str(i * 0.00001)),
                tick_id=f"TEST-{i:06d}",
                source=DataSource.TEST,
            )
        )
    return ticks


@pytest.fixture
def sample_ticks_df(sample_ticks: list[Tick]) -> pd.DataFrame:
    """Convert sample ticks to a DataFrame suitable for processing."""
    records = [
        {
            "symbol": t.symbol,
            "timestamp": t.timestamp,
            "price": float(t.price),
            "tick_id": t.tick_id,
            "source": t.source.value,
        }
        for t in sample_ticks
    ]
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


@pytest.fixture
def sample_candle(utc_now: datetime) -> Candle:
    """A single valid test candle.

    ⚠️  TEST DATA ONLY.
    """
    return Candle(
        symbol="TEST-PAIR",
        timeframe=Timeframe.M1,
        timestamp=utc_now,
        open=Decimal("1.10000"),
        high=Decimal("1.10050"),
        low=Decimal("1.09950"),
        close=Decimal("1.10020"),
        source=DataSource.TEST,
    )


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> dict[str, Path]:
    """Provide temporary directories for storage tests."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    return {"raw": raw_dir, "processed": processed_dir}
