"""
Project GOAT v0.7 — Research Prioritization Context

Defines the immutable ResearchPrioritizationContext model carrying active artifact IDs across research prioritization operations.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResearchPrioritizationContext(BaseModel):
    """Immutable context carrying active artifact references for scientific research prioritization."""

    portfolio_ids: list[str] = Field(default_factory=list, description="Active Portfolio IDs (PFO_<HEX16>)")
    program_ids: list[str] = Field(default_factory=list, description="Active Program IDs (PRG_<HEX16>)")
    study_ids: list[str] = Field(default_factory=list, description="Active Study IDs (STD_<HEX16>)")
    experiment_ids: list[str] = Field(default_factory=list, description="Active Experiment IDs (EXP_<HEX16>)")
    evidence_ids: list[str] = Field(default_factory=list, description="Active Evidence IDs (EVD_<HEX16>)")
    synthesis_ids: list[str] = Field(default_factory=list, description="Active Synthesis IDs (SYN_<HEX16>)")
    consensus_ids: list[str] = Field(default_factory=list, description="Active Consensus IDs (CNS_<HEX16>)")
    knowledge_ids: list[str] = Field(default_factory=list, description="Active Knowledge IDs (KNW_<HEX16>)")
    evolution_ids: list[str] = Field(default_factory=list, description="Active Evolution IDs (KEV_<HEX16>)")
    scientific_memory_ids: list[str] = Field(default_factory=list, description="Active Scientific Memory IDs")
    registry_versions: dict[str, str] = Field(default_factory=dict, description="Registry schema versions")
    config_ids: list[str] = Field(default_factory=list, description="Active Configuration IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Context metadata annotations")

    class Config:
        frozen = True
        extra = "forbid"
