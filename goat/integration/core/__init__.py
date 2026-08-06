"""
Project GOAT v0.7 — Integration Core Package
"""

from goat.integration.core.canonical import (
    compute_conflict_id,
    compute_edge_id,
    compute_evidence_merge_id,
    compute_integrated_knowledge_id,
    compute_node_fingerprint,
    compute_node_id,
    compute_version_id,
    serialize_canonical_json,
)
from goat.integration.core.enums import (
    ConflictSeverity,
    ConflictType,
    KnowledgeNodeType,
    KnowledgeRelationship,
)
from goat.integration.core.models import (
    ConflictRecord,
    IntegratedKnowledge,
    KnowledgeEdge,
    KnowledgeNode,
)

__all__ = [
    "KnowledgeNodeType",
    "KnowledgeRelationship",
    "ConflictType",
    "ConflictSeverity",
    "KnowledgeNode",
    "KnowledgeEdge",
    "IntegratedKnowledge",
    "ConflictRecord",
    "compute_node_id",
    "compute_node_fingerprint",
    "compute_edge_id",
    "compute_integrated_knowledge_id",
    "compute_conflict_id",
    "compute_evidence_merge_id",
    "compute_version_id",
    "serialize_canonical_json",
]
