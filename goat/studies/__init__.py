"""
Project GOAT v0.7 — Scientific Research Study Engine Package
"""

from goat.studies.audit import StudyAuditEvent
from goat.studies.context import StudyContext
from goat.studies.coordinator import StudyCoordinator, StudyValidationError
from goat.studies.design import StudyDesign, compute_design_id
from goat.studies.enums import StudyStatus
from goat.studies.model import (
    ScientificStudy,
    compute_study_fingerprint,
    compute_study_id,
)
from goat.studies.registry import StudyExperimentRecord, StudyExperimentRegistry
from goat.studies.reporting import StudyReport, generate_study_report
from goat.studies.result import StudyResult, compute_study_result_id
from goat.studies.sqlite import SQLiteStudyRepository

__all__ = [
    # Enums
    "StudyStatus",
    # Domain Models & Identities
    "ScientificStudy",
    "compute_study_id",
    "compute_study_fingerprint",
    "StudyDesign",
    "compute_design_id",
    "StudyExperimentRecord",
    "StudyExperimentRegistry",
    "StudyResult",
    "compute_study_result_id",
    "StudyContext",
    # Coordinator & Audit
    "StudyCoordinator",
    "StudyValidationError",
    "StudyAuditEvent",
    # Persistence & Reporting
    "SQLiteStudyRepository",
    "StudyReport",
    "generate_study_report",
]
