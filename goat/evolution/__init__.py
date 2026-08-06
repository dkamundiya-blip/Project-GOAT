"""
Project GOAT v0.7 — Knowledge Evolution Engine Package
"""

from goat.evolution.context import KnowledgeEvolutionContext
from goat.evolution.engine import (
    KnowledgeEvolutionEngine,
    KnowledgeEvolutionValidationError,
)
from goat.evolution.enums import KnowledgeEvolutionType
from goat.evolution.lineage import KnowledgeLineageGraph
from goat.evolution.model import (
    KnowledgeEvolution,
    compute_evolution_fingerprint,
    compute_evolution_id,
)
from goat.evolution.reporting import KnowledgeEvolutionReport, generate_evolution_report
from goat.evolution.sqlite import SQLiteEvolutionRepository
from goat.evolution.version import KnowledgeVersion, compute_version_id

__all__ = [
    # Enums
    "KnowledgeEvolutionType",
    # Domain Models & Identities
    "KnowledgeEvolution",
    "compute_evolution_id",
    "compute_evolution_fingerprint",
    "KnowledgeVersion",
    "compute_version_id",
    "KnowledgeLineageGraph",
    "KnowledgeEvolutionContext",
    # Subsystems & Engine Services
    "KnowledgeEvolutionEngine",
    "KnowledgeEvolutionValidationError",
    # Persistence & Reporting
    "SQLiteEvolutionRepository",
    "KnowledgeEvolutionReport",
    "generate_evolution_report",
]
