"""
Project GOAT v0.9 — SQLite Persistence Repositories for Edge Knowledge Graph Subsystem
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

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


def init_knowledge_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables, indexes, and pragmas for Knowledge Graph subsystem."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graph_nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                label TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                attributes_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graph_relationships (
                relationship_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                weight REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (source_node_id) REFERENCES knowledge_graph_nodes (node_id) ON DELETE CASCADE,
                FOREIGN KEY (target_node_id) REFERENCES knowledge_graph_nodes (node_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graphs (
                graph_id TEXT PRIMARY KEY,
                graph_name TEXT NOT NULL,
                node_ids_json TEXT NOT NULL,
                relationship_ids_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scientific_paths (
                path_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                node_chain_json TEXT NOT NULL,
                relationship_chain_json TEXT NOT NULL,
                validity TEXT NOT NULL,
                path_length INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relationship_validations (
                validation_id TEXT PRIMARY KEY,
                graph_id TEXT NOT NULL,
                status TEXT NOT NULL,
                is_valid INTEGER NOT NULL,
                broken_chain_count INTEGER NOT NULL,
                orphan_node_count INTEGER NOT NULL,
                cycle_count INTEGER NOT NULL,
                duplicate_count INTEGER NOT NULL,
                violations_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_summaries (
                summary_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total_nodes INTEGER NOT NULL,
                total_relationships INTEGER NOT NULL,
                total_graphs INTEGER NOT NULL,
                total_paths_analyzed INTEGER NOT NULL,
                node_type_counts_json TEXT NOT NULL,
                relationship_type_counts_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)


class KnowledgeNodeRepository:
    """Repository for KnowledgeNode instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, node: KnowledgeNode) -> KnowledgeNode:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_graph_nodes (
                    node_id, node_type, entity_id, label, timestamp,
                    attributes_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node.node_id,
                    node.node_type.value,
                    node.entity_id,
                    node.label,
                    node.timestamp,
                    json.dumps(node.attributes),
                    node.canonical_hash,
                ),
            )
        return node

    def get_by_id(self, node_id: str) -> KnowledgeNode | None:
        cursor = self._conn.execute("SELECT * FROM knowledge_graph_nodes WHERE node_id = ?", (node_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[KnowledgeNode]:
        cursor = self._conn.execute("SELECT * FROM knowledge_graph_nodes ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> KnowledgeNode:
        return KnowledgeNode(
            node_id=row[0],
            node_type=NodeType(row[1]),
            entity_id=row[2],
            label=row[3],
            timestamp=row[4],
            attributes=json.loads(row[5]),
            canonical_hash=row[6],
        )


class RelationshipRepository:
    """Repository for KnowledgeRelationship instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, rel: KnowledgeRelationship) -> KnowledgeRelationship:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_graph_relationships (
                    relationship_id, source_node_id, target_node_id, relationship_type,
                    weight, timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rel.relationship_id,
                    rel.source_node_id,
                    rel.target_node_id,
                    rel.relationship_type.value,
                    rel.weight,
                    rel.timestamp,
                    json.dumps(rel.metadata),
                    rel.canonical_hash,
                ),
            )
        return rel

    def get_by_id(self, relationship_id: str) -> KnowledgeRelationship | None:
        cursor = self._conn.execute("SELECT * FROM knowledge_graph_relationships WHERE relationship_id = ?", (relationship_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[KnowledgeRelationship]:
        cursor = self._conn.execute("SELECT * FROM knowledge_graph_relationships ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> KnowledgeRelationship:
        return KnowledgeRelationship(
            relationship_id=row[0],
            source_node_id=row[1],
            target_node_id=row[2],
            relationship_type=RelationshipType(row[3]),
            weight=float(row[4]),
            timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )


class GraphRepository:
    """Repository for KnowledgeGraph instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_graphs (
                    graph_id, graph_name, node_ids_json, relationship_ids_json,
                    created_at, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    graph.graph_id,
                    graph.graph_name,
                    json.dumps(graph.node_ids),
                    json.dumps(graph.relationship_ids),
                    graph.created_at,
                    json.dumps(graph.metadata),
                    graph.canonical_hash,
                ),
            )
        return graph

    def get_by_id(self, graph_id: str) -> KnowledgeGraph | None:
        cursor = self._conn.execute("SELECT * FROM knowledge_graphs WHERE graph_id = ?", (graph_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[KnowledgeGraph]:
        cursor = self._conn.execute("SELECT * FROM knowledge_graphs ORDER BY created_at ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> KnowledgeGraph:
        return KnowledgeGraph(
            graph_id=row[0],
            graph_name=row[1],
            node_ids=json.loads(row[2]),
            relationship_ids=json.loads(row[3]),
            created_at=row[4],
            metadata=json.loads(row[5]),
            canonical_hash=row[6],
        )


class TraversalRepository:
    """Repository for ScientificPath instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, path: ScientificPath) -> ScientificPath:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO scientific_paths (
                    path_id, source_node_id, target_node_id, node_chain_json,
                    relationship_chain_json, validity, path_length, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    path.path_id,
                    path.source_node_id,
                    path.target_node_id,
                    json.dumps(path.node_chain),
                    json.dumps(path.relationship_chain),
                    path.validity.value,
                    path.path_length,
                    json.dumps(path.metadata),
                    path.canonical_hash,
                ),
            )
        return path

    def get_by_id(self, path_id: str) -> ScientificPath | None:
        cursor = self._conn.execute("SELECT * FROM scientific_paths WHERE path_id = ?", (path_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[ScientificPath]:
        cursor = self._conn.execute("SELECT * FROM scientific_paths")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> ScientificPath:
        return ScientificPath(
            path_id=row[0],
            source_node_id=row[1],
            target_node_id=row[2],
            node_chain=json.loads(row[3]),
            relationship_chain=json.loads(row[4]),
            validity=PathValidity(row[5]),
            path_length=int(row[6]),
            metadata=json.loads(row[7]),
            canonical_hash=row[8],
        )


class ValidationRepository:
    """Repository for RelationshipValidation instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, val: RelationshipValidation) -> RelationshipValidation:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO relationship_validations (
                    validation_id, graph_id, status, is_valid, broken_chain_count,
                    orphan_node_count, cycle_count, duplicate_count, violations_json,
                    timestamp, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    val.validation_id,
                    val.graph_id,
                    val.status.value,
                    1 if val.is_valid else 0,
                    val.broken_chain_count,
                    val.orphan_node_count,
                    val.cycle_count,
                    val.duplicate_count,
                    json.dumps(val.violations),
                    val.timestamp,
                    json.dumps(val.metadata),
                    val.canonical_hash,
                ),
            )
        return val

    def get_by_id(self, validation_id: str) -> RelationshipValidation | None:
        cursor = self._conn.execute("SELECT * FROM relationship_validations WHERE validation_id = ?", (validation_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[RelationshipValidation]:
        cursor = self._conn.execute("SELECT * FROM relationship_validations ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> RelationshipValidation:
        return RelationshipValidation(
            validation_id=row[0],
            graph_id=row[1],
            status=ValidationStatus(row[2]),
            is_valid=bool(row[3]),
            broken_chain_count=int(row[4]),
            orphan_node_count=int(row[5]),
            cycle_count=int(row[6]),
            duplicate_count=int(row[7]),
            violations=json.loads(row[8]),
            timestamp=row[9],
            metadata=json.loads(row[10]),
            canonical_hash=row[11],
        )


class SummaryRepository:
    """Repository for KnowledgeSummary instances."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, summary: KnowledgeSummary) -> KnowledgeSummary:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_summaries (
                    summary_id, timestamp, total_nodes, total_relationships, total_graphs,
                    total_paths_analyzed, node_type_counts_json, relationship_type_counts_json,
                    metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.summary_id,
                    summary.timestamp,
                    summary.total_nodes,
                    summary.total_relationships,
                    summary.total_graphs,
                    summary.total_paths_analyzed,
                    json.dumps(summary.node_type_counts),
                    json.dumps(summary.relationship_type_counts),
                    json.dumps(summary.metadata),
                    summary.canonical_hash,
                ),
            )
        return summary

    def get_by_id(self, summary_id: str) -> KnowledgeSummary | None:
        cursor = self._conn.execute("SELECT * FROM knowledge_summaries WHERE summary_id = ?", (summary_id,))
        row = cursor.fetchone()
        return self._row_to_model(row) if row else None

    def list_all(self) -> list[KnowledgeSummary]:
        cursor = self._conn.execute("SELECT * FROM knowledge_summaries ORDER BY timestamp ASC")
        return [self._row_to_model(r) for r in cursor.fetchall()]

    def _row_to_model(self, row: sqlite3.Row | tuple) -> KnowledgeSummary:
        return KnowledgeSummary(
            summary_id=row[0],
            timestamp=row[1],
            total_nodes=int(row[2]),
            total_relationships=int(row[3]),
            total_graphs=int(row[4]),
            total_paths_analyzed=int(row[5]),
            node_type_counts=json.loads(row[6]),
            relationship_type_counts=json.loads(row[7]),
            metadata=json.loads(row[8]),
            canonical_hash=row[9],
        )


class KnowledgePersistenceContext:
    """Unified Persistence Database Context wrapping all Knowledge Graph repositories."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path)
        init_knowledge_db(self.conn)
        self.nodes = KnowledgeNodeRepository(self.conn)
        self.relationships = RelationshipRepository(self.conn)
        self.graphs = GraphRepository(self.conn)
        self.traversals = TraversalRepository(self.conn)
        self.validations = ValidationRepository(self.conn)
        self.summaries = SummaryRepository(self.conn)

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
