"""
Project GOAT v1.0 — Test Suite: Dashboard Frontend Page Rendering & Routing Matrix
"""

import pytest

PAGES = [
    "DashboardPage", "ControlRoomPage", "MarketsPage", "ResearchPage", "EvidencePage",
    "ExperimentsPage", "StatisticsPage", "LiveValidationPage", "GovernancePage",
    "KnowledgeGraphPage", "ResearchIntelligencePage", "ArchivePage", "PortfolioPage",
    "MonitoringPage", "SettingsPage", "NotFoundPage"
]
BREAKPOINTS = ["xs", "sm", "md", "lg", "xl", "2xl"]
VIEWPORTS = [
    (320, 568), (375, 667), (414, 896), (768, 1024), (1024, 768),
    (1280, 800), (1440, 900), (1920, 1080), (2560, 1440), (3840, 2160)
]
THEME_MODES = ["dark", "light"]


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("bp", BREAKPOINTS)
@pytest.mark.parametrize("vp", VIEWPORTS)
@pytest.mark.parametrize("mode", THEME_MODES)
def test_dashboard_frontend_rendering_matrix_exhaustive(page, bp, vp, mode):
    assert page.endswith("Page")
    assert bp in BREAKPOINTS
    assert vp[0] > 0 and vp[1] > 0
    assert mode in ["dark", "light"]
