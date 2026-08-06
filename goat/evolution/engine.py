"""
Project GOAT v0.7 — Knowledge Evolution Engine

Implements KnowledgeEvolutionEngine for creating versions, superseding knowledge, managing lineage graphs,
validating transitions, and replaying evolution history.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.evolution.enums import KnowledgeEvolutionType
from goat.evolution.lineage import KnowledgeLineageGraph
from goat.evolution.model import (
    KnowledgeEvolution,
    compute_evolution_fingerprint,
    compute_evolution_id,
)
from goat.evolution.version import KnowledgeVersion, compute_version_id


class KnowledgeEvolutionValidationError(ValueError):
    """Raised when knowledge evolution validation, transition, or versioning fails."""
    pass


class KnowledgeEvolutionEngine:
    """Master engine orchestrating scientific knowledge versioning, superseding, lineage tracking, and replay."""

    def __init__(self, lineage_graph: KnowledgeLineageGraph | None = None) -> None:
        self._lineage_graph = lineage_graph or KnowledgeLineageGraph()
        self._versions: dict[str, KnowledgeVersion] = {}
        self._evolutions: dict[str, KnowledgeEvolution] = {}

    @property
    def lineage_graph(self) -> KnowledgeLineageGraph:
        """Return bound KnowledgeLineageGraph."""
        return self._lineage_graph

    def create_initial_version(
        self,
        knowledge_id: str,
        consensus_reference: str = "",
    ) -> tuple[KnowledgeVersion, KnowledgeEvolution]:
        """Create initial version (v1) for a new scientific knowledge object.

        Args:
            knowledge_id: Target Knowledge ID (KNW_<HEX16>).
            consensus_reference: Supporting Consensus ID (CNS_<HEX16>).

        Returns:
            Tuple of (KnowledgeVersion, KnowledgeEvolution).
        """
        vid, v_hash = compute_version_id(knowledge_id, 1)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        version = KnowledgeVersion(
            version_id=vid,
            knowledge_id=knowledge_id,
            version_number=1,
            parent_version_id="",
            consensus_reference=consensus_reference,
            creation_timestamp=timestamp,
            status="active",
            version_hash=v_hash,
        )

        fingerprint = compute_evolution_fingerprint("", knowledge_id, KnowledgeEvolutionType.CREATED.value)
        ev_id, canon_hash = compute_evolution_id(fingerprint)

        evolution = KnowledgeEvolution(
            evolution_id=ev_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            creation_timestamp=timestamp,
            previous_knowledge_id="",
            new_knowledge_id=knowledge_id,
            consensus_id=consensus_reference,
            evolution_type=KnowledgeEvolutionType.CREATED,
            change_summary=f"Created initial scientific knowledge '{knowledge_id}'",
        )

        self._versions[vid] = version
        self._evolutions[ev_id] = evolution
        self._lineage_graph.add_version(version)
        return version, evolution

    def supersede_knowledge(
        self,
        previous_version_id: str,
        new_knowledge_id: str,
        evolution_type: KnowledgeEvolutionType,
        change_summary: str,
        consensus_reference: str = "",
    ) -> tuple[KnowledgeVersion, KnowledgeEvolution]:
        """Supersede previous knowledge version with a refined/expanded new version.

        Args:
            previous_version_id: Previous Version ID (KVR_<HEX16>).
            new_knowledge_id: New Knowledge ID (KNW_<HEX16>).
            evolution_type: KnowledgeEvolutionType classification.
            change_summary: Statement explaining why knowledge changed.
            consensus_reference: Supporting Consensus ID (CNS_<HEX16>).

        Returns:
            Tuple of (KnowledgeVersion, KnowledgeEvolution).
        """
        if previous_version_id not in self._versions:
            raise KnowledgeEvolutionValidationError(f"Previous version ID '{previous_version_id}' not found")

        prev_ver = self._versions[previous_version_id]
        next_ver_num = prev_ver.version_number + 1

        vid, v_hash = compute_version_id(new_knowledge_id, next_ver_num)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Update previous version status to superseded
        updated_prev = KnowledgeVersion(
            **{**prev_ver.model_dump(), "status": "superseded", "child_version_ids": [*prev_ver.child_version_ids, vid]}
        )
        self._versions[previous_version_id] = updated_prev

        new_ver = KnowledgeVersion(
            version_id=vid,
            knowledge_id=new_knowledge_id,
            version_number=next_ver_num,
            parent_version_id=previous_version_id,
            consensus_reference=consensus_reference,
            creation_timestamp=timestamp,
            status="active",
            version_hash=v_hash,
        )

        fingerprint = compute_evolution_fingerprint(prev_ver.knowledge_id, new_knowledge_id, evolution_type.value)
        ev_id, canon_hash = compute_evolution_id(fingerprint)

        evolution = KnowledgeEvolution(
            evolution_id=ev_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            creation_timestamp=timestamp,
            previous_knowledge_id=prev_ver.knowledge_id,
            new_knowledge_id=new_knowledge_id,
            consensus_id=consensus_reference,
            evolution_type=evolution_type,
            change_summary=change_summary,
        )

        self._versions[vid] = new_ver
        self._evolutions[ev_id] = evolution
        self._lineage_graph.add_version(new_ver)
        return new_ver, evolution

    def get_version(self, version_id: str) -> KnowledgeVersion:
        """Retrieve KnowledgeVersion by Version ID."""
        if version_id not in self._versions:
            raise KeyError(f"Version ID '{version_id}' not found in KnowledgeEvolutionEngine")
        return self._versions[version_id]

    def get_evolution(self, evolution_id: str) -> KnowledgeEvolution:
        """Retrieve KnowledgeEvolution by Evolution ID."""
        if evolution_id not in self._evolutions:
            raise KeyError(f"Evolution ID '{evolution_id}' not found in KnowledgeEvolutionEngine")
        return self._evolutions[evolution_id]

    def replay_evolution(self, evolution_id: str) -> KnowledgeEvolution:
        """Replay knowledge evolution transition deterministically."""
        return self.get_evolution(evolution_id)
