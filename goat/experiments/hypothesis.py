"""
Project GOAT v0.7 — Hypothesis Registry

Defines HypothesisRecord model (HYP_<HEX16>) and HypothesisRegistry for managing research hypothesis lifecycles.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field

from goat.experiments.enums import HypothesisStatus
from goat.research.edge.canonical import compute_canonical_sha256


def compute_hypothesis_id(title: str, version: str = "1.0.0") -> str:
    """Compute deterministic Hypothesis ID (HYP_<HEX16>).

    Args:
        title: Hypothesis title string.
        version: Version string.

    Returns:
        String formatted as 'HYP_' + first 16 uppercase hex characters of SHA-256 digest.
    """
    payload = {
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"HYP_{digest[:16].upper()}"


class HypothesisRecord(BaseModel):
    """Immutable representation of a proposed scientific research hypothesis."""

    hypothesis_id: str = Field(
        ...,
        description="Unique Hypothesis ID formatted as HYP_<HEX16>",
        pattern=r"^HYP_[A-Fa-f0-9]{16}$",
    )
    title: str = Field(..., description="Hypothesis title")
    description: str = Field(..., description="Formal scientific statement of hypothesis")
    target_feature_ids: list[str] = Field(default_factory=list, description="Target Feature IDs under study")
    candidate_ids: list[str] = Field(default_factory=list, description="Target Candidate IDs under study")
    status: HypothesisStatus = Field(default=HypothesisStatus.PROPOSED, description="Hypothesis status")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    version: str = Field(default="1.0.0", description="Hypothesis version string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"


class HypothesisRegistry:
    """Registry maintaining scientific hypotheses, versioning, and status tracking."""

    def __init__(self) -> None:
        self._hypotheses: dict[str, HypothesisRecord] = {}

    def register_hypothesis(
        self,
        title: str,
        description: str,
        target_feature_ids: list[str] | None = None,
        candidate_ids: list[str] | None = None,
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> HypothesisRecord:
        """Register a new scientific hypothesis into the registry.

        Args:
            title: Title string.
            description: Statement string.
            target_feature_ids: Target Feature IDs.
            candidate_ids: Target Candidate IDs.
            version: Version string.
            metadata: Metadata dictionary.

        Returns:
            Registered HypothesisRecord.
        """
        hyp_id = compute_hypothesis_id(title, version)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if hyp_id in self._hypotheses:
            return self._hypotheses[hyp_id]

        record = HypothesisRecord(
            hypothesis_id=hyp_id,
            title=title,
            description=description,
            target_feature_ids=target_feature_ids or [],
            candidate_ids=candidate_ids or [],
            status=HypothesisStatus.PROPOSED,
            creation_timestamp=timestamp,
            version=version,
            metadata=metadata or {},
        )

        self._hypotheses[hyp_id] = record
        return record

    def get_hypothesis(self, hypothesis_id: str) -> HypothesisRecord:
        """Retrieve HypothesisRecord by Hypothesis ID."""
        if hypothesis_id not in self._hypotheses:
            raise KeyError(f"Hypothesis ID '{hypothesis_id}' not found in HypothesisRegistry")
        return self._hypotheses[hypothesis_id]

    def update_status(self, hypothesis_id: str, new_status: HypothesisStatus) -> HypothesisRecord:
        """Update hypothesis status."""
        rec = self.get_hypothesis(hypothesis_id)
        d = rec.model_dump()
        d["status"] = new_status
        updated = HypothesisRecord(**d)
        self._hypotheses[hypothesis_id] = updated
        return updated

    def list_all(self) -> list[HypothesisRecord]:
        """List all hypotheses."""
        return list(self._hypotheses.values())
