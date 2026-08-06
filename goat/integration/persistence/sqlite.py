"""
Project GOAT v0.7 — SQLite Persistence for Knowledge Integration & Evidence Graph Engine

Provides repositories supporting round-trip persistence and foreign-key integrity:
- KnowledgeRepository
- GraphRepository
- ConflictRepository
- IntegrationRepository
- EvidenceRepository
- ReportRepository
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from goat.integration.core.models import (
    ConflictRecord,
    IntegratedKnowledge,
    KnowledgeEdge,
    KnowledgeNode,
)
from goat.integration.evidence.models import EvidenceMergeRecord
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.integration.reporting.reports import (
    ConflictReport,
    EvidenceMergeReport,
    KnowledgeEvolutionReport,
    KnowledgeGraphReport,
    KnowledgeIntegrationReport,
)
from goat.integration.versioning import KnowledgeStateVersion


def init_integration_db(conn: sqlite3.Connection) -> None:
    """Initialize SQLite database tables and foreign key pragmas."""
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_nodes (
                node_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                node_type TEXT NOT NULL,
                description TEXT NOT NULL,
                originating_validation TEXT NOT NULL,
                creation_timestamp TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                fingerprint TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_edges (
                edge_id TEXT PRIMARY KEY,
                source_node TEXT NOT NULL,
                destination_node TEXT NOT NULL,
                relationship TEXT NOT NULL,
                confidence REAL NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                FOREIGN KEY (source_node) REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE,
                FOREIGN KEY (destination_node) REFERENCES knowledge_nodes(node_id) ON DELETE CASCADE
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS integrated_knowledge (
                knowledge_id TEXT PRIMARY KEY,
                participating_validations_json TEXT NOT NULL,
                participating_hypotheses_json TEXT NOT NULL,
                participating_experiments_json TEXT NOT NULL,
                overall_confidence REAL NOT NULL,
                reproducibility REAL NOT NULL,
                consensus_strength REAL NOT NULL,
                conflict_score REAL NOT NULL,
                creation_timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                version TEXT NOT NULL,
                audit_metadata_json TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conflict_records (
                conflict_id TEXT PRIMARY KEY,
                validation_a TEXT NOT NULL,
                validation_b TEXT NOT NULL,
                conflict_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                explanation TEXT NOT NULL,
                supporting_evidence_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_merge_records (
                merge_id TEXT PRIMARY KEY,
                source_evidence_ids_json TEXT NOT NULL,
                target_knowledge_id TEXT NOT NULL,
                accumulated_confidence REAL NOT NULL,
                accumulated_reproducibility REAL NOT NULL,
                accumulated_consensus REAL NOT NULL,
                experiment_refs_json TEXT NOT NULL,
                study_refs_json TEXT NOT NULL,
                execution_refs_json TEXT NOT NULL,
                feature_refs_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_versions (
                version_id TEXT PRIMARY KEY,
                knowledge_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                state_hash TEXT NOT NULL,
                parent_version_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                graph_state_json TEXT NOT NULL,
                integrated_knowledge_json TEXT NOT NULL,
                canonical_hash TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS integration_reports (
                report_id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                report_json TEXT NOT NULL
            );
        """)


