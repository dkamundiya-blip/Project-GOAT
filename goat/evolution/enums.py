"""
Project GOAT v0.7 — Knowledge Evolution Enums

Defines KnowledgeEvolutionType enum for scientific knowledge version transitions.
"""

from __future__ import annotations

from enum import Enum


class KnowledgeEvolutionType(str, Enum):
    """Transition classifications for scientific knowledge evolution."""

    CREATED = "created"
    REFINED = "refined"
    EXPANDED = "expanded"
    STRENGTHENED = "strengthened"
    WEAKENED = "weakened"
    SUPERSEDED = "superseded"
    RETIRED = "retired"
