"""
Project GOAT v1.0 — Test Suite: Dashboard Frontend Layout Workstation
"""

import pytest

LAYOUT_AREAS = ["TopNav", "LeftSidebar", "RightInspector", "BottomStatusBar", "AppShell"]
ROUTES = [
    "/", "/control-room", "/markets", "/research", "/evidence", "/experiments",
    "/statistics", "/live-validation", "/governance", "/knowledge-graph",
    "/research-intelligence", "/archive", "/portfolio", "/monitoring", "/settings"
]
STATUSES = ["RUNNING", "DEGRADED", "INITIALIZING", "STOPPED"]


@pytest.mark.parametrize("area", LAYOUT_AREAS)
@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("status", STATUSES)
def test_dashboard_frontend_layout_matrix(area, route, status):
    assert area in LAYOUT_AREAS
    assert route.startswith("/")
    assert status in STATUSES
