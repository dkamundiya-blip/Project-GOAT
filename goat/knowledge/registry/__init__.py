"""
Project GOAT v0.7 — Knowledge Registry Package
"""

from goat.knowledge.registry.model import KnowledgeAuditEvent, KnowledgeRegistryRecord
from goat.knowledge.registry.service import KnowledgeRegistry, KnowledgeValidationError
from goat.knowledge.registry.sqlite import (
    KnowledgeRegistryVerifier,
    SQLiteKnowledgeRepository,
)

__all__ = [
    "KnowledgeRegistryRecord",
    "KnowledgeAuditEvent",
    "SQLiteKnowledgeRepository",
    "KnowledgeRegistryVerifier",
    "KnowledgeRegistry",
    "KnowledgeValidationError",
]
