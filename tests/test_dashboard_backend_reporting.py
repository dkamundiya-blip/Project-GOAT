"""
Project GOAT v1.0 — Test Suite: Dashboard Backend Reporting
"""

import json
import pytest

from goat.dashboard.core.enums import ServerStatus
from goat.dashboard.core.models import DashboardHealthStatus, DashboardSession
from goat.dashboard.reporting.reports import (
    generate_dashboard_json_report,
    generate_dashboard_session_report,
)

STATUSES = list(ServerStatus)


@pytest.mark.parametrize("status", STATUSES)
def test_generate_dashboard_reports_matrix(status):
    session = DashboardSession(
        session_id="DSH_0123456789ABCDEF",
        host="127.0.0.1",
        port=8000,
        status=status,
        start_time="2026-08-06T12:00:00Z",
    )
    health = DashboardHealthStatus(
        status=status,
        uptime_seconds=120.0,
        active_ws_clients=2,
        system_memory_mb=128.5,
        database_status="HEALTHY",
        frozen_backend_version="v0.9.1",
    )

    md = generate_dashboard_session_report(session, health)
    assert "# PROJECT GOAT v1.0 — DASHBOARD BACKEND SESSION REPORT" in md
    assert "DSH_0123456789ABCDEF" in md
    assert status.value in md

    js = generate_dashboard_json_report(session, health)
    data = json.loads(js)
    assert data["session"]["session_id"] == "DSH_0123456789ABCDEF"
    assert data["health"]["frozen_backend_version"] == "v0.9.1"
