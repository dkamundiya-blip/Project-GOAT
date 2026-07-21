"""
Project GOAT v0.1 — Candle Aggregation Engine

Generates OHLC candles from raw tick data.  Currently supports the
``M1`` (one-minute) timeframe; additional timeframes can be added by
extending the ``TIMEFRAME_FREQ`` mapping.

This module operates on DataFrames and produces DataFrames.
It does **not** modify the source tick data.
"""

from __future__ import annotations

import pandas as pd

from goat.data.schemas import Timeframe
from goat.logging import get_logger

_log = get_logger("processing.aggregation")

# Mapping from Timeframe enum to pandas frequency alias.
# Extend this dict to support additional timeframes — no other code
# changes required.
TIMEFRAME_FREQ: dict[Timeframe, str] = {
    Timeframe.M1: "1min",
}


def aggregate_ticks_to_candles(
    ticks_df: pd.DataFrame,
    timeframe: Timeframe,
    source: str = "test",
) -> pd.DataFrame:
    """Aggregate tick data into OHLC candles.

    Groups ticks by symbol and time bucket, then computes
    ``first`` / ``max`` / ``min`` / ``last`` for OHLC.

    Args:
        ticks_df: DataFrame with at least columns ``symbol``,
                  ``timestamp`` (timezone-aware), and ``price``.
        timeframe: Target candle timeframe (e.g. ``Timeframe.M1``).
        source: Provenance tag applied to every generated candle.

    Returns:
        DataFrame with columns: ``symbol``, ``timeframe``, ``timestamp``,
        ``open``, ``high``, ``low``, ``close``, ``source``, ``metadata``.
        Returns an empty DataFrame if the input is empty or contains
        no valid price data.

    Raises:
        ValueError: If the timeframe is not in ``TIMEFRAME_FREQ``
                    or required columns are missing.
    """
    if timeframe not in TIMEFRAME_FREQ:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}. "
            f"Supported: {list(TIMEFRAME_FREQ.keys())}"
        )

    if ticks_df.empty:
        _log.info("aggregation_skipped", reason="empty input")
        return _empty_candle_df()

    required_cols = {"symbol", "timestamp", "price"}
    missing = required_cols - set(ticks_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    freq = TIMEFRAME_FREQ[timeframe]
    all_candles: list[pd.DataFrame] = []

    for symbol, group in ticks_df.groupby("symbol"):
        group = group.copy()
        group["timestamp"] = pd.to_datetime(group["timestamp"], utc=True)
        group = group.sort_values("timestamp")
        group = group.set_index("timestamp")

        # Ensure price column is numeric for aggregation
        group["price"] = pd.to_numeric(group["price"], errors="coerce")

        ohlc = group["price"].resample(freq).agg(
            open="first",
            high="max",
            low="min",
            close="last",
        )

        # Drop periods with no ticks (NaN open)
        ohlc = ohlc.dropna(subset=["open"])

        if ohlc.empty:
            continue

        ohlc = ohlc.reset_index()
        ohlc["symbol"] = symbol
        ohlc["timeframe"] = timeframe.value
        ohlc["source"] = source
        ohlc["metadata"] = None

        ohlc = ohlc[
            [
                "symbol",
                "timeframe",
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "source",
                "metadata",
            ]
        ]
        all_candles.append(ohlc)

    if not all_candles:
        _log.info("aggregation_produced_no_candles", timeframe=timeframe.value)
        return _empty_candle_df()

    result = pd.concat(all_candles, ignore_index=True)
    _log.info(
        "aggregation_complete",
        timeframe=timeframe.value,
        candles_produced=len(result),
    )
    return result


def _empty_candle_df() -> pd.DataFrame:
    """Return an empty DataFrame with the standard candle columns."""
    return pd.DataFrame(
        columns=[
            "symbol",
            "timeframe",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "source",
            "metadata",
        ]
    )
