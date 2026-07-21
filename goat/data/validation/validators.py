"""
Project GOAT v0.1 — Data Validation Engine

Detects data-quality issues in tick and candle DataFrames and produces
structured validation reports.

.. important::

    **CRITICAL PRINCIPLE**: Validators **NEVER** modify, repair, drop,
    reorder, interpolate, or otherwise mutate raw observations.
    They produce reports **ONLY**.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from goat.logging import get_logger

_log = get_logger("validation")


class IssueSeverity(str, enum.Enum):
    """Severity level for validation issues."""

    WARNING = "warning"
    ERROR = "error"


class IssueType(str, enum.Enum):
    """Classification of validation issues."""

    MISSING_VALUE = "missing_value"
    DUPLICATE = "duplicate"
    NON_MONOTONIC = "non_monotonic_timestamp"
    INVALID_PRICE = "invalid_price"
    TIMESTAMP_GAP = "suspicious_timestamp_gap"
    OHLC_INCONSISTENCY = "ohlc_inconsistency"
    CORRUPTED_RECORD = "corrupted_record"


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation issue found in the data.

    Attributes:
        severity: ``WARNING`` or ``ERROR``.
        issue_type: Classification of the issue.
        row_index: DataFrame row index where the issue was found.
        timestamp: Timestamp of the problematic record, if available.
        field: Column name involved, if applicable.
        description: Human-readable explanation of the issue.
    """

    severity: IssueSeverity
    issue_type: IssueType
    row_index: int | None = None
    timestamp: datetime | None = None
    field: str | None = None
    description: str = ""


