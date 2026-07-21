"""
Project GOAT v0.1 — Validation Tests

Tests for the data-validation engine, covering:
- Duplicate detection
- Non-monotonic timestamp detection
- Invalid price detection
- Missing value detection
- Suspicious gap detection
- OHLC inconsistency detection
- Provenance-aware validation
- Report-only guarantee (no data mutation)

All test data is clearly identified as TEST DATA.
"""

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from goat.data.validation.validators import (
    IssueType,
    IssueSeverity,
    validate_candles,
    validate_ticks,
)


class TestTickValidation:
    """Tests for tick data validation."""

    def test_clean_data_passes(self, sample_ticks_df: pd.DataFrame) -> None:
        """Clean, well-formed data should pass validation."""
        report = validate_ticks(sample_ticks_df)
        assert report.is_valid

    def test_duplicate_detection(self) -> None:
        """Duplicate ticks should be detected and reported."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"] * 3,
                "timestamp": [base, base, base + timedelta(seconds=1)],
                "price": [1.1, 1.1, 1.2],
                "tick_id": ["T1", "T1", "T2"],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_ticks(df)
        dup_issues = [i for i in report.issues if i.issue_type == IssueType.DUPLICATE]
        assert len(dup_issues) >= 1

    def test_non_monotonic_timestamp(self) -> None:
        """Non-monotonic timestamps should be flagged as errors."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"] * 3,
                "timestamp": [
                    base,
                    base + timedelta(seconds=2),
                    base + timedelta(seconds=1),  # backward
                ],
                "price": [1.1, 1.2, 1.15],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_ticks(df)
        mono_issues = [
            i for i in report.issues if i.issue_type == IssueType.NON_MONOTONIC
        ]
        assert len(mono_issues) >= 1
        assert mono_issues[0].severity == IssueSeverity.ERROR

    def test_invalid_price_detection(self) -> None:
        """Non-positive prices should be flagged as errors."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"] * 3,
                "timestamp": [
                    base,
                    base + timedelta(seconds=1),
                    base + timedelta(seconds=2),
                ],
                "price": [1.1, 0, -1.5],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_ticks(df)
        price_issues = [
            i for i in report.issues if i.issue_type == IssueType.INVALID_PRICE
        ]
        assert len(price_issues) == 2  # zero and negative

    def test_missing_value_detection(self) -> None:
        """Missing values in required fields should be detected."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD", None, "EURUSD"],
                "timestamp": [
                    base,
                    base + timedelta(seconds=1),
                    base + timedelta(seconds=2),
                ],
                "price": [1.1, 1.2, None],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_ticks(df)
        missing = [i for i in report.issues if i.issue_type == IssueType.MISSING_VALUE]
        assert len(missing) >= 2  # symbol=None and price=None

    def test_gap_detection(self) -> None:
        """Suspicious timestamp gaps should be flagged as warnings."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        timestamps = [base + timedelta(seconds=i) for i in range(10)]
        # Insert a 60-second gap (>> 5× median of 1s)
        timestamps.append(base + timedelta(seconds=70))
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"] * len(timestamps),
                "timestamp": timestamps,
                "price": [1.1] * len(timestamps),
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_ticks(df)
        gaps = [i for i in report.issues if i.issue_type == IssueType.TIMESTAMP_GAP]
        assert len(gaps) >= 1
        assert gaps[0].severity == IssueSeverity.WARNING

    def test_validation_does_not_modify_data(
        self, sample_ticks_df: pd.DataFrame
    ) -> None:
        """Validation must NEVER modify the input DataFrame."""
        original = sample_ticks_df.copy()
        validate_ticks(sample_ticks_df)
        pd.testing.assert_frame_equal(sample_ticks_df, original)

    def test_empty_dataframe(self) -> None:
        """Empty DataFrame should produce a valid report with no issues."""
        df = pd.DataFrame(columns=["symbol", "timestamp", "price"])
        report = validate_ticks(df)
        assert report.is_valid
        assert report.total_records == 0

    def test_report_summary_string(self, sample_ticks_df: pd.DataFrame) -> None:
        """Report summary should be a non-empty human-readable string."""
        report = validate_ticks(sample_ticks_df)
        summary = report.summary()
        assert "Validation Report" in summary
        assert "Total records" in summary

    def test_valid_records_count(self) -> None:
        """valid_records should exclude only rows with ERROR issues."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"] * 3,
                "timestamp": [
                    base,
                    base + timedelta(seconds=1),
                    base + timedelta(seconds=2),
                ],
                "price": [1.1, -1.0, 1.2],  # one invalid
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_ticks(df)
        assert report.valid_records == 2
        assert report.total_records == 3


