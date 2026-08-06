"""
Project GOAT v0.7 — Scientific Evidence Synthesis Engine Package
"""

from goat.synthesis.cluster import EvidenceCluster, compute_cluster_id
from goat.synthesis.context import EvidenceSynthesisContext
from goat.synthesis.contradiction import (
    ContradictionRecord,
    EvidenceContradictionDetector,
    compute_contradiction_id,
)
from goat.synthesis.engine import (
    EvidenceSynthesisEngine,
    EvidenceSynthesisValidationError,
)
from goat.synthesis.enums import ContradictionSeverity, ReplicationQuality
from goat.synthesis.model import (
    EvidenceSynthesis,
    compute_synthesis_fingerprint,
    compute_synthesis_id,
)
from goat.synthesis.replication import EvidenceReplicationEngine, ReplicationRecord
from goat.synthesis.reporting import EvidenceSynthesisReport, generate_synthesis_report
from goat.synthesis.sqlite import SQLiteSynthesisRepository

__all__ = [
    # Enums
    "ContradictionSeverity",
    "ReplicationQuality",
    # Domain Models & Identities
    "EvidenceSynthesis",
    "compute_synthesis_id",
    "compute_synthesis_fingerprint",
    "EvidenceCluster",
    "compute_cluster_id",
    "ContradictionRecord",
    "compute_contradiction_id",
    "ReplicationRecord",
    "EvidenceSynthesisContext",
    # Subsystems & Engine Services
    "EvidenceContradictionDetector",
    "EvidenceReplicationEngine",
    "EvidenceSynthesisEngine",
    "EvidenceSynthesisValidationError",
    # Persistence & Reporting
    "SQLiteSynthesisRepository",
    "EvidenceSynthesisReport",
    "generate_synthesis_report",
]
