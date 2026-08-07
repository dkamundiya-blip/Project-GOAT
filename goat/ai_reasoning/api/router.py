"""
Project GOAT Phase 7 — Research API Router (`goat.ai_reasoning.api`)

FastAPI router exposing endpoints for quantitative edge explanations, research reports,
evidence retrieval, knowledge graph queries, and ranking summaries.
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


def create_research_router(master_engine: Any) -> Any:
    """Create FastAPI router exposing Phase 7 Research API endpoints."""
    if not _HAS_FASTAPI:
        raise RuntimeError("FastAPI is required to instantiate research API router. Install fastapi to enable HTTP router.")

    router = APIRouter(prefix="/api/v1/research", tags=["AI Research & Reasoning Engine"])

    @router.get("/explain/{edge_id}")
    def get_edge_explanation(
        edge_id: str,
        level: Any = Query(default="PROFESSIONAL_QUANT"),
    ):
        """Fetch persona-tailored quantitative explanation for a specific edge."""
        edge = master_engine.edge_repository.get_edge(edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found.")
        return master_engine.explanation_layer.explain_edge(edge, level=level)

    @router.get("/report/{edge_id}")
    def get_research_report(
        edge_id: str,
        level: Any = Query(default="PROFESSIONAL_QUANT"),
    ):
        """Generate and retrieve a full evidence-backed ResearchReport."""
        edge = master_engine.edge_repository.get_edge(edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found.")
        report = master_engine.report_generator.generate_report(edge, explanation_level=level)
        return report.model_dump()

    @router.get("/evidence/{edge_id}")
    def get_evidence_bundle(edge_id: str):
        """Retrieve 100% traceable EvidenceBundle backing an edge."""
        edge = master_engine.edge_repository.get_edge(edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found.")
        bundle = master_engine.evidence_engine.build_evidence_bundle(edge)
        return bundle.model_dump()

    @router.get("/graph/summary")
    def get_knowledge_graph_summary():
        """Retrieve summary counts for the Research Knowledge Graph."""
        return {
            "node_count": master_engine.knowledge_graph.node_count(),
            "edge_count": master_engine.knowledge_graph.edge_count(),
        }

    @router.get("/ranking")
    def get_edge_ranking_summary(limit: int = Query(default=20, ge=1, le=100)):
        """Retrieve top ranked active edges."""
        top_edges = master_engine.edge_repository.get_top_edges(limit=limit)
        return [
            {
                "edge_id": e.edge_id,
                "composite_score": e.composite_score,
                "expected_value": e.metrics.expected_value,
                "sharpe_ratio": e.metrics.sharpe_ratio,
                "p_value": e.p_value,
                "symbols": e.supported_symbols,
                "features": e.feature_combination,
                "status": e.status.value,
            }
            for e in top_edges
        ]

    return router
