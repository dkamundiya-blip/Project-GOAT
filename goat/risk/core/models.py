"""
Project GOAT v0.7 — Core Immutable Models for Scientific Risk Management Engine

Defines immutable Pydantic domain models:
- RiskProfile (RPF_<HEX16>)
- PositionSizingDecision (PSD_<HEX16>)
- CapitalAllocation (CAL_<HEX16>)
- ExposureAssessment (EXP_<HEX16>)
- RiskAssessment (RSA_<HEX16>)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.risk.core.enums import ExposureStatus


class RiskProfile(BaseModel):
    """Immutable model representing account-level risk parameters and constraints."""

    risk_profile_id: str = Field(
        ...,
        description="Unique risk profile ID formatted as RPF_<HEX16>",
        pattern=r"^RPF_[A-Fa-f0-9]{16}$",
    )
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    simulation_result_id: str = Field(..., description="Target SimulationResult ID (SRS_<HEX16>)")
    account_currency: str = Field(default="USD", description="Account base currency ISO code")
    account_balance: float = Field(default=100000.0, gt=0.0, description="Total account balance amount")
    maximum_risk_percent: float = Field(default=0.02, ge=0.001, le=0.20, description="Maximum risk per trade fraction (e.g. 0.02 = 2%)")
    maximum_portfolio_exposure: float = Field(default=0.20, ge=0.01, le=1.0, description="Maximum overall portfolio exposure fraction")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class PositionSizingDecision(BaseModel):
    """Immutable model representing deterministic position sizing, stop-loss, and take-profit recommendations."""

    sizing_id: str = Field(
        ...,
        description="Unique position sizing ID formatted as PSD_<HEX16>",
        pattern=r"^PSD_[A-Fa-f0-9]{16}$",
    )
    risk_profile_id: str = Field(..., description="Target RiskProfile ID (RPF_<HEX16>)")
    instrument: str = Field(..., description="Financial instrument ticker symbol")
    entry_price: float = Field(..., gt=0.0, description="Recommended entry price")
    stop_loss_price: float = Field(..., gt=0.0, description="Recommended stop loss price")
    take_profit_price: float = Field(..., gt=0.0, description="Recommended take profit price")
    stop_distance: float = Field(..., ge=0.0, description="Distance from entry to stop loss")
    reward_distance: float = Field(..., ge=0.0, description="Distance from entry to take profit")
    risk_reward_ratio: float = Field(..., ge=0.0, description="Ratio of expected reward distance to stop distance")
    position_size: float = Field(..., ge=0.0, description="Raw calculated position units")
    minimum_lot_size: float = Field(default=0.01, gt=0.0, description="Broker minimum lot size")
    recommended_lot_size: float = Field(..., ge=0.0, description="Normalized lot size rounded to lot step")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class CapitalAllocation(BaseModel):
    """Immutable model representing capital reservation and utilization across opportunities."""

    allocation_id: str = Field(
        ...,
        description="Unique allocation ID formatted as CAL_<HEX16>",
        pattern=r"^CAL_[A-Fa-f0-9]{16}$",
    )
    qualification_id: str = Field(..., description="Target ScientificQualification ID (SQL_<HEX16>)")
    allocated_capital: float = Field(..., ge=0.0, description="Monetary capital allocated to this opportunity")
    available_capital: float = Field(..., ge=0.0, description="Remaining unallocated account capital")
    reserved_capital: float = Field(..., ge=0.0, description="Total capital reserved across all active opportunities")
    utilization_percent: float = Field(..., ge=0.0, le=1.0, description="Portfolio capital utilization fraction (0.0 to 1.0)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class ExposureAssessment(BaseModel):
    """Immutable model representing portfolio and asset exposure analysis."""

    exposure_id: str = Field(
        ...,
        description="Unique exposure ID formatted as EXP_<HEX16>",
        pattern=r"^EXP_[A-Fa-f0-9]{16}$",
    )
    active_positions: list[str] = Field(default_factory=list, description="IDs of active position sizing decisions")
    portfolio_exposure: float = Field(..., ge=0.0, description="Total portfolio monetary exposure")
    instrument_exposure: float = Field(..., ge=0.0, description="Monetary exposure to target instrument")
    correlated_exposure: float = Field(..., ge=0.0, description="Monetary exposure to correlated assets")
    exposure_status: ExposureStatus = Field(..., description="Assigned exposure assessment status")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


class RiskAssessment(BaseModel):
    """Immutable model summarizing overall monetary risk, reward, and drawdown impact."""

    assessment_id: str = Field(
        ...,
        description="Unique risk assessment ID formatted as RSA_<HEX16>",
        pattern=r"^RSA_[A-Fa-f0-9]{16}$",
    )
    sizing_id: str = Field(..., description="Target PositionSizingDecision ID (PSD_<HEX16>)")
    total_risk: float = Field(..., ge=0.0, description="Total risk score rating")
    monetary_risk: float = Field(..., ge=0.0, description="Exact risk amount in account base currency")
    expected_reward: float = Field(..., ge=0.0, description="Exact expected reward amount in account base currency")
    expected_return_percent: float = Field(..., description="Expected return on account balance percentage")
    drawdown_impact: float = Field(..., ge=0.0, le=1.0, description="Estimated drawdown impact fraction")
    assessment_summary: str = Field(default="", description="Executive risk assessment summary narrative")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    canonical_hash: str = Field(default="", description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"
