"""
Unit tests for ResearchReportGenerator compiling evidence-backed reports.
"""

from goat.ai_reasoning.models import ExplanationLevel
from goat.ai_reasoning.reporting.generator import ResearchReportGenerator
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)


def test_research_report_generator():
    edge = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength"],
        supported_symbols=["CRASH_500"],
        supported_timeframes=["1m"],
        metrics=EdgePerformanceMetrics(
            sample_size=120,
            win_rate=0.65,
            loss_rate=0.35,
            expected_value=0.008,
            average_return=0.008,
            median_return=0.007,
            max_gain=0.03,
            max_loss=0.015,
            profit_factor=2.2,
            sharpe_ratio=2.8,
            sortino_ratio=3.5,
            calmar_ratio=4.5,
            max_drawdown=0.04,
            recovery_factor=6.0,
            trade_frequency=12.0,
            holding_period=4.0,
        ),
        p_value=0.005,
        confidence_interval_low=0.003,
        confidence_interval_high=0.012,
        effect_size=0.9,
        composite_score=0.92,
        discovery_date="2026-08-07T12:00:00Z",
        last_validation_date="2026-08-07T12:00:00Z",
        status=EdgeStatus.ACTIVE,
        regime_performance={},
        walk_forward_metrics={},
        checksum="CHK",
        metadata={},
        canonical_hash="HASH",
    )

    generator = ResearchReportGenerator()
    report = generator.generate_report(edge, explanation_level=ExplanationLevel.PROFESSIONAL_QUANT)

    assert report.report_id.startswith("REP_")
    assert report.explanation_level == ExplanationLevel.PROFESSIONAL_QUANT
    assert len(report.conclusions) == 1
    assert len(report.risk_factors) >= 2
    assert len(report.limitations) >= 2
    assert len(report.recommended_next_steps) >= 2
    assert "chart_metadata" in report.metadata
