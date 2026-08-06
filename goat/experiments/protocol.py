"""
Project GOAT v0.7 — Experiment Protocol Model

Defines the immutable ExperimentProtocol model (PROT_<HEX16>) specifying experimental stages, inputs, and validation rules.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_protocol_id(name: str, version: str, stages: list[str]) -> tuple[str, str]:
    """Compute deterministic Protocol ID (PROT_<HEX16>) and full SHA-256 protocol hash.

    Args:
        name: Protocol name string.
        version: Version string.
        stages: Ordered list of protocol stage names.

    Returns:
        Tuple of (protocol_id, protocol_hash).
    """
    payload = {
        "name": str(name).strip(),
        "stages": [str(s).strip() for s in stages],
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    protocol_id = f"PROT_{digest[:16].upper()}"
    return protocol_id, digest


class ExperimentProtocol(BaseModel):
    """Immutable scientific specification defining experiment stages, required inputs, and stopping rules."""

    protocol_id: str = Field(
        ...,
        description="Unique Protocol ID formatted as PROT_<HEX16>",
        pattern=r"^PROT_[A-Fa-f0-9]{16}$",
    )
    protocol_version: str = Field(default="1.0.0", description="Protocol specification version")
    protocol_name: str = Field(..., description="Protocol specification name")
    stages: list[str] = Field(default_factory=list, description="Ordered list of required protocol stages")
    required_inputs: dict[str, Any] = Field(default_factory=dict, description="Required input specification")
    required_outputs: dict[str, Any] = Field(default_factory=dict, description="Required output specification")
    validation_criteria: dict[str, Any] = Field(default_factory=dict, description="Validation criteria bounds")
    stopping_conditions: dict[str, Any] = Field(default_factory=dict, description="Early stopping conditions")
    failure_conditions: dict[str, Any] = Field(default_factory=dict, description="Failure criteria bounds")
    success_conditions: dict[str, Any] = Field(default_factory=dict, description="Success criteria bounds")
    protocol_hash: str = Field(..., description="Full 64-character SHA-256 canonical protocol hash digest")

    class Config:
        frozen = True
        extra = "forbid"
