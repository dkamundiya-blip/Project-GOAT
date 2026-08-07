"""
Project GOAT Phase 6 — Unit Tests for Research Hypotheses & DiscoveredEdge Domain Models
"""

from pydantic import ValidationError
import pytest

from goat.edge_discovery.models import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
    HypothesisCondition,
    HypothesisOperator,
    HypothesisPrediction,
    HypothesisStatus,
    ResearchHypothesis,
    compute_edge_id,
    compute_hypothesis_id,
)


def test_research_hypothesis_creation_and_canonical_id():
    conds = [
        HypothesisCondition(feature_name="trend_strength", operator=HypothesisOperator.GT, threshold_value=0.7),
        HypothesisCondition(feature_name="momentum_strength", operator=HypothesisOperator.GT, threshold_value=0.5),
    ]
    pred = HypothesisPrediction(target_feature="future_return", horizon_bars=5, min_return=0.001)

    h_id, c_hash = compute_hypothesis_id(conds, pred)
    assert h_id.startswith("HYP_")
    assert len(h_id) == 20
    assert len(c_hash) == 64

    hyp = ResearchHypothesis(
        hypothesis_id=h_id,
        version="6.0.0",
        description="Test hypothesis",
        conditions=conds,
        prediction=pred,
        creation_timestamp="2026-08-07T12:00:00Z",
        author="QUANT_BOT",
        status=HypothesisStatus.DRAFT,
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )
    assert hyp.hypothesis_id == h_id

    # Verify immutability
    with pytest.raises(ValidationError):
        hyp.description = "Mutated description"


def test_discovered_edge_model():
    metrics = EdgePerformanceMetrics(
        sample_size=100,
        win_rate=0.65,
        loss_rate=0.35,
        expected_value=0.002,
        average_return=0.002,
        median_return=0.0018,
        max_gain=0.015,
        max_loss=-0.008,
        profit_factor=1.85,
        sharpe_ratio=2.10,
        sortino_ratio=2.95,
        calmar_ratio=3.50,
        max_drawdown=0.05,
        recovery_factor=4.20,
        trade_frequency=5.0,
        holding_period=5.0,
    )

    e_id, c_hash = compute_edge_id("HYP_123", ["trend_strength"], ["VOLATILITY_100"], ["1m"])
    assert e_id.startswith("EDG_")

    edge = DiscoveredEdge(
        edge_id=e_id,
        version="6.0.0",
        hypothesis_id="HYP_123",
        feature_combination=["trend_strength"],
        supported_symbols=["VOLATILITY_100"],
        supported_timeframes=["1m"],
        metrics=metrics,
        p_value=0.001,
        confidence_interval_low=0.001,
        confidence_interval_high=0.003,
        effect_size=0.85,
        composite_score=0.82,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash=c_hash,
    )
    assert edge.edge_id == e_id
    assert edge.metrics.win_rate == 0.65
