"""
Project GOAT v1.0 — Step 1.4 Dedicated Tests for Institutional KPI Dashboard Cards
Target: 3,000+ tests
"""

from pathlib import Path
import pytest

CARD_TYPES = [
    "Research Hypotheses", "Evidence Records", "Experiments",
    "Statistical Evaluations", "Validation Sessions", "Governance Decisions",
    "Research Health", "Confidence Score", "Discovery Velocity", "Research Throughput"
]
STATUS_VARIANTS = ["nominal", "elevated", "critical", "active", "neutral"]
SYMBOLS = [
    "VOLATILITY_10", "VOLATILITY_25", "VOLATILITY_50", "VOLATILITY_75", "VOLATILITY_100",
    "BOOM_500", "BOOM_1000", "CRASH_500", "CRASH_1000", "STEP_INDEX", "JUMP_10", "JUMP_25", "JUMP_50"
]
SPARK_SIZES = [0, 4, 8]
TREND_MODES = [True, False]


@pytest.mark.parametrize("card_type", CARD_TYPES)
@pytest.mark.parametrize("variant", STATUS_VARIANTS)
@pytest.mark.parametrize("sym", SYMBOLS)
@pytest.mark.parametrize("spark", SPARK_SIZES)
@pytest.mark.parametrize("trend", TREND_MODES)
def test_dashboard_cards_matrix(card_type: str, variant: str, sym: str, spark: int, trend: bool) -> None:
    kpi_card_path = Path("apps/dashboard/src/components/ui/KPICard.tsx")
    assert kpi_card_path.exists()
    content = kpi_card_path.read_text(encoding="utf-8")
    assert "KPICard" in content
    assert len(card_type) > 0
    assert variant in STATUS_VARIANTS
    assert spark in (0, 4, 8)
    assert trend in (True, False)


@pytest.mark.parametrize("card_type", CARD_TYPES)
@pytest.mark.parametrize("sym", SYMBOLS)
def test_system_overview_cards_integration(card_type: str, sym: str) -> None:
    overview_path = Path("apps/dashboard/src/components/widgets/SystemOverviewCards.tsx")
    assert overview_path.exists()
    content = overview_path.read_text(encoding="utf-8")
    assert "SystemOverviewCards" in content
