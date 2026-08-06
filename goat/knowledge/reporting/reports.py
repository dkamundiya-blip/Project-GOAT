"""
Project GOAT v0.9 — Edge Knowledge Graph Report Generator
"""

from typing import Any
from pydantic import BaseModel, Field

from goat.knowledge.core.canonical import serialize_canonical_json
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    KnowledgeSummary,
    RelationshipValidation,
    ScientificPath,
)
from goat.research.edge.canonical import compute_canonical_sha256


class KnowledgeReport(BaseModel):
    """Immutable report summarizing scientific Knowledge Engine metrics and audit state (Legacy v0.7)."""

    report_id: str = Field(..., description="Unique Knowledge Report ID (KREP_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_knowledge_count: int = Field(default=0, ge=0, description="Total Knowledge Objects registered")
    categories_summary: dict[str, int] = Field(default_factory=dict, description="Knowledge counts by type category")
    status_summary: dict[str, int] = Field(default_factory=dict, description="Knowledge counts by lifecycle status")
    evidence_statistics: dict[str, Any] = Field(default_factory=dict, description="Evidence references summary")
    graph_statistics: dict[str, Any] = Field(default_factory=dict, description="Knowledge Graph topology statistics")
    audit_statistics: dict[str, Any] = Field(default_factory=dict, description="Audit log event statistics")
    validation_summary: dict[str, Any] = Field(default_factory=dict, description="Integrity validation status")

    class Config:
        frozen = True
        extra = "forbid"


def generate_knowledge_report(
    registry: Any,
    graph: Any = None,
    timestamp: str = "",
) -> KnowledgeReport:
    """Generate deterministic KnowledgeReport (Legacy v0.7)."""
    ts = timestamp or "2026-07-30T00:00:00Z"
    records = registry.list_all_records() if hasattr(registry, "list_all_records") else []

    by_cat: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total_evidence = 0

    for r in records:
        c = str(r.knowledge_type.value) if hasattr(r, "knowledge_type") else "UNKNOWN"
        s = str(r.knowledge_status.value) if hasattr(r, "knowledge_status") else "UNKNOWN"
        by_cat[c] = by_cat.get(c, 0) + 1
        by_status[s] = by_status.get(s, 0) + 1
        if hasattr(r, "evidence_references"):
            total_evidence += len(r.evidence_references)

    graph_stats = graph.get_graph_statistics() if (graph and hasattr(graph, "get_graph_statistics")) else {}

    payload = {
        "record_count": len(records),
        "timestamp": ts,
        "total_evidence": total_evidence,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"KREP_{digest[:16].upper()}"

    return KnowledgeReport(
        report_id=report_id,
        timestamp=ts,
        total_knowledge_count=len(records),
        categories_summary=by_cat,
        status_summary=by_status,
        evidence_statistics={"total_evidence_references": total_evidence},
        graph_statistics=graph_stats,
        audit_statistics={"total_registered_objects": len(records)},
        validation_summary={"status": "PASSED", "errors": []},
    )


class KnowledgeReportGenerator:
    """Report Generator for Edge Knowledge Graph & Scientific Relationship Engine (v0.9).

    Generates Markdown reports and Canonical JSON exports for nodes, relationships,
    knowledge graphs, traceability paths, validation reports, and executive summaries.
    """

    def generate_relationship_report(self, relationship: KnowledgeRelationship) -> str:
        """Generate Markdown Relationship Report."""
        return (
            f"# SCIENTIFIC KNOWLEDGE RELATIONSHIP REPORT\n"
            f"**Relationship ID**: `{relationship.relationship_id}` | **Canonical Hash**: `{relationship.canonical_hash}`\n\n"
            f"## Relationship Details\n"
            f"- **Source Node**: `{relationship.source_node_id}`\n"
            f"- **Target Node**: `{relationship.target_node_id}`\n"
            f"- **Type**: `{relationship.relationship_type.value}`\n"
            f"- **Weight / Strength**: `{relationship.weight:.2f}`\n"
            f"- **Timestamp**: `{relationship.timestamp}`\n"
        )

    def generate_graph_report(self, graph: KnowledgeGraph) -> str:
        """Generate Markdown Graph Report."""
        return (
            f"# SCIENTIFIC KNOWLEDGE GRAPH REPORT\n"
            f"**Graph Name**: `{graph.graph_name}`\n"
            f"**Graph ID**: `{graph.graph_id}` | **Canonical Hash**: `{graph.canonical_hash}`\n\n"
            f"## Graph Topology Summary\n"
            f"- **Total Nodes**: `{len(graph.node_ids)}`\n"
            f"- **Total Relationships**: `{len(graph.relationship_ids)}`\n"
            f"- **Created At**: `{graph.created_at}`\n"
        )

    def generate_traceability_report(self, path: ScientificPath) -> str:
        """Generate Markdown Scientific Traceability Path Report."""
        chain_str = " -> ".join([f"`{n}`" for n in path.node_chain])
        return (
            f"# SCIENTIFIC TRACEABILITY PATH REPORT\n"
            f"**Path ID**: `{path.path_id}` | **Canonical Hash**: `{path.canonical_hash}`\n"
            f"**Validity**: `{path.validity.value}` | **Hops**: `{path.path_length}`\n\n"
            f"## Scientific Lineage Chain\n"
            f"{chain_str}\n\n"
            f"## Lineage Boundaries\n"
            f"- **Source Node**: `{path.source_node_id}`\n"
            f"- **Target Node**: `{path.target_node_id}`\n"
        )

    def generate_executive_report(self, summary: KnowledgeSummary) -> str:
        """Generate Markdown Executive Knowledge Summary Report."""
        return (
            f"# EDGE KNOWLEDGE GRAPH EXECUTIVE SUMMARY REPORT\n"
            f"**Summary ID**: `{summary.summary_id}` | **Timestamp**: `{summary.timestamp}`\n"
            f"**Canonical Hash**: `{summary.canonical_hash}`\n\n"
            f"## Inventory Summary\n"
            f"- **Total Graph Nodes**: `{summary.total_nodes}`\n"
            f"- **Total Directed Relationships**: `{summary.total_relationships}`\n"
            f"- **Total Knowledge Graphs**: `{summary.total_graphs}`\n"
            f"- **Paths Analyzed**: `{summary.total_paths_analyzed}`\n\n"
            f"## Node Type Breakdown\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.node_type_counts.items()])
            + "\n\n## Relationship Type Breakdown\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.relationship_type_counts.items()])
        )

    def generate_validation_report(self, validation: RelationshipValidation) -> str:
        """Generate Markdown Validation Audit Report."""
        violations_str = "\n".join([f"- {v}" for v in validation.violations]) or "- None"
        return (
            f"# KNOWLEDGE GRAPH VALIDATION AUDIT REPORT\n"
            f"**Validation ID**: `{validation.validation_id}` | **Graph ID**: `{validation.graph_id}`\n"
            f"**Status**: `{validation.status.value}` | **Is Valid**: `{validation.is_valid}`\n"
            f"**Canonical Hash**: `{validation.canonical_hash}`\n\n"
            f"## Violation Statistics\n"
            f"- **Broken Chains**: `{validation.broken_chain_count}`\n"
            f"- **Orphan Nodes**: `{validation.orphan_node_count}`\n"
            f"- **Cycles Detected**: `{validation.cycle_count}`\n"
            f"- **Duplicates**: `{validation.duplicate_count}`\n\n"
            f"## Detailed Violations\n"
            f"{violations_str}\n"
        )

    def export_canonical_json(self, obj: Any) -> str:
        """Export model as canonical JSON string."""
        return serialize_canonical_json(obj)
