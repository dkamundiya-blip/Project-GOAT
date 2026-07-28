"""
Project GOAT v0.6 — Edge Intelligence & Validation Package

Foundational v0.6 domain models, enums, canonical serialization, deterministic scientific identity layer, and persistence backend.
"""

from __future__ import annotations

from goat.research.edge.canonical import canonical_json, compute_canonical_sha256
from goat.research.edge.definition import CandidateEdge, compute_hypothesis_version
from goat.research.edge.enums import (
    EdgeLifecycleStatus,
    EdgeScope,
    EvidenceDimensionType,
    MultiplicityStrategy,
    ValidationStageOutcome,
)
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import (
    ValidationRunInfo,
    compute_confirmatory_audit_id,
    compute_validation_run_id,
)
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.policy import ValidationPolicy

__all__ = [
    "EdgeScope",
    "EdgeLifecycleStatus",
    "ValidationStageOutcome",
    "EvidenceDimensionType",
    "MultiplicityStrategy",
    "canonical_json",
    "compute_canonical_sha256",
    "CandidateEdge",
    "compute_hypothesis_version",
    "ValidationPolicy",
    "AtomicEvidenceRecord",
    "ValidationRunInfo",
    "compute_validation_run_id",
    "compute_confirmatory_audit_id",
    "SQLiteEdgeRepository",
]
