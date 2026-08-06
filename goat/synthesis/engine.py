"""
Project GOAT v0.7 — Scientific Evidence Synthesis Engine

Implements EvidenceSynthesisEngine for aggregating evidence, building clusters, detecting contradictions,
evaluating replications, and generating EvidenceSynthesis objects.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.synthesis.cluster import EvidenceCluster, compute_cluster_id
from goat.synthesis.contradiction import EvidenceContradictionDetector
from goat.synthesis.model import (
    EvidenceSynthesis,
    compute_synthesis_fingerprint,
    compute_synthesis_id,
)
from goat.synthesis.replication import EvidenceReplicationEngine


class EvidenceSynthesisValidationError(ValueError):
    """Raised when evidence synthesis validation, clustering, or generation fails."""
    pass


class EvidenceSynthesisEngine:
    """Master engine orchestrating evidence clustering, contradiction detection, replication analysis, and synthesis generation."""

    def __init__(
        self,
        replication_engine: EvidenceReplicationEngine | None = None,
        contradiction_detector: EvidenceContradictionDetector | None = None,
    ) -> None:
        self._replication_engine = replication_engine or EvidenceReplicationEngine()
        self._contradiction_detector = contradiction_detector or EvidenceContradictionDetector()
        self._clusters: dict[str, EvidenceCluster] = {}
        self._syntheses: dict[str, EvidenceSynthesis] = {}

    def create_cluster(
        self,
        member_evidence_ids: list[str],
        supporting_study_ids: list[str] | None = None,
        supporting_experiment_ids: list[str] | None = None,
        confidence_statistics: dict[str, Any] | None = None,
    ) -> EvidenceCluster:
        """Construct an immutable EvidenceCluster."""
        if not member_evidence_ids:
            raise EvidenceSynthesisValidationError("Cannot create empty EvidenceCluster")

        cid, c_hash = compute_cluster_id(member_evidence_ids)
        cluster = EvidenceCluster(
            cluster_id=cid,
            member_evidence_ids=member_evidence_ids,
            supporting_study_ids=supporting_study_ids or [],
            supporting_experiment_ids=supporting_experiment_ids or [],
            confidence_statistics=confidence_statistics or {},
            replication_count=max(0, len(member_evidence_ids) - 1),
            cluster_hash=c_hash,
        )
        self._clusters[cid] = cluster
        return cluster

    def synthesize_evidence(
        self,
        evidence_list: list[dict[str, Any]],
        knowledge_ids: list[str] | None = None,
        version: str = "1.0.0",
    ) -> EvidenceSynthesis:
        """Synthesize evidence references deterministically across clusters, replications, and contradictions.

        Args:
            evidence_list: List of evidence metadata dictionaries containing 'evidence_id', 'source_id', 'outcome', etc.
            knowledge_ids: Associated Knowledge IDs.
            version: Version string.

        Returns:
            Immutable EvidenceSynthesis instance (SYN_<HEX16>).
        """
        if not evidence_list:
            raise EvidenceSynthesisValidationError("Cannot synthesize empty evidence list")

        evd_ids = [e["evidence_id"] for e in evidence_list if "evidence_id" in e]
        knw_ids = knowledge_ids or []

        # Run contradiction detection
        contradictions = self._contradiction_detector.detect_contradictions(evidence_list)

        # Run replication analysis
        replications = self._replication_engine.analyze_replications(evidence_list)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_synthesis_fingerprint(evd_ids, knw_ids, version)
        syn_id, canon_hash = compute_synthesis_id(fingerprint, version)

        # Build summaries
        conf_summary = {
            "total_evidence_count": len(evd_ids),
            "validated_count": len([e for e in evidence_list if e.get("outcome") == "validated"]),
            "rejected_count": len([e for e in evidence_list if e.get("outcome") == "rejected"]),
        }

        rep_summary = {
            "total_replications": len(replications),
            "exact_replications": len([r for r in replications if r.quality.value == "exact"]),
        }

        conflicts_summary = {
            "total_contradictions": len(contradictions),
            "high_severity_count": len([c for c in contradictions if c.severity.value in ["high", "critical"]]),
        }

        synthesis = EvidenceSynthesis(
            synthesis_id=syn_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            version=version,
            creation_timestamp=timestamp,
            evidence_ids=evd_ids,
            knowledge_ids=knw_ids,
            confidence_summary=conf_summary,
            replication_summary=rep_summary,
            conflict_summary=conflicts_summary,
        )

        self._syntheses[syn_id] = synthesis
        return synthesis

    def get_cluster(self, cluster_id: str) -> EvidenceCluster:
        """Retrieve EvidenceCluster by Cluster ID."""
        if cluster_id not in self._clusters:
            raise KeyError(f"Cluster ID '{cluster_id}' not found in EvidenceSynthesisEngine")
        return self._clusters[cluster_id]

    def get_synthesis(self, synthesis_id: str) -> EvidenceSynthesis:
        """Retrieve EvidenceSynthesis by Synthesis ID."""
        if synthesis_id not in self._syntheses:
            raise KeyError(f"Synthesis ID '{synthesis_id}' not found in EvidenceSynthesisEngine")
        return self._syntheses[synthesis_id]
