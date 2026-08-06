"""
Project GOAT v0.9 — Edge Knowledge Graph Scientific Relationship Engine
"""

from typing import Any

from goat.knowledge.core.canonical import compute_knowledge_relationship_id
from goat.knowledge.core.enums import RelationshipType
from goat.knowledge.core.models import KnowledgeNode, KnowledgeRelationship


class RelationshipEngine:
    """Quantitative Sub-Engine for Creating Deterministic Scientific Links.

    Links hypotheses, evidence, microstructure observations, experiments,
    statistical evaluations, live validation sessions, governance decisions,
    discovered edges, and archives into an unbroken scientific lineage chain.
    """

    def create_relationship(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: RelationshipType | str,
        weight: float = 1.0,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeRelationship:
        """Create a deterministic KnowledgeRelationship link between two nodes."""
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)

        meta = dict(metadata or {})

        rel_id, r_hash = compute_knowledge_relationship_id(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type.value,
        )

        return KnowledgeRelationship(
            relationship_id=rel_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            weight=weight,
            timestamp=timestamp_str,
            metadata=meta,
            canonical_hash=r_hash,
        )

    def link_scientific_chain(
        self,
        nodes: list[KnowledgeNode],
        relationship_types: list[RelationshipType] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> list[KnowledgeRelationship]:
        """Link a sequence of ordered KnowledgeNode instances into a continuous scientific chain."""
        if len(nodes) < 2:
            return []

        relationships: list[KnowledgeRelationship] = []

        for i in range(1, len(nodes)):
            src = nodes[i - 1]
            tgt = nodes[i]

            if relationship_types and i - 1 < len(relationship_types):
                rel_type = relationship_types[i - 1]
            else:
                rel_type = self._infer_relationship_type(src, tgt)

            rel = self.create_relationship(
                source_node_id=src.node_id,
                target_node_id=tgt.node_id,
                relationship_type=rel_type,
                timestamp_str=timestamp_str,
            )
            relationships.append(rel)

        return relationships

    def _infer_relationship_type(self, src: KnowledgeNode, tgt: KnowledgeNode) -> RelationshipType:
        src_t = src.node_type.value
        tgt_t = tgt.node_type.value

        if src_t == "HYPOTHESIS" and tgt_t == "EVIDENCE":
            return RelationshipType.GENERATES_EVIDENCE
        elif src_t == "EVIDENCE" and tgt_t == "EXPERIMENT":
            return RelationshipType.CONDUCTS_EXPERIMENT
        elif src_t == "EXPERIMENT" and tgt_t == "STATISTICAL_EVALUATION":
            return RelationshipType.EVALUATES_STATISTICS
        elif src_t == "STATISTICAL_EVALUATION" and tgt_t == "LIVE_VALIDATION":
            return RelationshipType.VALIDATES_LIVE
        elif src_t == "LIVE_VALIDATION" and tgt_t == "GOVERNANCE_DECISION":
            return RelationshipType.DECIDES_GOVERNANCE
        elif src_t == "GOVERNANCE_DECISION" and tgt_t == "DISCOVERED_EDGE":
            return RelationshipType.DISCOVERS_EDGE
        elif src_t == "DISCOVERED_EDGE" and tgt_t == "ARCHIVE":
            return RelationshipType.ARCHIVES_ARTIFACT
        elif src_t == "OBSERVATION":
            return RelationshipType.OBSERVES_BEHAVIOR

        return RelationshipType.DERIVED_FROM
