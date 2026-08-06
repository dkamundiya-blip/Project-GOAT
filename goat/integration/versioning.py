"""
Project GOAT v0.7 — Knowledge Evolution & Versioning Engine

Provides immutable, deterministic versioning for scientific knowledge states.
Every integration event produces an immutable KnowledgeStateVersion (KVR_<HEX16>).
Supports complete forward and backward deterministic replay.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import compute_canonical_sha256, compute_version_id
from goat.integration.core.models import IntegratedKnowledge
from goat.integration.graph.engine import ScientificKnowledgeGraph


class KnowledgeStateVersion(BaseModel):
    """Immutable version snapshot of an integrated scientific knowledge state."""

    version_id: str = Field(
        ...,
        description="Unique deterministic version ID formatted as KVR_<HEX16>",
        pattern=r"^KVR_[A-Fa-f0-9]{16}$",
    )
    knowledge_id: str = Field(..., description="Target Integrated Knowledge ID (IKN_<HEX16>)")
    version_number: int = Field(..., ge=1, description="Sequential version counter (1-indexed)")
    state_hash: str = Field(..., description="Full canonical state digest")
    parent_version_id: str = Field(default="", description="Parent version ID (KVR_<HEX16>) if applicable")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    graph_state: dict[str, Any] = Field(..., description="Serialized graph state (nodes & edges)")
    integrated_knowledge: IntegratedKnowledge = Field(..., description="Snapshot of IntegratedKnowledge")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class KnowledgeEvolutionEngine:
    """Engine managing deterministic knowledge evolution and state version replay."""

    def __init__(self) -> None:
        self._history: dict[str, KnowledgeStateVersion] = {}  # version_id -> version
        self._knowledge_versions: dict[str, list[str]] = {}  # knowledge_id -> list of version_ids

    def create_version(
        self,
        integrated_knowledge: IntegratedKnowledge,
        graph: ScientificKnowledgeGraph,
        timestamp: str,
        parent_version_id: str = "",
    ) -> KnowledgeStateVersion:
        """Create a new immutable KnowledgeStateVersion snapshot.

        Args:
            integrated_knowledge: Current IntegratedKnowledge model.
            graph: Current ScientificKnowledgeGraph.
            timestamp: ISO 8601 UTC timestamp.
            parent_version_id: Parent version ID if chained.

        Returns:
            KnowledgeStateVersion object.
        """
        kn_id = integrated_knowledge.knowledge_id
        existing_versions = self._knowledge_versions.get(kn_id, [])
        version_number = len(existing_versions) + 1

        graph_dict = graph.to_dict()
        state_payload = {
            "graph_state": graph_dict,
            "integrated_knowledge": integrated_knowledge.dict(),
        }
        state_hash = compute_canonical_sha256(state_payload).upper()

        version_id, _ = compute_version_id(kn_id, state_hash, version_number)

        payload = {
            "graph_state": graph_dict,
            "integrated_knowledge": integrated_knowledge.dict(),
            "knowledge_id": kn_id,
            "parent_version_id": parent_version_id,
            "state_hash": state_hash,
            "timestamp": timestamp,
            "version_id": version_id,
            "version_number": version_number,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        version_snapshot = KnowledgeStateVersion(
            version_id=version_id,
            knowledge_id=kn_id,
            version_number=version_number,
            state_hash=state_hash,
            parent_version_id=parent_version_id,
            timestamp=timestamp,
            graph_state=graph_dict,
            integrated_knowledge=integrated_knowledge,
            canonical_hash=canonical_hash,
        )

        self._history[version_id] = version_snapshot
        if kn_id not in self._knowledge_versions:
            self._knowledge_versions[kn_id] = []
        self._knowledge_versions[kn_id].append(version_id)

        return version_snapshot

    def get_version(self, version_id: str) -> KnowledgeStateVersion | None:
        """Lookup version snapshot by version_id."""
        return self._history.get(version_id)

    def list_versions_for_knowledge(self, knowledge_id: str) -> list[KnowledgeStateVersion]:
        """Return all version snapshots for a given knowledge ID ordered by version_number."""
        v_ids = self._knowledge_versions.get(knowledge_id, [])
        versions = [self._history[vid] for vid in v_ids if vid in self._history]
        return sorted(versions, key=lambda v: v.version_number)

    def replay_version(
        self, version_id: str
    ) -> tuple[IntegratedKnowledge, ScientificKnowledgeGraph]:
        """Replay and reconstruct exact IntegratedKnowledge and ScientificKnowledgeGraph state from snapshot.

        Raises:
            KeyError: If version_id is not found.
        """
        if version_id not in self._history:
            raise KeyError(f"Version ID '{version_id}' not found in evolution history.")

        snapshot = self._history[version_id]
        graph = ScientificKnowledgeGraph.from_dict(snapshot.graph_state)
        return snapshot.integrated_knowledge, graph

    def to_dict(self) -> dict[str, Any]:
        """Serialize full evolution history."""
        return {
            "versions": [v.dict() for v in sorted(self._history.values(), key=lambda x: x.version_id)]
        }
