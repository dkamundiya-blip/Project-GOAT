"""
Project GOAT v0.6 — Candidate Edge & Parameterization Identity

Defines CandidateEdge domain model and canonical identity computation logic according to SPEC.3.
Separates semantic statistical identity (edge_id) from display metadata and operational state.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from goat.research.edge.canonical import compute_canonical_sha256, freeze_structure
from goat.research.edge.enums import EdgeLifecycleStatus


class CandidateEdge(BaseModel):
    """Immutable formal Candidate Edge domain model."""

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    edge_id: str = ""
    proposition_name: str
    causal_primitive: str
    target_feature: str
    economic_rationale_category: str
    base_condition_spec: Any
    description: str = ""
    notes: str = ""
    display_labels: Any = Field(default_factory=tuple)
    hypothesis_ids: Any = Field(default_factory=tuple)
    lifecycle_state: EdgeLifecycleStatus = EdgeLifecycleStatus.CANDIDATE
    edge_schema_version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("proposition_name", "causal_primitive", "target_feature", "economic_rationale_category")
    @classmethod
    def _validate_non_empty_str(cls, v: str, info: Any) -> str:
        if not str(v).strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string")
        return str(v).strip()

    @field_validator("base_condition_spec", "display_labels", "hypothesis_ids")
    @classmethod
    def _freeze_nested(cls, v: Any) -> Any:
        return freeze_structure(v)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        computed = self.compute_id()
        if self.edge_id and self.edge_id != computed:
            raise ValueError(f"Supplied edge_id '{self.edge_id}' does not match computed identity '{computed}'")
        object.__setattr__(self, "edge_id", computed)

    def compute_id(self) -> str:
        """Compute deterministic SHA-256 edge identity string: EDGE_<HEX16>."""
        payload = {
            "base_condition_spec": self.base_condition_spec,
            "causal_primitive": str(self.causal_primitive).strip().lower(),
            "economic_rationale_category": str(self.economic_rationale_category).strip().lower(),
            "edge_schema_version": int(self.edge_schema_version),
            "target_feature": str(self.target_feature).strip().lower(),
        }
        digest = compute_canonical_sha256(payload, length=16)
        return f"EDGE_{digest.upper()}"


def compute_hypothesis_version(
    edge_id: str,
    condition_parameters: dict[str, Any],
    forward_outcome_metric: str,
    forward_horizon: int,
) -> str:
    """Compute deterministic SHA-256 parameterization version hash string (12 hex chars).

    Inputs participating in version identity:
    - edge_id
    - condition_parameters (sorted canonically)
    - forward_outcome_metric
    - forward_horizon
    """
    if not str(edge_id).strip():
        raise ValueError("edge_id must be a non-empty string")
    if not str(forward_outcome_metric).strip():
        raise ValueError("forward_outcome_metric must be a non-empty string")
    if forward_horizon < 1:
        raise ValueError(f"forward_horizon must be >= 1, got {forward_horizon}")

    payload = {
        "condition_parameters": condition_parameters,
        "edge_id": str(edge_id).strip(),
        "forward_horizon": int(forward_horizon),
        "forward_outcome_metric": str(forward_outcome_metric).strip(),
    }
    return compute_canonical_sha256(payload, length=12)
