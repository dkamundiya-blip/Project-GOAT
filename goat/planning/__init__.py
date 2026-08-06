"""
Project GOAT v0.7 — Scientific Planning Engine Package
"""

from goat.planning.context import ScientificPlanningContext
from goat.planning.engine import (
    ScientificPlanningEngine,
    ScientificPlanningValidationError,
)
from goat.planning.enums import ScientificPlanStage
from goat.planning.graph import ScientificPlanningGraph
from goat.planning.model import (
    ScientificPlan,
    compute_plan_fingerprint,
    compute_plan_id,
)
from goat.planning.reporting import ScientificPlanningReport, generate_planning_report
from goat.planning.sqlite import SQLitePlanningRepository
from goat.planning.task import ScientificPlanTask, compute_task_id

__all__ = [
    # Enums
    "ScientificPlanStage",
    # Domain Models & Identities
    "ScientificPlan",
    "compute_plan_id",
    "compute_plan_fingerprint",
    "ScientificPlanTask",
    "compute_task_id",
    "ScientificPlanningGraph",
    "ScientificPlanningContext",
    # Subsystems & Engine Services
    "ScientificPlanningEngine",
    "ScientificPlanningValidationError",
    # Persistence & Reporting
    "SQLitePlanningRepository",
    "ScientificPlanningReport",
    "generate_planning_report",
]
