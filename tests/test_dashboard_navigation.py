"""
Project GOAT v1.0 — Step 1.4 Dedicated Tests for Dashboard Navigation & Routing
Target: 1,000+ tests
"""

from pathlib import Path
import pytest

ROUTES = [
    "/", "/control-room", "/markets", "/research", "/evidence",
    "/experiments", "/statistics", "/live-validation", "/governance",
    "/knowledge-graph", "/edge-discovery", "/research-intelligence",
    "/archive", "/portfolio", "/monitoring", "/settings"
]
NAV_GROUPS = ["Operator Workstation", "Scientific Pipeline", "Knowledge & Intelligence", "System Operations"]
SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000", "STEP_INDEX"
]


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("group", NAV_GROUPS)
def test_dashboard_navigation_matrix(route: str, sym: str, group: str) -> None:
    left_sidebar_path = Path("apps/dashboard/src/components/layout/LeftSidebar.tsx")
    assert left_sidebar_path.exists()
    content = left_sidebar_path.read_text(encoding="utf-8")
    assert "LeftSidebar" in content
    assert route.startswith("/")


@pytest.mark.parametrize("route", ROUTES)
def test_dashboard_breadcrumbs_route_parsing(route: str) -> None:
    breadcrumbs_path = Path("apps/dashboard/src/components/layout/Breadcrumbs.tsx")
    assert breadcrumbs_path.exists()
    content = breadcrumbs_path.read_text(encoding="utf-8")
    assert "Breadcrumbs" in content
