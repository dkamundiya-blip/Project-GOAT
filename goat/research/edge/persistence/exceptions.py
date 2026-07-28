"""
Project GOAT v0.6 — Persistence Error Taxonomy

Defines explicit exception hierarchy for Edge Registry storage operations.
Translates SQLite-specific errors into domain-meaningful persistence errors.
"""

from __future__ import annotations


class EdgePersistenceError(Exception):
    """Base exception for all Edge Registry persistence failures."""


class SchemaVersionError(EdgePersistenceError):
    """Raised when database schema version is incompatible or missing."""


class PersistenceIntegrityError(EdgePersistenceError):
    """Raised when a foreign key constraint or structural integrity rule fails."""


class IdentityConflictError(EdgePersistenceError):
    """Raised when an entity with an existing ID has a conflicting scientific identity payload."""


class EvidenceConflictError(EdgePersistenceError):
    """Raised when an atomic evidence record with an existing evidence_id has a conflicting evidence_payload_hash."""


class RecordNotFoundError(EdgePersistenceError):
    """Raised when a requested record is not found in the persistence store."""
