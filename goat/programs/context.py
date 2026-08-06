"""
Project GOAT v0.7 — Program Context

Defines the immutable ProgramContext model carrying active artifact IDs across research program executions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProgramContext(BaseModel):
    """Immutable context carrying active artifact references for a scientific research program."""

    program_id: str = Field(..., description="Target Program ID (PRG_<HEX16>)")
    study_ids: list[str] = Field(default_factory=list, description="Active Study IDs (STD_<HEX16>)")
    experiment_ids: list[str] = Field(default_factory=list, description="Active Experiment IDs (EXP_<HEX16>)")
    pipeline_ids: list[str] = Field(default_factory=list, description="Active Pipeline IDs (PIPE_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Active Knowledge IDs (KNW_<HEX16>)")
    registry_version: str = Field(default="1.0.0", description="Registry schema version")
    config_ids: list[str] = Field(default_factory=list, description="Active Configuration IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
