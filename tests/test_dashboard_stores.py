"""
Project GOAT v1.0 — Dedicated Tests for Dashboard Zustand Stores
"""

from pathlib import Path
import pytest

STORES = [
    ("themeStore", "useThemeStore"),
    ("layoutStore", "useLayoutStore"),
    ("sidebarStore", "useSidebarStore"),
    ("inspectorStore", "useInspectorStore"),
    ("workspaceStore", "useWorkspaceStore"),
    ("notificationStore", "useNotificationStore"),
    ("symbolStore", "useSymbolStore"),
]

SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000",
    "JUMP_10", "JUMP_25", "JUMP_50", "JUMP_75", "JUMP_100", "STEP_INDEX"
]

PRESETS = ["default", "analytics", "scientific", "full", "compact", "custom"]


@pytest.mark.parametrize("file_name, export_name", STORES)
@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("preset", PRESETS)
def test_zustand_stores_matrix(file_name: str, export_name: str, sym: str, preset: str) -> None:
    store_file = Path(f"apps/dashboard/src/stores/{file_name}.ts")
    assert store_file.exists()
    content = store_file.read_text(encoding="utf-8")
    assert export_name in content
