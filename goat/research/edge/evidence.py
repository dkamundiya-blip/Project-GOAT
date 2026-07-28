"""
Project GOAT v0.6 — Atomic Evidence Record Model

Defines AtomicEvidenceRecord with strict separation between observation identity (evidence_id)
and scientific result payload (evidence_payload_hash) according to SPEC.3.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from goat.research.edge.canonical import compute_canonical_sha256, freeze_structure
from goat.research.edge.enums import EvidenceDimensionType


class AtomicEvidenceRecord(BaseModel):
    """Immutable normalized atomic evidence observation record."""

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    evidence_id: str = ""
    evidence_payload_hash: str = ""
    validation_run_id: str
    edge_id: str
    dimension_type: EvidenceDimensionType
    dimension_key: str
    partition_identity: str  # e.g., "train", "validation", "holdout"

    # Quantitative Result Payload
    sample_count: int
    effect_size: float
    effect_size_type: str = "cohens_d"
    raw_p_value: float
    adjusted_q_value: float | None = None
    statistic_value: float = 0.0
    confidence_interval: Any = None

    # Context & Metadata
    context_metadata: Any = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("validation_run_id", "edge_id", "dimension_key", "partition_identity")
    @classmethod
    def _validate_non_empty(cls, v: str, info: Any) -> str:
        if not str(v).strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string")
        return str(v).strip()

    @field_validator("confidence_interval", "context_metadata")
    @classmethod
    def _freeze_nested(cls, v: Any) -> Any:
        return freeze_structure(v) if v is not None else None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        computed_id = self.compute_evidence_id()
        computed_payload = self.compute_payload_hash()

        if self.evidence_id and self.evidence_id != computed_id:
            raise ValueError(f"Supplied evidence_id '{self.evidence_id}' does not match computed '{computed_id}'")
        if self.evidence_payload_hash and self.evidence_payload_hash != computed_payload:
            raise ValueError(f"Supplied evidence_payload_hash '{self.evidence_payload_hash}' does not match computed '{computed_payload}'")

        object.__setattr__(self, "evidence_id", computed_id)
        object.__setattr__(self, "evidence_payload_hash", computed_payload)

    def compute_evidence_id(self) -> str:
        """Compute deterministic observation identity: EVD_<SHA256[:16]>.

        Observation identity depends ONLY on WHAT observation was targetted:
        - validation_run_id
        - dimension_type
        - dimension_key
        - partition_identity

        It does NOT change when result values (p-value, effect size) change.
        """
        payload = {
            "dimension_key": str(self.dimension_key).strip(),
            "dimension_type": self.dimension_type.value if isinstance(self.dimension_type, EvidenceDimensionType) else str(self.dimension_type),
            "partition_identity": str(self.partition_identity).strip().lower(),
            "validation_run_id": str(self.validation_run_id).strip(),
        }
        digest = compute_canonical_sha256(payload, length=16)
        return f"EVD_{digest.upper()}"

    def compute_payload_hash(self) -> str:
        """Compute deterministic scientific result payload hash: EVP_<SHA256[:16]>.

        Payload hash captures quantitative evaluation metrics:
        - sample_count
        - effect_size
        - effect_size_type
        - raw_p_value
        - adjusted_q_value
        - statistic_value
        - confidence_interval
        """
        payload = {
            "adjusted_q_value": float(self.adjusted_q_value) if self.adjusted_q_value is not None else None,
            "confidence_interval": [float(x) for x in self.confidence_interval] if self.confidence_interval is not None else None,
            "effect_size": float(self.effect_size),
            "effect_size_type": str(self.effect_size_type).strip(),
            "raw_p_value": float(self.raw_p_value),
            "sample_count": int(self.sample_count),
            "statistic_value": float(self.statistic_value),
        }
        digest = compute_canonical_sha256(payload, length=16)
        return f"EVP_{digest.upper()}"
