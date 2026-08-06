"""
Project GOAT v0.7 — Scientific Risk Management Package

Public API Exports for Step 6.5 (Phase VI).
"""

from goat.risk.allocation import CapitalAllocationEngine
from goat.risk.calculators import MonetaryRiskCalculator, RiskRulesEngine
from goat.risk.core import (
    CapitalAllocation,
    ExposureAssessment,
    ExposureStatus,
    PositionEligibility,
    PositionSizingDecision,
    RiskAssessment,
    RiskProfile,
    RiskRuleStatus,
    SizingMethod,
    compute_allocation_id,
    compute_exposure_id,
    compute_risk_assessment_id,
    compute_risk_profile_id,
    compute_risk_report_id,
    compute_sizing_id,
    serialize_canonical_json,
)
from goat.risk.engine import ScientificRiskEngineCoordinator
from goat.risk.exposure import ExposureAssessmentEngine
from goat.risk.persistence import (
    CapitalAllocationRepository,
    ExposureRepository,
    PositionSizingRepository,
    RiskAssessmentRepository,
    RiskProfileRepository,
    RiskReportRepository,
    init_risk_db,
)
from goat.risk.reporting import (
    CapitalAllocationReport,
    ExposureAssessmentReport,
    PositionSizingReport,
    RiskAssessmentReport,
    RiskExecutiveReport,
    RiskProfileReport,
)
from goat.risk.sizing import PositionSizingEngine

__all__ = [
    # Core Models & Enums
    "ExposureStatus",
    "SizingMethod",
    "RiskRuleStatus",
    "PositionEligibility",
    "RiskProfile",
    "PositionSizingDecision",
    "CapitalAllocation",
    "ExposureAssessment",
    "RiskAssessment",
    # Identifiers & Canonical Hashing
    "compute_risk_profile_id",
    "compute_sizing_id",
    "compute_allocation_id",
    "compute_exposure_id",
    "compute_risk_assessment_id",
    "compute_risk_report_id",
    "serialize_canonical_json",
    # Engines & Coordinators
    "ScientificRiskEngineCoordinator",
    "PositionSizingEngine",
    "CapitalAllocationEngine",
    "ExposureAssessmentEngine",
    "MonetaryRiskCalculator",
    "RiskRulesEngine",
    # Reports
    "RiskProfileReport",
    "PositionSizingReport",
    "CapitalAllocationReport",
    "ExposureAssessmentReport",
    "RiskAssessmentReport",
    "RiskExecutiveReport",
    # Repositories & Database Initialization
    "init_risk_db",
    "RiskProfileRepository",
    "PositionSizingRepository",
    "CapitalAllocationRepository",
    "ExposureRepository",
    "RiskAssessmentRepository",
    "RiskReportRepository",
]
