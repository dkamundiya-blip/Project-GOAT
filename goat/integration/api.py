"""
Project GOAT Phase 7.5 — System Validation REST API (`goat.integration.api`)

FastAPI router exposing live subsystem health status, latency benchmarks, symbol/timeframe switching,
and failure recovery controls for the System Validation Dashboard Page.
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


def create_validation_router(master_integration_engine: Any) -> Any:
    """Create FastAPI router exposing System Validation endpoints."""
    if not _HAS_FASTAPI:
        raise RuntimeError("FastAPI is required to instantiate validation REST router.")

    router = APIRouter(prefix="/api/v1/validation", tags=["System Live Validation"])

    @router.get("/status")
    def get_system_validation_status():
        """Retrieve real-time live health, latency, error count, and throughput across all 9 components."""
        return master_integration_engine.get_system_health_status()

    @router.post("/symbol")
    def switch_active_symbol(symbol: str = Query(..., description="Target instrument symbol (e.g. BOOM_1000, VOLATILITY_100)")):
        """Switch active monitoring symbol across all 7 engine layers."""
        master_integration_engine.switch_symbol(symbol)
        return {"status": "SUCCESS", "active_symbol": master_integration_engine.symbol}

    @router.post("/timeframe")
    def switch_active_timeframe(timeframe: str = Query(..., description="Target timeframe resolution (1m, 5m, 15m, 30m, 1H, 4H, 1D)")):
        """Switch active candle & feature evaluation timeframe."""
        master_integration_engine.switch_timeframe(timeframe)
        return {"status": "SUCCESS", "active_timeframe": master_integration_engine.timeframe}

    @router.post("/simulate-failure")
    def simulate_component_failure(component: str = Query(..., description="Target component key")):
        """Simulate component failure to verify UI & pipeline fault tolerance."""
        master_integration_engine.simulate_failure(component)
        return {"status": "SUCCESS", "component": component, "health_state": "FAILED"}

    @router.post("/recover-failure")
    def recover_component_failure(component: str = Query(..., description="Target component key")):
        """Recover simulated component failure."""
        master_integration_engine.recover_failure(component)
        return {"status": "SUCCESS", "component": component, "health_state": "HEALTHY"}

    return router
