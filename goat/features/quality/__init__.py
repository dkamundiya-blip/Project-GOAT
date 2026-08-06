"""
Project GOAT v0.7 — Pre-Validation Quality Gate Framework Package

Exposes QualityGateStatus, QualityGateReport, BaseQualityGate, the 7 Quality Gates,
FeatureQualitySummaryReport, and QualityGatePipeline.
"""

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
from goat.features.quality.pipeline import (
    FeatureQualitySummaryReport,
    QualityGatePipeline,
)

__all__ = [
    "QualityGateStatus",
    "QualityGateReport",
    "BaseQualityGate",
    "VarianceQualityGate",
    "StationarityQualityGate",
    "LeakageQualityGate",
    "NumericalStabilityQualityGate",
    "MulticollinearityQualityGate",
    "ComplexityQualityGate",
    "RegistryConsistencyQualityGate",
    "FeatureQualitySummaryReport",
    "QualityGatePipeline",
]