class KnowledgeRepository:
    """Repository for storing and retrieving KnowledgeNode models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_integration_db(self.conn)

    def save_node(self, node: KnowledgeNode) -> None:
        """Save a KnowledgeNode to database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_nodes (
                    node_id, title, node_type, description, originating_validation,
                    creation_timestamp, metadata_json, canonical_hash, fingerprint
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node.node_id,
                    node.title,
                    node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type),
                    node.description,
                    node.originating_validation,
                    node.creation_timestamp,
                    json.dumps(node.metadata, sort_keys=True),
                    node.canonical_hash,
                    node.fingerprint,
                ),
            )

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        """Fetch a KnowledgeNode by ID."""
        cursor = self.conn.execute(
            "SELECT node_id, title, node_type, description, originating_validation, creation_timestamp, metadata_json, canonical_hash, fingerprint FROM knowledge_nodes WHERE node_id = ?",
            (node_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return KnowledgeNode(
            node_id=row[0],
            title=row[1],
            node_type=row[2],
            description=row[3],
            originating_validation=row[4],
            creation_timestamp=row[5],
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
            fingerprint=row[8],
        )

    def list_nodes(self) -> list[KnowledgeNode]:
        """List all KnowledgeNodes sorted by node_id."""
        cursor = self.conn.execute("SELECT node_id FROM knowledge_nodes ORDER BY node_id ASC")
        nodes = []
        for row in cursor.fetchall():
            nd = self.get_node(row[0])
            if nd:
                nodes.append(nd)
        return nodes


class GraphRepository:
    """Repository for storing and retrieving full ScientificKnowledgeGraph objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_integration_db(self.conn)
        self._node_repo = KnowledgeRepository(conn)

    def save_edge(self, edge: KnowledgeEdge) -> None:
        """Save a KnowledgeEdge to database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_edges (
                    edge_id, source_node, destination_node, relationship,
                    confidence, supporting_evidence_json, metadata_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge.edge_id,
                    edge.source_node,
                    edge.destination_node,
                    edge.relationship.value if hasattr(edge.relationship, "value") else str(edge.relationship),
                    edge.confidence,
                    json.dumps(edge.supporting_evidence, sort_keys=True),
                    json.dumps(edge.metadata, sort_keys=True),
                    edge.canonical_hash,
                ),
            )

    def get_edge(self, edge_id: str) -> KnowledgeEdge | None:
        """Fetch KnowledgeEdge by ID."""
        cursor = self.conn.execute(
            "SELECT edge_id, source_node, destination_node, relationship, confidence, supporting_evidence_json, metadata_json, canonical_hash FROM knowledge_edges WHERE edge_id = ?",
            (edge_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return KnowledgeEdge(
            edge_id=row[0],
            source_node=row[1],
            destination_node=row[2],
            relationship=row[3],
            confidence=row[4],
            supporting_evidence=json.loads(row[5]),
            metadata=json.loads(row[6]),
            canonical_hash=row[7],
        )

    def save_graph(self, graph: ScientificKnowledgeGraph) -> None:
        """Save an entire ScientificKnowledgeGraph to database."""
        for node in graph.get_nodes():
            self._node_repo.save_node(node)
        for edge in graph.get_edges():
            self.save_edge(edge)

    def load_graph(self) -> ScientificKnowledgeGraph:
        """Load ScientificKnowledgeGraph from database."""
        graph = ScientificKnowledgeGraph()
        for node in self._node_repo.list_nodes():
            graph.add_node(node)
        cursor = self.conn.execute("SELECT edge_id FROM knowledge_edges ORDER BY edge_id ASC")
        for row in cursor.fetchall():
            edge = self.get_edge(row[0])
            if edge:
                graph.add_edge(edge)
        return graph


class ConflictRepository:
    """Repository for storing and retrieving ConflictRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_integration_db(self.conn)

    def save_conflict(self, conflict: ConflictRecord) -> None:
        """Save ConflictRecord to database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO conflict_records (
                    conflict_id, validation_a, validation_b, conflict_type,
                    severity, explanation, supporting_evidence_json, canonical_hash, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conflict.conflict_id,
                    conflict.validation_a,
                    conflict.validation_b,
                    conflict.conflict_type.value if hasattr(conflict.conflict_type, "value") else str(conflict.conflict_type),
                    conflict.severity.value if hasattr(conflict.severity, "value") else str(conflict.severity),
                    conflict.explanation,
                    json.dumps(conflict.supporting_evidence, sort_keys=True),
                    conflict.canonical_hash,
                    conflict.timestamp,
                ),
            )

    def get_conflict(self, conflict_id: str) -> ConflictRecord | None:
        """Fetch ConflictRecord by ID."""
        cursor = self.conn.execute(
            "SELECT conflict_id, validation_a, validation_b, conflict_type, severity, explanation, supporting_evidence_json, canonical_hash, timestamp FROM conflict_records WHERE conflict_id = ?",
            (conflict_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return ConflictRecord(
            conflict_id=row[0],
            validation_a=row[1],
            validation_b=row[2],
            conflict_type=row[3],
            severity=row[4],
            explanation=row[5],
            supporting_evidence=json.loads(row[6]),
            canonical_hash=row[7],
            timestamp=row[8],
        )

    def list_conflicts(self) -> list[ConflictRecord]:
        """List all ConflictRecords sorted by conflict_id."""
        cursor = self.conn.execute("SELECT conflict_id FROM conflict_records ORDER BY conflict_id ASC")
        records = []
        for row in cursor.fetchall():
            rec = self.get_conflict(row[0])
            if rec:
                records.append(rec)
        return records


class IntegrationRepository:
    """Repository for storing and retrieving IntegratedKnowledge models and version states."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_integration_db(self.conn)

    def save_integrated_knowledge(self, ik: IntegratedKnowledge) -> None:
        """Save IntegratedKnowledge model to database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO integrated_knowledge (
                    knowledge_id, participating_validations_json, participating_hypotheses_json,
                    participating_experiments_json, overall_confidence, reproducibility,
                    consensus_strength, conflict_score, creation_timestamp, canonical_hash,
                    version, audit_metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ik.knowledge_id,
                    json.dumps(ik.participating_validations, sort_keys=True),
                    json.dumps(ik.participating_hypotheses, sort_keys=True),
                    json.dumps(ik.participating_experiments, sort_keys=True),
                    ik.overall_confidence,
                    ik.reproducibility,
                    ik.consensus_strength,
                    ik.conflict_score,
                    ik.creation_timestamp,
                    ik.canonical_hash,
                    ik.version,
                    json.dumps(ik.audit_metadata, sort_keys=True),
                ),
            )

    def get_integrated_knowledge(self, knowledge_id: str) -> IntegratedKnowledge | None:
        """Fetch IntegratedKnowledge model by ID."""
        cursor = self.conn.execute(
            """
            SELECT knowledge_id, participating_validations_json, participating_hypotheses_json,
                   participating_experiments_json, overall_confidence, reproducibility,
                   consensus_strength, conflict_score, creation_timestamp, canonical_hash,
                   version, audit_metadata_json
            FROM integrated_knowledge WHERE knowledge_id = ?
            """,
            (knowledge_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return IntegratedKnowledge(
            knowledge_id=row[0],
            participating_validations=json.loads(row[1]),
            participating_hypotheses=json.loads(row[2]),
            participating_experiments=json.loads(row[3]),
            overall_confidence=row[4],
            reproducibility=row[5],
            consensus_strength=row[6],
            conflict_score=row[7],
            creation_timestamp=row[8],
            canonical_hash=row[9],
            version=row[10],
            audit_metadata=json.loads(row[11]),
        )

    def save_version(self, version: KnowledgeStateVersion) -> None:
        """Save KnowledgeStateVersion model to database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_versions (
                    version_id, knowledge_id, version_number, state_hash,
                    parent_version_id, timestamp, graph_state_json, integrated_knowledge_json, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version.version_id,
                    version.knowledge_id,
                    version.version_number,
                    version.state_hash,
                    version.parent_version_id,
                    version.timestamp,
                    json.dumps(version.graph_state, sort_keys=True),
                    json.dumps(version.integrated_knowledge.dict(), sort_keys=True),
                    version.canonical_hash,
                ),
            )

    def get_version(self, version_id: str) -> KnowledgeStateVersion | None:
        """Fetch KnowledgeStateVersion model by ID."""
        cursor = self.conn.execute(
            """
            SELECT version_id, knowledge_id, version_number, state_hash, parent_version_id,
                   timestamp, graph_state_json, integrated_knowledge_json, canonical_hash
            FROM knowledge_versions WHERE version_id = ?
            """,
            (version_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return KnowledgeStateVersion(
            version_id=row[0],
            knowledge_id=row[1],
            version_number=row[2],
            state_hash=row[3],
            parent_version_id=row[4],
            timestamp=row[5],
            graph_state=json.loads(row[6]),
            integrated_knowledge=IntegratedKnowledge(**json.loads(row[7])),
            canonical_hash=row[8],
        )

    def list_versions_for_knowledge(self, knowledge_id: str) -> list[KnowledgeStateVersion]:
        """List all version snapshots for a knowledge ID ordered by version_number."""
        cursor = self.conn.execute(
            "SELECT version_id FROM knowledge_versions WHERE knowledge_id = ? ORDER BY version_number ASC",
            (knowledge_id,),
        )
        versions = []
        for row in cursor.fetchall():
            v = self.get_version(row[0])
            if v:
                versions.append(v)
        return versions


class EvidenceRepository:
    """Repository for storing and retrieving EvidenceMergeRecord models."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_integration_db(self.conn)

    def save_merge_record(self, record: EvidenceMergeRecord) -> None:
        """Save EvidenceMergeRecord to database."""
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO evidence_merge_records (
                    merge_id, source_evidence_ids_json, target_knowledge_id,
                    accumulated_confidence, accumulated_reproducibility, accumulated_consensus,
                    experiment_refs_json, study_refs_json, execution_refs_json, feature_refs_json,
                    timestamp, canonical_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.merge_id,
                    json.dumps(record.source_evidence_ids, sort_keys=True),
                    record.target_knowledge_id,
                    record.accumulated_confidence,
                    record.accumulated_reproducibility,
                    record.accumulated_consensus,
                    json.dumps(record.experiment_refs, sort_keys=True),
                    json.dumps(record.study_refs, sort_keys=True),
                    json.dumps(record.execution_refs, sort_keys=True),
                    json.dumps(record.feature_refs, sort_keys=True),
                    record.timestamp,
                    record.canonical_hash,
                ),
            )

    def get_merge_record(self, merge_id: str) -> EvidenceMergeRecord | None:
        """Fetch EvidenceMergeRecord by ID."""
        cursor = self.conn.execute(
            """
            SELECT merge_id, source_evidence_ids_json, target_knowledge_id,
                   accumulated_confidence, accumulated_reproducibility, accumulated_consensus,
                   experiment_refs_json, study_refs_json, execution_refs_json, feature_refs_json,
                   timestamp, canonical_hash
            FROM evidence_merge_records WHERE merge_id = ?
            """,
            (merge_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return EvidenceMergeRecord(
            merge_id=row[0],
            source_evidence_ids=json.loads(row[1]),
            target_knowledge_id=row[2],
            accumulated_confidence=row[3],
            accumulated_reproducibility=row[4],
            accumulated_consensus=row[5],
            experiment_refs=json.loads(row[6]),
            study_refs=json.loads(row[7]),
            execution_refs=json.loads(row[8]),
            feature_refs=json.loads(row[9]),
            timestamp=row[10],
            canonical_hash=row[11],
        )


class ReportRepository:
    """Repository for storing and retrieving report objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        init_integration_db(self.conn)

    def save_report(self, report_id: str, report_type: str, timestamp: str, report_model: Any) -> None:
        """Save a report object to database."""
        report_json = report_model.to_json() if hasattr(report_model, "to_json") else json.dumps(report_model.dict(), sort_keys=True)
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO integration_reports (report_id, report_type, timestamp, report_json) VALUES (?, ?, ?, ?)",
                (report_id, report_type, timestamp, report_json),
            )

    def get_report_json(self, report_id: str) -> str | None:
        """Fetch raw JSON representation of a report."""
        cursor = self.conn.execute(
            "SELECT report_json FROM integration_reports WHERE report_id = ?",
            (report_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
