"""
Project GOAT v0.7 — Step 4.2 Quality Gate Framework Test Suite
"""

from __future__ import annotations

import pandas as pd
import pytest

from goat.features import (
    BarRange,
    BodyRatio,
    ComplexityQualityGate,
    LeakageQualityGate,
    LogReturn,
    MarketDataWindow,
    NumericalStabilityQualityGate,
    QualityGatePipeline,
    QualityGateStatus,
    StationarityQualityGate,
    VarianceQualityGate,
)


@pytest.fixture
def sample_data():
    dates = pd.date_range("2026-01-01 09:30", periods=5, freq="5min")
    data = {
        "timestamp": dates,
        "open": [100.0, 102.0, 101.0, 105.0, 104.0],
        "high": [103.0, 104.0, 106.0, 107.0, 105.0],
        "low": [99.0, 100.0, 100.0, 103.0, 101.0],
        "close": [102.0, 101.0, 105.0, 104.0, 102.0],
        "volume": [1000.0, 1500.0, 1200.0, 1800.0, 1100.0],
    }
    return MarketDataWindow(data)


def test_quality_gate_pipeline_pass(sample_data):
    """Verify standard primitive features pass the 7 quality gates."""
    feat = LogReturn()
    pipeline = QualityGatePipeline()

    report = pipeline.evaluate_feature(feat, sample_data)

    assert report.feature_id == feat.feature_id
    assert report.scientific_fingerprint == feat.scientific_fingerprint
    assert report.overall_status == QualityGateStatus.PASSED
    assert len(report.gate_reports) == 7


def test_complexity_gate_failure(sample_data):
    """Verify ComplexityQualityGate fails when parameter count exceeds threshold."""
    feat = LogReturn()
    # Mutate parameters to 5 (threshold is 4)
    feat._parameters = {"p1": 1, "p2": 2, "p3": 3, "p4": 4, "p5": 5}

    gate = ComplexityQualityGate(max_params=4)
    rep = gate.evaluate(feat, sample_data)

    assert rep.status == QualityGateStatus.FAILED
    assert "exceeds maximum allowed" in rep.reason


def test_leakage_gate_pass(sample_data):
    """Verify LeakageQualityGate passes for strictly causal features."""
    feat = BarRange()
    gate = LeakageQualityGate()

    rep = gate.evaluate(feat, sample_data)
    assert rep.status == QualityGateStatus.PASSED
    assert "Zero forward leakage detected" in rep.reason
