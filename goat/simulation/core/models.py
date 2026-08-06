"""
Project GOAT v0.7 — Core Immutable Models for Scientific Simulation & Walk-Forward Engine

Defines immutable Pydantic domain models:
- SimulationScenario (SIM_<HEX16>)
- SimulationRun (SRN_<HEX16>)
- SimulationResult (SRS_<HEX16>)
- WalkForwardWindow (WFW_<HEX16>)
- PerformanceAttribution (PAT_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.simulation.core.enums import SimulationRunStatus, ValidationStatus


class SimulationScenario(BaseModel):
    """Immutable model representing a deterministic simulation scenario configuration."""

    scenario_id: str = Field(
        ...,
        description="Unique scenario ID formatted as SIM_<HEX16>",
        pattern=r"^SIM_[A-Fa-f0-9]{16}$",
    )
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    composite_id: str = Field(..., description="Target CompositeEdge ID (CMP_<HEX16>)")
    regime_id: str = Field(..., description="Target MarketRegime ID (MRG_<HEX16>)")
    dataset_reference: str = Field(..., description="Reference name or URI of historical event dataset")
    simulation_window: list[str] = Field(default_factory=list, description="Tuple/list of [start_timestamp, end_timestamp]")
    configuration: dict[str, Any] = Field(default_factory=dict, description="Simulation parameter dictionary")
    creation_timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class SimulationRun(BaseModel):
    """Immutable model representing a single deterministic simulation execution run."""

    run_id: str = Field(
        ...,
        description="Unique run ID formatted as SRN_<HEX16>",
        pattern=r"^SRN_[A-Fa-f0-9]{16}$",
    )
    scenario_id: str = Field(..., description="Target SimulationScenario ID (SIM_<HEX16>)")
    execution_timestamp: str = Field(..., description="ISO 8601 UTC execution timestamp")
    replay_seed: int = Field(default=42, ge=0, description="Deterministic seed value for reproducible replay")
    deterministic_hash: str = Field(..., description="Full SHA-256 hash verifying replay integrity")
    status: SimulationRunStatus = Field(default=SimulationRunStatus.COMPLETED, description="Run status")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class SimulationResult(BaseModel):
    """Immutable model representing the outcome of a simulation run."""

    result_id: str = Field(
        ...,
        description="Unique result ID formatted as SRS_<HEX16>",
        pattern=r"^SRS_[A-Fa-f0-9]{16}$",
    )
    run_id: str = Field(..., description="Target SimulationRun ID (SRN_<HEX16>)")
    simulated_events: list[dict[str, Any]] = Field(default_factory=list, description="List of simulated events")
    outcome_summary: dict[str, Any] = Field(default_factory=dict, description="Summary dictionary of simulation outcomes")
    validation_status: ValidationStatus = Field(..., description="Assigned validation decision status")
    statistical_metrics: dict[str, float] = Field(default_factory=dict, description="Dictionary of 15 descriptive statistical metrics")
    attribution: dict[str, Any] = Field(default_factory=dict, description="Dictionary summarizing performance attribution")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class WalkForwardWindow(BaseModel):
    """Immutable model representing a single walk-forward validation window."""

    window_id: str = Field(
        ...,
        description="Unique window ID formatted as WFW_<HEX16>",
        pattern=r"^WFW_[A-Fa-f0-9]{16}$",
    )
    training_period: list[str] = Field(..., description="List of [start_timestamp, end_timestamp] for training/in-sample period")
    validation_period: list[str] = Field(..., description="List of [start_timestamp, end_timestamp] for validation/out-of-sample period")
    sequence_number: int = Field(..., ge=1, description="1-indexed sequence number of walk-forward window")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class PerformanceAttribution(BaseModel):
    """Immutable model quantifying scientific contribution breakdown."""

    attribution_id: str = Field(
        ...,
        description="Unique attribution ID formatted as PAT_<HEX16>",
        pattern=r"^PAT_[A-Fa-f0-9]{16}$",
    )
    result_id: str = Field(..., description="Target SimulationResult ID (SRS_<HEX16>)")
    contributing_edges: dict[str, float] = Field(default_factory=dict, description="ScientificEdge contribution weights")
    contributing_regimes: dict[str, float] = Field(default_factory=dict, description="MarketRegime contribution weights")
    contributing_evidence: dict[str, float] = Field(default_factory=dict, description="Evidence contribution weights")
    contribution_breakdown: dict[str, float] = Field(default_factory=dict, description="Overall contribution percentage breakdown")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
