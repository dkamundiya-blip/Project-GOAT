"""
Project GOAT v0.7 — Study Context

Defines the immutable StudyContext model carrying active artifact IDs across study executions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StudyContext(BaseModel):
    """Immutable context carrying active artifact references for a scientific research study."""

    study_id: str = Field(..., description="Target Study ID (STD_<HEX16>)")
    experiment_ids: list[str] = Field(default_factory=list, description="Active Experiment IDs (EXP_<HEX16>)")
    pipeline_ids: list[str] = Field(default_factory=list, description="Active Pipeline IDs (PIPE_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Active Knowledge IDs (KNW_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Active Evidence IDs (EVD_<HEX16>)")
    registry_version: str = Field(default="1.0.0", description="Registry schema version")
    config_ids: list[str] = Field(default_factory=list, description="Active Configuration IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
