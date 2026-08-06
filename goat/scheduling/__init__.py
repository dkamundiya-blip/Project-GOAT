"""
Project GOAT v0.7 — Scientific Research Scheduling Package
"""

from goat.scheduling.context import ScientificSchedulingContext
from goat.scheduling.coordinator import ScientificScheduleCoordinator
from goat.scheduling.engine import (
    ScientificResearchScheduler,
    ScientificSchedulingValidationError,
    VALID_STATE_TRANSITIONS,
)
from goat.scheduling.enums import ScheduleExecutionState
from goat.scheduling.model import (
    ResearchSchedule,
    compute_schedule_fingerprint,
    compute_schedule_id,
)
from goat.scheduling.reporting import (
    ScientificSchedulingReport,
    generate_scheduling_report,
)
from goat.scheduling.sqlite import SQLiteSchedulingRepository, SCHEDULING_SCHEMA_VERSION
from goat.scheduling.task import ScheduledTask, compute_scheduled_task_id

__all__ = [
    # Enums
    "ScheduleExecutionState",
    # Domain Models & Identities
    "ResearchSchedule",
    "compute_schedule_id",
    "compute_schedule_fingerprint",
    "ScheduledTask",
    "compute_scheduled_task_id",
    "ScientificSchedulingContext",
    # Subsystems & Engine Services
    "ScientificResearchScheduler",
    "ScientificScheduleCoordinator",
    "ScientificSchedulingValidationError",
    "VALID_STATE_TRANSITIONS",
    # Persistence & Reporting
    "SQLiteSchedulingRepository",
    "SCHEDULING_SCHEMA_VERSION",
    "ScientificSchedulingReport",
    "generate_scheduling_report",
]