@dataclass
class ValidationReport:
    """Aggregated validation results for a dataset.

    Provides a summary of all issues found along with record counts.
    """

    total_records: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid_records(self) -> int:
        """Number of records without ERROR-severity issues."""
        error_rows = {
            i.row_index
            for i in self.issues
            if i.severity == IssueSeverity.ERROR and i.row_index is not None
        }
        return self.total_records - len(error_rows)

    @property
    def is_valid(self) -> bool:
        """``True`` if no ERROR-severity issues were found."""
        return not any(i.severity == IssueSeverity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        """Number of ERROR-severity issues."""
        return sum(1 for i in self.issues if i.severity == IssueSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Number of WARNING-severity issues."""
        return sum(1 for i in self.issues if i.severity == IssueSeverity.WARNING)

    def summary(self) -> str:
        """Generate a human-readable summary of the validation report."""
        lines = [
            "Validation Report",
            f"  Total records:  {self.total_records}",
            f"  Valid records:  {self.valid_records}",
            f"  Errors:         {self.error_count}",
            f"  Warnings:       {self.warning_count}",
            f"  Status:         {'PASS' if self.is_valid else 'FAIL'}",
        ]
        if self.issues:
            lines.append("  Issues:")
            for issue in self.issues:
                lines.append(
                    f"    [{issue.severity.value.upper()}] "
                    f"row={issue.row_index} "
                    f"type={issue.issue_type.value} "
                    f"field={issue.field}: {issue.description}"
                )
        return "\n".join(lines)


# ================================================================== #
#  Tick Validation                                                    #
# ================================================================== #


def validate_ticks(
    df: pd.DataFrame,
    gap_threshold_multiplier: float = 5.0,
) -> ValidationReport:
    """Validate a tick DataFrame for data-quality issues.

    Checks for:

    - Missing values in required fields
    - Duplicate ticks
    - Non-monotonic timestamps
    - Invalid (non-positive) prices
    - Suspicious timestamp gaps

    This function **NEVER** modifies the input DataFrame.

    Args:
        df: DataFrame with columns ``symbol``, ``timestamp``, ``price``
            (and optionally ``tick_id``).
        gap_threshold_multiplier: A gap is flagged if it exceeds this
            multiple of the median inter-tick interval.

    Returns:
        ``ValidationReport`` with all detected issues.
    """
    report = ValidationReport(total_records=len(df))

    if df.empty:
        return report

    _check_missing_values(df, ["symbol", "timestamp", "price"], report)
    _check_tick_duplicates(df, report)
    _check_non_monotonic(df, report)
    _check_invalid_prices(df, ["price"], report)
    _check_timestamp_gaps(df, gap_threshold_multiplier, report)

    _log.info(
        "tick_validation_complete",
        total=report.total_records,
        errors=report.error_count,
        warnings=report.warning_count,
    )
    return report


# ================================================================== #
#  Candle Validation                                                  #
# ================================================================== #


def validate_candles(
    df: pd.DataFrame,
    gap_threshold_multiplier: float = 5.0,
) -> ValidationReport:
    """Validate a candle DataFrame for data-quality issues.

    Checks everything in ``validate_ticks`` (adapted for candle fields)
    plus OHLC consistency invariants::

        high >= open   and   high >= close
        low  <= open   and   low  <= close
        high >= low

    This function **NEVER** modifies the input DataFrame.

    Args:
        df: DataFrame with columns ``symbol``, ``timeframe``,
            ``timestamp``, ``open``, ``high``, ``low``, ``close``.
        gap_threshold_multiplier: Gap detection threshold.

    Returns:
        ``ValidationReport`` with all detected issues.
    """
    report = ValidationReport(total_records=len(df))

    if df.empty:
        return report

    required = ["symbol", "timeframe", "timestamp", "open", "high", "low", "close"]
    _check_missing_values(df, required, report)
    _check_candle_duplicates(df, report)
    _check_non_monotonic(df, report)
    _check_invalid_prices(df, ["open", "high", "low", "close"], report)
    _check_ohlc_consistency(df, report)
    _check_timestamp_gaps(df, gap_threshold_multiplier, report)

    _log.info(
        "candle_validation_complete",
        total=report.total_records,
        errors=report.error_count,
        warnings=report.warning_count,
    )
    return report


# ================================================================== #
#  Private validation helpers                                        #
# ================================================================== #


def _check_missing_values(
    df: pd.DataFrame, columns: list[str], report: ValidationReport
) -> None:
    """Flag missing (NaN/None) values in required columns."""
    for col in columns:
        if col not in df.columns:
            continue
        nulls = df[df[col].isna()]
        for idx in nulls.index:
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    issue_type=IssueType.MISSING_VALUE,
                    row_index=int(idx),
                    field=col,
                    description=f"Missing value in required field '{col}'",
                )
            )


def _check_tick_duplicates(df: pd.DataFrame, report: ValidationReport) -> None:
    """Flag duplicate ticks based on (timestamp, symbol[, tick_id])."""
    dedup_cols = ["timestamp", "symbol"]
    if "tick_id" in df.columns:
        dedup_cols = ["timestamp", "symbol", "tick_id"]

    available = [c for c in dedup_cols if c in df.columns]
    if not available:
        return

    dups = df[df.duplicated(subset=available, keep="first")]
    for idx in dups.index:
        ts = df.at[idx, "timestamp"] if "timestamp" in df.columns else None
        report.issues.append(
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                issue_type=IssueType.DUPLICATE,
                row_index=int(idx),
                timestamp=ts,
                description="Duplicate tick detected",
            )
        )


def _check_candle_duplicates(df: pd.DataFrame, report: ValidationReport) -> None:
    """Flag duplicate candles based on (timestamp, symbol, timeframe)."""
    dedup_cols = ["timestamp", "symbol", "timeframe"]
    available = [c for c in dedup_cols if c in df.columns]
    if not available:
        return

    dups = df[df.duplicated(subset=available, keep="first")]
    for idx in dups.index:
        report.issues.append(
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                issue_type=IssueType.DUPLICATE,
                row_index=int(idx),
                description="Duplicate candle detected",
            )
        )


def _check_non_monotonic(df: pd.DataFrame, report: ValidationReport) -> None:
    """Flag timestamps that go backward (non-monotonically increasing)."""
    if "timestamp" not in df.columns or len(df) < 2:
        return

    timestamps = pd.to_datetime(df["timestamp"], utc=True)
    diffs = timestamps.diff().dt.total_seconds()
    non_mono_mask = diffs < 0

    for idx in df.index[non_mono_mask]:
        report.issues.append(
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                issue_type=IssueType.NON_MONOTONIC,
                row_index=int(idx),
                timestamp=df.at[idx, "timestamp"],
                field="timestamp",
                description="Timestamp is earlier than the preceding record",
            )
        )


def _check_invalid_prices(
    df: pd.DataFrame, price_columns: list[str], report: ValidationReport
) -> None:
    """Flag non-positive or non-numeric values in price columns."""
    for col in price_columns:
        if col not in df.columns:
            continue
        prices = pd.to_numeric(df[col], errors="coerce")
        invalid_mask = prices.isna() | (prices <= 0)
        for idx in df.index[invalid_mask]:
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    issue_type=IssueType.INVALID_PRICE,
                    row_index=int(idx),
                    field=col,
                    description=(
                        f"Non-positive or non-numeric {col}: {df.at[idx, col]}"
                    ),
                )
            )


def _check_ohlc_consistency(df: pd.DataFrame, report: ValidationReport) -> None:
    """Flag candles violating OHLC invariants."""
    price_cols = ["open", "high", "low", "close"]
    if not all(c in df.columns for c in price_cols):
        return

    o = pd.to_numeric(df["open"], errors="coerce")
    h = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    c = pd.to_numeric(df["close"], errors="coerce")

    for idx in df.index:
        issues_here: list[str] = []

        h_val, o_val, l_val, c_val = h.at[idx], o.at[idx], low.at[idx], c.at[idx]

        # Skip if any value is NaN (already caught by missing/invalid checks)
        if pd.isna(h_val) or pd.isna(o_val) or pd.isna(l_val) or pd.isna(c_val):
            continue

        if h_val < o_val:
            issues_here.append(f"high ({h_val}) < open ({o_val})")
        if h_val < c_val:
            issues_here.append(f"high ({h_val}) < close ({c_val})")
        if l_val > o_val:
            issues_here.append(f"low ({l_val}) > open ({o_val})")
        if l_val > c_val:
            issues_here.append(f"low ({l_val}) > close ({c_val})")
        if h_val < l_val:
            issues_here.append(f"high ({h_val}) < low ({l_val})")

        if issues_here:
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    issue_type=IssueType.OHLC_INCONSISTENCY,
                    row_index=int(idx),
                    description="; ".join(issues_here),
                )
            )


def _check_timestamp_gaps(
    df: pd.DataFrame,
    gap_threshold_multiplier: float,
    report: ValidationReport,
) -> None:
    """Flag suspiciously large gaps between consecutive timestamps."""
    if "timestamp" not in df.columns or len(df) < 3:
        return

    timestamps = pd.to_datetime(df["timestamp"], utc=True)
    deltas = timestamps.diff().dt.total_seconds().iloc[1:]
    median_delta = deltas.median()

    if pd.isna(median_delta) or median_delta <= 0:
        return

    threshold = median_delta * gap_threshold_multiplier
    gap_mask = deltas > threshold

    for idx in deltas.index[gap_mask]:
        report.issues.append(
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                issue_type=IssueType.TIMESTAMP_GAP,
                row_index=int(idx),
                timestamp=df.at[idx, "timestamp"],
                field="timestamp",
                description=(
                    f"Gap of {deltas.at[idx]:.1f}s "
                    f"(threshold: {threshold:.1f}s, "
                    f"median: {median_delta:.1f}s)"
                ),
            )
        )
