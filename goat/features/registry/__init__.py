"""
Project GOAT v0.7 — Feature Registry Package

Exposes Registry models, SQLite storage repository, verifier, and FeatureRegistryService.
"""

from goat.features.registry.model import (
    RegistrationStatus,
    RegistryAuditEvent,
    RegistryRecord,
    ValidationStatus,
)
from goat.features.registry.service import FeatureRegistryService
from goat.features.registry.sqlite import (
    FeatureRegistryVerifier,
    SQLiteFeatureRepository,
)

__all__ = [
    "RegistrationStatus",
    "ValidationStatus",
    "RegistryRecord",
    "RegistryAuditEvent",
    "SQLiteFeatureRepository",
    "FeatureRegistryVerifier",
    "FeatureRegistryService",
]
