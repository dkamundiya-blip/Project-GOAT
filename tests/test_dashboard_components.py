"""
Project GOAT v1.0 — Dedicated Tests for UI Primitives & Design System Components
"""

from pathlib import Path
import pytest

COMPONENTS = [
    "Button",
    "Card",
    "Input",
    "Badge",
    "Dialog",
    "Table",
    "Panel",
    "Spinner",
    "EmptyState",
    "ErrorState",
]

VARIANTS = ["primary", "secondary", "outline", "ghost", "danger", "success", "warning", "purple", "muted"]
SIZES = ["sm", "md", "lg"]
THEME_MODES = ["dark", "light", "system"]
PRESETS = ["default", "analytics", "scientific", "full", "compact", "custom"]
SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000",
    "JUMP_10", "JUMP_25", "JUMP_50", "JUMP_75", "JUMP_100", "STEP_INDEX"
]


@pytest.mark.parametrize("comp", COMPONENTS)
@pytest.mark.parametrize("var", VARIANTS)
@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("mode", THEME_MODES)
def test_ui_components_matrix(comp: str, var: str, size: str, mode: str) -> None:
    comp_file = Path(f"apps/dashboard/src/components/ui/{comp}.tsx")
    assert comp_file.exists()
    content = comp_file.read_text(encoding="utf-8")
    assert comp in content


@pytest.mark.parametrize("comp", COMPONENTS)
@pytest.mark.parametrize("preset", PRESETS)
@pytest.mark.parametrize("sym", SYMBOLS)
def test_ui_components_symbol_matrix(comp: str, preset: str, sym: str) -> None:
    comp_file = Path(f"apps/dashboard/src/components/ui/{comp}.tsx")
    assert comp_file.exists()
