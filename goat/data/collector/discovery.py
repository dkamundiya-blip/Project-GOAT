"""
Project GOAT v0.2 — Deriv Symbol Discovery

Discovers available synthetic market instruments from Deriv API and filters
them according to configurable collection scope allowlists.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from goat.data.collector.deriv_schemas import DerivSymbolMetadata
from goat.logging import get_logger

if TYPE_CHECKING:
    from goat.data.collector.deriv import DerivMarketDataCollector

_log = get_logger("collector.discovery")


class DerivSymbolDiscovery:
    """Discovers and parses synthetic symbols from Deriv WebSocket API.

    Args:
        collector: Active or instantiated DerivMarketDataCollector.
    """

    def __init__(self, collector: DerivMarketDataCollector) -> None:
        self._collector = collector

    async def fetch_active_symbols(
        self,
        allowlist: list[str] | None = None,
    ) -> list[DerivSymbolMetadata]:
        """Request active symbols from provider and return normalized metadata list.

        Args:
            allowlist: Optional list of provider symbol strings (e.g. ``["R_10", "R_75"]``).
                       If provided, only matching symbols will be returned.

        Returns:
            List of ``DerivSymbolMetadata`` objects.
        """
        _log.info("discovering_active_symbols", allowlist=allowlist)

        raw_response = await self._collector.request(
            {"active_symbols": "brief", "product_type": "basic"}
        )

        active_symbols_raw = raw_response.get("active_symbols")
        if not isinstance(active_symbols_raw, list):
            _log.warning("invalid_active_symbols_response", raw_response=raw_response)
            return []

        discovered: list[DerivSymbolMetadata] = []
        allowlist_set = set(allowlist) if allowlist else None

        for item in active_symbols_raw:
            if not isinstance(item, dict):
                continue
            try:
                meta = DerivSymbolMetadata.from_active_symbol_dict(item)
                if allowlist_set is None or meta.symbol in allowlist_set:
                    discovered.append(meta)
            except Exception as exc:
                _log.debug("failed_to_parse_symbol_item", item=item, error=str(exc))

        _log.info(
            "active_symbols_discovered",
            total_discovered=len(discovered),
            allowlist_filter=bool(allowlist),
        )
        return discovered
