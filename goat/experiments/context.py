"""
Project GOAT v0.7 — Experiment Context

Defines the immutable ExperimentContext model carrying active artifact IDs across experiment steps.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExperimentContext(BaseModel):
    """Immutable context carrying active artifact references for an experiment."""

    experiment_id: str = Field(..., description="Target Experiment ID (EXP_<HEX16>)")
    pipeline_id: str = Field(default="", description="Target Pipeline ID (PIPE_<HEX16>)")
    feature_ids: list[str] = Field(default_factory=list, description="Active Feature IDs")
    candidate_ids: list[str] = Field(default_factory=list, description="Active Candidate IDs")
    decision_ids: list[str] = Field(default_factory=list, description="Active Decision IDs")
    validation_ids: list[str] = Field(default_factory=list, description="Active Validation IDs")
    evidence_ids: list[str] = Field(default_factory=list, description="Active Evidence IDs")
    knowledge_ids: list[str] = Field(default_factory=list, description="Active Knowledge IDs")
    config_ids: list[str] = Field(default_factory=list, description="Active Configuration IDs")
    registry_version: str = Field(default="1.0.0", description="Registry schema version")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
