"""
Project GOAT v0.7 — Scientific Hypothesis Model

Defines the immutable ScientificHypothesis model (HYP_<HEX16>) representing
a scientific trading hypothesis submitted for validation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256
from goat.validation.core.enums import ValidationState


def compute_hypothesis_fingerprint(
    title: str,
    originating_experiment: str,
    originating_study: str,
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Hypothesis Fingerprint (HYPFP_<HEX64>).

    Args:
        title: Hypothesis title string.
        originating_experiment: Source Experiment ID.
        originating_study: Source Study ID.
        version: Version string.

    Returns:
        String formatted as 'HYPFP_' + 64 uppercase hex characters.
    """
    payload = {
        "originating_experiment": str(originating_experiment).strip(),
        "originating_study": str(originating_study).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"HYPFP_{digest.upper()}"


def compute_hypothesis_id(fingerprint: str, version: str = "1.0.0") -> tuple[str, str]:
    """Compute deterministic Hypothesis ID (HYP_<HEX16>) and full SHA-256 canonical hash.

    Args:
        fingerprint: Hypothesis Fingerprint (HYPFP_<HEX64>).
        version: Semantic version string.

    Returns:
        Tuple of (hypothesis_id, canonical_hash).
    """
    payload = {
        "fingerprint": str(fingerprint).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    hypothesis_id = f"HYP_{digest[:16].upper()}"
    return hypothesis_id, digest


class ScientificHypothesis(BaseModel):
    """Immutable scientific hypothesis submitted for validation."""

    hypothesis_id: str = Field(
        ...,
        description="Unique Hypothesis ID formatted as HYP_<HEX16>",
        pattern=r"^HYP_[A-Fa-f0-9]{16}$",
    )
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")
    scientific_fingerprint: str = Field(..., description="Hypothesis Fingerprint (HYPFP_<HEX64>)")
    hypothesis_version: str = Field(default="1.0.0", description="Semantic hypothesis version")
    title: str = Field(..., description="Hypothesis title")
    description: str = Field(default="", description="Hypothesis description")
    originating_program: str = Field(default="", description="Source Program ID (PRG_<HEX16>)")
    originating_experiment: str = Field(default="", description="Source Experiment ID (EXP_<HEX16>)")
    originating_study: str = Field(default="", description="Source Study ID (STD_<HEX16>)")
    author: str = Field(default="system", description="Author identifier")
    creation_time: str = Field(..., description="ISO 8601 UTC creation timestamp")
    assumptions: list[str] = Field(default_factory=list, description="Hypothesis assumptions")
    expected_behavior: str = Field(default="", description="Expected observable behavior")
    validation_state: ValidationState = Field(
        default=ValidationState.PENDING,
        description="Current validation lifecycle state",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Hypothesis metadata")

    class Config:
        frozen = True
        extra = "forbid"
