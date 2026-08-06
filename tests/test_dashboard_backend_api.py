"""
Project GOAT v1.0 — Test Suite: Dashboard Backend REST API Handlers & Router
"""

import pytest

from goat.dashboard.api.router import create_dashboard_router
from goat.dashboard.persistence.sqlite import DashboardReadOnlyRepositoryAdapter
from goat.dashboard.telemetry.collector import SystemTelemetryCollector


@pytest.fixture
def api_router():
    repo = DashboardReadOnlyRepositoryAdapter()
    collector = SystemTelemetryCollector()
    return create_dashboard_router(repo=repo, collector=collector)


def test_api_health_endpoint(api_router):
    res = api_router.dispatch("/health")
    assert res is not None
    assert res.status == "RUNNING"
    assert res.frozen_backend_version == "v0.9.1"


def test_api_summary_endpoint(api_router):
    res = api_router.dispatch("/api/v1/summary")
    assert res is not None
    assert res.payload_id.startswith("DAP_")
    assert res.data["database_status"] == "ONLINE_READ_ONLY"


def test_api_hypotheses_endpoint(api_router):
    res = api_router.dispatch("/api/v1/hypotheses", limit=10)
    assert res is not None
    assert res.payload_id.startswith("DAP_")
    assert "hypotheses" in res.data


def test_api_governance_endpoint(api_router):
    res = api_router.dispatch("/api/v1/governance", limit=10)
    assert res is not None
    assert res.payload_id.startswith("DAP_")
    assert "decisions" in res.data


def test_api_symbols_endpoint(api_router):
    res = api_router.dispatch("/api/v1/symbols")
    assert res is not None
    assert res.payload_id.startswith("DAP_")
    assert len(res.data["symbols"]) == 12
