"""
Project GOAT v0.7 — Research Execution Context

Defines the immutable ResearchExecutionContext model passing active artifact IDs across pipeline stages.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResearchExecutionContext(BaseModel):
    """Immutable execution context carrying active scientific artifact references across pipeline stages."""

    pipeline_id: str = Field(..., description="Target Research Pipeline ID (PIPE_<HEX16>)")
    feature_ids: list[str] = Field(default_factory=list, description="Active Feature IDs (FEAT_<HEX16>)")
    candidate_ids: list[str] = Field(default_factory=list, description="Active Candidate IDs (CAND_<HEX16>)")
    decision_ids: list[str] = Field(default_factory=list, description="Active Decision IDs (DEC_<HEX16>)")
    validation_ids: list[str] = Field(default_factory=list, description="Active Validation IDs (VAL_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Active Evidence IDs (EVD_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Active Knowledge IDs (KNW_<HEX16>)")
    registry_version: str = Field(default="1.0.0", description="Registry schema version")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution context metadata")

    class Config:
        frozen = True
        extra = "forbid"
