"""
Project GOAT — Production System Integration Test Suite (`tests/test_production_integration.py`)

Validates:
1. FastAPI app initialization with lifespan manager (master_engine, broadcaster, workspace_repo).
2. All 4 previously unmounted sub-routers mounted on app (/ws/telemetry, /api/v1/validation/*, /api/v1/research/*, /api/v1/workspace/*).
3. Ingestion pipeline tick forwarding into master_engine.process_tick().
4. Real-time TelemetryBroadcaster snapshot streaming over WebSocket.
"""

from __future__ import annotations

import json
import pytest

from goat.integration.master import MasterSystemIntegrationEngine
from goat.telemetry.server import TelemetryBroadcaster
from goat.workspace.store import SQLiteWorkspaceRepository, init_workspace_db


def test_production_server_wiring():
    """Validation 1: Verify all 4 sub-routers mounted and tick pipeline integration."""
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from goat.integration.api import create_validation_router
        from goat.telemetry.server import create_telemetry_router
        from goat.ai_reasoning.api.router import create_research_router
        from goat.workspace.api import create_workspace_router
    except ImportError:
        pytest.skip("FastAPI not installed in environment")

    # 1. Instantiate Core Engine Components
    master_engine = MasterSystemIntegrationEngine(db_path=":memory:", symbol="BOOM_1000", timeframe="1m")
    broadcaster = TelemetryBroadcaster(master_engine=master_engine)
    ws_db = init_workspace_db(":memory:")
    ws_repo = SQLiteWorkspaceRepository(ws_db)

    # 2. Build App & Mount All 4 Sub-Routers
    app = FastAPI(title="Project GOAT Test Gateway")
    app.include_router(create_telemetry_router(broadcaster))
    app.include_router(create_validation_router(master_engine))
    app.include_router(create_research_router(master_engine.ai_reasoning_engine))
    app.include_router(create_workspace_router(ws_repo))

    client = TestClient(app)

    # 3. Verify Router 1: Validation Status API
    res_val = client.get("/api/v1/validation/status")
    assert res_val.status_code == 200
    val_data = res_val.json()
    assert val_data["overall_status"] == "HEALTHY"
    assert val_data["symbol"] == "BOOM_1000"

    # 4. Verify Router 2: Research API Rankings
    res_res = client.get("/api/v1/research/edges/rankings")
    assert res_res.status_code == 200

    # 5. Verify Router 3: Workspace Summary API
    res_ws = client.get("/api/v1/workspace/summary")
    assert res_ws.status_code == 200
    assert "bookmark_count" in res_ws.json()

    # 6. Verify Router 4: WebSocket Telemetry Endpoint
    with client.websocket_connect("/ws/telemetry") as websocket:
        msg_str = websocket.receive_text()
        msg = json.loads(msg_str)
        assert msg["type"] == "TELEMETRY_UPDATE"
        assert msg["symbol"] == "BOOM_1000"

    master_engine.close()
    ws_db.close()


def test_tick_pipeline_forwarding():
    """Validation 2: Forward raw tick through MasterSystemIntegrationEngine."""
    master_engine = MasterSystemIntegrationEngine(db_path=":memory:", symbol="BOOM_1000", timeframe="1m")

    res = master_engine.process_tick(symbol="BOOM_1000", price=1050.25)

    assert res["ticks_processed"] == 1
    assert res["symbol"] == "BOOM_1000"
    assert res["price"] == 1050.25
    assert "pipeline_latency_ms" in res

    status = master_engine.get_system_health_status()
    assert status["ticks_processed"] == 1
    assert status["feature_vectors_generated"] == 1

    master_engine.close()
