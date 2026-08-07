"""
Unit tests for ReasoningEngine deterministic conclusion deduction.
"""

from goat.ai_reasoning.reasoning.engine import ReasoningEngine
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)


def test_reasoning_engine_deduction():
    edge_active = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength"],
        supported_symbols=["VOLATILITY_100"],
        supported_timeframes=["1m"],
        metrics=EdgePerformanceMetrics(
            sample_size=100,
            win_rate=0.6,
            loss_rate=0.4,
            expected_value=0.005,
            average_return=0.005,
            median_return=0.004,
            max_gain=0.02,
            max_loss=0.01,
            profit_factor=2.0,
            sharpe_ratio=2.5,
            sortino_ratio=3.0,
            calmar_ratio=4.0,
            max_drawdown=0.05,
            recovery_factor=5.0,
            trade_frequency=10.0,
            holding_period=5.0,
        ),
        p_value=0.01,
        confidence_interval_low=0.002,
        confidence_interval_high=0.008,
        effect_size=0.8,
        composite_score=0.85,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash="HASH",
    )

    engine = ReasoningEngine()
    conclusion = engine.deduce_edge_status_conclusion(edge_active)

    assert conclusion.status_verdict == "ACTIVE"
    assert "remains ACTIVE" in conclusion.claim
    assert len(conclusion.reasoning_steps) >= 4
    assert len(conclusion.supporting_evidence_ids) >= 5
