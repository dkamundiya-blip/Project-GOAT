"""
Project GOAT Phase 7 — Master AI Research & Reasoning Engine (`goat.ai_reasoning.engine`)

Master orchestrator unifying the Research Knowledge Graph, Research Query Engine, Evidence Engine,
Reasoning Engine, Research Report Generator, Natural Language Explanation Layer, and Research API.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable

from goat.ai_reasoning.api.router import create_research_router
from goat.ai_reasoning.evidence.engine import EvidenceEngine
from goat.ai_reasoning.explanation.layer import NaturalLanguageExplanationLayer
from goat.ai_reasoning.knowledge_graph.engine import ResearchKnowledgeGraph
from goat.ai_reasoning.models.report import ExplanationLevel, ResearchReport
from goat.ai_reasoning.query.engine import ResearchQueryEngine
from goat.ai_reasoning.reasoning.engine import ReasoningEngine
from goat.ai_reasoning.reporting.generator import ResearchReportGenerator
from goat.edge_discovery.models.edge import DiscoveredEdge
from goat.edge_discovery.persistence.in_memory import InMemoryEdgeRepository
from goat.edge_discovery.persistence.interfaces import IEdgeRepository
from goat.edge_discovery.persistence.sqlite import (
    SQLiteEdgeRepository,
    init_edge_discovery_db,
)
from goat.logging import get_logger

_log = get_logger("ai_reasoning.engine")


class MasterAIReasoningEngine:
    """Master AI Research & Reasoning Engine orchestrating deterministic quantitative research reasoning."""

    def __init__(
        self,
        db_path: str | Path | sqlite3.Connection = ":memory:",
        edge_repository: IEdgeRepository | None = None,
        version: str = "7.0.0",
    ) -> None:
        self.version = version

        # Persistence & Edge Store Setup
        if edge_repository is not None:
            self.edge_repository = edge_repository
        elif isinstance(db_path, sqlite3.Connection):
            conn = init_edge_discovery_db(db_path)
            self.edge_repository = SQLiteEdgeRepository(conn)
        elif isinstance(db_path, (str, Path)):
            path_str = str(db_path)
            if path_str == ":memory:":
                self.edge_repository = InMemoryEdgeRepository()
            else:
                conn = init_edge_discovery_db(path_str)
                self.edge_repository = SQLiteEdgeRepository(conn)
        else:
            self.edge_repository = InMemoryEdgeRepository()

        # Phase 7 Subsystem Components
        self.knowledge_graph = ResearchKnowledgeGraph()
        self.evidence_engine = EvidenceEngine()
        self.query_engine = ResearchQueryEngine(
            knowledge_graph=self.knowledge_graph,
            edge_repository=self.edge_repository,
        )
        self.reasoning_engine = ReasoningEngine(evidence_engine=self.evidence_engine)
        self.report_generator = ResearchReportGenerator(
            evidence_engine=self.evidence_engine,
            reasoning_engine=self.reasoning_engine,
        )
        self.explanation_layer = NaturalLanguageExplanationLayer()

        # Observer EventBus
        self._report_listeners: list[Callable[[ResearchReport], None]] = []
        self._bus_lock = threading.RLock()

        # Populate knowledge graph from initial repository state
        self._sync_knowledge_graph()

    def _sync_knowledge_graph(self) -> None:
        """Sync existing edges into the knowledge graph."""
        top_edges = self.edge_repository.get_top_edges(limit=100)
        for e in top_edges:
            self.knowledge_graph.ingest_discovered_edge(e)

    def ingest_edge(self, edge: DiscoveredEdge) -> None:
        """Ingest a DiscoveredEdge, save to repository, and update KnowledgeGraph."""
        self.edge_repository.save_edge(edge)
        self.knowledge_graph.ingest_discovered_edge(edge)

    def subscribe_reports(self, callback: Callable[[ResearchReport], None]) -> None:
        """Subscribe to real-time research report events."""
        with self._bus_lock:
            self._report_listeners.append(callback)

    def generate_and_broadcast_report(
        self,
        edge: DiscoveredEdge,
        explanation_level: ExplanationLevel = ExplanationLevel.PROFESSIONAL_QUANT,
    ) -> ResearchReport:
        """Generate a ResearchReport and notify all subscribed observers."""
        report = self.report_generator.generate_report(edge, explanation_level=explanation_level)
        with self._bus_lock:
            for cb in self._report_listeners:
                try:
                    cb(report)
                except Exception as exc:
                    _log.error("report_listener_exception", error=str(exc))
        return report

    def get_router(self):
        """Get FastAPI router for Phase 7 Research API."""
        return create_research_router(self)


# Convenience alias matching prompt naming
AIReasoningEngine = MasterAIReasoningEngine
