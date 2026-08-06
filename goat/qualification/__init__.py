"""
Project GOAT v0.7 — Scientific Qualification Engine Package

Public API Exports for Step 6.3 (Phase VI).
"""

from goat.qualification.core import (
    BlockingConditionType,
    DecisionReadiness,
    GateCategory,
    GateEvaluation,
    QualificationExplainabilityRecord,
    QualificationGate,
    QualificationState,
    ReadinessLevel,
    ScientificQualification,
    compute_evaluation_id,
    compute_gate_id,
    compute_qualification_explanation_id,
    compute_qualification_id,
    compute_qualification_report_id,
    compute_readiness_id,
    serialize_canonical_json,
)
from goat.qualification.engine import ScientificQualificationEngineCoordinator
from goat.qualification.evaluation import ScientificQualificationEngine
from goat.qualification.gates import QualificationGateEngine
from goat.qualification.persistence import (
    DecisionReadinessRepository,
    GateEvaluationRepository,
    GateRepository,
    QualificationReportRepository,
    QualificationRepository,
    init_qualification_db,
)
from goat.qualification.readiness import DecisionReadinessEngine
from goat.qualification.reporting import (
    DecisionReadinessReport,
    GateEvaluationReport,
    QualificationSummaryReport,
    ScientificQualificationReport,
    ScientificReadinessReport,
)

__all__ = [
    # Core Models & Enums
    "QualificationState",
    "ReadinessLevel",
    "GateCategory",
    "BlockingConditionType",
    "ScientificQualification",
    "QualificationGate",
    "GateEvaluation",
    "DecisionReadiness",
    "QualificationExplainabilityRecord",
    # Identifiers & Canonical Hashing
    "compute_qualification_id",
    "compute_gate_id",
    "compute_evaluation_id",
    "compute_readiness_id",
    "compute_qualification_explanation_id",
    "compute_qualification_report_id",
    "serialize_canonical_json",
    # Engines & Coordinators
    "ScientificQualificationEngineCoordinator",
    "ScientificQualificationEngine",
    "QualificationGateEngine",
    "DecisionReadinessEngine",
    # Reports
    "ScientificQualificationReport",
    "GateEvaluationReport",
    "DecisionReadinessReport",
    "QualificationSummaryReport",
    "ScientificReadinessReport",
    # Repositories & Database Initialization
    "init_qualification_db",
    "QualificationRepository",
    "GateRepository",
    "GateEvaluationRepository",
    "DecisionReadinessRepository",
    "QualificationReportRepository",
]
