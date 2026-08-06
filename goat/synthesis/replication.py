"""
Project GOAT v0.7 — Evidence Replication Engine

Defines ReplicationRecord model and EvidenceReplicationEngine for identifying evidence replications across independent studies.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.synthesis.enums import ReplicationQuality


class ReplicationRecord(BaseModel):
    """Immutable record representing an evidence replication finding."""

    replication_id: str = Field(..., description="Unique Replication ID (REP_<HEX16>)")
    source_evidence_id: str = Field(..., description="Source Evidence ID (EVD_<HEX16>)")
    replicated_evidence_id: str = Field(..., description="Replicated Evidence ID (EVD_<HEX16>)")
    quality: ReplicationQuality = Field(..., description="Replication quality classification")
    study_ids: list[str] = Field(default_factory=list, description="Independent Study IDs involved")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")

    class Config:
        frozen = True
        extra = "forbid"


class EvidenceReplicationEngine:
    """Engine identifying evidence replications and computing independent confirmation statistics."""

    def __init__(self) -> None:
        self._records: list[ReplicationRecord] = []

    def analyze_replications(self, evidence_list: list[dict[str, Any]]) -> list[ReplicationRecord]:
        """Analyze evidence references deterministically to identify independent replications.

        Args:
            evidence_list: List of evidence metadata dictionaries containing 'evidence_id', 'source_id', 'study_id', 'outcome', etc.

        Returns:
            List of detected ReplicationRecords.
        """
        records: list[ReplicationRecord] = []
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        n = len(evidence_list)
        for i in range(n):
            for j in range(i + 1, n):
                e1 = evidence_list[i]
                e2 = evidence_list[j]

                eid1 = e1.get("evidence_id", "")
                eid2 = e2.get("evidence_id", "")
                source1 = e1.get("source_id", "")
                source2 = e2.get("source_id", "")
                out1 = e1.get("outcome", "")
                out2 = e2.get("outcome", "")
                st1 = e1.get("study_id", "")
                st2 = e2.get("study_id", "")

                # Match if testing same target feature/hypothesis with same positive outcome in different studies/experiments
                if source1 and (source1 == source2) and out1 and (out1 == out2 == "validated") and eid1 != eid2:
                    quality = ReplicationQuality.EXACT if (st1 != st2) else ReplicationQuality.HIGH
                    payload = {"e1": eid1, "e2": eid2, "timestamp": timestamp}
                    digest = compute_canonical_sha256(payload)
                    rep_id = f"REP_{digest[:16].upper()}"

                    record = ReplicationRecord(
                        replication_id=rep_id,
                        source_evidence_id=eid1,
                        replicated_evidence_id=eid2,
                        quality=quality,
                        study_ids=[s for s in [st1, st2] if s],
                        timestamp=timestamp,
                    )
                    records.append(record)

        self._records.extend(records)
        return records
