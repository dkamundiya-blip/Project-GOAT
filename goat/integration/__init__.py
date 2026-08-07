"""
Project GOAT v0.7 — Scientific Knowledge Integration & Evidence Graph Engine Package

Public API Exports for Step 5.8.
"""

from goat.integration.conflicts import ConflictDetector
from goat.integration.core import (
    ConflictRecord,
    ConflictSeverity,
    ConflictType,
    IntegratedKnowledge,
    KnowledgeEdge,
    KnowledgeNode,
    KnowledgeNodeType,
    KnowledgeRelationship,
    compute_conflict_id,
    compute_edge_id,
    compute_evidence_merge_id,
    compute_integrated_knowledge_id,
    compute_node_fingerprint,
    compute_node_id,
    compute_version_id,
    serialize_canonical_json,
)
from goat.integration.engine import ScientificKnowledgeIntegrationEngine
from goat.integration.master import MasterSystemIntegrationEngine
from goat.integration.evidence import EvidenceMergeRecord, EvidenceMerger
from goat.integration.graph import ScientificKnowledgeGraph
from goat.integration.persistence import (
    ConflictRepository,
    EvidenceRepository,
    GraphRepository,
    IntegrationRepository,
    KnowledgeRepository,
    ReportRepository,
    init_integration_db,
)
from goat.integration.reporting import (
    ConflictReport,
    EvidenceMergeReport,
    KnowledgeEvolutionReport,
    KnowledgeGraphReport,
    KnowledgeIntegrationReport,
)
from goat.integration.versioning import (
    KnowledgeEvolutionEngine,
    KnowledgeStateVersion,
)

__all__ = [
    # Master System Integration
    "MasterSystemIntegrationEngine",
    # Core Models & Enums
    "KnowledgeNodeType",
    "KnowledgeRelationship",
    "ConflictType",
    "ConflictSeverity",
    "KnowledgeNode",
    "KnowledgeEdge",
    "IntegratedKnowledge",
    "ConflictRecord",
    # Deterministic Hashing & Identifiers
    "compute_node_id",
    "compute_node_fingerprint",
    "compute_edge_id",
    "compute_integrated_knowledge_id",
    "compute_conflict_id",
    "compute_evidence_merge_id",
    "compute_version_id",
    "serialize_canonical_json",
    # Graph Engine
    "ScientificKnowledgeGraph",
    # Integration Engine
    "ScientificKnowledgeIntegrationEngine",
    # Evidence Merging
    "EvidenceMergeRecord",
    "EvidenceMerger",
    # Conflict Detection
    "ConflictDetector",
    # Evolution & Versioning
    "KnowledgeStateVersion",
    "KnowledgeEvolutionEngine",
    # Reports
    "KnowledgeIntegrationReport",
    "ConflictReport",
    "KnowledgeGraphReport",
    "EvidenceMergeReport",
    "KnowledgeEvolutionReport",
    # Persistence Repositories
    "init_integration_db",
    "KnowledgeRepository",
    "GraphRepository",
    "ConflictRepository",
    "IntegrationRepository",
    "EvidenceRepository",
    "ReportRepository",
]
