"""
Project GOAT v0.7 — Exploration Decision Model

Defines the immutable ExplorationDecision model representing exploration intent and rationale,
with deterministic DEC_<HEX16> identity calculation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_decision_id(
    search_strategy_id: str,
    generation_rule_id: str,
    parent_candidate_ids: list[str],
    transformation_ids: list[str],
    depth: int = 0,
) -> tuple[str, str]:
    """Compute deterministic Exploration Decision ID (DEC_<HEX16>) and full SHA-256 decision hash.

    Args:
        search_strategy_id: Identifier of the executing search strategy.
        generation_rule_id: Identifier of the active generation rule.
        parent_candidate_ids: List of upstream parent Candidate IDs.
        transformation_ids: List of applied Transformation IDs.
        depth: Decision depth level.

    Returns:
        Tuple of (decision_id, decision_hash) where decision_id is 'DEC_' + first 16 uppercase hex chars.
    """
    payload = {
        "depth": int(depth),
        "generation_rule_id": str(generation_rule_id).strip(),
        "parent_candidate_ids": sorted([str(p).strip() for p in parent_candidate_ids]),
        "search_strategy_id": str(search_strategy_id).strip(),
        "transformation_ids": sorted([str(t).strip() for t in transformation_ids]),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"DEC_{digest[:16].upper()}"
    return decision_id, digest


class ExplorationDecision(BaseModel):
    """Immutable representation of an exploration decision capturing scientific intent and provenance."""

    decision_id: str = Field(
        ...,
        description="Unique Exploration Decision ID formatted as DEC_<HEX16>",
        pattern=r"^DEC_[A-Fa-f0-9]{16}$",
    )
    decision_version: str = Field(default="1.0.0", description="Decision specification version")
    generation_rule_id: str = Field(default="rule_expansion", description="Rule or grammar pattern identifier")
    search_strategy_id: str = Field(..., description="Executing search strategy identifier")
    parent_candidate_ids: list[str] = Field(default_factory=list, description="Upstream parent Candidate IDs")
    transformation_ids: list[str] = Field(default_factory=list, description="Applied Transformation IDs")
    decision_timestamp: str = Field(..., description="ISO 8601 UTC decision timestamp")
    decision_depth: int = Field(default=0, ge=0, description="Decision depth level")
    budget_snapshot: dict[str, Any] = Field(default_factory=dict, description="Resource budget state snapshot")
    scientific_notes: str = Field(default="", description="Scientific notes explaining decision rationale")
    decision_hash: str = Field(..., description="Full 64-character SHA-256 canonical decision hash digest")

    class Config:
        frozen = True
        extra = "forbid"
