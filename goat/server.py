"""
Project GOAT v1.1 — Production ASGI FastAPI Server & Gateway

Central ASGI application orchestrating:
- Live Deriv Market Data Ingestion Engine (LiveMarketDataIngestionEngine)
- Automatic WebSocket connection & feed subscription on startup
- CORS middleware for multi-origin dashboard access
- Production REST API endpoints (/api/v1/market-data/* and /api/v1/*)
- Real-time WebSocket streaming gateway (/api/v1/market-data/ws)
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from goat.logging import get_logger
from goat.market_data.engine import LiveMarketDataIngestionEngine
from goat.market_data.api.rest import MarketDataRESTHandler
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.telemetry.collector import SystemTelemetryCollector
from goat.dashboard.api.rest import DashboardRESTHandler

_log = get_logger("goat.server")

# Global Engine & Handler References
engine: LiveMarketDataIngestionEngine | None = None
market_handler: MarketDataRESTHandler | None = None
dashboard_handler: DashboardRESTHandler | None = None
connected_websockets: set[WebSocket] = set()


async def broadcast_tick_to_websockets(raw_payload: dict[str, Any]) -> None:
    """Broadcast incoming live Deriv tick to all connected WebSocket clients."""
    if not connected_websockets:
        return
    disconnected = set()
    for ws in list(connected_websockets):
        try:
            await ws.send_json(raw_payload)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        connected_websockets.discard(ws)


async def on_tick_pipeline_wrapper(raw_payload: dict[str, Any]) -> None:
    """Master tick pipeline handler: Normalizes tick into engine & broadcasts to browser WebSockets."""
    if engine:
        await engine._on_raw_tick_received(raw_payload)
    await broadcast_tick_to_websockets(raw_payload)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: Start Live Market Engine on startup & stop on shutdown."""
    global engine, market_handler, dashboard_handler
    _log.info("starting_goat_production_server")

    # 1. Initialize Ingestion Engine
    engine = LiveMarketDataIngestionEngine(db_path=":memory:")
    await engine.start()

    # 2. Register tick callback pipeline wrapper (Engine pipeline + Browser WebSocket broadcast)
    engine.ws_manager.set_on_tick_callback(on_tick_pipeline_wrapper)

    # 3. Connect Feed & Subscribe All Symbols
    feed_connected = await engine.connect_feed()
    if feed_connected:
        _log.info("deriv_feed_connected_successfully")
        subscribed_count = await engine.subscribe_all()
        _log.info("subscribed_initial_symbols", count=subscribed_count)
    else:
        _log.warning("deriv_feed_connection_degraded")

    # 4. Initialize REST Handlers
    market_handler = MarketDataRESTHandler(engine=engine)

    repo = DashboardReadOnlyRepositoryAdapter(":memory:")
    collector = SystemTelemetryCollector()
    dashboard_handler = DashboardRESTHandler(repo=repo, collector=collector)

    yield

    # Shutdown Workflow
    _log.info("stopping_goat_production_server")
    if engine:
        await engine.stop()
    _log.info("goat_production_server_stopped")


app = FastAPI(
    title="Project GOAT — Institutional Trading Platform API",
    description="Live Deriv Market Data Ingestion & Institutional Dashboard API",
    version="1.1.0",
    lifespan=lifespan,
)

# Enable CORS for frontend clients (Vite dev server, Netlify deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper to convert Pydantic APIResponsePayload to FastAPI JSONResponse
def _to_json_response(payload: Any) -> JSONResponse:
    if hasattr(payload, "model_dump"):
        content = payload.model_dump()
    elif isinstance(payload, dict):
        content = payload
    else:
        content = str(payload)
    status_code = getattr(payload, "status_code", 200)
    return JSONResponse(content=content, status_code=status_code)


# =====================================================================
# SYSTEM & HEALTH ENDPOINTS
# =====================================================================

@app.get("/api/v1/health")
@app.get("/health")
def get_health():
    if dashboard_handler:
        res = dashboard_handler.get_health()
        return res.model_dump()
    return {"status": "RUNNING", "backend": "v1.1.0"}


