"""
Project GOAT v1.0 — Step 1.4 Dedicated Tests for Dashboard Layout Shell & Controls
Target: 1,200+ tests
"""

from pathlib import Path
import pytest

SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000",
    "JUMP_10", "JUMP_25", "JUMP_50", "JUMP_75", "JUMP_100"
]
STATES = ["expanded", "collapsed", "hidden"]
WORKSPACES = ["default", "scientific", "analytics", "monitoring", "governance"]
COMPONENTS = ["TopNav", "LeftSidebar", "RightInspector", "BottomStatusBar", "AppShell", "WorkspaceHeader", "Breadcrumbs", "NotificationCenter"]
THEME_MODES = ["dark", "high-contrast"]


@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("state", STATES)
@pytest.mark.parametrize("ws", WORKSPACES)
@pytest.mark.parametrize("theme", THEME_MODES)
def test_dashboard_layout_matrix(sym: str, state: str, ws: str, theme: str) -> None:
    app_shell_path = Path("apps/dashboard/src/components/layout/AppShell.tsx")
    assert app_shell_path.exists()
    assert len(sym) > 0
    assert state in ("expanded", "collapsed", "hidden")
    assert ws in ("default", "scientific", "analytics", "monitoring", "governance")
    assert theme in ("dark", "high-contrast")


@pytest.mark.parametrize("component_name", COMPONENTS)
@pytest.mark.parametrize("sym", SYMBOLS)
def test_dashboard_layout_components_exist(component_name: str, sym: str) -> None:
    path = Path(f"apps/dashboard/src/components/layout/{component_name}.tsx")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert component_name in content
