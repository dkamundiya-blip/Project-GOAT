"""
Project GOAT v0.7 — Scientific Research Prioritization Engine

Implements ResearchPrioritizationEngine for evaluating research opportunities, creating priorities,
building ordered priority queues, and replaying research prioritization states.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.prioritization.model import (
    ResearchPriority,
    compute_priority_fingerprint,
    compute_priority_id,
)
from goat.prioritization.queue import ResearchPriorityQueue, compute_queue_id
from goat.prioritization.rules import ResearchPriorityRuleEngine
from goat.research.edge.canonical import compute_canonical_sha256


class ResearchPriorityValidationError(ValueError):
    """Raised when research prioritization, rule execution, or queue creation fails."""
    pass


class ResearchPrioritizationEngine:
    """Master engine evaluating scientific opportunities, ordering research queues, and replaying priority history."""

    def __init__(self, rule_engine: ResearchPriorityRuleEngine | None = None) -> None:
        self._rule_engine = rule_engine or ResearchPriorityRuleEngine()
        self._priorities: dict[str, ResearchPriority] = {}
        self._queues: dict[str, ResearchPriorityQueue] = {}

    def prioritize_opportunity(
        self,
        opportunity_data: dict[str, Any],
        supporting_consensus_ids: list[str] | None = None,
        supporting_knowledge_ids: list[str] | None = None,
        supporting_conflict_ids: list[str] | None = None,
        supporting_evolution_ids: list[str] | None = None,
        version: str = "1.0.0",
    ) -> ResearchPriority:
        """Prioritize a scientific opportunity via rule engine and create ResearchPriority.

        Args:
            opportunity_data: Opportunity metadata dictionary.
            supporting_consensus_ids: Supporting Consensus IDs (CNS_<HEX16>).
            supporting_knowledge_ids: Supporting Knowledge IDs (KNW_<HEX16>).
            supporting_conflict_ids: Supporting Conflict IDs (CCF_<HEX16>).
            supporting_evolution_ids: Supporting Evolution IDs (KEV_<HEX16>).
            version: Version string.

        Returns:
            Immutable ResearchPriority instance (RPR_<HEX16>).
        """
        eval_res = self._rule_engine.evaluate_opportunity(opportunity_data)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_priority_fingerprint(eval_res["opportunity_type"].value, eval_res["justification"], version)
        pr_id, canon_hash = compute_priority_id(fingerprint, version)

        priority = ResearchPriority(
            priority_id=pr_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            semantic_version=version,
            creation_timestamp=timestamp,
            priority_score=eval_res["score"],
            priority_level=eval_res["level"],
            opportunity_type=eval_res["opportunity_type"],
            supporting_consensus_ids=supporting_consensus_ids or [],
            supporting_knowledge_ids=supporting_knowledge_ids or [],
            supporting_conflict_ids=supporting_conflict_ids or [],
            supporting_evolution_ids=supporting_evolution_ids or [],
            scientific_justification=eval_res["justification"],
        )

        self._priorities[pr_id] = priority
        return priority

    def build_priority_queue(self, priority_ids: list[str]) -> ResearchPriorityQueue:
        """Construct an immutable ResearchPriorityQueue with priorities sorted deterministically by score descending.

        Args:
            priority_ids: List of Priority IDs (RPR_<HEX16>).

        Returns:
            Immutable ResearchPriorityQueue instance (RPQ_<HEX16>).
        """
        if not priority_ids:
            raise ResearchPriorityValidationError("Cannot build empty ResearchPriorityQueue")

        # Lookup priorities and sort by priority_score descending, then priority_id ascending
        priority_objs: list[ResearchPriority] = []
        for pid in priority_ids:
            if pid not in self._priorities:
                raise ResearchPriorityValidationError(f"Priority ID '{pid}' not found in engine")
            priority_objs.append(self._priorities[pid])

        priority_objs.sort(key=lambda p: (-p.priority_score, p.priority_id))
        ordered_ids = [p.priority_id for p in priority_objs]

        qid, q_hash = compute_queue_id(ordered_ids)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        queue = ResearchPriorityQueue(
            queue_id=qid,
            ordered_priority_ids=ordered_ids,
            queue_hash=q_hash,
            creation_timestamp=timestamp,
        )

        self._queues[qid] = queue
        return queue

    def get_priority(self, priority_id: str) -> ResearchPriority:
        """Retrieve ResearchPriority by Priority ID."""
        if priority_id not in self._priorities:
            raise KeyError(f"Priority ID '{priority_id}' not found in ResearchPrioritizationEngine")
        return self._priorities[priority_id]

    def get_queue(self, queue_id: str) -> ResearchPriorityQueue:
        """Retrieve ResearchPriorityQueue by Queue ID."""
        if queue_id not in self._queues:
            raise KeyError(f"Queue ID '{queue_id}' not found in ResearchPrioritizationEngine")
        return self._queues[queue_id]

    def replay_prioritization(self, queue_id: str) -> ResearchPriorityQueue:
        """Replay research priority queue ordering deterministically."""
        return self.get_queue(queue_id)
