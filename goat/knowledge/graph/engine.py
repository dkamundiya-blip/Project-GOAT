"""
Project GOAT v0.9 — Edge Knowledge Graph Node & Graph Creation Engine
"""

from typing import Any

from goat.knowledge.core.canonical import (
    compute_knowledge_graph_id,
    compute_knowledge_node_id,
)
from goat.knowledge.core.enums import NodeType
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
)


class KnowledgeGraphEngine:
    """Quantitative Sub-Engine for Graph Node & Graph Creation.

    Creates immutable KnowledgeNode instances for all scientific entities in GOAT,
    and constructs container KnowledgeGraph instances.
    """

    def create_node(
        self,
        node_type: NodeType | str,
        entity_id: str,
        label: str,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        attributes: dict[str, Any] | None = None,
    ) -> KnowledgeNode:
        """Create an immutable KnowledgeNode for a given entity."""
        if isinstance(node_type, str):
            node_type = NodeType(node_type)

        attrs = dict(attributes or {})

        node_id, n_hash = compute_knowledge_node_id(
            node_type=node_type.value,
            entity_id=entity_id,
            label=label,
        )

        return KnowledgeNode(
            node_id=node_id,
            node_type=node_type,
            entity_id=entity_id,
            label=label,
            timestamp=timestamp_str,
            attributes=attrs,
            canonical_hash=n_hash,
        )

    def assemble_graph(
        self,
        graph_name: str,
        nodes: list[KnowledgeNode],
        relationships: list[KnowledgeRelationship],
        created_at_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeGraph:
        """Assemble a list of nodes and relationships into an immutable KnowledgeGraph."""
        meta = dict(metadata or {})
        n_ids = [n.node_id for n in nodes]
        r_ids = [r.relationship_id for r in relationships]

        graph_id, g_hash = compute_knowledge_graph_id(
            graph_name=graph_name,
            node_ids=n_ids,
            relationship_ids=r_ids,
        )

        return KnowledgeGraph(
            graph_id=graph_id,
            graph_name=graph_name,
            node_ids=n_ids,
            relationship_ids=r_ids,
            created_at=created_at_str,
            metadata=meta,
            canonical_hash=g_hash,
        )