@app.get("/api/v1/summary")
def get_summary():
    if not dashboard_handler:
        raise HTTPException(status_code=500, detail="Dashboard handler not initialized")
    return _to_json_response(dashboard_handler.get_summary())


@app.get("/api/v1/hypotheses")
def get_hypotheses(limit: int = Query(default=50, ge=1, le=500)):
    if not dashboard_handler:
        raise HTTPException(status_code=500, detail="Dashboard handler not initialized")
    return _to_json_response(dashboard_handler.get_hypotheses(limit=limit))


@app.get("/api/v1/governance")
def get_governance(limit: int = Query(default=50, ge=1, le=500)):
    if not dashboard_handler:
        raise HTTPException(status_code=500, detail="Dashboard handler not initialized")
    return _to_json_response(dashboard_handler.get_governance(limit=limit))


# =====================================================================
# MARKET DATA REST ENDPOINTS
# =====================================================================

@app.get("/api/v1/market-data/status")
def get_market_status():
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(market_handler.get_status())


@app.get("/api/v1/market-data/symbols")
def get_market_symbols():
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(market_handler.get_symbols())


@app.get("/api/v1/market-data/symbol/{symbol_id}")
def get_market_symbol_detail(symbol_id: str):
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(market_handler.get_symbol_detail(symbol_id))


@app.get("/api/v1/market-data/ticks/{symbol_id}")
def get_market_ticks(symbol_id: str, limit: int = Query(default=50, ge=1, le=500)):
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(market_handler.get_ticks(symbol_id, limit=limit))


@app.get("/api/v1/market-data/candles/latest/{symbol_id}")
def get_market_latest_candle(symbol_id: str, timeframe: str = Query(default="1M")):
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(market_handler.get_latest_candle(symbol_id, timeframe=timeframe))


@app.get("/api/v1/market-data/candles/history/{symbol_id}")
def get_market_historical_candles(
    symbol_id: str,
    timeframe: str = Query(default="1M"),
    limit: int = Query(default=100, ge=1, le=1000),
):
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(
        market_handler.get_historical_candles(symbol_id, timeframe=timeframe, limit=limit)
    )


@app.get("/api/v1/market-data/metrics")
def get_market_metrics():
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    return _to_json_response(market_handler.get_metrics())


# =====================================================================
# OPERATOR CONTROL ENDPOINTS
# =====================================================================

@app.post("/api/v1/market-data/connect")
async def post_market_connect():
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    res = await market_handler.post_connect()
    return _to_json_response(res)


@app.post("/api/v1/market-data/disconnect")
async def post_market_disconnect():
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    res = await market_handler.post_disconnect()
    return _to_json_response(res)


@app.post("/api/v1/market-data/reconnect")
async def post_market_reconnect():
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    res = await market_handler.post_reconnect()
    return _to_json_response(res)


@app.post("/api/v1/market-data/subscribe/{symbol_id}")
async def post_market_subscribe(symbol_id: str):
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    res = await market_handler.post_subscribe(symbol_id)
    return _to_json_response(res)


@app.post("/api/v1/market-data/unsubscribe/{symbol_id}")
async def post_market_unsubscribe(symbol_id: str):
    if not market_handler:
        raise HTTPException(status_code=500, detail="Market handler not initialized")
    res = await market_handler.post_unsubscribe(symbol_id)
    return _to_json_response(res)


# =====================================================================
# REALTIME BROWSER WEBSOCKET GATEWAY
# =====================================================================

@app.websocket("/api/v1/market-data/ws")
async def websocket_stream_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint streaming live Deriv ticks directly to browser UI."""
    await websocket.accept()
    connected_websockets.add(websocket)
    _log.info("browser_websocket_client_connected", count=len(connected_websockets))

    try:
        while True:
            # Keep connection alive & await client messages if any
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)
        _log.info("browser_websocket_client_disconnected", count=len(connected_websockets))
    except Exception as exc:
        connected_websockets.discard(websocket)
        _log.warning("browser_websocket_client_error", error=str(exc))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("goat.server:app", host="0.0.0.0", port=8000, reload=False)
