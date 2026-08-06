"""
Project GOAT v0.7 — Portfolio Result Model

Defines the immutable PortfolioResult model (PFR_<HEX16>) summarizing program, study, experiment, evidence, and knowledge references for a portfolio.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


def compute_portfolio_result_id(portfolio_id: str, timestamp: str) -> tuple[str, str]:
    """Compute deterministic Portfolio Result ID (PFR_<HEX16>) and full SHA-256 canonical hash.

    Args:
        portfolio_id: Associated Portfolio ID (PFO_<HEX16>).
        timestamp: ISO 8601 completion timestamp string.

    Returns:
        Tuple of (result_id, canonical_hash).
    """
    payload = {
        "portfolio_id": str(portfolio_id).strip(),
        "timestamp": str(timestamp).strip(),
    }
    digest = compute_canonical_sha256(payload)
    result_id = f"PFR_{digest[:16].upper()}"
    return result_id, digest


class PortfolioResult(BaseModel):
    """Immutable representation summarizing the aggregated scientific results of a research portfolio."""

    result_id: str = Field(
        ...,
        description="Unique Portfolio Result ID formatted as PFR_<HEX16>",
        pattern=r"^PFR_[A-Fa-f0-9]{16}$",
    )
    portfolio_id: str = Field(..., description="Parent Portfolio ID (PFO_<HEX16>)")
    program_references: list[str] = Field(default_factory=list, description="Executed Program IDs (PRG_<HEX16>)")
    study_references: list[str] = Field(default_factory=list, description="Executed Study IDs (STD_<HEX16>)")
    experiment_references: list[str] = Field(default_factory=list, description="Executed Experiment IDs (EXP_<HEX16>)")
    evidence_references: list[str] = Field(default_factory=list, description="Supporting Evidence IDs (EVD_<HEX16>)")
    knowledge_references: list[str] = Field(default_factory=list, description="Associated Knowledge IDs (KNW_<HEX16>)")
    completion_timestamp: str = Field(..., description="ISO 8601 UTC completion timestamp")
    canonical_hash: str = Field(..., description="Full 64-character SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
