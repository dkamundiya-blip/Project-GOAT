"""
Project GOAT v0.7 — Scientific Plan Task Model

Defines the immutable ScientificPlanTask model (PTK_<HEX16>) representing granular planning tasks in a research plan.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from goat.planning.enums import ScientificPlanStage
from goat.research.edge.canonical import compute_canonical_sha256


def compute_task_id(plan_id: str, execution_order: int, stage: str) -> tuple[str, str]:
    """Compute deterministic Task ID (PTK_<HEX16>) and full SHA-256 task hash.

    Args:
        plan_id: Parent Plan ID (PLN_<HEX16>).
        execution_order: 1-indexed execution order integer.
        stage: ScientificPlanStage string.

    Returns:
        Tuple of (task_id, task_hash).
    """
    payload = {
        "execution_order": int(execution_order),
        "plan_id": str(plan_id).strip(),
        "stage": str(stage).strip().lower(),
    }
    digest = compute_canonical_sha256(payload)
    task_id = f"PTK_{digest[:16].upper()}"
    return task_id, digest


class ScientificPlanTask(BaseModel):
    """Immutable planning task artifact representing a single step within a scientific plan."""

    task_id: str = Field(
        ...,
        description="Unique Task ID formatted as PTK_<HEX16>",
        pattern=r"^PTK_[A-Fa-f0-9]{16}$",
    )
    parent_plan_id: str = Field(..., description="Parent Plan ID (PLN_<HEX16>)")
    stage: ScientificPlanStage = Field(..., description="Plan execution stage classification")
    dependencies: list[str] = Field(default_factory=list, description="Prerequisite Task IDs (PTK_<HEX16>)")
    assigned_study_id: str = Field(default="", description="Assigned Study ID (STD_<HEX16>) if applicable")
    assigned_experiment_id: str = Field(default="", description="Assigned Experiment ID (EXP_<HEX16>) if applicable")
    execution_order: int = Field(default=1, ge=1, description="1-indexed execution order position")
    status: str = Field(default="pending", description="Task status ('pending', 'completed', 'failed')")
    task_hash: str = Field(..., description="Full 64-character SHA-256 canonical task hash digest")

    class Config:
        frozen = True
        extra = "forbid"
