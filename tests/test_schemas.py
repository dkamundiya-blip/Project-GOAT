"""
Project GOAT v0.1 — Schema Tests

Tests for ``Tick`` and ``Candle`` Pydantic models, including validation,
immutability, provenance distinction, and OHLC consistency enforcement.

All test data is clearly identified as TEST DATA.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from goat.data.schemas import Candle, DataSource, Tick, Timeframe


class TestTick:
    """Tests for the Tick schema."""

    def test_valid_tick_creation(self) -> None:
        """A tick with all valid fields should be created successfully."""
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            price=Decimal("1.10500"),
            tick_id="T001",
            source=DataSource.TEST,
        )
        assert tick.symbol == "EURUSD"
        assert tick.price == Decimal("1.10500")
        assert tick.source == DataSource.TEST

    def test_symbol_whitespace_stripped(self) -> None:
        """Leading/trailing whitespace should be stripped from symbol."""
        tick = Tick(
            symbol="  EURUSD  ",
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            price=Decimal("1.10"),
        )
        assert tick.symbol == "EURUSD"

    def test_empty_symbol_rejected(self) -> None:
        """An empty symbol string must be rejected."""
        with pytest.raises(ValueError, match="non-empty"):
            Tick(
                symbol="",
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                price=Decimal("1.10"),
            )

    def test_whitespace_only_symbol_rejected(self) -> None:
        """A whitespace-only symbol must be rejected."""
        with pytest.raises(ValueError, match="non-empty"):
            Tick(
                symbol="   ",
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                price=Decimal("1.10"),
            )

    def test_naive_timestamp_rejected(self) -> None:
        """A timezone-naive timestamp must be rejected."""
        with pytest.raises(ValueError, match="timezone-aware"):
            Tick(
                symbol="EURUSD",
                timestamp=datetime(2025, 1, 1, 12, 0, 0),
                price=Decimal("1.10"),
            )

    def test_timestamp_normalized_to_utc(self) -> None:
        """Non-UTC timezone should be converted to UTC."""
        est = timezone(timedelta(hours=-5))
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, 12, 0, 0, tzinfo=est),
            price=Decimal("1.10"),
        )
        assert tick.timestamp.tzinfo == timezone.utc
        assert tick.timestamp.hour == 17  # 12 EST = 17 UTC

    def test_zero_price_rejected(self) -> None:
        """Zero price must be rejected."""
        with pytest.raises(ValueError, match="positive"):
            Tick(
                symbol="EURUSD",
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                price=Decimal("0"),
            )

    def test_negative_price_rejected(self) -> None:
        """Negative price must be rejected."""
        with pytest.raises(ValueError, match="positive"):
            Tick(
                symbol="EURUSD",
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                price=Decimal("-1.50"),
            )

    def test_tick_is_immutable(self) -> None:
        """Tick must be frozen — attribute assignment should fail."""
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            price=Decimal("1.10"),
        )
        with pytest.raises(Exception):
            tick.price = Decimal("2.0")  # type: ignore[misc]

    def test_default_source_is_test(self) -> None:
        """Default DataSource should be TEST."""
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            price=Decimal("1.10"),
        )
        assert tick.source == DataSource.TEST

    def test_metadata_extensibility(self) -> None:
        """Metadata dict should accept arbitrary provider extensions."""
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            price=Decimal("1.10"),
            metadata={"volume": 1000, "spread": 0.00012},
        )
        assert tick.metadata is not None
        assert tick.metadata["volume"] == 1000

    def test_provenance_live(self) -> None:
        """Tick with LIVE source should be distinguished from TEST."""
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            price=Decimal("1.10"),
            source=DataSource.LIVE,
        )
        assert tick.source == DataSource.LIVE
        assert tick.source != DataSource.TEST

    def test_provenance_historical(self) -> None:
        """Tick with HISTORICAL_IMPORT source should be distinguished."""
        tick = Tick(
            symbol="EURUSD",
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            price=Decimal("1.10"),
            source=DataSource.HISTORICAL_IMPORT,
        )
        assert tick.source == DataSource.HISTORICAL_IMPORT
        assert tick.source != DataSource.TEST
        assert tick.source != DataSource.LIVE


class TestCandle:
    """Tests for the Candle schema."""

    def test_valid_candle_creation(self) -> None:
        """A candle with consistent OHLC should be created successfully."""
        candle = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            open=Decimal("1.10000"),
            high=Decimal("1.10050"),
            low=Decimal("1.09950"),
            close=Decimal("1.10020"),
            source=DataSource.TEST,
        )
        assert candle.high >= candle.open
        assert candle.low <= candle.close

    def test_high_less_than_open_rejected(self) -> None:
        """OHLC where high < open must be rejected."""
        with pytest.raises(ValueError, match="OHLC inconsistency"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                open=Decimal("1.10000"),
                high=Decimal("1.09000"),
                low=Decimal("1.08000"),
                close=Decimal("1.09000"),
            )

    def test_high_less_than_close_rejected(self) -> None:
        """OHLC where high < close must be rejected."""
        with pytest.raises(ValueError, match="OHLC inconsistency"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                open=Decimal("1.09000"),
                high=Decimal("1.09500"),
                low=Decimal("1.08000"),
                close=Decimal("1.10000"),
            )

    def test_low_greater_than_open_rejected(self) -> None:
        """OHLC where low > open must be rejected."""
        with pytest.raises(ValueError, match="OHLC inconsistency"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                open=Decimal("1.10000"),
                high=Decimal("1.11000"),
                low=Decimal("1.10500"),
                close=Decimal("1.10800"),
            )

    def test_low_greater_than_close_rejected(self) -> None:
        """OHLC where low > close must be rejected."""
        with pytest.raises(ValueError, match="OHLC inconsistency"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                open=Decimal("1.10500"),
                high=Decimal("1.11000"),
                low=Decimal("1.10200"),
                close=Decimal("1.10100"),
            )

    def test_high_less_than_low_rejected(self) -> None:
        """OHLC where high < low must be rejected."""
        with pytest.raises(ValueError, match="OHLC inconsistency"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                open=Decimal("1.10000"),
                high=Decimal("1.09000"),
                low=Decimal("1.09500"),
                close=Decimal("1.09000"),
            )

    def test_candle_is_immutable(self) -> None:
        """Candle must be frozen — attribute assignment should fail."""
        candle = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.11"),
            low=Decimal("1.09"),
            close=Decimal("1.10"),
        )
        with pytest.raises(Exception):
            candle.close = Decimal("999")  # type: ignore[misc]

    def test_flat_candle_valid(self) -> None:
        """A flat candle (open=high=low=close) is valid."""
        candle = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.10"),
            low=Decimal("1.10"),
            close=Decimal("1.10"),
        )
        assert candle.open == candle.high == candle.low == candle.close

    def test_negative_candle_price_rejected(self) -> None:
        """Negative prices in candles must be rejected."""
        with pytest.raises(ValueError, match="positive"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                open=Decimal("-1.10"),
                high=Decimal("1.11"),
                low=Decimal("1.09"),
                close=Decimal("1.10"),
            )

    def test_candle_metadata(self) -> None:
        """Candle metadata should store optional extensions."""
        candle = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.11"),
            low=Decimal("1.09"),
            close=Decimal("1.10"),
            metadata={"tick_count": 240, "volume": 5000},
        )
        assert candle.metadata is not None
        assert candle.metadata["tick_count"] == 240

    def test_provenance_distinction(self) -> None:
        """Different provenance tags must be distinguishable."""
        live = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.11"),
            low=Decimal("1.09"),
            close=Decimal("1.10"),
            source=DataSource.LIVE,
        )
        test = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.11"),
            low=Decimal("1.09"),
            close=Decimal("1.10"),
            source=DataSource.TEST,
        )
        hist = Candle(
            symbol="EURUSD",
            timeframe=Timeframe.M1,
            timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
            open=Decimal("1.10"),
            high=Decimal("1.11"),
            low=Decimal("1.09"),
            close=Decimal("1.10"),
            source=DataSource.HISTORICAL_IMPORT,
        )
        assert live.source != test.source
        assert test.source != hist.source
        assert live.source != hist.source

    def test_naive_timestamp_rejected(self) -> None:
        """Candle with naive timestamp must be rejected."""
        with pytest.raises(ValueError, match="timezone-aware"):
            Candle(
                symbol="EURUSD",
                timeframe=Timeframe.M1,
                timestamp=datetime(2025, 1, 1),
                open=Decimal("1.10"),
                high=Decimal("1.11"),
                low=Decimal("1.09"),
                close=Decimal("1.10"),
            )
