"""
Project GOAT v0.7 — Scientific Memory System

Implements ScientificMemory for deterministic retrieval of preserved scientific knowledge, evidence,
relationships, version history, timeline reconstruction, and historical scientific summaries.
"""

from __future__ import annotations

from typing import Any

from goat.knowledge.enums import KnowledgeStatus, KnowledgeType
from goat.knowledge.evidence import EvidenceReference
from goat.knowledge.graph.graph import KnowledgeGraph
from goat.knowledge.model import KnowledgeObject
from goat.knowledge.registry.service import KnowledgeRegistry


class ScientificMemory:
    """Deterministic scientific memory retrieval system."""

    def __init__(
        self,
        registry: KnowledgeRegistry,
        graph: KnowledgeGraph | None = None,
    ) -> None:
        self._registry = registry
        self._graph = graph or KnowledgeGraph()

    @property
    def registry(self) -> KnowledgeRegistry:
        """Return bound KnowledgeRegistry."""
        return self._registry

    @property
    def graph(self) -> KnowledgeGraph:
        """Return bound KnowledgeGraph."""
        return self._graph

    def retrieve_knowledge(self, knowledge_id: str) -> KnowledgeObject:
        """Retrieve KnowledgeObject by Knowledge ID (KNW_<HEX16>)."""
        record = self._registry.get_by_id(knowledge_id)
        return record.knowledge_object

    def retrieve_evidence(self, knowledge_id: str) -> list[EvidenceReference]:
        """Retrieve all supporting EvidenceReferences for a Knowledge ID."""
        record = self._registry.get_by_id(knowledge_id)
        return list(record.evidence_references)

    def retrieve_relationships(self, knowledge_id: str) -> dict[str, list[str]]:
        """Retrieve upstream ancestors and downstream descendants for a Knowledge ID."""
        ancestors = self._graph.get_ancestors(knowledge_id)
        descendants = self._graph.get_descendants(knowledge_id)
        return {
            "ancestors": ancestors,
            "descendants": descendants,
        }

    def reconstruct_timeline(self) -> list[dict[str, Any]]:
        """Reconstruct chronological scientific knowledge timeline."""
        records = self._registry.list_all_records()
        timeline = []
        for r in records:
            obj = r.knowledge_object
            timeline.append({
                "creation_timestamp": obj.creation_timestamp,
                "evidence_count": len(r.evidence_references),
                "knowledge_id": obj.knowledge_id,
                "status": obj.knowledge_status.value,
                "title": obj.title,
                "type": obj.knowledge_type.value,
            })
        return sorted(timeline, key=lambda item: item["creation_timestamp"])

    def generate_scientific_summary(self) -> dict[str, Any]:
        """Generate deterministic scientific summary of preserved long-term memory."""
        records = self._registry.list_all_records()
        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}

        for r in records:
            t = r.knowledge_type.value
            s = r.knowledge_status.value
            by_type[t] = by_type.get(t, 0) + 1
            by_status[s] = by_status.get(s, 0) + 1

        return {
            "by_status": by_status,
            "by_type": by_type,
            "graph_stats": self._graph.get_graph_statistics() if len(self._graph.nodes) > 0 else {},
            "total_knowledge_objects": len(records),
        }
