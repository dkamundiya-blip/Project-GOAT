"""
Unit tests for FastAPI Research API router endpoints.
"""

import pytest

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

from goat.ai_reasoning.engine import MasterAIReasoningEngine
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)


def test_research_api_endpoints():
    if not _HAS_FASTAPI:
        pytest.skip("FastAPI is not installed in the testing environment.")

    engine = MasterAIReasoningEngine()

    edge = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength"],
        supported_symbols=["STEP_INDEX"],
        supported_timeframes=["1m"],
        metrics=EdgePerformanceMetrics(
            sample_size=100,
            win_rate=0.6,
            loss_rate=0.4,
            expected_value=0.005,
            average_return=0.005,
            median_return=0.004,
            max_gain=0.02,
            max_loss=0.01,
            profit_factor=2.0,
            sharpe_ratio=2.5,
            sortino_ratio=3.0,
            calmar_ratio=4.0,
            max_drawdown=0.05,
            recovery_factor=5.0,
            trade_frequency=10.0,
            holding_period=5.0,
        ),
        p_value=0.01,
        confidence_interval_low=0.002,
        confidence_interval_high=0.008,
        effect_size=0.8,
        composite_score=0.85,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash="HASH",
    )
    engine.ingest_edge(edge)

    app = FastAPI()
    app.include_router(engine.get_router())
    client = TestClient(app)

    # 1. GET /api/v1/research/explain/EDG_0000000000000001
    resp_exp = client.get("/api/v1/research/explain/EDG_0000000000000001?level=PROFESSIONAL_QUANT")
    assert resp_exp.status_code == 200
    assert resp_exp.json()["edge_id"] == "EDG_0000000000000001"

    # 2. GET /api/v1/research/report/EDG_0000000000000001
    resp_rep = client.get("/api/v1/research/report/EDG_0000000000000001")
    assert resp_rep.status_code == 200
    assert resp_rep.json()["report_id"].startswith("REP_")

    # 3. GET /api/v1/research/evidence/EDG_0000000000000001
    resp_ev = client.get("/api/v1/research/evidence/EDG_0000000000000001")
    assert resp_ev.status_code == 200
    assert resp_ev.json()["bundle_id"].startswith("EVB_")

    # 4. GET /api/v1/research/graph/summary
    resp_graph = client.get("/api/v1/research/graph/summary")
    assert resp_graph.status_code == 200
    assert resp_graph.json()["node_count"] > 0

    # 5. GET /api/v1/research/ranking
    resp_rank = client.get("/api/v1/research/ranking")
    assert resp_rank.status_code == 200
    assert len(resp_rank.json()) == 1
