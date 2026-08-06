"""
Project GOAT v0.9 — Core Enums for Edge Promotion & Retirement Governance Subsystem
"""

from enum import Enum


class EdgeStatus(str, Enum):
    """Lifecycle status of a quantitative trading edge candidate."""

    RESEARCH = "RESEARCH"
    VALIDATING = "VALIDATING"
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    RETIRED = "RETIRED"
    ARCHIVED = "ARCHIVED"


class GovernanceDecisionOutcome(str, Enum):
    """Constitutional decision outcome regarding edge promotion, retention, or retirement."""

    PROMOTE = "PROMOTE"
    RETAIN = "RETAIN"
    PAUSE = "PAUSE"
    RETURN_TO_RESEARCH = "RETURN_TO_RESEARCH"
    RETIRE = "RETIRE"


class GovernanceReason(str, Enum):
    """Constitutional and scientific rationale categories for governance decisions."""

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    LIVE_CONFIRMATION = "LIVE_CONFIRMATION"
    EXPECTANCY_DEGRADATION = "EXPECTANCY_DEGRADATION"
    STRUCTURAL_SHIFT = "STRUCTURAL_SHIFT"
    BROKER_FRICTION = "BROKER_FRICTION"
    CAPITAL_INCOMPATIBILITY = "CAPITAL_INCOMPATIBILITY"
    RESEARCH_PROTOCOL = "RESEARCH_PROTOCOL"
    CONSTITUTIONAL_RULE = "CONSTITUTIONAL_RULE"
