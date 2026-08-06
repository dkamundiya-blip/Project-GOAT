"""
Project GOAT v0.7 — Quality Gate Pipeline Engine

Coordinates sequential evaluation of candidate features across registered Quality Gates,
producing consolidated FeatureQualitySummaryReport.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from goat.features.core.base import BaseFeature
from goat.features.core.context import MarketDataWindow
from goat.features.quality.base import (
    BaseQualityGate,
    QualityGateReport,
    QualityGateStatus,
)
from goat.features.quality.gates import (
    ComplexityQualityGate,
    LeakageQualityGate,
    MulticollinearityQualityGate,
    NumericalStabilityQualityGate,
    RegistryConsistencyQualityGate,
    StationarityQualityGate,
    VarianceQualityGate,
)


class FeatureQualitySummaryReport(BaseModel):
    """Consolidated summary report of quality gate evaluations for a candidate feature."""

    feature_id: str = Field(..., description="Target Feature ID")
    scientific_fingerprint: str = Field(..., description="Scientific Feature Fingerprint")
    overall_status: QualityGateStatus = Field(..., description="Consolidated overall status")
    gate_reports: list[QualityGateReport] = Field(..., description="List of individual gate reports")
    execution_timestamp: str = Field(..., description="ISO-8601 UTC evaluation timestamp")

    class Config:
        frozen = True
        extra = "forbid"


class QualityGatePipeline:
    """Sequential quality gate evaluation pipeline."""

    def __init__(self, gates: list[BaseQualityGate] | None = None) -> None:
        """Initialize quality gate pipeline.

        Args:
            gates: Optional list of Quality Gate instances. Defaults to standard 7 gates.
        """
        self._gates: list[BaseQualityGate] = []
        if gates:
            for g in gates:
                self.register_gate(g)
        else:
            self._register_default_gates()

    def _register_default_gates(self) -> None:
        """Register default suite of 7 Pre-Validation Quality Gates."""
        self.register_gate(VarianceQualityGate())
        self.register_gate(StationarityQualityGate())
        self.register_gate(LeakageQualityGate())
        self.register_gate(NumericalStabilityQualityGate())
        self.register_gate(MulticollinearityQualityGate())
        self.register_gate(ComplexityQualityGate())
        self.register_gate(RegistryConsistencyQualityGate())

    def register_gate(self, gate: BaseQualityGate) -> None:
        """Register a new Quality Gate into the pipeline."""
        if any(g.gate_id == gate.gate_id for g in self._gates):
            raise ValueError(f"Quality gate '{gate.gate_id}' is already registered in pipeline")
        self._gates.append(gate)

    @property
    def gates(self) -> list[BaseQualityGate]:
        """Return list of registered gates."""
        return list(self._gates)

    def evaluate_feature(
        self,
        feature: BaseFeature,
        context: MarketDataWindow | None = None,
    ) -> FeatureQualitySummaryReport:
        """Evaluate a candidate feature against all registered Quality Gates.

        Fail-Closed Policy: If any gate returns FAILED, overall_status is FAILED.

        Args:
            feature: Target BaseFeature instance.
            context: Optional MarketDataWindow dataset.

        Returns:
            FeatureQualitySummaryReport instance.
        """
        ts = datetime.now(timezone.utc).isoformat()
        reports: list[QualityGateReport] = []
        overall = QualityGateStatus.PASSED

        for gate in self._gates:
            report = gate.evaluate(feature, context)
            reports.append(report)

            if report.status == QualityGateStatus.FAILED:
                overall = QualityGateStatus.FAILED

        return FeatureQualitySummaryReport(
            feature_id=feature.feature_id,
            scientific_fingerprint=feature.scientific_fingerprint,
            overall_status=overall,
            gate_reports=reports,
            execution_timestamp=ts,
        )
