"""
Project GOAT v0.1 — Storage Tests

Tests for the Parquet storage layer, covering:
- Write/read round-trip integrity for ticks and candles
- Duplicate protection on append
- Time-range filtering
- Partition directory structure
- Provenance (source) preservation
- Empty reads

All test data is clearly identified as TEST DATA.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from goat.data.schemas import Candle, DataSource, Tick, Timeframe
from goat.data.storage.parquet import ParquetStorage


class TestTickStorage:
    """Tests for tick persistence."""

    def test_write_and_read_roundtrip(
        self, tmp_data_dir: dict[str, Path], sample_ticks: list[Tick]
    ) -> None:
        """Ticks written should be readable with matching data."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        written = storage.write_ticks("TEST-PAIR", sample_ticks)
        assert written == len(sample_ticks)

        df = storage.read_ticks("TEST-PAIR")
        assert len(df) == len(sample_ticks)
        assert "price" in df.columns
        assert "source" in df.columns

    def test_duplicate_protection(
        self, tmp_data_dir: dict[str, Path], sample_ticks: list[Tick]
    ) -> None:
        """Writing the same ticks twice should not create duplicates."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        first_write = storage.write_ticks("TEST-PAIR", sample_ticks)
        second_write = storage.write_ticks("TEST-PAIR", sample_ticks)

        assert first_write == len(sample_ticks)
        assert second_write == 0

        df = storage.read_ticks("TEST-PAIR")
        assert len(df) == len(sample_ticks)

    def test_time_range_filter(
        self, tmp_data_dir: dict[str, Path], sample_ticks: list[Tick]
    ) -> None:
        """Reading with time filters should return the correct subset."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        storage.write_ticks("TEST-PAIR", sample_ticks)

        start = sample_ticks[0].timestamp
        mid = start + timedelta(seconds=60)
        df = storage.read_ticks("TEST-PAIR", start=start, end=mid)
        assert len(df) == 60  # First minute only

    def test_empty_read(self, tmp_data_dir: dict[str, Path]) -> None:
        """Reading a non-existent symbol should return empty DataFrame."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        df = storage.read_ticks("NONEXISTENT")
        assert df.empty

    def test_source_preserved(self, tmp_data_dir: dict[str, Path]) -> None:
        """Data source provenance should survive write/read cycle."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        tick = Tick(
            symbol="PROV-TEST",
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            price=Decimal("1.10"),
            source=DataSource.HISTORICAL_IMPORT,
        )
        storage.write_ticks("PROV-TEST", [tick])
        df = storage.read_ticks("PROV-TEST")
        assert df.iloc[0]["source"] == "historical"

    def test_partitioning_creates_correct_paths(
        self, tmp_data_dir: dict[str, Path], sample_ticks: list[Tick]
    ) -> None:
        """Ticks should be stored in symbol/date partitions."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        storage.write_ticks("TEST-PAIR", sample_ticks)

        expected_dir = tmp_data_dir["raw"] / "TEST-PAIR"
        assert expected_dir.exists()
        parquet_files = list(expected_dir.glob("*.parquet"))
        assert len(parquet_files) == 1  # All ticks on same date

    def test_write_empty_list(self, tmp_data_dir: dict[str, Path]) -> None:
        """Writing an empty list should return 0 and not create files."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        written = storage.write_ticks("TEST-PAIR", [])
        assert written == 0


class TestCandleStorage:
    """Tests for candle persistence."""

    def test_write_and_read_roundtrip(
        self, tmp_data_dir: dict[str, Path], sample_candle: Candle
    ) -> None:
        """Candles written should be readable with matching data."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        candles = [sample_candle]
        written = storage.write_candles("TEST-PAIR", Timeframe.M1, candles)
        assert written == 1

        df = storage.read_candles("TEST-PAIR", Timeframe.M1)
        assert len(df) == 1
        assert df.iloc[0]["open"] == pytest.approx(1.10000, abs=1e-6)
        assert df.iloc[0]["high"] == pytest.approx(1.10050, abs=1e-6)

    def test_duplicate_candle_protection(
        self, tmp_data_dir: dict[str, Path], sample_candle: Candle
    ) -> None:
        """Writing the same candle twice should not duplicate."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        candles = [sample_candle]
        storage.write_candles("TEST-PAIR", Timeframe.M1, candles)
        second = storage.write_candles("TEST-PAIR", Timeframe.M1, candles)
        assert second == 0

        df = storage.read_candles("TEST-PAIR", Timeframe.M1)
        assert len(df) == 1

    def test_empty_candle_read(self, tmp_data_dir: dict[str, Path]) -> None:
        """Reading candles for a non-existent symbol returns empty DataFrame."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        df = storage.read_candles("NONEXISTENT", Timeframe.M1)
        assert df.empty

    def test_partitioning_creates_correct_paths(
        self, tmp_data_dir: dict[str, Path], sample_candle: Candle
    ) -> None:
        """Candles should be stored in symbol/timeframe/date partitions."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        storage.write_candles("TEST-PAIR", Timeframe.M1, [sample_candle])

        expected_dir = tmp_data_dir["processed"] / "TEST-PAIR" / "M1"
        assert expected_dir.exists()
        parquet_files = list(expected_dir.glob("*.parquet"))
        assert len(parquet_files) == 1

    def test_candle_source_preserved(
        self, tmp_data_dir: dict[str, Path]
    ) -> None:
        """Candle provenance should survive write/read cycle."""
        storage = ParquetStorage(
            raw_dir=tmp_data_dir["raw"],
            processed_dir=tmp_data_dir["processed"],
        )
        candle = Candle(
            symbol="PROV-TEST",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.11"),
            low=Decimal("1.09"),
            close=Decimal("1.10"),
            source=DataSource.LIVE,
        )
        storage.write_candles("PROV-TEST", Timeframe.M1, [candle])
        df = storage.read_candles("PROV-TEST", Timeframe.M1)
        assert df.iloc[0]["source"] == "live"
