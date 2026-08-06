"""
Project GOAT v0.7 — Scientific Research Prioritization Engine Package
"""

from goat.prioritization.context import ResearchPrioritizationContext
from goat.prioritization.engine import (
    ResearchPrioritizationEngine,
    ResearchPriorityValidationError,
)
from goat.prioritization.enums import PriorityLevel, ResearchOpportunityType
from goat.prioritization.model import (
    ResearchPriority,
    compute_priority_fingerprint,
    compute_priority_id,
)
from goat.prioritization.queue import ResearchPriorityQueue, compute_queue_id
from goat.prioritization.reporting import ResearchPriorityReport, generate_priority_report
from goat.prioritization.rules import ResearchPriorityRuleEngine
from goat.prioritization.sqlite import SQLitePrioritizationRepository

__all__ = [
    # Enums
    "PriorityLevel",
    "ResearchOpportunityType",
    # Domain Models & Identities
    "ResearchPriority",
    "compute_priority_id",
    "compute_priority_fingerprint",
    "ResearchPriorityQueue",
    "compute_queue_id",
    "ResearchPrioritizationContext",
    # Subsystems & Rule Services
    "ResearchPriorityRuleEngine",
    "ResearchPrioritizationEngine",
    "ResearchPriorityValidationError",
    # Persistence & Reporting
    "SQLitePrioritizationRepository",
    "ResearchPriorityReport",
    "generate_priority_report",
]
