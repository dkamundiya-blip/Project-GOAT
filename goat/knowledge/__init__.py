"""
Project GOAT v0.9 — Edge Knowledge Graph & Scientific Relationship Engine Package
"""

from goat.knowledge.core.canonical import (
    compute_canonical_sha256,
    compute_knowledge_graph_id,
    compute_knowledge_node_id,
    compute_knowledge_relationship_id,
    compute_knowledge_summary_id,
    compute_relationship_validation_id,
    compute_scientific_path_id,
    serialize_canonical_json,
)
from goat.knowledge.core.enums import (
    NodeType,
    PathValidity,
    RelationshipType,
    ValidationStatus,
)
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    KnowledgeSummary,
    RelationshipValidation,
    ScientificPath,
)

# Legacy v0.7 exports (retained for backward compatibility)
from goat.knowledge.enums import (
    EvidenceType,
    KnowledgeRelationshipType,
    KnowledgeStatus,
    KnowledgeType,
)
from goat.knowledge.evidence import EvidenceReference, compute_evidence_id
from goat.knowledge.graph import (
    CircularKnowledgeDependencyError,
    KnowledgeEdge,
    KnowledgeGraphValidationError,
    compute_knowledge_edge_id,
)
from goat.knowledge.memory import ScientificMemory
from goat.knowledge.model import (
    KnowledgeObject,
    compute_knowledge_fingerprint,
    compute_knowledge_id,
)
from goat.knowledge.provenance import KnowledgeProvenanceEngine
from goat.knowledge.registry import (
    KnowledgeAuditEvent,
    KnowledgeRegistry,
    KnowledgeRegistryRecord,
    KnowledgeRegistryVerifier,
    KnowledgeValidationError,
    SQLiteKnowledgeRepository,
)
from goat.knowledge.reporting import KnowledgeReport, generate_knowledge_report

# Sub-Engines
from goat.knowledge.engine import MasterKnowledgeEngine
from goat.knowledge.graph.engine import KnowledgeGraphEngine
from goat.knowledge.persistence.sqlite import (
    GraphRepository,
    KnowledgeNodeRepository,
    KnowledgePersistenceContext,
    RelationshipRepository,
    SummaryRepository,
    TraversalRepository,
    ValidationRepository,
)
from goat.knowledge.relationships.engine import RelationshipEngine
from goat.knowledge.reporting.reports import KnowledgeReportGenerator
from goat.knowledge.traversal.engine import TraversalEngine
from goat.knowledge.validation.engine import ValidationEngine

__all__ = [
    # v0.9 Enums
    "NodeType",
    "RelationshipType",
    "ValidationStatus",
    "PathValidity",
    # v0.9 Models
    "KnowledgeNode",
    "KnowledgeRelationship",
    "KnowledgeGraph",
    "ScientificPath",
    "RelationshipValidation",
    "KnowledgeSummary",
    # v0.9 Canonical Utilities
    "serialize_canonical_json",
    "compute_canonical_sha256",
    "compute_knowledge_node_id",
    "compute_knowledge_relationship_id",
    "compute_knowledge_graph_id",
    "compute_scientific_path_id",
    "compute_relationship_validation_id",
    "compute_knowledge_summary_id",
    # Sub-Engines
    "KnowledgeGraphEngine",
    "RelationshipEngine",
    "TraversalEngine",
    "ValidationEngine",
    "MasterKnowledgeEngine",
    # Reporting & Persistence
    "KnowledgeReportGenerator",
    "KnowledgeNodeRepository",
    "RelationshipRepository",
    "GraphRepository",
    "TraversalRepository",
    "ValidationRepository",
    "SummaryRepository",
    "KnowledgePersistenceContext",
    # Legacy v0.7 Exports
    "KnowledgeType",
    "KnowledgeStatus",
    "EvidenceType",
    "KnowledgeRelationshipType",
    "KnowledgeObject",
    "compute_knowledge_id",
    "compute_knowledge_fingerprint",
    "EvidenceReference",
    "compute_evidence_id",
    "KnowledgeRegistryRecord",
    "KnowledgeAuditEvent",
    "SQLiteKnowledgeRepository",
    "KnowledgeRegistryVerifier",
    "KnowledgeRegistry",
    "KnowledgeValidationError",
    "KnowledgeEdge",
    "compute_knowledge_edge_id",
    "CircularKnowledgeDependencyError",
    "KnowledgeGraphValidationError",
    "ScientificMemory",
    "KnowledgeProvenanceEngine",
    "KnowledgeReport",
    "generate_knowledge_report",
]
