"""
Project GOAT v0.6 — Edge Registry Persistence Package
"""

from goat.research.edge.persistence.exceptions import (
    EdgePersistenceError,
    EvidenceConflictError,
    IdentityConflictError,
    PersistenceIntegrityError,
    RecordNotFoundError,
    SchemaVersionError,
)
from goat.research.edge.persistence.schema import (
    CURRENT_SCHEMA_VERSION,
    initialize_database,
)
from goat.research.edge.persistence.sqlite import SQLiteEdgeRepository

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "EdgePersistenceError",
    "EvidenceConflictError",
    "IdentityConflictError",
    "PersistenceIntegrityError",
    "RecordNotFoundError",
    "SQLiteEdgeRepository",
    "SchemaVersionError",
    "initialize_database",
]
