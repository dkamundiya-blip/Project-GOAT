"""
Project GOAT v1.0 — Test Suite: Master Dashboard Backend Server
"""

import pytest

from goat.dashboard.core.enums import ServerStatus
from goat.dashboard.server import MasterDashboardServer

PORTS = [8000, 8080, 9000]


@pytest.mark.parametrize("port", PORTS)
def test_master_dashboard_server_matrix(port):
    server = MasterDashboardServer(host="127.0.0.1", port=port)
    assert server.port == port
    assert server.status == ServerStatus.RUNNING

    session = server.get_session()
    assert session.session_id.startswith("DSH_")
    assert session.port == port
    assert session.status == ServerStatus.RUNNING

    health = server.get_health()
    assert health.status == ServerStatus.RUNNING
    assert health.frozen_backend_version == "v0.9.1"

    md = server.generate_markdown_report()
    assert "DASHBOARD BACKEND SESSION REPORT" in md

    js = server.generate_json_report()
    assert "DSH_" in js
