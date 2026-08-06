"""
Project GOAT v0.9 — Core Enums for Observation & Evidence Subsystem
"""

from enum import Enum


class ObservationStatus(str, Enum):
    """Lifecycle status of a scientific observation."""

    CREATED = "CREATED"
    COLLECTED = "COLLECTED"
    VERIFIED = "VERIFIED"
    LINKED = "LINKED"
    ARCHIVED = "ARCHIVED"


class ObservationSource(str, Enum):
    """Origin source of a scientific observation."""

    LIVE_MARKET = "LIVE_MARKET"
    REPLAY = "REPLAY"
    SIMULATION = "SIMULATION"
    MANUAL = "MANUAL"


class EvidenceCategory(str, Enum):
    """Category classification of scientific evidence."""

    PRICE = "PRICE"
    VOLATILITY = "VOLATILITY"
    STRUCTURE = "STRUCTURE"
    LIQUIDITY = "LIQUIDITY"
    MICROSTRUCTURE = "MICROSTRUCTURE"
    TIME = "TIME"
    BROKER = "BROKER"
    OTHER = "OTHER"
