"""
Project GOAT v0.1 — Parquet Storage Implementation

Persists market observations as Parquet files with date-based partitioning::

    Ticks:   {raw_dir}/{symbol}/{YYYY-MM-DD}.parquet
    Candles: {processed_dir}/{symbol}/{timeframe}/{YYYY-MM-DD}.parquet

Design Decisions
----------------
- **Prices** are stored as ``float64`` in Parquet for pandas/numpy ecosystem
  compatibility.  The canonical ``Decimal`` precision lives in the Pydantic
  schema layer.  Research modules may later implement explicit Decimal↔float
  conversion utilities when needed.
- **Duplicate protection** via deduplication on append.
- **Atomic writes** via temp-file-then-rename pattern.
- **Partition strategy** is encapsulated in private methods and can be
  changed without affecting callers of the public interface.
- **Date-level granularity** avoids excessive small files while keeping
  individual partitions manageable.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from goat.data.schemas import Candle, Tick, Timeframe
from goat.data.storage.base import AbstractStorage
from goat.logging import get_logger

_log = get_logger("storage.parquet")

# ------------------------------------------------------------------ #
#  PyArrow schemas — enforce consistent column types on disk          #
# ------------------------------------------------------------------ #

_TICK_SCHEMA = pa.schema(
    [
        ("symbol", pa.string()),
        ("timestamp", pa.timestamp("us", tz="UTC")),
        ("price", pa.float64()),
        ("tick_id", pa.string()),
        ("source", pa.string()),
        ("metadata", pa.string()),  # JSON-serialized
    ]
)

_CANDLE_SCHEMA = pa.schema(
    [
        ("symbol", pa.string()),
        ("timeframe", pa.string()),
        ("timestamp", pa.timestamp("us", tz="UTC")),
        ("open", pa.float64()),
        ("high", pa.float64()),
        ("low", pa.float64()),
        ("close", pa.float64()),
        ("source", pa.string()),
        ("metadata", pa.string()),  # JSON-serialized
    ]
)


class ParquetStorage(AbstractStorage):
    """Parquet-based storage for market observations.

    Partitions data by symbol and date to balance query performance
    with file-management simplicity.  Provides duplicate protection
    and atomic write safety.

    Args:
        raw_dir: Root directory for raw tick storage.
        processed_dir: Root directory for processed candle storage.
    """

    def __init__(self, raw_dir: Path, processed_dir: Path) -> None:
        self._raw_dir = Path(raw_dir)
        self._processed_dir = Path(processed_dir)

    # ================================================================ #
    #  Tick I/O                                                        #
    # ================================================================ #

    def write_ticks(self, symbol: str, ticks: list[Tick]) -> int:
        """Persist ticks with date-partitioning and deduplication."""
        if not ticks:
            return 0

        records = []
        for t in ticks:
            records.append(
                {
                    "symbol": t.symbol,
                    "timestamp": t.timestamp,
                    "price": float(t.price),
                    "tick_id": t.tick_id,
                    "source": t.source.value,
                    "metadata": json.dumps(t.metadata) if t.metadata else None,
                }
            )

        df_new = pd.DataFrame(records)
        df_new["timestamp"] = pd.to_datetime(df_new["timestamp"], utc=True)

        total_written = 0
        for date, group in df_new.groupby(df_new["timestamp"].dt.date):
            path = self._tick_partition_path(symbol, date)
            written = self._merge_and_write(
                path,
                group,
                dedup_cols=["timestamp", "tick_id"],
                schema=_TICK_SCHEMA,
            )
            total_written += written

        _log.info(
            "ticks_written",
            symbol=symbol,
            total=len(ticks),
            new=total_written,
        )
        return total_written

    def read_ticks(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Read tick data, optionally filtered by time range."""
        symbol_dir = self._raw_dir / symbol
        if not symbol_dir.exists():
            return self._empty_tick_df()

        frames: list[pd.DataFrame] = []
        for parquet_file in sorted(symbol_dir.glob("*.parquet")):
            df = pq.read_table(parquet_file).to_pandas()
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                frames.append(df)

        if not frames:
            return self._empty_tick_df()

        result = pd.concat(frames, ignore_index=True)
        result = self._filter_time_range(result, start, end)
        return result.sort_values("timestamp").reset_index(drop=True)

    # ================================================================ #
    #  Candle I/O                                                      #
    # ================================================================ #

    def write_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        candles: list[Candle],
    ) -> int:
        """Persist candles with date-partitioning and deduplication."""
        if not candles:
            return 0

        records = []
        for c in candles:
            records.append(
                {
                    "symbol": c.symbol,
                    "timeframe": c.timeframe.value,
                    "timestamp": c.timestamp,
                    "open": float(c.open),
                    "high": float(c.high),
                    "low": float(c.low),
                    "close": float(c.close),
                    "source": c.source.value,
                    "metadata": json.dumps(c.metadata) if c.metadata else None,
                }
            )

        df_new = pd.DataFrame(records)
        df_new["timestamp"] = pd.to_datetime(df_new["timestamp"], utc=True)

        total_written = 0
        for date, group in df_new.groupby(df_new["timestamp"].dt.date):
            path = self._candle_partition_path(symbol, timeframe, date)
            written = self._merge_and_write(
                path,
                group,
                dedup_cols=["timestamp", "symbol", "timeframe"],
                schema=_CANDLE_SCHEMA,
            )
            total_written += written

        _log.info(
            "candles_written",
            symbol=symbol,
            timeframe=timeframe.value,
            total=len(candles),
            new=total_written,
        )
        return total_written

    def read_candles(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Read candle data, optionally filtered by time range."""
        candle_dir = self._processed_dir / symbol / timeframe.value
        if not candle_dir.exists():
            return self._empty_candle_df()

        frames: list[pd.DataFrame] = []
        for parquet_file in sorted(candle_dir.glob("*.parquet")):
            df = pq.read_table(parquet_file).to_pandas()
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                frames.append(df)

        if not frames:
            return self._empty_candle_df()

        result = pd.concat(frames, ignore_index=True)
        result = self._filter_time_range(result, start, end)
        return result.sort_values("timestamp").reset_index(drop=True)

    # ================================================================ #
    #  Partition paths (encapsulated — changeable without API impact)   #
    # ================================================================ #

    def _tick_partition_path(self, symbol: str, date: object) -> Path:
        """Compute the Parquet file path for a tick date-partition."""
        return self._raw_dir / symbol / f"{date}.parquet"

    def _candle_partition_path(
        self, symbol: str, timeframe: Timeframe, date: object
    ) -> Path:
        """Compute the Parquet file path for a candle date-partition."""
        return self._processed_dir / symbol / timeframe.value / f"{date}.parquet"

    # ================================================================ #
    #  Internal helpers                                                #
    # ================================================================ #

    def _merge_and_write(
        self,
        path: Path,
        df_new: pd.DataFrame,
        dedup_cols: list[str],
        schema: pa.Schema,
    ) -> int:
        """Merge new data with existing partition, deduplicate, and write.

        Uses a temp-file-then-rename pattern for atomic writes.

        Returns:
            Number of genuinely new records written.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            df_existing = pq.read_table(path).to_pandas()
            df_existing["timestamp"] = pd.to_datetime(
                df_existing["timestamp"], utc=True
            )
            count_before = len(df_existing)
            df_merged = pd.concat([df_existing, df_new], ignore_index=True)
            df_merged = df_merged.drop_duplicates(subset=dedup_cols, keep="first")
            new_count = len(df_merged) - count_before
        else:
            df_merged = df_new.drop_duplicates(subset=dedup_cols, keep="first")
            new_count = len(df_merged)

        df_merged = df_merged.sort_values("timestamp").reset_index(drop=True)

        # Atomic write: temp file → rename
        table = pa.Table.from_pandas(df_merged, schema=schema, preserve_index=False)
        fd, tmp_path = tempfile.mkstemp(
            suffix=".parquet.tmp", dir=str(path.parent)
        )
        os.close(fd)
        try:
            pq.write_table(table, tmp_path)
            # On Windows, remove target before rename
            if path.exists():
                path.unlink()
            Path(tmp_path).rename(path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

        return new_count

    @staticmethod
    def _filter_time_range(
        df: pd.DataFrame,
        start: datetime | None,
        end: datetime | None,
    ) -> pd.DataFrame:
        """Filter DataFrame to the requested ``[start, end)`` time range."""
        if start is not None:
            start_ts = pd.Timestamp(start)
            if start_ts.tzinfo is None:
                start_ts = start_ts.tz_localize("UTC")
            else:
                start_ts = start_ts.tz_convert("UTC")
            df = df[df["timestamp"] >= start_ts]
        if end is not None:
            end_ts = pd.Timestamp(end)
            if end_ts.tzinfo is None:
                end_ts = end_ts.tz_localize("UTC")
            else:
                end_ts = end_ts.tz_convert("UTC")
            df = df[df["timestamp"] < end_ts]
        return df

    @staticmethod
    def _empty_tick_df() -> pd.DataFrame:
        """Return an empty DataFrame with the tick column schema."""
        return pd.DataFrame(
            columns=["symbol", "timestamp", "price", "tick_id", "source", "metadata"]
        )

    @staticmethod
    def _empty_candle_df() -> pd.DataFrame:
        """Return an empty DataFrame with the candle column schema."""
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
