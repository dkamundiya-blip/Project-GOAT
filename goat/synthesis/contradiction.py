"""
Project GOAT v0.7 — Evidence Contradiction Detector

Defines ContradictionRecord model (CON_<HEX16>) and EvidenceContradictionDetector for deterministic conflict analysis.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.synthesis.enums import ContradictionSeverity


def compute_contradiction_id(evidence_ids: list[str], severity: str) -> tuple[str, str]:
    """Compute deterministic Contradiction Record ID (CON_<HEX16>) and full SHA-256 record hash.

    Args:
        evidence_ids: Conflicting Evidence IDs (EVD_<HEX16>).
        severity: ContradictionSeverity string.

    Returns:
        Tuple of (record_id, record_hash).
    """
    payload = {
        "evidence_ids": sorted([str(e).strip() for e in evidence_ids]),
        "severity": str(severity).strip().lower(),
    }
    digest = compute_canonical_sha256(payload)
    record_id = f"CON_{digest[:16].upper()}"
    return record_id, digest


class ContradictionRecord(BaseModel):
    """Immutable record representing a scientific contradiction or incompatible findings between evidence references."""

    record_id: str = Field(
        ...,
        description="Unique Contradiction Record ID formatted as CON_<HEX16>",
        pattern=r"^CON_[A-Fa-f0-9]{16}$",
    )
    evidence_ids: list[str] = Field(default_factory=list, description="Conflicting Evidence IDs (EVD_<HEX16>)")
    severity: ContradictionSeverity = Field(..., description="Contradiction severity classification")
    explanation_metadata: dict[str, Any] = Field(default_factory=dict, description="Deterministic conflict commentary metadata")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    record_hash: str = Field(..., description="Full 64-character SHA-256 canonical record hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class EvidenceContradictionDetector:
    """Detector analyzing evidence pairs deterministically to identify conflicting outcomes."""

    def __init__(self) -> None:
        self._records: list[ContradictionRecord] = []

    def detect_contradictions(self, evidence_list: list[dict[str, Any]]) -> list[ContradictionRecord]:
        """Detect incompatible evidence findings deterministically based on outcome contrasts.

        Args:
            evidence_list: List of evidence metadata dictionaries containing 'evidence_id', 'outcome', etc.

        Returns:
            List of detected ContradictionRecords.
        """
        records: list[ContradictionRecord] = []
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Pairwise comparison
        n = len(evidence_list)
        for i in range(n):
            for j in range(i + 1, n):
                e1 = evidence_list[i]
                e2 = evidence_list[j]

                eid1 = e1.get("evidence_id", "")
                eid2 = e2.get("evidence_id", "")
                out1 = e1.get("outcome", "")
                out2 = e2.get("outcome", "")

                # Detect conflict if outcomes are opposite (e.g. validated vs rejected on same feature)
                if out1 and out2 and (out1 != out2):
                    target1 = e1.get("source_id", "")
                    target2 = e2.get("source_id", "")
                    if target1 == target2:
                        severity = ContradictionSeverity.HIGH
                        rec_id, rec_hash = compute_contradiction_id([eid1, eid2], severity.value)
                        record = ContradictionRecord(
                            record_id=rec_id,
                            evidence_ids=[eid1, eid2],
                            severity=severity,
                            explanation_metadata={
                                "evidence_1_outcome": out1,
                                "evidence_2_outcome": out2,
                                "source_id": target1,
                            },
                            timestamp=timestamp,
                            record_hash=rec_hash,
                        )
                        records.append(record)

        self._records.extend(records)
        return records
