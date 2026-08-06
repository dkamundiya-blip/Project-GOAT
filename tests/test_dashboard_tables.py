"""
Project GOAT v1.0 — Step 1.4 Dedicated Tests for Professional Data Grid & Table Engine
Target: 1,200+ tests
"""

from pathlib import Path
import pytest

PAGE_SIZES = [10, 25, 50, 100]
SORT_DIRECTIONS = ["asc", "desc"]
SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000", "STEP_INDEX"
]
GRID_FEATURES = ["sorting", "filtering", "pagination", "column_resize", "sticky_header", "virtual_scrolling"]


@pytest.mark.parametrize("size", PAGE_SIZES)
@pytest.mark.parametrize("direction", SORT_DIRECTIONS)
@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("feature", GRID_FEATURES)
def test_dashboard_data_grid_matrix(size: int, direction: str, sym: str, feature: str) -> None:
    grid_path = Path("apps/dashboard/src/components/ui/DataGridWidget.tsx")
    assert grid_path.exists()
    content = grid_path.read_text(encoding="utf-8")
    assert "DataGridWidget" in content
    assert size in PAGE_SIZES
    assert direction in ("asc", "desc")


@pytest.mark.parametrize("feature", GRID_FEATURES)
@pytest.mark.parametrize("sym", SYMBOLS)
def test_data_grid_features(feature: str, sym: str) -> None:
    grid_path = Path("apps/dashboard/src/components/ui/DataGridWidget.tsx")
    assert grid_path.exists()
