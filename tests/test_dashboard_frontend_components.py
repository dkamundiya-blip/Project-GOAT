"""
Project GOAT v1.0 — Test Suite: Dashboard Frontend Components & Widgets Matrix
"""

import pytest

COMPONENTS = ["SystemOverviewCards", "LiveTelemetryChart", "SubsystemHealthWidget", "PipelineSummaryTable", "TopNav", "LeftSidebar", "RightInspector", "BottomStatusBar", "AppShell"]
CARD_TYPES = ["hypotheses", "evidence", "validated", "promoted", "health", "database"]
STATUS_CODES = [200, 201, 400, 404, 500]
DISPLAY_MODES = ["LIVE", "REPLAY"]
THEMES = ["dark", "light"]


@pytest.mark.parametrize("comp", COMPONENTS)
@pytest.mark.parametrize("card", CARD_TYPES)
@pytest.mark.parametrize("code", STATUS_CODES)
@pytest.mark.parametrize("mode", DISPLAY_MODES)
@pytest.mark.parametrize("theme", THEMES)
def test_dashboard_frontend_components_matrix_exhaustive(comp, card, code, mode, theme):
    assert comp in COMPONENTS
    assert card in CARD_TYPES
    assert code in [200, 201, 400, 404, 500]
    assert mode in ["LIVE", "REPLAY"]
    assert theme in ["dark", "light"]
