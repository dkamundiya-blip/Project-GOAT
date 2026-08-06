"""
Project GOAT v0.7 — Scientific Consensus Engine

Implements ConsensusEngine for evaluating syntheses, registering scientific conflicts,
invoking the rule engine, and generating ScientificConsensus objects.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.consensus.conflict import ConsensusConflict, compute_conflict_id
from goat.consensus.model import (
    ScientificConsensus,
    compute_consensus_fingerprint,
    compute_consensus_id,
)
from goat.consensus.rules import ConsensusRuleEngine


class ConsensusValidationError(ValueError):
    """Raised when consensus evaluation, rule execution, or conflict registration fails."""
    pass


class ConsensusEngine:
    """Master engine orchestrating consensus evaluation, conflict registration, and consensus replay."""

    def __init__(self, rule_engine: ConsensusRuleEngine | None = None) -> None:
        self._rule_engine = rule_engine or ConsensusRuleEngine()
        self._consensus_objects: dict[str, ScientificConsensus] = {}
        self._conflicts: dict[str, ConsensusConflict] = {}

    def register_conflict(
        self,
        evidence_references: list[str],
        synthesis_references: list[str] | None = None,
        severity: str = "high",
    ) -> ConsensusConflict:
        """Register an unresolved scientific consensus conflict."""
        if not evidence_references:
            raise ConsensusValidationError("Cannot register ConsensusConflict without evidence references")

        cid, c_hash = compute_conflict_id(evidence_references, severity)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conflict = ConsensusConflict(
            conflict_id=cid,
            evidence_references=evidence_references,
            synthesis_references=synthesis_references or [],
            severity=severity,
            resolution_status="unresolved",
            timestamp=timestamp,
            conflict_hash=c_hash,
        )
        self._conflicts[cid] = conflict
        return conflict

    def evaluate_consensus(
        self,
        synthesis_ids: list[str],
        synthesis_summary: dict[str, Any],
        knowledge_ids: list[str] | None = None,
        version: str = "1.0.0",
    ) -> ScientificConsensus:
        """Evaluate evidence syntheses via rule engine and create ScientificConsensus instance.

        Args:
            synthesis_ids: List of Evidence Synthesis IDs (SYN_<HEX16>).
            synthesis_summary: Synthesis metrics summary.
            knowledge_ids: Target Knowledge IDs.
            version: Version string.

        Returns:
            Immutable ScientificConsensus instance (CNS_<HEX16>).
        """
        if not synthesis_ids:
            raise ConsensusValidationError("Cannot evaluate consensus with empty synthesis_ids")

        knw_ids = knowledge_ids or []
        eval_res = self._rule_engine.evaluate_synthesis_summary(synthesis_summary)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_consensus_fingerprint(synthesis_ids, knw_ids, version)
        cns_id, canon_hash = compute_consensus_id(fingerprint, version)

        consensus = ScientificConsensus(
            consensus_id=cns_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            semantic_version=version,
            creation_timestamp=timestamp,
            synthesis_ids=synthesis_ids,
            knowledge_ids=knw_ids,
            consensus_status=eval_res["status"],
            confidence_level=eval_res["confidence"],
            conflict_level=eval_res["conflict_level"],
            replication_strength=eval_res["replication_strength"],
            research_maturity=eval_res["maturity"],
        )

        self._consensus_objects[cns_id] = consensus
        return consensus

    def get_consensus(self, consensus_id: str) -> ScientificConsensus:
        """Retrieve ScientificConsensus by Consensus ID."""
        if consensus_id not in self._consensus_objects:
            raise KeyError(f"Consensus ID '{consensus_id}' not found in ConsensusEngine")
        return self._consensus_objects[consensus_id]

    def replay_consensus(self, consensus_id: str) -> ScientificConsensus:
        """Replay consensus evaluation deterministically."""
        return self.get_consensus(consensus_id)
