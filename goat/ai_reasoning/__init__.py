"""
Project GOAT Phase 7 — AI Research & Reasoning Engine (`goat.ai_reasoning`)

Public API package exporting domain models, knowledge graph, query engine, evidence engine,
reasoning engine, report generator, explanation layer, FastAPI router, and master orchestrator.
"""

from goat.ai_reasoning.api.router import create_research_router
from goat.ai_reasoning.engine import AIReasoningEngine, MasterAIReasoningEngine
from goat.ai_reasoning.evidence.engine import EvidenceEngine
from goat.ai_reasoning.explanation.layer import NaturalLanguageExplanationLayer
from goat.ai_reasoning.knowledge_graph.engine import ResearchKnowledgeGraph
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
from goat.ai_reasoning.query.engine import ResearchQueryEngine
from goat.ai_reasoning.reasoning.engine import ReasoningEngine
from goat.ai_reasoning.reporting.generator import ResearchReportGenerator

__all__ = [
    # Master Engine
    "MasterAIReasoningEngine",
    "AIReasoningEngine",
    # Subsystems
    "ResearchKnowledgeGraph",
    "ResearchQueryEngine",
    "EvidenceEngine",
    "ReasoningEngine",
    "ResearchReportGenerator",
    "NaturalLanguageExplanationLayer",
    "create_research_router",
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
