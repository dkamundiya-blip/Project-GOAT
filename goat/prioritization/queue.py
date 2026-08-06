"""
Project GOAT v0.7 — Research Priority Queue Model

Defines the immutable ResearchPriorityQueue model (RPQ_<HEX16>) representing ordered research candidate queues.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_queue_id(ordered_priority_ids: list[str]) -> tuple[str, str]:
    """Compute deterministic Research Priority Queue ID (RPQ_<HEX16>) and full SHA-256 queue hash.

    Args:
        ordered_priority_ids: Ordered list of Priority IDs (RPR_<HEX16>).

    Returns:
        Tuple of (queue_id, queue_hash).
    """
    payload = {
        "ordered_priority_ids": [str(p).strip() for p in ordered_priority_ids],
    }
    digest = compute_canonical_sha256(payload)
    queue_id = f"RPQ_{digest[:16].upper()}"
    return queue_id, digest


class ResearchPriorityQueue(BaseModel):
    """Immutable queue containing prioritized Research Priority IDs ordered deterministically by score."""

    queue_id: str = Field(
        ...,
        description="Unique Queue ID formatted as RPQ_<HEX16>",
        pattern=r"^RPQ_[A-Fa-f0-9]{16}$",
    )
    ordered_priority_ids: list[str] = Field(default_factory=list, description="Ordered Priority IDs (RPR_<HEX16>)")
    queue_hash: str = Field(..., description="Full 64-character SHA-256 canonical queue hash digest")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    replay_metadata: dict[str, Any] = Field(default_factory=dict, description="Replay metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
