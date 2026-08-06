"""
Project GOAT v0.9 — Master Edge Knowledge Graph & Scientific Relationship Engine
"""

from typing import Any

from goat.knowledge.core.canonical import compute_knowledge_summary_id
from goat.knowledge.core.enums import NodeType, RelationshipType
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    KnowledgeSummary,
    RelationshipValidation,
    ScientificPath,
)
from goat.knowledge.graph.engine import KnowledgeGraphEngine
from goat.knowledge.persistence.sqlite import KnowledgePersistenceContext
from goat.knowledge.relationships.engine import RelationshipEngine
from goat.knowledge.reporting.reports import KnowledgeReportGenerator
from goat.knowledge.traversal.engine import TraversalEngine
from goat.knowledge.validation.engine import ValidationEngine


class MasterKnowledgeEngine:
    """Master Orchestrator for Step 9.10 Edge Knowledge Graph Subsystem.

    Integrates node creation, relationship linking, graph assembly, deterministic
    traversal, structural validation, database persistence, and reporting.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.persistence = KnowledgePersistenceContext(db_path)
        self.graph_engine = KnowledgeGraphEngine()
        self.relationship_engine = RelationshipEngine()
        self.traversal_engine = TraversalEngine()
        self.validation_engine = ValidationEngine()
        self.report_generator = KnowledgeReportGenerator()

    def add_node(
        self,
        node_type: NodeType | str,
        entity_id: str,
        label: str,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        attributes: dict[str, Any] | None = None,
    ) -> KnowledgeNode:
        """Create a node and save to database persistence."""
        node = self.graph_engine.create_node(
            node_type=node_type,
            entity_id=entity_id,
            label=label,
            timestamp_str=timestamp_str,
            attributes=attributes,
        )
        self.persistence.nodes.save(node)
        return node

    def add_relationship(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: RelationshipType | str,
        weight: float = 1.0,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeRelationship:
        """Create a directed relationship link and save to database persistence."""
        rel = self.relationship_engine.create_relationship(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            weight=weight,
            timestamp_str=timestamp_str,
            metadata=metadata,
        )
        self.persistence.relationships.save(rel)
        return rel

    def build_graph(
        self,
        graph_name: str,
        nodes: list[KnowledgeNode] | None = None,
        relationships: list[KnowledgeRelationship] | None = None,
        created_at_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgeGraph:
        """Assemble a graph from provided or persisted nodes/relationships and save to DB."""
        if nodes is None:
            nodes = self.persistence.nodes.list_all()
        if relationships is None:
            relationships = self.persistence.relationships.list_all()

        graph = self.graph_engine.assemble_graph(
            graph_name=graph_name,
            nodes=nodes,
            relationships=relationships,
            created_at_str=created_at_str,
            metadata=metadata,
        )
        self.persistence.graphs.save(graph)
        return graph

    def traverse_paths(
        self,
        source_node_id: str,
        target_node_id: str,
        max_depth: int = 10,
    ) -> list[ScientificPath]:
        """Find deterministic scientific paths between source and target nodes."""
        nodes = self.persistence.nodes.list_all()
        relationships = self.persistence.relationships.list_all()

        paths = self.traversal_engine.find_paths(
            nodes=nodes,
            relationships=relationships,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            max_depth=max_depth,
        )

        for p in paths:
            self.persistence.traversals.save(p)

        return paths

    def validate_graph(
        self,
        graph_id: str,
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> RelationshipValidation:
        """Validate structural and scientific integrity of a graph state."""
        graph = self.persistence.graphs.get_by_id(graph_id)
        all_nodes = {n.node_id: n for n in self.persistence.nodes.list_all()}
        all_rels = {r.relationship_id: r for r in self.persistence.relationships.list_all()}

        if graph:
            g_nodes = [all_nodes[nid] for nid in graph.node_ids if nid in all_nodes]
            g_rels = [all_rels[rid] for rid in graph.relationship_ids if rid in all_rels]
        else:
            g_nodes = list(all_nodes.values())
            g_rels = list(all_rels.values())

        validation = self.validation_engine.validate_graph(
            graph_id=graph_id,
            nodes=g_nodes,
            relationships=g_rels,
            timestamp_str=timestamp_str,
        )
        self.persistence.validations.save(validation)
        return validation

    def generate_executive_summary(
        self,
        timestamp_str: str = "2026-01-01T00:00:00Z",
    ) -> KnowledgeSummary:
        """Compute executive summary across all persisted nodes, relationships, and graphs."""
        nodes = self.persistence.nodes.list_all()
        rels = self.persistence.relationships.list_all()
        graphs = self.persistence.graphs.list_all()
        paths = self.persistence.traversals.list_all()

        n_counts: dict[str, int] = {}
        for n in nodes:
            n_counts[n.node_type.value] = n_counts.get(n.node_type.value, 0) + 1

        r_counts: dict[str, int] = {}
        for r in rels:
            r_counts[r.relationship_type.value] = r_counts.get(r.relationship_type.value, 0) + 1

        sum_id, s_hash = compute_knowledge_summary_id(
            timestamp=timestamp_str,
            total_nodes=len(nodes),
            total_relationships=len(rels),
        )

        summary = KnowledgeSummary(
            summary_id=sum_id,
            timestamp=timestamp_str,
            total_nodes=len(nodes),
            total_relationships=len(rels),
            total_graphs=len(graphs),
            total_paths_analyzed=len(paths),
            node_type_counts=n_counts,
            relationship_type_counts=r_counts,
            metadata={},
            canonical_hash=s_hash,
        )

        self.persistence.summaries.save(summary)
        return summary

    def close(self) -> None:
        """Close database persistence connection."""
        self.persistence.close()
