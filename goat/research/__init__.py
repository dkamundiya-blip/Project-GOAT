"""
Project GOAT v0.9 — Scientific Research Subsystem Public API
"""

from goat.research.core.canonical import (
    compute_approval_id,
    compute_canonical_sha256,
    compute_hypothesis_id,
    compute_revision_id,
    compute_summary_id,
    compute_validation_id,
    serialize_canonical_json,
)
from goat.research.core.enums import (
    EvidenceLevel,
    HypothesisPriority,
    HypothesisStatus,
)
from goat.research.core.models import (
    HypothesisApproval,
    HypothesisRegistrySummary,
    HypothesisRevision,
    HypothesisValidation,
    ScientificHypothesis,
)
from goat.research.engine import ScientificResearchEngine
from goat.research.persistence.sqlite import (
    ApprovalRepository,
    HypothesisRepository,
    ResearchPersistenceContext,
    RevisionRepository,
    SummaryRepository,
    ValidationRepository,
    init_research_db,
)
from goat.research.registry.engine import ScientificHypothesisRegistry
from goat.research.reporting.reports import (
    generate_executive_report,
    generate_json_report,
    generate_markdown_report,
    generate_registry_summary_report,
    generate_validation_report,
)
from goat.research.validation.engine import HypothesisValidationEngine

__all__ = [
    "ApprovalRepository",
    "EvidenceLevel",
    "HypothesisApproval",
    "HypothesisPriority",
    "HypothesisRegistrySummary",
    "HypothesisRepository",
    "HypothesisRevision",
    "HypothesisStatus",
    "HypothesisValidation",
    "HypothesisValidationEngine",
    "ResearchPersistenceContext",
    "RevisionRepository",
    "ScientificHypothesis",
    "ScientificHypothesisRegistry",
    "ScientificResearchEngine",
    "SummaryRepository",
    "ValidationRepository",
    "compute_approval_id",
    "compute_canonical_sha256",
    "compute_hypothesis_id",
    "compute_revision_id",
    "compute_summary_id",
    "compute_validation_id",
    "generate_executive_report",
    "generate_json_report",
    "generate_markdown_report",
    "generate_registry_summary_report",
    "generate_validation_report",
    "init_research_db",
    "serialize_canonical_json",
]
