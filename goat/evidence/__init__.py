"""
Project GOAT v0.9 — Scientific Observation & Evidence Subsystem Public API
"""

from goat.evidence.collection.engine import EvidenceCollectionEngine
from goat.evidence.core.canonical import (
    compute_canonical_sha256,
    compute_collection_id,
    compute_evidence_record_id,
    compute_link_id,
    compute_observation_id,
    compute_summary_id,
    serialize_canonical_json,
)
from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
    ObservationStatus,
)
from goat.evidence.core.models import (
    EvidenceLink,
    EvidenceRecord,
    EvidenceSummary,
    ObservationCollection,
    ScientificObservation,
)
from goat.evidence.engine import ScientificEvidenceEngine
from goat.evidence.linkage.engine import EvidenceLinkageEngine
from goat.evidence.observation.engine import ScientificObservationEngine
from goat.evidence.persistence.sqlite import (
    CollectionRepository,
    EvidencePersistenceContext,
    EvidenceRepository,
    LinkRepository,
    ObservationRepository,
    SummaryRepository,
    init_evidence_db,
)
from goat.evidence.reporting.reports import (
    generate_collection_summary_report,
    generate_evidence_report,
    generate_evidence_summary_report,
    generate_executive_report,
    generate_json_report,
    generate_observation_report,
)

__all__ = [
    "CollectionRepository",
    "EvidenceCategory",
    "EvidenceCollectionEngine",
    "EvidenceLink",
    "EvidenceLinkageEngine",
    "EvidencePersistenceContext",
    "EvidenceRecord",
    "EvidenceRepository",
    "EvidenceSummary",
    "LinkRepository",
    "ObservationCollection",
    "ObservationRepository",
    "ObservationSource",
    "ObservationStatus",
    "ScientificEvidenceEngine",
    "ScientificObservation",
    "ScientificObservationEngine",
    "SummaryRepository",
    "compute_canonical_sha256",
    "compute_collection_id",
    "compute_evidence_record_id",
    "compute_link_id",
    "compute_observation_id",
    "compute_summary_id",
    "generate_collection_summary_report",
    "generate_evidence_report",
    "generate_evidence_summary_report",
    "generate_executive_report",
    "generate_json_report",
    "generate_observation_report",
    "init_evidence_db",
    "serialize_canonical_json",
]
