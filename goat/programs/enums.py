"""
Project GOAT v0.7 — Scientific Research Program Enums

Defines ProgramStatus and MilestoneStatus enums for research program lifecycles.
"""

from __future__ import annotations

from enum import Enum


class ProgramStatus(str, Enum):
    """Lifecycle status of a ScientificResearchProgram."""

    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ARCHIVED = "archived"


class MilestoneStatus(str, Enum):
    """Status of a ProgramMilestone."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    FAILED = "failed"
