"""
Project GOAT v0.7 — Consensus Rule Engine

Defines ConsensusRuleEngine for evaluating evidence synthesis statistics deterministically against scientific consensus rules.
"""

from __future__ import annotations

from typing import Any

from goat.consensus.enums import ConsensusStatus


class ConsensusRuleEngine:
    """Rule engine evaluating evidence synthesis metrics deterministically without statistical inference."""

    def evaluate_synthesis_summary(self, synthesis_summary: dict[str, Any]) -> dict[str, Any]:
        """Evaluate synthesis statistics and determine consensus status, confidence level, and research maturity.

        Args:
            synthesis_summary: Dictionary containing 'confidence_summary', 'replication_summary', 'conflict_summary'.

        Returns:
            Dictionary containing 'status', 'confidence', 'conflict_level', 'replication_strength', 'maturity'.
        """
        conf = synthesis_summary.get("confidence_summary", {})
        rep = synthesis_summary.get("replication_summary", {})
        conflict = synthesis_summary.get("conflict_summary", {})

        total_evd = conf.get("total_evidence_count", 0)
        validated = conf.get("validated_count", 0)
        high_conflicts = conflict.get("high_severity_count", 0)
        total_conflicts = conflict.get("total_contradictions", 0)
        exact_reps = rep.get("exact_replications", 0)
        total_reps = rep.get("total_replications", 0)

        # Fail-closed / Insufficient check
        if total_evd < 2:
            return {
                "status": ConsensusStatus.INSUFFICIENT_EVIDENCE,
                "confidence": 0.1,
                "conflict_level": 0.0,
                "replication_strength": float(total_reps),
                "maturity": "early",
            }

        # Conflict check
        if high_conflicts > 0:
            return {
                "status": ConsensusStatus.CONFLICTED,
                "confidence": 0.3,
                "conflict_level": 0.8,
                "replication_strength": float(total_reps),
                "maturity": "intermediate",
            }

        # Full Consensus check
        if validated >= 5 and exact_reps >= 2 and total_conflicts == 0:
            return {
                "status": ConsensusStatus.CONSENSUS,
                "confidence": 0.95,
                "conflict_level": 0.0,
                "replication_strength": float(total_reps * 2),
                "maturity": "mature",
            }

        # Strong check
        if validated >= 3 and total_reps >= 1:
            return {
                "status": ConsensusStatus.STRONG,
                "confidence": 0.8,
                "conflict_level": 0.1,
                "replication_strength": float(total_reps),
                "maturity": "intermediate",
            }

        # Moderate check
        if validated >= 2:
            return {
                "status": ConsensusStatus.MODERATE,
                "confidence": 0.6,
                "conflict_level": 0.2,
                "replication_strength": float(total_reps),
                "maturity": "intermediate",
            }

        # Emerging check
        return {
            "status": ConsensusStatus.EMERGING,
            "confidence": 0.4,
            "conflict_level": 0.3,
            "replication_strength": float(total_reps),
            "maturity": "early",
        }
