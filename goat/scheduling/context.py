"""
Project GOAT v0.7 — Scientific Scheduling Context

Defines the immutable ScientificSchedulingContext model carrying active artifact IDs across scheduling operations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScientificSchedulingContext(BaseModel):
    """Immutable context carrying active artifact references for scientific scheduling."""

    schedule_ids: list[str] = Field(default_factory=list, description="Active Schedule IDs (SCH_<HEX16>)")
    plan_ids: list[str] = Field(default_factory=list, description="Active Plan IDs (PLN_<HEX16>)")
    priority_ids: list[str] = Field(default_factory=list, description="Active Priority IDs (RPR_<HEX16>)")
    portfolio_ids: list[str] = Field(default_factory=list, description="Active Portfolio IDs (PFO_<HEX16>)")
    program_ids: list[str] = Field(default_factory=list, description="Active Program IDs (PRG_<HEX16>)")
    study_ids: list[str] = Field(default_factory=list, description="Active Study IDs (STD_<HEX16>)")
    experiment_ids: list[str] = Field(default_factory=list, description="Active Experiment IDs (EXP_<HEX16>)")
    registry_versions: dict[str, str] = Field(default_factory=dict, description="Registry schema versions")
    config_ids: list[str] = Field(default_factory=list, description="Active Configuration IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