class TestCandleValidation:
    """Tests for candle data validation."""

    def test_valid_candles_pass(self) -> None:
        """Well-formed OHLC candles should pass validation."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD", "EURUSD"],
                "timeframe": ["M1", "M1"],
                "timestamp": [base, base + timedelta(minutes=1)],
                "open": [1.10, 1.11],
                "high": [1.12, 1.13],
                "low": [1.09, 1.10],
                "close": [1.11, 1.12],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        assert report.is_valid

    def test_ohlc_high_less_than_open(self) -> None:
        """high < open should be flagged as OHLC inconsistency."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"],
                "timeframe": ["M1"],
                "timestamp": [base],
                "open": [1.10],
                "high": [1.09],  # < open
                "low": [1.08],
                "close": [1.09],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        ohlc = [
            i for i in report.issues if i.issue_type == IssueType.OHLC_INCONSISTENCY
        ]
        assert len(ohlc) >= 1

    def test_ohlc_high_less_than_close(self) -> None:
        """high < close should be flagged as OHLC inconsistency."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"],
                "timeframe": ["M1"],
                "timestamp": [base],
                "open": [1.09],
                "high": [1.095],
                "low": [1.08],
                "close": [1.10],  # > high
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        ohlc = [
            i for i in report.issues if i.issue_type == IssueType.OHLC_INCONSISTENCY
        ]
        assert len(ohlc) >= 1

    def test_ohlc_low_greater_than_close(self) -> None:
        """low > close should be flagged as OHLC inconsistency."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"],
                "timeframe": ["M1"],
                "timestamp": [base],
                "open": [1.10],
                "high": [1.12],
                "low": [1.09],
                "close": [1.08],  # < low
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        ohlc = [
            i for i in report.issues if i.issue_type == IssueType.OHLC_INCONSISTENCY
        ]
        assert len(ohlc) >= 1

    def test_ohlc_high_less_than_low(self) -> None:
        """high < low should be flagged as OHLC inconsistency."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"],
                "timeframe": ["M1"],
                "timestamp": [base],
                "open": [1.08],
                "high": [1.08],
                "low": [1.09],  # > high
                "close": [1.08],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        ohlc = [
            i for i in report.issues if i.issue_type == IssueType.OHLC_INCONSISTENCY
        ]
        assert len(ohlc) >= 1

    def test_duplicate_candle_detection(self) -> None:
        """Duplicate candles should be detected."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD", "EURUSD"],
                "timeframe": ["M1", "M1"],
                "timestamp": [base, base],  # same timestamp
                "open": [1.10, 1.10],
                "high": [1.12, 1.12],
                "low": [1.09, 1.09],
                "close": [1.11, 1.11],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        dups = [i for i in report.issues if i.issue_type == IssueType.DUPLICATE]
        assert len(dups) >= 1

    def test_validation_does_not_modify_candle_data(self) -> None:
        """Validation must NEVER modify the input DataFrame."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"],
                "timeframe": ["M1"],
                "timestamp": [base],
                "open": [1.10],
                "high": [1.09],  # malformed on purpose
                "low": [1.08],
                "close": [1.09],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        original = df.copy()
        validate_candles(df)
        pd.testing.assert_frame_equal(df, original)

    def test_candle_non_monotonic(self) -> None:
        """Non-monotonic candle timestamps should be detected."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"] * 3,
                "timeframe": ["M1"] * 3,
                "timestamp": [
                    base,
                    base + timedelta(minutes=2),
                    base + timedelta(minutes=1),  # backward
                ],
                "open": [1.10, 1.11, 1.12],
                "high": [1.12, 1.13, 1.14],
                "low": [1.09, 1.10, 1.11],
                "close": [1.11, 1.12, 1.13],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        mono = [
            i for i in report.issues if i.issue_type == IssueType.NON_MONOTONIC
        ]
        assert len(mono) >= 1

    def test_candle_invalid_price(self) -> None:
        """Non-positive candle prices should be flagged."""
        base = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        df = pd.DataFrame(
            {
                "symbol": ["EURUSD"],
                "timeframe": ["M1"],
                "timestamp": [base],
                "open": [0],  # invalid
                "high": [1.12],
                "low": [1.09],
                "close": [1.11],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        report = validate_candles(df)
        price_issues = [
            i for i in report.issues if i.issue_type == IssueType.INVALID_PRICE
        ]
        assert len(price_issues) >= 1
