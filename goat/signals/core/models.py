"""
Project GOAT v0.7 — Core Immutable Models for Scientific Signal Generation Engine

Defines immutable Pydantic domain models:
- TradingSignal (SIG_<HEX16>)
- SignalPayload (SPL_<HEX16>)
- SignalLifecycleEvent (SLE_<HEX16>)
- ExecutionReadiness (EXR_<HEX16>)
- SignalAuditRecord (SAD_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.signals.core.enums import (
    ExecutionStatus,
    PayloadFormat,
    SignalDirection,
    SignalLifecycleState,
)


class TradingSignal(BaseModel):
    """Immutable model representing an execution-ready scientific trading signal."""

    signal_id: str = Field(
        ...,
        description="Unique signal ID formatted as SIG_<HEX16>",
        pattern=r"^SIG_[A-Fa-f0-9]{16}$",
    )
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    simulation_result_id: str = Field(..., description="Target SimulationResult ID (SRS_<HEX16>)")
    risk_assessment_id: str = Field(..., description="Target RiskAssessment ID (RSA_<HEX16>)")
    composite_id: str = Field(..., description="Target CompositeEdge ID (CMP_<HEX16>)")
    regime_id: str = Field(..., description="Target MarketRegime ID (MRG_<HEX16>)")
    instrument: str = Field(..., description="Financial instrument ticker symbol")
    direction: SignalDirection = Field(..., description="Trade direction (BUY/SELL/FLAT)")
    entry_price: float = Field(..., gt=0.0, description="Recommended entry price target")
    stop_loss: float = Field(..., gt=0.0, description="Recommended stop loss price target")
    take_profit: float = Field(..., gt=0.0, description="Recommended take profit price target")
    recommended_lot_size: float = Field(..., ge=0.0, description="Normalized lot size")
    minimum_lot_size: float = Field(default=0.01, gt=0.0, description="Minimum lot size constraint")
    monetary_risk: float = Field(..., ge=0.0, description="Risk amount in account base currency")
    monetary_reward: float = Field(..., ge=0.0, description="Expected reward amount in account base currency")
    risk_reward_ratio: float = Field(..., ge=0.0, description="Ratio of expected reward to stop loss distance")
    scientific_confidence: float = Field(..., ge=0.0, le=1.0, description="Scientific confidence rating (0.0 to 1.0)")
    readiness_level: str = Field(default="READY_FOR_SIMULATION", description="Decision readiness level string")
    generation_timestamp: str = Field(..., description="ISO 8601 UTC generation timestamp")
    expiration_timestamp: str = Field(..., description="ISO 8601 UTC expiration timestamp")
    lifecycle_state: SignalLifecycleState = Field(default=SignalLifecycleState.CREATED, description="Current lifecycle state")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    # Special Required Properties for Public API & Dashboards/Adapters
    @property
    def qualification_status(self) -> str:
        return self.metadata.get("qualification_status", "QUALIFIED")

    @property
    def validation_status(self) -> str:
        return self.metadata.get("validation_status", "VALIDATED")

    @property
    def risk_percentage(self) -> float:
        return self.metadata.get("risk_percentage", 2.0)

    @property
    def replay_reference(self) -> str:
        return self.metadata.get("replay_reference", f"REPLAY_{self.signal_id}")

    @property
    def audit_reference(self) -> str:
        return self.metadata.get("audit_reference", f"SAD_{self.signal_id.replace('SIG_', '')}")

    class Config:
        frozen = True
        extra = "forbid"


class SignalPayload(BaseModel):
    """Immutable model representing formatted payload data for distribution targets."""

    payload_id: str = Field(
        ...,
        description="Unique payload ID formatted as SPL_<HEX16>",
        pattern=r"^SPL_[A-Fa-f0-9]{16}$",
    )
    signal_id: str = Field(..., description="Target TradingSignal ID (SIG_<HEX16>)")
    notification_version: str = Field(default="1.0.0", description="Notification schema version string")
    payload_format: PayloadFormat = Field(..., description="Format target (JSON, MARKDOWN, TELEGRAM, etc.)")
    payload_data: dict[str, Any] = Field(default_factory=dict, description="Formatted payload data payload")
    checksum: str = Field(..., description="SHA-256 payload checksum digest")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class SignalLifecycleEvent(BaseModel):
    """Immutable audit model representing state transitions in the signal lifecycle."""

    lifecycle_event_id: str = Field(
        ...,
        description="Unique lifecycle event ID formatted as SLE_<HEX16>",
        pattern=r"^SLE_[A-Fa-f0-9]{16}$",
    )
    signal_id: str = Field(..., description="Target TradingSignal ID (SIG_<HEX16>)")
    previous_state: SignalLifecycleState = Field(..., description="Previous lifecycle state")
    current_state: SignalLifecycleState = Field(..., description="New current lifecycle state")
    event_timestamp: str = Field(..., description="ISO 8601 UTC timestamp string")
    triggering_reason: str = Field(default="", description="Explanation narrative for transition")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExecutionReadiness(BaseModel):
    """Immutable model representing execution readiness verification for a trading signal."""

    readiness_id: str = Field(
        ...,
        description="Unique readiness ID formatted as EXR_<HEX16>",
        pattern=r"^EXR_[A-Fa-f0-9]{16}$",
    )
    signal_id: str = Field(..., description="Target TradingSignal ID (SIG_<HEX16>)")
    execution_status: ExecutionStatus = Field(..., description="Assigned execution readiness status")
    broker_requirements: dict[str, Any] = Field(default_factory=dict, description="Broker requirement checks map")
    validation_summary: str = Field(default="", description="Summary narrative of readiness checks")
    readiness_score: float = Field(..., ge=0.0, le=1.0, description="Readiness confidence score (0.0 to 1.0)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class SignalAuditRecord(BaseModel):
    """Immutable model representing complete scientific auditability and provenance trace."""

    audit_id: str = Field(
        ...,
        description="Unique signal audit ID formatted as SAD_<HEX16>",
        pattern=r"^SAD_[A-Fa-f0-9]{16}$",
    )
    signal_id: str = Field(..., description="Target TradingSignal ID (SIG_<HEX16>)")
    qualification_reference: str = Field(..., description="Qualification ID reference")
    simulation_reference: str = Field(..., description="Simulation Result ID reference")
    risk_reference: str = Field(..., description="Risk Assessment ID reference")
    replay_reference: str = Field(..., description="Replay ID reference")
    scientific_trace: dict[str, Any] = Field(default_factory=dict, description="Full scientific provenance lineage trace")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
