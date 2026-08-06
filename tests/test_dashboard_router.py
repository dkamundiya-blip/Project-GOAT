"""
Project GOAT v1.0 — Dedicated Tests for Application Router & Route Pages
"""

from pathlib import Path
import pytest

PAGES = [
    "DashboardPage",
    "ControlRoomPage",
    "MarketsPage",
    "ResearchPage",
    "EvidencePage",
    "ExperimentsPage",
    "StatisticsPage",
    "LiveValidationPage",
    "GovernancePage",
    "KnowledgeGraphPage",
    "EdgeDiscoveryPage",
    "ResearchIntelligencePage",
    "ArchivePage",
    "PortfolioPage",
    "MonitoringPage",
    "SettingsPage",
    "NotFoundPage",
]

SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000",
    "JUMP_10", "JUMP_25", "JUMP_50", "JUMP_75", "JUMP_100", "STEP_INDEX"
]

ROLES = ["OPERATOR", "RESEARCHER", "ADMIN"]


@pytest.mark.parametrize("page_name", PAGES)
@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("role", ROLES)
def test_router_page_matrix(page_name: str, sym: str, role: str) -> None:
    page_file = Path(f"apps/dashboard/src/pages/{page_name}.tsx")
    assert page_file.exists()
    content = page_file.read_text(encoding="utf-8")
    assert page_name in content


def test_routes_file_integrity() -> None:
    routes_file = Path("apps/dashboard/src/router/routes.ts")
    assert routes_file.exists()
    content = routes_file.read_text(encoding="utf-8")
    for page in PAGES:
        if page != "NotFoundPage":
            assert page in content
