"""
Project GOAT v0.9 — Controlled Live Scientific Validation Subsystem Public API
"""

from goat.live_validation.core.canonical import (
    compute_audit_id,
    compute_candidate_id,
    compute_canonical_sha256,
    compute_observation_id,
    compute_session_id,
    compute_summary_id,
    compute_validation_decision_id,
    serialize_canonical_json,
)
from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationAudit,
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
    ValidationSummary,
)
from goat.live_validation.eligibility.engine import ValidationEligibilityEngine
from goat.live_validation.engine import MasterLiveValidationEngine
from goat.live_validation.monitoring.engine import ValidationMonitoringEngine
from goat.live_validation.persistence.sqlite import (
    AuditRepository,
    CandidateRepository,
    DecisionRepository,
    LiveValidationPersistenceContext,
    ObservationRepository,
    SummaryRepository,
    ValidationSessionRepository,
    init_live_validation_db,
)
from goat.live_validation.reporting.reports import (
    generate_decision_report,
    generate_eligibility_report,
    generate_executive_report,
    generate_json_report,
    generate_monitoring_report,
    generate_validation_report,
)
from goat.live_validation.retirement.engine import ValidationRetirementEngine
from goat.live_validation.validation.engine import ControlledLiveValidationEngine

__all__ = [
    "AuditRepository",
    "CandidateRepository",
    "ControlledLiveValidationEngine",
    "DecisionRepository",
    "LiveValidationCandidate",
    "LiveValidationPersistenceContext",
    "MasterLiveValidationEngine",
    "MonitoringStatus",
    "ObservationRepository",
    "SummaryRepository",
    "ValidationAudit",
    "ValidationDecision",
    "ValidationDecisionOutcome",
    "ValidationEligibilityEngine",
    "ValidationMonitoringEngine",
    "ValidationObservation",
    "ValidationRetirementEngine",
    "ValidationSession",
    "ValidationSessionRepository",
    "ValidationStatus",
    "ValidationSummary",
    "compute_audit_id",
    "compute_candidate_id",
    "compute_canonical_sha256",
    "compute_observation_id",
    "compute_session_id",
    "compute_summary_id",
    "compute_validation_decision_id",
    "generate_decision_report",
    "generate_eligibility_report",
    "generate_executive_report",
    "generate_json_report",
    "generate_monitoring_report",
    "generate_validation_report",
    "init_live_validation_db",
    "serialize_canonical_json",
]
