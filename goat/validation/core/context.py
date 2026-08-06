"""
Project GOAT v0.7 — Validation Context

Defines the immutable ValidationContext model carrying active artifact references
across validation operations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ValidationContext(BaseModel):
    """Immutable context carrying active artifact references for hypothesis validation."""

    hypothesis_ids: list[str] = Field(default_factory=list, description="Active Hypothesis IDs (HYP_<HEX16>)")
    validation_run_ids: list[str] = Field(default_factory=list, description="Active Validation Run IDs (VRN_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Active Evidence IDs (VEV_<HEX16>)")
    decision_ids: list[str] = Field(default_factory=list, description="Active Decision IDs (VDC_<HEX16>)")
    experiment_ids: list[str] = Field(default_factory=list, description="Referenced Experiment IDs")
    study_ids: list[str] = Field(default_factory=list, description="Referenced Study IDs")
    consensus_ids: list[str] = Field(default_factory=list, description="Referenced Consensus IDs")
    registry_versions: dict[str, str] = Field(default_factory=dict, description="Registry schema versions")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
