"""
Project GOAT v0.9 — Validation Monitoring Engine
"""

from typing import Sequence

from goat.live_validation.core.enums import MonitoringStatus
from goat.live_validation.core.models import ValidationObservation


class ValidationMonitoringEngine:
    """Validation Monitoring Engine for observing live execution quality, slippage, spread stability,

    latency, and fill consistency.

    IMPORTANT: This engine ONLY observes and reports execution metrics.
    It SHALL NOT place trades, execute orders, or optimize strategy parameters.
    """

    def __init__(
        self,
        max_slippage_threshold: float = 0.005,
        max_latency_ms_threshold: float = 500.0,
        min_fill_ratio_threshold: float = 0.85,
    ) -> None:
        self.max_slippage_threshold = max_slippage_threshold
        self.max_latency_ms_threshold = max_latency_ms_threshold
        self.min_fill_ratio_threshold = min_fill_ratio_threshold

    def evaluate_monitoring_status(self, observations: Sequence[ValidationObservation]) -> MonitoringStatus:
        """Evaluate real-time execution monitoring health status based on accumulated live observations."""
        if not observations:
            return MonitoringStatus.NORMAL

        avg_slippage = sum(abs(o.slippage) for o in observations) / float(len(observations))
        avg_latency = sum(o.latency_ms for o in observations) / float(len(observations))
        avg_fill_ratio = sum(o.fill_ratio for o in observations) / float(len(observations))

        critical_triggers = (
            avg_slippage > (self.max_slippage_threshold * 2.0)
            or avg_latency > (self.max_latency_ms_threshold * 2.0)
            or avg_fill_ratio < (self.min_fill_ratio_threshold * 0.70)
        )

        if critical_triggers:
            return MonitoringStatus.CRITICAL

        warning_triggers = (
            avg_slippage > self.max_slippage_threshold
            or avg_latency > self.max_latency_ms_threshold
            or avg_fill_ratio < self.min_fill_ratio_threshold
        )

        if warning_triggers:
            return MonitoringStatus.WARNING

        watch_triggers = (
            avg_slippage > (self.max_slippage_threshold * 0.70)
            or avg_latency > (self.max_latency_ms_threshold * 0.70)
        )

        if watch_triggers:
            return MonitoringStatus.WATCH

        return MonitoringStatus.NORMAL
