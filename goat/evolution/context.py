"""
Project GOAT v0.7 — Knowledge Evolution Context

Defines the immutable KnowledgeEvolutionContext model carrying active artifact IDs across knowledge evolution operations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeEvolutionContext(BaseModel):
    """Immutable context carrying active artifact references for scientific knowledge evolution."""

    portfolio_ids: list[str] = Field(default_factory=list, description="Active Portfolio IDs (PFO_<HEX16>)")
    program_ids: list[str] = Field(default_factory=list, description="Active Program IDs (PRG_<HEX16>)")
    study_ids: list[str] = Field(default_factory=list, description="Active Study IDs (STD_<HEX16>)")
    experiment_ids: list[str] = Field(default_factory=list, description="Active Experiment IDs (EXP_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Active Evidence IDs (EVD_<HEX16>)")
    synthesis_ids: list[str] = Field(default_factory=list, description="Active Synthesis IDs (SYN_<HEX16>)")
    consensus_ids: list[str] = Field(default_factory=list, description="Active Consensus IDs (CNS_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Active Knowledge IDs (KNW_<HEX16>)")
    registry_versions: dict[str, str] = Field(default_factory=dict, description="Registry schema versions")
    config_ids: list[str] = Field(default_factory=list, description="Active Configuration IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
