"""
Project GOAT Phase 7 — AI Research & Reasoning Models Package
"""

from goat.ai_reasoning.models.evidence import (
    EvidenceBundle,
    EvidenceRecord,
    EvidenceType,
    compute_evidence_bundle_id,
    compute_evidence_record_id,
)
from goat.ai_reasoning.models.graph import (
    EdgeType,
    NodeType,
    ResearchGraphEdge,
    ResearchGraphNode,
    compute_edge_id,
    compute_node_id,
)
from goat.ai_reasoning.models.report import (
    ExplanationLevel,
    ReasoningConclusion,
    ResearchReport,
    compute_conclusion_id,
    compute_report_id,
)

__all__ = [
    # Graph Models
    "NodeType",
    "EdgeType",
    "ResearchGraphNode",
    "ResearchGraphEdge",
    "compute_node_id",
    "compute_edge_id",
    # Evidence Models
    "EvidenceType",
    "EvidenceRecord",
    "EvidenceBundle",
    "compute_evidence_record_id",
    "compute_evidence_bundle_id",
    # Report Models
    "ExplanationLevel",
    "ReasoningConclusion",
    "ResearchReport",
    "compute_conclusion_id",
    "compute_report_id",
]
