"""
Project GOAT v0.7 — Scientific Planning Enums

Defines ScientificPlanStage enum representing stages in a scientific plan execution lifecycle.
"""

from __future__ import annotations

from enum import Enum


class ScientificPlanStage(str, Enum):
    """Execution stages of a ScientificPlan."""

    INITIALIZATION = "initialization"
    LITERATURE_REVIEW = "literature_review"
    DATA_PREPARATION = "data_preparation"
    EXPERIMENT_DESIGN = "experiment_design"
    EXECUTION = "execution"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    REVIEW = "review"
    COMPLETED = "completed"
