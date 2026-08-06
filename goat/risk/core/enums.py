"""
Project GOAT v0.7 — Scientific Risk Management & Capital Allocation Enums

Defines deterministic enums for exposure status, sizing method, risk rule status, and position eligibility.
"""

from enum import Enum


class ExposureStatus(str, Enum):
    """Deterministic status for portfolio exposure assessment."""

    ACCEPTABLE = "ACCEPTABLE"
    WARNING = "WARNING"
    VIOLATION_EXCEEDED = "VIOLATION_EXCEEDED"


class SizingMethod(str, Enum):
    """Deterministic position sizing methodology."""

    FIXED_PERCENTAGE_RISK = "FIXED_PERCENTAGE_RISK"
    FIXED_MONETARY_RISK = "FIXED_MONETARY_RISK"
    VOLATILITY_ADJUSTED = "VOLATILITY_ADJUSTED"


class RiskRuleStatus(str, Enum):
    """Evaluation outcome for risk management rules."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class PositionEligibility(str, Enum):
    """Eligibility state for capital allocation and position sizing."""

    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE_INSUFFICIENT_CAPITAL = "INELIGIBLE_INSUFFICIENT_CAPITAL"
    INELIGIBLE_EXPOSURE_VIOLATION = "INELIGIBLE_EXPOSURE_VIOLATION"
    INELIGIBLE_REWARD_RISK_TOO_LOW = "INELIGIBLE_REWARD_RISK_TOO_LOW"
