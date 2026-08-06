"""
Project GOAT v0.7 — Market Data Window & Input Context

Defines MarketDataWindow for encapsulating historical bar observation windows
with strict causality, non-empty, and numerical type validation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class MarketDataWindow:
    """Encapsulates a causal, timestamp-indexed market data observation window."""

    def __init__(self, data: pd.DataFrame | dict[str, Any]) -> None:
        """Initialize and validate market data window.

        Args:
            data: DataFrame or dictionary of arrays containing at least OHLCV columns.
        """
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise TypeError(f"MarketDataWindow input must be DataFrame or dict, got '{type(data).__name__}'")

        if df.empty:
            raise ValueError("MarketDataWindow input data cannot be empty")

        # Standardize column names to lowercase
        df.columns = [str(col).lower() for col in df.columns]

        # Check required columns
        required_cols = {"open", "high", "low", "close"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"MarketDataWindow missing required OHLC columns: {sorted(missing)}")

        # Validate timestamp ordering if present
        if "timestamp" in df.columns:
            ts_series = pd.to_datetime(df["timestamp"])
            if not ts_series.is_monotonic_increasing:
                raise ValueError("MarketDataWindow timestamps must be strictly monotonically increasing")

        # Validate price invariants (high >= open, high >= low, high >= close, low <= open, low <= close)
        highs = df["high"].to_numpy(dtype=np.float64)
        lows = df["low"].to_numpy(dtype=np.float64)
        opens = df["open"].to_numpy(dtype=np.float64)
        closes = df["close"].to_numpy(dtype=np.float64)

        if np.any(highs < lows):
            raise ValueError("MarketDataWindow contains invalid price bars where high < low")
        if np.any(highs < opens) or np.any(highs < closes):
            raise ValueError("MarketDataWindow contains invalid price bars where high < max(open, close)")
        if np.any(lows > opens) or np.any(lows > closes):
            raise ValueError("MarketDataWindow contains invalid price bars where low > min(open, close)")

        self._df = df
        self._length = len(df)

    @property
    def length(self) -> int:
        """Return bar length of data window."""
        return self._length

    def get_column(self, col_name: str) -> np.ndarray:
        """Extract a column as IEEE 754 float64 numpy array.

        Args:
            col_name: Name of column (case-insensitive).

        Returns:
            np.ndarray of dtype float64.
        """
        col = col_name.lower()
        if col not in self._df.columns:
            raise KeyError(f"Column '{col_name}' not found in MarketDataWindow")
        return self._df[col].to_numpy(dtype=np.float64)

    @property
    def open(self) -> np.ndarray:
        """Get open price array (float64)."""
        return self.get_column("open")

    @property
    def high(self) -> np.ndarray:
        """Get high price array (float64)."""
        return self.get_column("high")

    @property
    def low(self) -> np.ndarray:
        """Get low price array (float64)."""
        return self.get_column("low")

    @property
    def close(self) -> np.ndarray:
        """Get close price array (float64)."""
        return self.get_column("close")

    @property
    def volume(self) -> np.ndarray:
        """Get volume array (float64). Returns zero array if volume column absent."""
        if "volume" in self._df.columns:
            return self.get_column("volume")
        return np.zeros(self._length, dtype=np.float64)

    def to_dataframe(self) -> pd.DataFrame:
        """Return copy of internal DataFrame."""
        return self._df.copy()
