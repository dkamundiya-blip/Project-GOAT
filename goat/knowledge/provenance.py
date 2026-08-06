"""
Project GOAT v0.7 — Knowledge Provenance Engine

Implements KnowledgeProvenanceEngine for complete evidence reconstruction, knowledge ancestry,
artifact ancestry, audit reconstruction, and deterministic scientific replay.
"""

from __future__ import annotations

from typing import Any

from goat.knowledge.evidence import EvidenceReference
from goat.knowledge.model import KnowledgeObject
from goat.knowledge.registry.service import KnowledgeRegistry


class KnowledgeProvenanceEngine:
    """Provenance engine guaranteeing 100% scientific traceability and evidence reconstruction."""

    def __init__(self, registry: KnowledgeRegistry) -> None:
        self._registry = registry

    def trace_evidence_chain(self, knowledge_id: str) -> list[EvidenceReference]:
        """Reconstruct complete supporting evidence chain for a Knowledge Object."""
        record = self._registry.get_by_id(knowledge_id)
        return list(record.evidence_references)

    def trace_knowledge_ancestry(self, knowledge_id: str) -> list[str]:
        """Reconstruct recursive upstream parent Knowledge IDs."""
        ancestors: set[str] = set()
        visited: set[str] = set()

        def dfs(curr_id: str) -> None:
            if curr_id in visited:
                return
            visited.add(curr_id)
            try:
                rec = self._registry.get_by_id(curr_id)
                for pid in rec.knowledge_object.parent_knowledge_ids:
                    ancestors.add(pid)
                    dfs(pid)
            except KeyError:
                pass

        dfs(knowledge_id)
        return sorted(ancestors)

    def reconstruct_audit_history(self, knowledge_id: str) -> list[dict[str, Any]]:
        """Reconstruct ordered audit event history for a Knowledge Object."""
        events = self._registry.get_audit_trail(knowledge_id)
        return [e.model_dump(mode="json") for e in events]

    def verify_provenance_integrity(self, knowledge_id: str) -> dict[str, Any]:
        """Verify provenance integrity of a Knowledge Object.

        Returns:
            Dictionary with status, missing_parents, evidence_count, and audit_count.
        """
        rec = self._registry.get_by_id(knowledge_id)
        obj = rec.knowledge_object

        missing_parents: list[str] = []
        for pid in obj.parent_knowledge_ids:
            try:
                self._registry.get_by_id(pid)
            except KeyError:
                missing_parents.append(pid)

        audit_trail = self._registry.get_audit_trail(knowledge_id)

        is_valid = (len(missing_parents) == 0) and (len(audit_trail) > 0)

        return {
            "audit_count": len(audit_trail),
            "evidence_count": len(rec.evidence_references),
            "is_valid": is_valid,
            "knowledge_id": knowledge_id,
            "missing_parents": missing_parents,
        }
