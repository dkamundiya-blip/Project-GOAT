"""
Project GOAT v0.9 — Dedicated Unit Tests for Validation Monitoring Engine
"""

import pytest

from goat.live_validation.core.enums import MonitoringStatus
from goat.live_validation.core.models import ValidationObservation
from goat.live_validation.monitoring.engine import ValidationMonitoringEngine


@pytest.fixture
def mon_engine():
    return ValidationMonitoringEngine(
        max_slippage_threshold=0.005,
        max_latency_ms_threshold=500.0,
        min_fill_ratio_threshold=0.85,
    )


def test_evaluate_monitoring_normal(mon_engine: ValidationMonitoringEngine):
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id="VSN_1234567890ABCDEF",
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
            slippage=0.001,
            spread=0.0002,
            latency_ms=50.0,
            fill_ratio=1.0,
        )
        for i in range(10)
    ]

    status = mon_engine.evaluate_monitoring_status(observations)
    assert status == MonitoringStatus.NORMAL


def test_evaluate_monitoring_critical_slippage(mon_engine: ValidationMonitoringEngine):
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id="VSN_1234567890ABCDEF",
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
            slippage=0.02,  # Severe slippage (> 2.0 * threshold)
            spread=0.0002,
            latency_ms=50.0,
            fill_ratio=1.0,
        )
        for i in range(10)
    ]

    status = mon_engine.evaluate_monitoring_status(observations)
    assert status == MonitoringStatus.CRITICAL


def test_evaluate_monitoring_warning_latency(mon_engine: ValidationMonitoringEngine):
    observations = [
        ValidationObservation(
            observation_id=f"VOB_{i:016X}",
            session_id="VSN_1234567890ABCDEF",
            timestamp="2026-08-04T12:00:00Z",
            live_outcome=0.5,
            expected_outcome=0.4,
            slippage=0.001,
            spread=0.0002,
            latency_ms=600.0,  # Latency > 500 ms threshold
            fill_ratio=1.0,
        )
        for i in range(10)
    ]

    status = mon_engine.evaluate_monitoring_status(observations)
    assert status == MonitoringStatus.WARNING
