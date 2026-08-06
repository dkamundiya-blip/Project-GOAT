"""
Project GOAT v0.7 — Scientific Consensus Engine Package
"""

from goat.consensus.conflict import ConsensusConflict, compute_conflict_id
from goat.consensus.context import ConsensusContext
from goat.consensus.engine import ConsensusEngine, ConsensusValidationError
from goat.consensus.enums import ConsensusStatus
from goat.consensus.model import (
    ScientificConsensus,
    compute_consensus_fingerprint,
    compute_consensus_id,
)
from goat.consensus.reporting import ConsensusReport, generate_consensus_report
from goat.consensus.rules import ConsensusRuleEngine
from goat.consensus.sqlite import SQLiteConsensusRepository

__all__ = [
    # Enums
    "ConsensusStatus",
    # Domain Models & Identities
    "ScientificConsensus",
    "compute_consensus_id",
    "compute_consensus_fingerprint",
    "ConsensusConflict",
    "compute_conflict_id",
    "ConsensusContext",
    # Subsystems & Rule Services
    "ConsensusRuleEngine",
    "ConsensusEngine",
    "ConsensusValidationError",
    # Persistence & Reporting
    "SQLiteConsensusRepository",
    "ConsensusReport",
    "generate_consensus_report",
]
