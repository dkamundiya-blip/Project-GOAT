"""
Integration tests for MasterAIReasoningEngine pipeline and EventBus.
"""

from goat.ai_reasoning.engine import MasterAIReasoningEngine
from goat.ai_reasoning.models import ResearchReport
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)


def test_master_ai_reasoning_engine_pipeline():
    engine = MasterAIReasoningEngine()

    received_reports: list[ResearchReport] = []

    def on_report(report: ResearchReport):
        received_reports.append(report)

    engine.subscribe_reports(on_report)

    edge = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength"],
        supported_symbols=["BOOM_500"],
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

    engine.ingest_edge(edge)
    report = engine.generate_and_broadcast_report(edge)

    assert report is not None
    assert len(received_reports) == 1
    assert received_reports[0].report_id == report.report_id
