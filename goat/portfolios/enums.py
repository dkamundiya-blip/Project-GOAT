"""
Project GOAT v0.7 — Scientific Portfolio Enums

Defines PortfolioStatus enum for research portfolio lifecycles.
"""

from __future__ import annotations

from enum import Enum


class PortfolioStatus(str, Enum):
    """Lifecycle status of a ScientificResearchPortfolio."""

    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ARCHIVED = "archived"
