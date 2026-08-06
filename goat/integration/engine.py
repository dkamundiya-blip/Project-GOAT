"""
Project GOAT v0.7 — Scientific Knowledge Integration & Evidence Graph Engine

Main coordinator executing the long-term scientific memory workflow:
1. Receive newly validated hypothesis/validation findings
2. Load existing knowledge base
3. Compare findings & detect contradictions (ConflictDetector)
4. Merge compatible evidence (EvidenceMerger)
5. Construct/update Knowledge Nodes & Edges in ScientificKnowledgeGraph
6. Generate IntegratedKnowledge model
7. Version evolution tracking (KnowledgeEvolutionEngine)
8. Persist to SQLite repositories
9. Generate reports
10. Deterministic Replay
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.integration.conflicts.detector import ConflictDetector
from goat.integration.core.canonical import (
    compute_edge_id,
    compute_integrated_knowledge_id,
    compute_node_id,
    compute_canonical_sha256,
)
from goat.integration.core.enums import (
    KnowledgeNodeType,
    KnowledgeRelationship,
)
from goat.integration.core.models import (
    ConflictRecord,
    IntegratedKnowledge,
    KnowledgeEdge,
    KnowledgeNode,
)
from goat.integration.evidence.merger import EvidenceMerger
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.integration.persistence.sqlite import (
    ConflictRepository,
    EvidenceRepository,
    GraphRepository,
    IntegrationRepository,
    KnowledgeRepository,
    ReportRepository,
)
from goat.integration.reporting.reports import (
    ConflictReport,
    EvidenceMergeReport,
    KnowledgeEvolutionReport,
    KnowledgeGraphReport,
    KnowledgeIntegrationReport,
)
from goat.integration.versioning import KnowledgeEvolutionEngine, KnowledgeStateVersion


class ScientificKnowledgeIntegrationEngine:
    """Deterministic Scientific Knowledge Integration & Evidence Graph Engine."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.graph = ScientificKnowledgeGraph()
        self.conflict_detector = ConflictDetector()
        self.evidence_merger = EvidenceMerger()
        self.evolution_engine = KnowledgeEvolutionEngine()

        # SQLite Repositories
        self.node_repo = KnowledgeRepository(self.conn)
        self.graph_repo = GraphRepository(self.conn)
        self.conflict_repo = ConflictRepository(self.conn)
        self.integration_repo = IntegrationRepository(self.conn)
        self.evidence_repo = EvidenceRepository(self.conn)
        self.report_repo = ReportRepository(self.conn)

    def process_validation_run(
        self,
        validation_payload: dict[str, Any],
        timestamp: str,
        existing_validations: list[dict[str, Any]] | None = None,
    ) -> tuple[IntegratedKnowledge, KnowledgeIntegrationReport]:
        """Integrate a newly validated hypothesis / validation run into the long-term scientific memory graph.

        Args:
            validation_payload: Dict containing validation details.
            timestamp: ISO 8601 UTC timestamp string.
            existing_validations: Optional list of previous validation dicts to compare against.

        Returns:
            Tuple of (IntegratedKnowledge, KnowledgeIntegrationReport).
        """
        val_id = str(validation_payload.get("validation_id") or validation_payload.get("id") or "VAL_NEW").strip()
        hyp_id = str(validation_payload.get("hypothesis_id") or validation_payload.get("hypothesis") or "HYP_NEW").strip()
        exp_id = str(validation_payload.get("experiment_id") or validation_payload.get("experiment") or "EXP_NEW").strip()
        title = str(validation_payload.get("title") or f"Validation Node {val_id}")
        desc = str(validation_payload.get("description") or "Validated hypothesis node")

        # 1. Create Knowledge Node for Validation
        val_node_id, val_hash, val_fp = compute_node_id(
            title=title,
            node_type=KnowledgeNodeType.VALIDATION.value,
            originating_validation=val_id,
        )
        val_node = KnowledgeNode(
            node_id=val_node_id,
            title=title,
            node_type=KnowledgeNodeType.VALIDATION,
            description=desc,
            originating_validation=val_id,
            creation_timestamp=timestamp,
            metadata=validation_payload.get("metadata", {}),
            canonical_hash=val_hash,
            fingerprint=val_fp,
        )
        self.graph.add_node(val_node)

        # 2. Create Knowledge Node for Hypothesis if provided
        hyp_node_id, hyp_hash, hyp_fp = compute_node_id(
            title=f"Hypothesis {hyp_id}",
            node_type=KnowledgeNodeType.HYPOTHESIS.value,
            originating_validation=val_id,
        )
        hyp_node = KnowledgeNode(
            node_id=hyp_node_id,
            title=f"Hypothesis {hyp_id}",
            node_type=KnowledgeNodeType.HYPOTHESIS,
            description=f"Hypothesis {hyp_id} associated with {val_id}",
            originating_validation=val_id,
            creation_timestamp=timestamp,
            metadata={"hypothesis_id": hyp_id},
            canonical_hash=hyp_hash,
            fingerprint=hyp_fp,
        )
        self.graph.add_node(hyp_node)

        # 3. Create Edge SUPPORTS between validation node and hypothesis node
        edge_id, edge_hash = compute_edge_id(
            source_node=val_node_id,
            destination_node=hyp_node_id,
            relationship=KnowledgeRelationship.SUPPORTS.value,
        )
        edge = KnowledgeEdge(
            edge_id=edge_id,
            source_node=val_node_id,
            destination_node=hyp_node_id,
            relationship=KnowledgeRelationship.SUPPORTS,
            confidence=float(validation_payload.get("confidence", 1.0)),
            supporting_evidence=[val_id],
            metadata={},
            canonical_hash=edge_hash,
        )
        self.graph.add_edge(edge)

        # 4. Conflict Detection
        all_validations = list(existing_validations or []) + [validation_payload]
        conflicts = self.conflict_detector.detect_all_conflicts(all_validations, timestamp=timestamp)
        conflict_score = min(1.0, float(len([c for c in conflicts if c.conflict_type.value == "CONTRADICTED"])) * 0.5)

        # Save conflicts to repo
        for c in conflicts:
            self.conflict_repo.save_conflict(c)

        # 5. Evidence Merging
        part_validations = sorted(list(set([str(v.get("validation_id") or v.get("id")) for v in all_validations if (v.get("validation_id") or v.get("id"))])))
        part_hypotheses = sorted(list(set([str(v.get("hypothesis_id") or v.get("hypothesis")) for v in all_validations if (v.get("hypothesis_id") or v.get("hypothesis"))])))
        part_experiments = sorted(list(set([str(v.get("experiment_id") or v.get("experiment")) for v in all_validations if (v.get("experiment_id") or v.get("experiment"))])))

        ik_id, ik_hash = compute_integrated_knowledge_id(
            participating_validations=part_validations,
            participating_hypotheses=part_hypotheses,
            participating_experiments=part_experiments,
        )

        merge_rec = self.evidence_merger.merge_evidence(
            evidence_items=all_validations,
            target_knowledge_id=ik_id,
            timestamp=timestamp,
        )
        self.evidence_repo.save_merge_record(merge_rec)

        # 6. Build IntegratedKnowledge Model
        integrated_knowledge = IntegratedKnowledge(
            knowledge_id=ik_id,
            participating_validations=part_validations,
            participating_hypotheses=part_hypotheses,
            participating_experiments=part_experiments,
            overall_confidence=merge_rec.accumulated_confidence,
            reproducibility=merge_rec.accumulated_reproducibility,
            consensus_strength=merge_rec.accumulated_consensus,
            conflict_score=conflict_score,
            creation_timestamp=timestamp,
            canonical_hash=ik_hash,
            version="1.0.0",
            audit_metadata={"validation_count": len(all_validations)},
        )
        self.integration_repo.save_integrated_knowledge(integrated_knowledge)

        # 7. Knowledge Evolution & State Versioning
        version_snapshot = self.evolution_engine.create_version(
            integrated_knowledge=integrated_knowledge,
            graph=self.graph,
            timestamp=timestamp,
        )
        self.integration_repo.save_version(version_snapshot)

        # 8. Save Graph State to SQLite
        self.graph_repo.save_graph(self.graph)

        # 9. Create Integration Report
        rep_id = f"REP_INT_{ik_id[4:12]}_{version_snapshot.version_number}"
        report = KnowledgeIntegrationReport(
            report_id=rep_id,
            timestamp=timestamp,
            integrated_knowledge=integrated_knowledge,
            node_count=len(self.graph.get_nodes()),
            edge_count=len(self.graph.get_edges()),
            conflict_count=len(conflicts),
            evidence_merge_id=merge_rec.merge_id,
            version_id=version_snapshot.version_id,
            summary_notes=f"Processed validation {val_id} and updated scientific knowledge graph.",
        )
        self.report_repo.save_report(rep_id, "KnowledgeIntegrationReport", timestamp, report)

        return integrated_knowledge, report

    def generate_all_reports(
        self,
        knowledge_id: str,
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate comprehensive reports for a knowledge integration state.

        Returns:
            Dict containing KnowledgeIntegrationReport, ConflictReport, KnowledgeGraphReport, EvidenceMergeReport, KnowledgeEvolutionReport.
        """
        ik = self.integration_repo.get_integrated_knowledge(knowledge_id)
        if not ik:
            raise KeyError(f"IntegratedKnowledge ID '{knowledge_id}' not found in database.")

        nodes = self.graph.get_nodes()
        edges = self.graph.get_edges()

        # Breakdown stats
        node_breakdown: dict[str, int] = {}
        for n in nodes:
            k = n.node_type.value if hasattr(n.node_type, "value") else str(n.node_type)
            node_breakdown[k] = node_breakdown.get(k, 0) + 1

        rel_breakdown: dict[str, int] = {}
        for e in edges:
            k = e.relationship.value if hasattr(e.relationship, "value") else str(e.relationship)
            rel_breakdown[k] = rel_breakdown.get(k, 0) + 1

        conflicts = self.conflict_repo.list_conflicts()
        versions = self.evolution_engine.list_versions_for_knowledge(knowledge_id)
        if not versions:
            versions = self.integration_repo.list_versions_for_knowledge(knowledge_id)

        graph_report = KnowledgeGraphReport(
            report_id=f"REP_GRP_{knowledge_id[4:12]}",
            timestamp=timestamp,
            total_nodes=len(nodes),
            total_edges=len(edges),
            node_types_breakdown=node_breakdown,
            relationship_types_breakdown=rel_breakdown,
        )

        conflict_report = ConflictReport(
            report_id=f"REP_CFL_{knowledge_id[4:12]}",
            timestamp=timestamp,
            conflicts=conflicts,
        )

        evolution_report = KnowledgeEvolutionReport(
            report_id=f"REP_EVO_{knowledge_id[4:12]}",
            timestamp=timestamp,
            knowledge_id=knowledge_id,
            versions=versions,
        )

        return {
            "graph_report": graph_report,
            "conflict_report": conflict_report,
            "evolution_report": evolution_report,
        }

    def replay_from_history(self, version_id: str) -> tuple[IntegratedKnowledge, ScientificKnowledgeGraph]:
        """Replay exact scientific knowledge state from a historical version ID."""
        v = self.integration_repo.get_version(version_id)
        if not v:
            v = self.evolution_engine.get_version(version_id)
        if not v:
            raise KeyError(f"Version ID '{version_id}' not found.")

        replayed_graph = ScientificKnowledgeGraph.from_dict(v.graph_state)
        return v.integrated_knowledge, replayed_graph
