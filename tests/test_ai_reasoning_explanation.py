"""
Unit tests for NaturalLanguageExplanationLayer persona translation.
"""

from goat.ai_reasoning.explanation.layer import NaturalLanguageExplanationLayer
from goat.ai_reasoning.models import ExplanationLevel
from goat.ai_reasoning.reporting.generator import ResearchReportGenerator
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgePerformanceMetrics,
    EdgeStatus,
)


def test_natural_language_explanation_layer():
    edge = DiscoveredEdge(
        edge_id="EDG_0000000000000001",
        version="6.0.0",
        hypothesis_id="HYP_0000000000000001",
        feature_combination=["trend_strength"],
        supported_symbols=["JUMP_50"],
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

    layer = NaturalLanguageExplanationLayer()

    # Beginner
    beg = layer.explain_edge(edge, level=ExplanationLevel.BEGINNER)
    assert beg["explanation_level"] == "BEGINNER"
    assert "trading pattern" in beg["summary_explanation"]

    # Intermediate
    inter = layer.explain_edge(edge, level=ExplanationLevel.INTERMEDIATE)
    assert inter["explanation_level"] == "INTERMEDIATE"
    assert "Expected Return" in inter["summary_explanation"]

    # Professional Quant
    quant = layer.explain_edge(edge, level=ExplanationLevel.PROFESSIONAL_QUANT)
    assert quant["explanation_level"] == "PROFESSIONAL_QUANT"
    assert "Null hypothesis rejected" in quant["summary_explanation"]

    # Report Rendering String
    generator = ResearchReportGenerator()
    report = generator.generate_report(edge)
    rendered = layer.explain_report(report)
    assert "=== Quantitative Research Report" in rendered
    assert "--- EXECUTIVE SUMMARY ---" in rendered
