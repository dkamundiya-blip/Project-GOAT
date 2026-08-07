"""
Unit tests for EvidenceEngine and 100% evidence traceability.
"""

from goat.ai_reasoning.evidence.engine import EvidenceEngine
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)


def test_evidence_engine_building_bundle():
    edge = DiscoveredEdge(
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
        regime_performance={"BULL_TREND": {"sample_size": 40, "expected_value": 0.007}},
        walk_forward_metrics={"oos_expected_value": 0.004},
        checksum="CHK",
        metadata={},
        canonical_hash="HASH",
    )

    engine = EvidenceEngine()
    bundle = engine.build_evidence_bundle(edge)

    assert bundle.target_id == "EDG_0000000000000001"
    assert len(bundle.records) >= 5
    assert bundle.overall_confidence == 1.0

    ev_records = [r for r in bundle.records if r.metric_name == "expected_value"]
    assert len(ev_records) == 1
    assert ev_records[0].is_supporting is True
    assert ev_records[0].metric_value == 0.005
