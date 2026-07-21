"""
Project GOAT v0.2 — Deriv Historical Data Import

Retrieves historical tick (and candle) observations from Deriv API via ticks_history.
Normalizes data into canonical GOAT Tick schemas with explicit DataSource.HISTORICAL_IMPORT
provenance, paginating long ranges safely within rate limits.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from goat.data.schemas import DataSource, Tick
from goat.logging import get_logger

if TYPE_CHECKING:
    from goat.data.collector.deriv import DerivMarketDataCollector
    from goat.data.storage.parquet import ParquetStorage

_log = get_logger("historical.deriv")


class DerivHistoricalImporter:
    """Historical data importer leveraging Deriv ticks_history endpoint.

    Args:
        collector: Connected DerivMarketDataCollector instance.
        storage: Optional ParquetStorage instance for automatic persistence.
    """

    def __init__(
        self,
        collector: DerivMarketDataCollector,
        storage: ParquetStorage | None = None,
    ) -> None:
        self._collector = collector
        self._storage = storage

    async def fetch_historical_ticks(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        chunk_size: int = 1000,
        throttle_delay: float = 0.1,
    ) -> list[Tick]:
        """Fetch historical ticks for a symbol between start and end times.

        Paginates in chunks if requested count exceeds single query limits.

        Args:
            symbol: Instrument identifier (e.g. ``"R_75"``).
            start: Start of historical window (inclusive), UTC.
            end: End of historical window (inclusive), UTC.
            chunk_size: Max ticks per query (Deriv default limit is 5000, recommended 1000).
            throttle_delay: Seconds pause between paginated requests to respect rate limits.

        Returns:
            List of ``Tick`` objects tagged with ``DataSource.HISTORICAL_IMPORT``.
        """
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        start_epoch = int(start_utc.timestamp())
        end_epoch = int(end_utc.timestamp())

        _log.info(
            "fetching_historical_ticks",
            symbol=symbol,
            start=start_utc.isoformat(),
            end=end_utc.isoformat(),
        )

        all_ticks: list[Tick] = []
        current_start_epoch = start_epoch

        while current_start_epoch < end_epoch:
            payload: dict[str, Any] = {
                "ticks_history": symbol,
                "start": current_start_epoch,
                "end": end_epoch,
                "style": "ticks",
                "count": chunk_size,
            }

            resp = await self._collector.request(payload)

            if "error" in resp:
                err_msg = resp["error"].get("message", "Unknown ticks_history error")
                _log.error("ticks_history_error", symbol=symbol, error=err_msg)
                raise RuntimeError(f"Historical import error for {symbol}: {err_msg}")

            history = resp.get("history")
            if not isinstance(history, dict):
                _log.info("no_more_historical_ticks", symbol=symbol)
                break

            prices = history.get("prices", [])
            times = history.get("times", [])

            if not prices or not times or len(prices) != len(times):
                break

            chunk_ticks: list[Tick] = []
            max_epoch_seen = current_start_epoch

            for price_val, time_val in zip(prices, times, strict=False):
                epoch_int = int(time_val)
                if epoch_int > max_epoch_seen:
                    max_epoch_seen = epoch_int

                dt = datetime.fromtimestamp(epoch_int, tz=timezone.utc)
                tick = Tick(
                    symbol=symbol,
                    timestamp=dt,
                    price=Decimal(str(price_val)),
                    source=DataSource.HISTORICAL_IMPORT,
                    metadata={"provider": "deriv", "query": "ticks_history"},
                )
                chunk_ticks.append(tick)

            all_ticks.extend(chunk_ticks)

            # Prevent infinite pagination loops
            if max_epoch_seen <= current_start_epoch:
                break
            current_start_epoch = max_epoch_seen + 1

            if throttle_delay > 0:
                await asyncio.sleep(throttle_delay)

        _log.info(
            "historical_ticks_imported",
            symbol=symbol,
            total_ticks=len(all_ticks),
        )

        # Automatically store if storage component is supplied
        if self._storage and all_ticks:
            self._storage.write_ticks(symbol, all_ticks)

        return all_ticks
