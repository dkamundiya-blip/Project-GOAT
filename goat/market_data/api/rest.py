"""
Project GOAT v1.0 — Market Data Subsystem REST Handlers

REST API handlers exposing market status, live quotes, recent ticks, candles, operator control actions,
and operational telemetry snapshots.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict
from goat.dashboard.core.canonical import compute_api_payload_id
from goat.dashboard.core.models import APIResponsePayload
from goat.market_data.engine import LiveMarketDataIngestionEngine


class MarketDataRESTHandler:
    """REST endpoint logic handlers for Market Data Subsystem."""

    def __init__(self, engine: LiveMarketDataIngestionEngine):
        self.engine = engine

    def get_status(self) -> APIResponsePayload:
        """GET /api/v1/market-data/status"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        telemetry = self.engine.get_telemetry_snapshot()
        data = {
            "connection_state": self.engine.ws_manager.connection_state,
            "uptime_seconds": self.engine.ws_manager.uptime_seconds,
            "subscribed_symbols": self.engine.ws_manager.subscribed_symbols,
            "total_ticks_received": telemetry.total_ticks_received,
            "ticks_per_second": telemetry.ticks_per_second,
            "reconnect_count": telemetry.reconnect_count,
            "dropped_packets": telemetry.dropped_packets,
        }
        payload_id = compute_api_payload_id("/api/v1/market-data/status", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/market-data/status",
            status_code=200,
            timestamp=now,
            data=data,
            meta={"frozen_backend": "v1.0.0"},
        )

    def get_symbols(self) -> APIResponsePayload:
        """GET /api/v1/market-data/symbols"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        quotes = self.engine.get_all_quotes()
        data_list = [q.model_dump() for q in quotes]
        payload_id = compute_api_payload_id("/api/v1/market-data/symbols", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/market-data/symbols",
            status_code=200,
            timestamp=now,
            data={"symbols": data_list, "count": len(data_list)},
            meta={"frozen_backend": "v1.0.0"},
        )

    def get_symbol_detail(self, symbol_id: str) -> APIResponsePayload:
        """GET /api/v1/market-data/symbol/{symbol_id}"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        quote = self.engine.get_symbol_quote(symbol_id)
        payload_id = compute_api_payload_id(f"/api/v1/market-data/symbol/{symbol_id}", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route=f"/api/v1/market-data/symbol/{symbol_id}",
            status_code=200,
            timestamp=now,
            data=quote.model_dump(),
            meta={"frozen_backend": "v1.0.0"},
        )

    def get_ticks(self, symbol_id: str, limit: int = 50) -> APIResponsePayload:
        """GET /api/v1/market-data/ticks/{symbol_id}"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        ticks = self.engine.get_recent_ticks(symbol_id, limit=limit)
        data_list = [t.model_dump() for t in ticks]
        payload_id = compute_api_payload_id(f"/api/v1/market-data/ticks/{symbol_id}", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route=f"/api/v1/market-data/ticks/{symbol_id}",
            status_code=200,
            timestamp=now,
            data={"symbol": symbol_id, "ticks": data_list, "count": len(data_list)},
            meta={"frozen_backend": "v1.0.0"},
        )

    def get_latest_candle(self, symbol_id: str, timeframe: str = "1M") -> APIResponsePayload:
        """GET /api/v1/market-data/candles/latest/{symbol_id}?timeframe=1M"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        candle = self.engine.get_latest_candle(symbol_id, timeframe=timeframe)
        data = candle.model_dump() if candle else None
        payload_id = compute_api_payload_id(f"/api/v1/market-data/candles/latest/{symbol_id}", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route=f"/api/v1/market-data/candles/latest/{symbol_id}",
            status_code=200,
            timestamp=now,
            data={"symbol": symbol_id, "timeframe": timeframe, "candle": data},
            meta={"frozen_backend": "v1.0.0"},
        )

    def get_historical_candles(
        self, symbol_id: str, timeframe: str = "1M", limit: int = 100
    ) -> APIResponsePayload:
        """GET /api/v1/market-data/candles/history/{symbol_id}?timeframe=1M&limit=100"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        candles = self.engine.get_historical_candles(symbol_id, timeframe=timeframe, limit=limit)
        data_list = [c.model_dump() for c in candles]
        payload_id = compute_api_payload_id(f"/api/v1/market-data/candles/history/{symbol_id}", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route=f"/api/v1/market-data/candles/history/{symbol_id}",
            status_code=200,
            timestamp=now,
            data={
                "symbol": symbol_id,
                "timeframe": timeframe,
                "candles": data_list,
                "count": len(data_list),
            },
            meta={"frozen_backend": "v1.0.0"},
        )

    def get_metrics(self) -> APIResponsePayload:
        """GET /api/v1/market-data/metrics"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        telemetry = self.engine.get_telemetry_snapshot()
        payload_id = compute_api_payload_id("/api/v1/market-data/metrics", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/market-data/metrics",
            status_code=200,
            timestamp=now,
            data=telemetry.model_dump(),
            meta={"frozen_backend": "v1.0.0"},
        )

    async def post_connect(self) -> APIResponsePayload:
        """POST /api/v1/market-data/connect"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        success = await self.engine.connect_feed()
        payload_id = compute_api_payload_id("/api/v1/market-data/connect", now, 200 if success else 500)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/market-data/connect",
            status_code=200 if success else 500,
            timestamp=now,
            data={"success": success, "connection_state": self.engine.ws_manager.connection_state},
            meta={"frozen_backend": "v1.0.0"},
        )

    async def post_disconnect(self) -> APIResponsePayload:
        """POST /api/v1/market-data/disconnect"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        await self.engine.disconnect_feed()
        payload_id = compute_api_payload_id("/api/v1/market-data/disconnect", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/market-data/disconnect",
            status_code=200,
            timestamp=now,
            data={"success": True, "connection_state": self.engine.ws_manager.connection_state},
            meta={"frozen_backend": "v1.0.0"},
        )

    async def post_reconnect(self) -> APIResponsePayload:
        """POST /api/v1/market-data/reconnect"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        success = await self.engine.reconnect_feed()
        payload_id = compute_api_payload_id("/api/v1/market-data/reconnect", now, 200 if success else 500)
        return APIResponsePayload(
            payload_id=payload_id,
            route="/api/v1/market-data/reconnect",
            status_code=200 if success else 500,
            timestamp=now,
            data={"success": success, "connection_state": self.engine.ws_manager.connection_state},
            meta={"frozen_backend": "v1.0.0"},
        )

    async def post_subscribe(self, symbol_id: str) -> APIResponsePayload:
        """POST /api/v1/market-data/subscribe/{symbol_id}"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        success = await self.engine.subscribe(symbol_id)
        payload_id = compute_api_payload_id(f"/api/v1/market-data/subscribe/{symbol_id}", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route=f"/api/v1/market-data/subscribe/{symbol_id}",
            status_code=200,
            timestamp=now,
            data={"symbol": symbol_id, "success": success},
            meta={"frozen_backend": "v1.0.0"},
        )

    async def post_unsubscribe(self, symbol_id: str) -> APIResponsePayload:
        """POST /api/v1/market-data/unsubscribe/{symbol_id}"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        success = await self.engine.unsubscribe(symbol_id)
        payload_id = compute_api_payload_id(f"/api/v1/market-data/unsubscribe/{symbol_id}", now, 200)
        return APIResponsePayload(
            payload_id=payload_id,
            route=f"/api/v1/market-data/unsubscribe/{symbol_id}",
            status_code=200,
            timestamp=now,
            data={"symbol": symbol_id, "success": success},
            meta={"frozen_backend": "v1.0.0"},
        )
