"""
Project GOAT v0.7 — Research Prioritization Enums

Defines PriorityLevel and ResearchOpportunityType enums for scientific research prioritization.
"""

from __future__ import annotations

from enum import Enum


class PriorityLevel(str, Enum):
    """Priority level classification for research opportunities."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ResearchOpportunityType(str, Enum):
    """Categorization of scientific research opportunities."""

    REPLICATION_REQUIRED = "replication_required"
    CONFLICT_RESOLUTION = "conflict_resolution"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    KNOWLEDGE_REFINEMENT = "knowledge_refinement"
    KNOWLEDGE_VALIDATION = "knowledge_validation"
    CONSENSUS_REVIEW = "consensus_review"
