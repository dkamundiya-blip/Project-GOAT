"""
Project GOAT v0.7 — Scientific Experiment Enums

Defines ExperimentStatus, HypothesisStatus, and ExperimentOutcome enums for experimental science.
"""

from __future__ import annotations

from enum import Enum


class ExperimentStatus(str, Enum):
    """Lifecycle status of a ScientificExperiment."""

    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ABORTED = "aborted"
    ARCHIVED = "archived"


class HypothesisStatus(str, Enum):
    """Lifecycle status of a research Hypothesis."""

    PROPOSED = "proposed"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ExperimentOutcome(str, Enum):
    """Outcome classification of an executed ScientificExperiment."""

    VALIDATED = "validated"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"
