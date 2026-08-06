"""
Project GOAT v0.7 — Scientific Research Program Engine Package
"""

from goat.programs.audit import ProgramAuditEvent
from goat.programs.context import ProgramContext
from goat.programs.coordinator import ProgramCoordinator, ProgramValidationError
from goat.programs.design import ProgramDesign, compute_program_design_id
from goat.programs.enums import MilestoneStatus, ProgramStatus
from goat.programs.milestone import ProgramMilestone, compute_milestone_id
from goat.programs.model import (
    ScientificResearchProgram,
    compute_program_fingerprint,
    compute_program_id,
)
from goat.programs.registry import ProgramStudyRecord, ProgramStudyRegistry
from goat.programs.reporting import ProgramReport, generate_program_report
from goat.programs.result import ProgramResult, compute_program_result_id
from goat.programs.sqlite import SQLiteProgramRepository

__all__ = [
    # Enums
    "ProgramStatus",
    "MilestoneStatus",
    # Domain Models & Identities
    "ScientificResearchProgram",
    "compute_program_id",
    "compute_program_fingerprint",
    "ProgramDesign",
    "compute_program_design_id",
    "ProgramMilestone",
    "compute_milestone_id",
    "ProgramStudyRecord",
    "ProgramStudyRegistry",
    "ProgramResult",
    "compute_program_result_id",
    "ProgramContext",
    # Coordinator & Audit
    "ProgramCoordinator",
    "ProgramValidationError",
    "ProgramAuditEvent",
    # Persistence & Reporting
    "SQLiteProgramRepository",
    "ProgramReport",
    "generate_program_report",
]
