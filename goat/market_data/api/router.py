"""
Project GOAT v1.0 — Market Data Router Specification
"""

from typing import Any, Callable, Dict, Optional
from goat.market_data.api.rest import MarketDataRESTHandler
from goat.market_data.engine import LiveMarketDataIngestionEngine


class MarketDataAPIRouter:
    """Independent API Router dispatching Market Data REST routes."""

    def __init__(self, engine: LiveMarketDataIngestionEngine):
        self.handler = MarketDataRESTHandler(engine)
        self.sync_routes: Dict[str, Callable[..., Any]] = {
            "/api/v1/market-data/status": self.handler.get_status,
            "/api/v1/market-data/symbols": self.handler.get_symbols,
            "/api/v1/market-data/metrics": self.handler.get_metrics,
        }
        self.async_routes: Dict[str, Callable[..., Any]] = {
            "/api/v1/market-data/connect": self.handler.post_connect,
            "/api/v1/market-data/disconnect": self.handler.post_disconnect,
            "/api/v1/market-data/reconnect": self.handler.post_reconnect,
        }

    def dispatch(self, path: str, **kwargs: Any) -> Optional[Any]:
        """Dispatch synchronous route."""
        if route_fn := self.sync_routes.get(path):
            return route_fn(**kwargs) if kwargs else route_fn()

        if path.startswith("/api/v1/market-data/symbol/"):
            symbol_id = path.replace("/api/v1/market-data/symbol/", "")
            return self.handler.get_symbol_detail(symbol_id)

        if path.startswith("/api/v1/market-data/ticks/"):
            symbol_id = path.replace("/api/v1/market-data/ticks/", "")
            limit = kwargs.get("limit", 50)
            return self.handler.get_ticks(symbol_id, limit=limit)

        if path.startswith("/api/v1/market-data/candles/latest/"):
            symbol_id = path.replace("/api/v1/market-data/candles/latest/", "")
            tf = kwargs.get("timeframe", "1M")
            return self.handler.get_latest_candle(symbol_id, timeframe=tf)

        if path.startswith("/api/v1/market-data/candles/history/"):
            symbol_id = path.replace("/api/v1/market-data/candles/history/", "")
            tf = kwargs.get("timeframe", "1M")
            limit = kwargs.get("limit", 100)
            return self.handler.get_historical_candles(symbol_id, timeframe=tf, limit=limit)

        return None

    async def dispatch_async(self, path: str, **kwargs: Any) -> Optional[Any]:
        """Dispatch asynchronous route."""
        if route_fn := self.async_routes.get(path):
            return await route_fn(**kwargs) if kwargs else await route_fn()

        if path.startswith("/api/v1/market-data/subscribe/"):
            symbol_id = path.replace("/api/v1/market-data/subscribe/", "")
            return await self.handler.post_subscribe(symbol_id)

        if path.startswith("/api/v1/market-data/unsubscribe/"):
            symbol_id = path.replace("/api/v1/market-data/unsubscribe/", "")
            return await self.handler.post_unsubscribe(symbol_id)

        return None
