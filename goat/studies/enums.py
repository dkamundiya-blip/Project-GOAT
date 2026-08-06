"""
Project GOAT v0.7 — Scientific Study Enums

Defines StudyStatus enum for research study lifecycles.
"""

from __future__ import annotations

from enum import Enum


class StudyStatus(str, Enum):
    """Lifecycle status of a ScientificStudy."""

    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ARCHIVED = "archived"
