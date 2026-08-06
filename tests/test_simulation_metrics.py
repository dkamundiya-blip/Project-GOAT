"""
Project GOAT v0.7 — Test Suite for StatisticalMetricsCalculator & PerformanceAttributionEngine

Coverage:
- Computation of 15 descriptive statistical metrics
- Performance attribution breakdown across edges, regimes, evidence
"""

from goat.composite.core.canonical import compute_composite_id
from goat.composite.core.models import CompositeEdge
from goat.regimes.core.canonical import compute_regime_id
from goat.regimes.core.enums import RegimeType
from goat.regimes.core.models import MarketRegime
from goat.simulation.metrics.attribution import PerformanceAttributionEngine
from goat.simulation.metrics.calculator import StatisticalMetricsCalculator


def test_statistical_metrics_calculator():
    calc = StatisticalMetricsCalculator()

    events = [
        {"pnl": 100.0},
        {"pnl": -50.0},
        {"pnl": 200.0},
        {"pnl": -40.0},
        {"pnl": 150.0},
    ]

    metrics = calc.compute_all_metrics(events)

    assert len(metrics) == 15
    assert metrics["win_rate"] == 0.60
    assert metrics["loss_rate"] == 0.40
    assert metrics["average_reward"] == 150.0
    assert metrics["average_risk"] == 45.0
    assert metrics["profit_factor"] > 4.0
    assert 0.0 <= metrics["maximum_drawdown"] <= 1.0


def test_performance_attribution_engine():
    engine = PerformanceAttributionEngine()

    c_id, c_hash = compute_composite_id(["SED_1", "SED_2"], "Composite")
    composite = CompositeEdge(
        composite_id=c_id,
        title="Composite",
        participating_edges=["SED_1", "SED_2"],
        supporting_evidence=["VAL_1"],
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=c_hash,
    )

    r_id, r_hash = compute_regime_id("TRENDING", "2026-07-30T00:00:00Z")
    regime = MarketRegime(regime_id=r_id, timestamp="2026-07-30T00:00:00Z", regime_type=RegimeType.TRENDING, confidence=0.85, canonical_hash=r_hash)

    attribution = engine.compute_attribution("SRS_1", composite, regime, {"profit_factor": 2.0})

    assert attribution.attribution_id.startswith("PAT_")
    assert "SED_1" in attribution.contributing_edges
    assert r_id in attribution.contributing_regimes
