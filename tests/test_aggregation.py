"""
Project GOAT v0.1 — Aggregation Tests

Tests for the tick-to-candle aggregation engine.  All test data is
deterministic and clearly identified as TEST DATA.
"""

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from goat.data.processing.aggregation import aggregate_ticks_to_candles
from goat.data.schemas import Timeframe


class TestAggregation:
    """Tests for tick-to-candle aggregation."""

    def test_m1_aggregation(self, sample_ticks_df: pd.DataFrame) -> None:
        """M1 aggregation should produce candles from 1-minute groups."""
        result = aggregate_ticks_to_candles(sample_ticks_df, Timeframe.M1)
        assert not result.empty
        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns
        assert "close" in result.columns
        # 120 seconds of ticks at 1/sec → 2 complete minutes
        assert len(result) == 2

    def test_ohlc_correctness(self, sample_ticks_df: pd.DataFrame) -> None:
        """Aggregated OHLC values must satisfy consistency invariants."""
        result = aggregate_ticks_to_candles(sample_ticks_df, Timeframe.M1)
        for _, row in result.iterrows():
            assert row["high"] >= row["open"], "high must be >= open"
            assert row["high"] >= row["close"], "high must be >= close"
            assert row["low"] <= row["open"], "low must be <= open"
            assert row["low"] <= row["close"], "low must be <= close"
            assert row["high"] >= row["low"], "high must be >= low"

    def test_empty_input(self) -> None:
        """Empty input should produce an empty DataFrame, not an error."""
        empty_df = pd.DataFrame(columns=["symbol", "timestamp", "price"])
        result = aggregate_ticks_to_candles(empty_df, Timeframe.M1)
        assert result.empty

    def test_multi_symbol(self) -> None:
        """Aggregation should handle multiple symbols independently."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        records = []
        for i in range(60):
            for sym in ["SYM-A", "SYM-B"]:
                price = 100.0 + i * 0.01 if sym == "SYM-A" else 200.0 + i * 0.01
                records.append(
                    {
                        "symbol": sym,
                        "timestamp": base + timedelta(seconds=i),
                        "price": price,
                    }
                )
        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        result = aggregate_ticks_to_candles(df, Timeframe.M1)
        assert len(result) == 2  # One M1 candle per symbol
        assert set(result["symbol"].unique()) == {"SYM-A", "SYM-B"}

    def test_source_tag_preserved(self, sample_ticks_df: pd.DataFrame) -> None:
        """Source provenance tag should be set on output candles."""
        result = aggregate_ticks_to_candles(
            sample_ticks_df, Timeframe.M1, source="test"
        )
        assert all(result["source"] == "test")

    def test_missing_columns_raises(self) -> None:
        """DataFrame missing required columns should raise ValueError."""
        df = pd.DataFrame({"foo": [1, 2, 3]})
        with pytest.raises(ValueError, match="Missing required columns"):
            aggregate_ticks_to_candles(df, Timeframe.M1)

    def test_first_last_price(self) -> None:
        """Open should be first tick price, close should be last."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        prices = [10.0, 12.0, 8.0, 11.0]
        records = [
            {
                "symbol": "TEST",
                "timestamp": base + timedelta(seconds=i * 10),
                "price": p,
            }
            for i, p in enumerate(prices)
        ]
        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        result = aggregate_ticks_to_candles(df, Timeframe.M1)
        assert len(result) == 1
        row = result.iloc[0]
        assert row["open"] == pytest.approx(10.0)
        assert row["high"] == pytest.approx(12.0)
        assert row["low"] == pytest.approx(8.0)
        assert row["close"] == pytest.approx(11.0)
