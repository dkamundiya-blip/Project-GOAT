"""
Public API export integrity tests for goat.ai_reasoning.
"""

import goat.ai_reasoning as ai_reasoning


def test_public_api_exports():
    expected_exports = [
        "MasterAIReasoningEngine",
        "AIReasoningEngine",
        "ResearchKnowledgeGraph",
        "ResearchQueryEngine",
        "EvidenceEngine",
        "ReasoningEngine",
        "ResearchReportGenerator",
        "NaturalLanguageExplanationLayer",
        "create_research_router",
        "NodeType",
        "EdgeType",
        "ResearchGraphNode",
        "ResearchGraphEdge",
        "compute_node_id",
        "compute_edge_id",
        "EvidenceType",
        "EvidenceRecord",
        "EvidenceBundle",
        "compute_evidence_record_id",
        "compute_evidence_bundle_id",
        "ExplanationLevel",
        "ReasoningConclusion",
        "ResearchReport",
        "compute_conclusion_id",
        "compute_report_id",
    ]

    for export_name in expected_exports:
        assert hasattr(ai_reasoning, export_name), f"Missing public API export '{export_name}'"
        assert getattr(ai_reasoning, export_name) is not None
