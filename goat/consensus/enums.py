"""
Project GOAT v0.7 — Scientific Consensus Enums

Defines ConsensusStatus enum representing scientific consensus assessment states.
"""

from __future__ import annotations

from enum import Enum


class ConsensusStatus(str, Enum):
    """Lifecycle and confidence state of a ScientificConsensus."""

    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    EMERGING = "emerging"
    MODERATE = "moderate"
    STRONG = "strong"
    CONSENSUS = "consensus"
    CONFLICTED = "conflicted"
    SUPERSEDED = "superseded"
